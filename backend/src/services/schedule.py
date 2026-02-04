"""Schedule service."""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schedule import ScheduleEntry, ScheduleSnapshot
from src.schemas.schedule import (
    CurrentLessonResponse,
    DayOfWeek,
    DayScheduleResponse,
    ScheduleEntryCreate,
    ScheduleEntryResponse,
    ScheduleEntryUpdate,
    ScheduleSnapshotCreate,
    WeekScheduleResponse,
)

if TYPE_CHECKING:
    from src.parser.omsu_parser import ParseResult

logger = logging.getLogger(__name__)

DAY_NAMES_RU = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


def get_week_number(d: date) -> int:
    """Get ISO week number."""
    return d.isocalendar()[1]


def is_odd_week(d: date) -> bool:
    """Check if the given date falls on an odd week."""
    return get_week_number(d) % 2 == 1


def get_week_bounds(d: date) -> tuple[date, date]:
    """Get start (Monday) and end (Sunday) of the week containing the date."""
    day_of_week = d.isoweekday()  # Monday=1, Sunday=7
    week_start = d - timedelta(days=day_of_week - 1)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


# Schedule Entry operations
async def get_schedule_entries(
    db: AsyncSession,
    day_of_week: int | None = None,
    week_type: str | None = None,
) -> list[ScheduleEntry]:
    """Get schedule entries with optional filters."""
    query = select(ScheduleEntry).order_by(
        ScheduleEntry.day_of_week, ScheduleEntry.start_time
    )

    conditions = []
    if day_of_week is not None:
        conditions.append(ScheduleEntry.day_of_week == day_of_week)

    if week_type is not None:
        # Include entries for specific week type OR entries without week type (both weeks)
        conditions.append(
            (ScheduleEntry.week_type == week_type) | (ScheduleEntry.week_type.is_(None))
        )

    if conditions:
        query = query.where(and_(*conditions))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_schedule_entry_by_id(
    db: AsyncSession, entry_id: int
) -> ScheduleEntry | None:
    """Get schedule entry by ID."""
    result = await db.execute(select(ScheduleEntry).where(ScheduleEntry.id == entry_id))
    return result.scalar_one_or_none()


async def create_schedule_entry(
    db: AsyncSession, data: ScheduleEntryCreate
) -> ScheduleEntry:
    """Create a new schedule entry."""
    entry = ScheduleEntry(
        day_of_week=data.day_of_week.value,
        start_time=data.start_time,
        end_time=data.end_time,
        week_type=data.week_type.value if data.week_type else None,
        subject_name=data.subject_name,
        lesson_type=data.lesson_type.value,
        teacher_name=data.teacher_name,
        room=data.room,
        building=data.building,
        group_name=data.group_name,
        subgroup=data.subgroup,
        notes=data.notes,
        subject_id=data.subject_id,
        teacher_id=data.teacher_id,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def update_schedule_entry(
    db: AsyncSession, entry: ScheduleEntry, data: ScheduleEntryUpdate
) -> ScheduleEntry:
    """Update schedule entry."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if (
            field == "day_of_week"
            and value is not None
            or field == "week_type"
            and value is not None
            or field == "lesson_type"
            and value is not None
        ):
            value = value.value
        setattr(entry, field, value)
    await db.commit()
    await db.refresh(entry)
    return entry


async def delete_schedule_entry(db: AsyncSession, entry: ScheduleEntry) -> None:
    """Delete schedule entry."""
    await db.delete(entry)
    await db.commit()


# High-level schedule operations
async def get_today_schedule(
    db: AsyncSession, target_date: date | None = None
) -> DayScheduleResponse:
    """Get schedule for today (or specified date)."""
    if target_date is None:
        target_date = datetime.now(UTC).date()

    day_of_week = target_date.isoweekday()
    week_type = "odd" if is_odd_week(target_date) else "even"

    entries = await get_schedule_entries(
        db, day_of_week=day_of_week, week_type=week_type
    )

    return DayScheduleResponse(
        date=target_date,
        day_of_week=DayOfWeek(day_of_week),
        day_name=DAY_NAMES_RU[day_of_week],
        entries=[ScheduleEntryResponse.model_validate(e) for e in entries],
    )


async def get_week_schedule(
    db: AsyncSession, target_date: date | None = None
) -> WeekScheduleResponse:
    """Get schedule for the week containing the specified date."""
    if target_date is None:
        target_date = datetime.now(UTC).date()

    week_start, week_end = get_week_bounds(target_date)
    week_number = get_week_number(target_date)
    odd_week = is_odd_week(target_date)
    week_type = "odd" if odd_week else "even"

    # Get all entries for this week type
    entries = await get_schedule_entries(db, week_type=week_type)

    # Group entries by day
    days: list[DayScheduleResponse] = []
    for day_num in range(1, 8):  # Monday to Sunday
        day_date = week_start + timedelta(days=day_num - 1)
        day_entries = [e for e in entries if e.day_of_week == day_num]

        days.append(
            DayScheduleResponse(
                date=day_date,
                day_of_week=DayOfWeek(day_num),
                day_name=DAY_NAMES_RU[day_num],
                entries=[ScheduleEntryResponse.model_validate(e) for e in day_entries],
            )
        )

    return WeekScheduleResponse(
        week_start=week_start,
        week_end=week_end,
        week_number=week_number,
        is_odd_week=odd_week,
        days=days,
    )


async def get_current_lesson(db: AsyncSession) -> CurrentLessonResponse:
    """Get current and next lesson."""
    now = datetime.now(UTC)
    current_date = now.date()
    current_time = now.time()
    day_of_week = current_date.isoweekday()
    week_type = "odd" if is_odd_week(current_date) else "even"

    # Get today's entries
    today_entries = await get_schedule_entries(
        db, day_of_week=day_of_week, week_type=week_type
    )

    current_lesson = None
    next_lesson = None

    for entry in today_entries:
        if entry.start_time <= current_time <= entry.end_time:
            current_lesson = entry
        elif entry.start_time > current_time and next_lesson is None:
            next_lesson = entry
            break

    # Calculate time until next lesson
    time_until_next = None
    if next_lesson:
        next_datetime = datetime.combine(current_date, next_lesson.start_time)
        now_naive = datetime.combine(current_date, current_time)
        diff = next_datetime - now_naive
        time_until_next = int(diff.total_seconds() // 60)

    return CurrentLessonResponse(
        current=ScheduleEntryResponse.model_validate(current_lesson)
        if current_lesson
        else None,
        next=ScheduleEntryResponse.model_validate(next_lesson) if next_lesson else None,
        time_until_next=time_until_next,
    )


# Schedule Snapshot operations
async def get_snapshots(db: AsyncSession, limit: int = 10) -> list[ScheduleSnapshot]:
    """Get recent schedule snapshots."""
    result = await db.execute(
        select(ScheduleSnapshot)
        .order_by(ScheduleSnapshot.snapshot_date.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_latest_snapshot(db: AsyncSession) -> ScheduleSnapshot | None:
    """Get the most recent schedule snapshot."""
    result = await db.execute(
        select(ScheduleSnapshot)
        .order_by(ScheduleSnapshot.snapshot_date.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_snapshot(
    db: AsyncSession, data: ScheduleSnapshotCreate
) -> ScheduleSnapshot:
    """Create a new schedule snapshot."""
    snapshot = ScheduleSnapshot(
        snapshot_date=data.snapshot_date,
        content_hash=data.content_hash,
        raw_data=data.raw_data,
        source_url=data.source_url,
        entries_count=data.entries_count,
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return snapshot


# Parser integration functions
async def parse_schedule(url: str | None = None) -> ParseResult:
    """Parse schedule from OmGU API.

    Args:
        url: Schedule API URL. Defaults to constructed from group_id.

    Returns:
        ParseResult with parsed entries and metadata.

    Raises:
        ParserException: If parsing fails.
    """
    from src.parser import OmsuScheduleParser

    async with OmsuScheduleParser(url=url) as parser:
        return await parser.parse()


async def _clear_schedule_entries(db: AsyncSession) -> int:
    """Delete all schedule entries.

    Args:
        db: Database session.

    Returns:
        Number of deleted entries.
    """
    result = await db.execute(delete(ScheduleEntry))
    await db.commit()
    return result.rowcount


async def sync_schedule(
    db: AsyncSession,
    force: bool = False,
    url: str | None = None,
) -> dict[str, Any]:
    """Synchronize schedule: parse, compare hash, update if changed.

    Args:
        db: Database session.
        force: Force update even if content hash unchanged.
        url: Schedule API URL. Defaults to constructed from group_id.

    Returns:
        Dictionary with sync result:
            - success: bool
            - changed: bool
            - entries_count: int
            - content_hash: str (if success)
            - message: str (error message if not success)
    """
    logger.info("Starting schedule sync (force=%s)", force)

    try:
        # Parse schedule
        parse_result = await parse_schedule(url=url)

        if parse_result.entries_count == 0:
            logger.warning("No entries parsed from schedule")
            return {
                "success": False,
                "changed": False,
                "entries_count": 0,
                "message": "No entries parsed from schedule",
            }

        # Check if content changed
        latest_snapshot = await get_latest_snapshot(db)
        if (
            latest_snapshot
            and latest_snapshot.content_hash == parse_result.content_hash
        ):
            if not force:
                logger.info(
                    "Schedule unchanged (hash: %s...)", parse_result.content_hash[:8]
                )
                return {
                    "success": True,
                    "changed": False,
                    "entries_count": latest_snapshot.entries_count,
                    "content_hash": parse_result.content_hash,
                    "message": "Schedule unchanged",
                }
            logger.info("Force sync requested, updating despite unchanged hash")

        # Clear existing entries
        deleted_count = await _clear_schedule_entries(db)
        logger.info("Deleted %d existing entries", deleted_count)

        # Create new entries
        for entry_data in parse_result.entries:
            await create_schedule_entry(db, entry_data)

        # Create snapshot
        snapshot_data = ScheduleSnapshotCreate(
            snapshot_date=parse_result.parsed_date,
            content_hash=parse_result.content_hash,
            raw_data=json.dumps(parse_result.raw_data, ensure_ascii=False),
            source_url=parse_result.source_url,
            entries_count=parse_result.entries_count,
        )
        await create_snapshot(db, snapshot_data)

        logger.info(
            "Schedule synced: %d entries, hash: %s...",
            parse_result.entries_count,
            parse_result.content_hash[:8],
        )

        return {
            "success": True,
            "changed": True,
            "entries_count": parse_result.entries_count,
            "content_hash": parse_result.content_hash,
            "message": "Schedule updated successfully",
        }

    except Exception as e:
        logger.error("Schedule sync failed: %s", e, exc_info=True)
        return {
            "success": False,
            "changed": False,
            "entries_count": 0,
            "message": str(e),
        }
