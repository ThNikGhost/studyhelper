"""Widget service layer.

Handles API key CRUD and next lesson lookup for phone widgets.
"""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.schedule import ScheduleEntry
from src.models.semester import Semester
from src.models.user import User
from src.models.widget_api_key import WidgetApiKey
from src.schemas.widget import (
    NextLessonResponse,
    TodayLessonItem,
    TodayScheduleResponse,
)
from src.services.schedule import get_schedule_entries_by_date_range
from src.utils.location import format_location
from src.utils.schedule_filters import filter_entries_by_user_prefs

logger = logging.getLogger(__name__)

OMSK_TZ = ZoneInfo(settings.timezone)

TOKEN_LENGTH = 48  # secrets.token_urlsafe(48) -> ~64 chars

LESSON_TYPE_NAMES = {
    "lecture": "Лекция",
    "practice": "Практика",
    "lab": "Лаб",
    "seminar": "Семинар",
    "exam": "Экзамен",
    "consultation": "Консультация",
    "other": "Другое",
}

LOOKAHEAD_DAYS = 7


# --- Token CRUD ---


async def get_key_by_user(
    db: AsyncSession,
    user_id: int,
) -> WidgetApiKey | None:
    """Get widget API key for a user."""
    result = await db.execute(
        select(WidgetApiKey).where(WidgetApiKey.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_key_by_token(
    db: AsyncSession,
    token: str,
) -> WidgetApiKey | None:
    """Get widget API key by public token."""
    result = await db.execute(select(WidgetApiKey).where(WidgetApiKey.token == token))
    return result.scalar_one_or_none()


async def create_or_regenerate_key(
    db: AsyncSession,
    user_id: int,
) -> WidgetApiKey:
    """Create a new widget API key or regenerate token for existing one.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        WidgetApiKey with a fresh token.
    """
    key = await get_key_by_user(db, user_id)
    new_token = secrets.token_urlsafe(TOKEN_LENGTH)

    if key is None:
        key = WidgetApiKey(user_id=user_id, token=new_token)
        db.add(key)
    else:
        key.token = new_token

    await db.flush()
    await db.commit()
    await db.refresh(key)
    return key


async def revoke_key(
    db: AsyncSession,
    user_id: int,
) -> bool:
    """Revoke (delete) widget API key for user.

    Returns:
        True if key existed and was removed, False otherwise.
    """
    key = await get_key_by_user(db, user_id)
    if key is None:
        return False
    await db.delete(key)
    await db.commit()
    return True


async def update_last_used(
    db: AsyncSession,
    key: WidgetApiKey,
) -> None:
    """Update last_used_at timestamp (throttled to once per hour)."""
    now = datetime.now(UTC)
    if key.last_used_at is not None and (now - key.last_used_at) < timedelta(hours=1):
        return
    key.last_used_at = now
    await db.flush()
    await db.commit()


# --- Token Authentication ---


async def _authenticate_by_token(
    db: AsyncSession,
    token: str,
) -> User | None:
    """Authenticate by widget API token and return the associated user.

    Looks up the token, validates the user, and updates last_used timestamp.

    Args:
        db: Database session.
        token: Widget API key token.

    Returns:
        User if token is valid, None otherwise.
    """
    key = await get_key_by_token(db, token)
    if key is None:
        return None

    result = await db.execute(select(User).where(User.id == key.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None

    await update_last_used(db, key)
    return user


async def get_next_lesson_by_token(
    db: AsyncSession,
    token: str,
) -> NextLessonResponse | None:
    """Authenticate by token, update last_used, and return next lesson.

    Args:
        db: Database session.
        token: Widget API key token.

    Returns:
        NextLessonResponse if token is valid, None otherwise.
    """
    user = await _authenticate_by_token(db, token)
    if user is None:
        return None
    return await get_next_lesson(db, user)


# --- Next Lesson Logic ---


def _build_location(entry: ScheduleEntry) -> str | None:
    """Build location string from room and building."""
    return format_location(entry.building, entry.room)


async def get_next_lesson(
    db: AsyncSession,
    user: User,
) -> NextLessonResponse:
    """Get the next upcoming lesson for the widget.

    Looks ahead up to LOOKAHEAD_DAYS days from today.

    Args:
        db: Database session.
        user: User whose preferences to apply.

    Returns:
        NextLessonResponse with next lesson data or no_more_lessons=True.
    """
    now = datetime.now(OMSK_TZ)
    today = now.date()
    end_date = today + timedelta(days=LOOKAHEAD_DAYS)
    cached_at = now.strftime("%Y-%m-%dT%H:%M:%S")

    # Check for current semester
    result = await db.execute(
        select(Semester).where(Semester.is_current.is_(True)).limit(1)
    )
    semester = result.scalar_one_or_none()
    if semester is None:
        return NextLessonResponse(no_more_lessons=True, cached_at=cached_at)

    # Load all entries for the lookahead range in one query
    entries = await get_schedule_entries_by_date_range(db, today, end_date)

    # Filter by user preferences (subgroup, PE teacher)
    filtered = filter_entries_by_user_prefs(entries, user)

    if not filtered:
        return NextLessonResponse(no_more_lessons=True, cached_at=cached_at)

    # Find next entry: today with start_time > now, or first entry on a future day
    current_time = now.time()

    for entry in filtered:
        if entry.lesson_date is None:
            continue

        entry_is_today = entry.lesson_date == today

        if entry_is_today and entry.start_time <= current_time:
            # This lesson already started or has passed
            continue

        # Found the next lesson
        lesson_type_name = LESSON_TYPE_NAMES.get(entry.lesson_type, entry.lesson_type)

        # Calculate minutes until lesson
        entry_dt = datetime.combine(entry.lesson_date, entry.start_time, tzinfo=OMSK_TZ)
        minutes_until = int((entry_dt - now).total_seconds() / 60)

        return NextLessonResponse(
            subject=entry.subject_name,
            time_start=entry.start_time.strftime("%H:%M"),
            time_end=entry.end_time.strftime("%H:%M"),
            location=_build_location(entry),
            teacher=entry.teacher_name,
            minutes_until=max(0, minutes_until),
            lesson_type=lesson_type_name,
            is_today=entry_is_today,
            cached_at=cached_at,
        )

    return NextLessonResponse(no_more_lessons=True, cached_at=cached_at)


# --- Today Schedule ---


def _build_lesson_item(entry: ScheduleEntry) -> TodayLessonItem:
    """Convert a ScheduleEntry into a TodayLessonItem."""
    return TodayLessonItem(
        subject=entry.subject_name,
        time_start=entry.start_time.strftime("%H:%M"),
        time_end=entry.end_time.strftime("%H:%M"),
        location=_build_location(entry),
        teacher=entry.teacher_name,
        lesson_type=LESSON_TYPE_NAMES.get(entry.lesson_type, entry.lesson_type),
    )


async def get_today_schedule(
    db: AsyncSession,
    user: User,
) -> TodayScheduleResponse:
    """Get all today's lessons plus first future lesson for offline widget.

    Args:
        db: Database session.
        user: User whose preferences to apply.

    Returns:
        TodayScheduleResponse with all today's lessons and optional future lesson.
    """
    now = datetime.now(OMSK_TZ)
    today = now.date()
    end_date = today + timedelta(days=LOOKAHEAD_DAYS)
    cached_at = now.strftime("%Y-%m-%dT%H:%M:%S")

    empty_response = TodayScheduleResponse(
        date=today.isoformat(),
        lessons=[],
        cached_at=cached_at,
    )

    # Check for current semester
    result = await db.execute(
        select(Semester).where(Semester.is_current.is_(True)).limit(1)
    )
    semester = result.scalar_one_or_none()
    if semester is None:
        return empty_response

    # Load all entries for the lookahead range
    entries = await get_schedule_entries_by_date_range(db, today, end_date)

    # Filter by user preferences (subgroup, PE teacher)
    filtered = filter_entries_by_user_prefs(entries, user)

    if not filtered:
        return empty_response

    # Split into today and future
    today_entries = [e for e in filtered if e.lesson_date == today]
    future_entries = [
        e for e in filtered if e.lesson_date is not None and e.lesson_date > today
    ]

    today_lessons = [_build_lesson_item(e) for e in today_entries]

    # First future lesson (entries are already sorted by date/time)
    next_future: TodayLessonItem | None = None
    next_future_date: str | None = None
    next_day_remaining: list[TodayLessonItem] = []
    if future_entries:
        next_future = _build_lesson_item(future_entries[0])
        next_future_date = future_entries[0].lesson_date.isoformat()
        # Up to 3 remaining lessons on the same day as the next future lesson
        next_day_remaining = [
            _build_lesson_item(e)
            for e in future_entries[1:4]
            if e.lesson_date == future_entries[0].lesson_date
        ]

    return TodayScheduleResponse(
        date=today.isoformat(),
        lessons=today_lessons,
        next_lesson_from_future=next_future,
        next_lesson_date=next_future_date,
        next_day_remaining=next_day_remaining,
        cached_at=cached_at,
    )


async def get_today_schedule_by_token(
    db: AsyncSession,
    token: str,
) -> TodayScheduleResponse | None:
    """Authenticate by token, update last_used, and return today schedule.

    Args:
        db: Database session.
        token: Widget API key token.

    Returns:
        TodayScheduleResponse if token is valid, None otherwise.
    """
    user = await _authenticate_by_token(db, token)
    if user is None:
        return None
    return await get_today_schedule(db, user)
