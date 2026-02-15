"""Shared schedule entry filtering utilities."""

from __future__ import annotations

from src.models.schedule import ScheduleEntry
from src.models.user import User


def filter_entries_by_user_prefs(
    entries: list[ScheduleEntry],
    user: User,
) -> list[ScheduleEntry]:
    """Filter schedule entries by user subgroup and PE teacher preferences.

    Args:
        entries: List of schedule entries to filter.
        user: User whose preferences to apply.

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

        filtered.append(entry)
    return filtered
