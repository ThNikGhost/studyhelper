"""Shared schedule entry filtering utilities."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import ScheduleEntry
from src.models.subject import Subject
from src.models.user import User


async def resolve_hidden_subject_names(
    db: AsyncSession,
    user: User,
) -> set[str]:
    """Resolve hidden subject IDs to subject names.

    Args:
        db: Database session.
        user: User whose hidden subjects to resolve.

    Returns:
        Set of subject names that should be hidden.
    """
    if not user.hidden_subjects:
        return set()
    result = await db.execute(
        select(Subject.name).where(Subject.id.in_(user.hidden_subjects))
    )
    return set(result.scalars().all())


def filter_entries_by_user_prefs(
    entries: list[ScheduleEntry],
    user: User,
    hidden_subject_names: set[str] | None = None,
) -> list[ScheduleEntry]:
    """Filter schedule entries by user subgroup, PE teacher, and hidden subjects.

    Args:
        entries: List of schedule entries to filter.
        user: User whose preferences to apply.
        hidden_subject_names: Pre-resolved hidden subject names.

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
            hidden_subject_names
            and entry.subject_name
            and entry.subject_name in hidden_subject_names
        ):
            continue

        filtered.append(entry)
    return filtered
