"""Telegram-specific schedule filtering utilities."""

from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.work import Work
from src.schemas.schedule import CurrentLessonResponse, DayScheduleResponse
from src.services.schedule import get_current_lesson, get_today_schedule
from src.utils.schedule_filters import (
    filter_entries_by_user_prefs,
    resolve_hidden_subjects,
)


async def get_filtered_day_schedule(
    db: AsyncSession,
    user: User,
    target_date: date | None = None,
) -> DayScheduleResponse:
    """Get day schedule filtered by user preferences.

    Applies subgroup, PE teacher, and hidden_subjects filters.

    Args:
        db: Database session.
        user: User whose preferences to apply.
        target_date: Target date (defaults to today).

    Returns:
        Day schedule with filtered entries.
    """
    # 1. Get raw schedule
    day = await get_today_schedule(db, target_date)

    # 2. Resolve hidden subjects
    hidden_config = await resolve_hidden_subjects(db, user)

    # 3. Filter entries
    filtered_entries = filter_entries_by_user_prefs(day.entries, user, hidden_config)

    # 4. Return with filtered entries
    return DayScheduleResponse(
        date=day.date,
        day_of_week=day.day_of_week,
        day_name=day.day_name,
        entries=filtered_entries,
    )


async def get_filtered_current_lesson(
    db: AsyncSession,
    user: User,
) -> CurrentLessonResponse:
    """Get current/next lesson filtered by user preferences.

    Args:
        db: Database session.
        user: User whose preferences to apply.

    Returns:
        Current lesson response with filtered entries.
    """
    # 1. Get raw current lesson data
    data = await get_current_lesson(db)

    # 2. Resolve hidden subjects
    hidden_config = await resolve_hidden_subjects(db, user)

    # 3. Helper to check if entry should be filtered
    def should_filter_entry(entry) -> bool:
        """Check if entry matches user's filtering criteria."""
        # Subgroup filter
        if (
            user.preferred_subgroup is not None
            and entry.subgroup is not None
            and entry.subgroup != user.preferred_subgroup
        ):
            return True

        # PE teacher filter
        if (
            user.preferred_pe_teacher is not None
            and entry.subject_name
            and "физическ" in entry.subject_name.lower()
            and entry.teacher_name
            and entry.teacher_name != user.preferred_pe_teacher
        ):
            return True

        # Hidden subjects filter
        if entry.subject_name and entry.subject_name in hidden_config:
            types = hidden_config[entry.subject_name]
            if types is None or entry.lesson_type.value in types:
                return True

        return False

    # 4. Filter current and next entries
    current_filtered = (
        None if data.current and should_filter_entry(data.current) else data.current
    )
    next_filtered = None if data.next and should_filter_entry(data.next) else data.next

    # 5. Return filtered response
    return CurrentLessonResponse(
        current=current_filtered,
        next=next_filtered,
        time_until_next=data.time_until_next if next_filtered else None,
    )


def filter_works_by_hidden_subjects(
    works: list[Work],
    hidden_subjects: dict[str, set[str] | None],
) -> list[Work]:
    """Filter works by fully hidden subjects only.

    Works are filtered if:
    - Subject is fully hidden (hidden_subjects[name] = None)

    Works are NOT filtered if:
    - Per-type hiding (hidden_subjects[name] = ["lab"]) — works are not lesson-type specific

    Args:
        works: List of works to filter.
        hidden_subjects: Pre-resolved hidden subject config ({name: types}).

    Returns:
        Filtered list of works.
    """
    return [
        w
        for w in works
        if not (
            w.subject
            and w.subject.name in hidden_subjects
            and hidden_subjects[w.subject.name] is None
        )
    ]
