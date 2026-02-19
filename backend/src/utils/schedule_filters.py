"""Shared schedule entry filtering utilities."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import ScheduleEntry
from src.models.subject import Subject
from src.models.user import User


async def resolve_hidden_subjects(
    db: AsyncSession,
    user: User,
) -> dict[str, set[str] | None]:
    """Resolve hidden subject config to {name: types} mapping.

    Args:
        db: Database session.
        user: User whose hidden subjects to resolve.

    Returns:
        Dict mapping subject name to hidden lesson types (None = all hidden).
    """
    if not user.hidden_subjects:
        return {}
    ids = [int(k) for k in user.hidden_subjects]
    result = await db.execute(
        select(Subject.id, Subject.name).where(Subject.id.in_(ids))
    )
    id_to_name = {row.id: row.name for row in result.all()}
    return {
        id_to_name[int(k)]: (set(v) if v else None)
        for k, v in user.hidden_subjects.items()
        if int(k) in id_to_name
    }


def filter_entries_by_user_prefs(
    entries: list[ScheduleEntry],
    user: User,
    hidden_subjects: dict[str, set[str] | None] | None = None,
) -> list[ScheduleEntry]:
    """Filter schedule entries by user subgroup, PE teacher, and hidden subjects.

    Args:
        entries: List of schedule entries to filter.
        user: User whose preferences to apply.
        hidden_subjects: Pre-resolved hidden subject config
            ({name: types} where types=None means hide all).

    Returns:
        Filtered list of schedule entries.
    """
    filtered = []
    for entry in entries:
        # Subgroup filter: show if entry has no subgroup or matches user's
        if (
            user.preferred_subgroup is not None
            and entry.subgroup is not None
            and entry.subgroup != user.preferred_subgroup
        ):
            continue

        # PE teacher filter
        if (
            user.preferred_pe_teacher is not None
            and entry.subject_name
            and "физическ" in entry.subject_name.lower()
            and entry.teacher_name
            and entry.teacher_name != user.preferred_pe_teacher
        ):
            continue

        # Hidden subjects filter (by name, since schedule entries lack subject_id)
        if (
            hidden_subjects
            and entry.subject_name
            and entry.subject_name in hidden_subjects
        ):
            types = hidden_subjects[entry.subject_name]
            if types is None or entry.lesson_type in types:
                continue

        filtered.append(entry)
    return filtered
