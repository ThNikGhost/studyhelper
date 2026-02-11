"""Attendance service — semester-based absences tracking."""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import Select, and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.attendance import Absence
from src.models.schedule import ScheduleEntry
from src.models.semester import Semester
from src.models.subject import Subject

logger = logging.getLogger(__name__)


async def mark_absent(
    db: AsyncSession,
    user_id: int,
    schedule_entry_id: int,
) -> Absence:
    """Mark a lesson as absent (insert absence record).

    Args:
        db: Database session.
        user_id: Current user ID.
        schedule_entry_id: Schedule entry ID.

    Returns:
        Created Absence record.

    Raises:
        ValueError: If entry not found, already marked, or lesson is in the future.
    """
    # Validate entry exists
    entry = await db.get(ScheduleEntry, schedule_entry_id)
    if entry is None:
        raise ValueError("Schedule entry not found")

    # Validate lesson_date is not in the future
    if entry.lesson_date is not None and entry.lesson_date > date.today():
        raise ValueError("Cannot mark future lessons as absent")

    # Check for duplicate
    existing = await db.execute(
        select(Absence).where(
            and_(
                Absence.user_id == user_id,
                Absence.schedule_entry_id == schedule_entry_id,
            )
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError("Already marked as absent")

    absence = Absence(
        user_id=user_id,
        schedule_entry_id=schedule_entry_id,
        subject_name=entry.subject_name,
        lesson_date=entry.lesson_date,
    )
    db.add(absence)
    await db.flush()
    await db.commit()
    await db.refresh(absence)
    return absence


async def mark_present(
    db: AsyncSession,
    user_id: int,
    schedule_entry_id: int,
) -> bool:
    """Mark a lesson as present (delete absence record).

    Args:
        db: Database session.
        user_id: Current user ID.
        schedule_entry_id: Schedule entry ID.

    Returns:
        True if an absence record was deleted, False if none found.
    """
    result = await db.execute(
        delete(Absence).where(
            and_(
                Absence.user_id == user_id,
                Absence.schedule_entry_id == schedule_entry_id,
            )
        )
    )
    await db.commit()
    return result.rowcount > 0  # type: ignore[union-attr]


def _get_completed_filter(today: date, current_time: time) -> Select:
    """Build filter for completed lessons.

    A lesson is completed if:
    - lesson_date < today (yesterday or earlier), OR
    - lesson_date == today AND end_time <= current_time

    Args:
        today: Current date.
        current_time: Current time.

    Returns:
        SQLAlchemy filter condition.
    """
    return or_(
        ScheduleEntry.lesson_date < today,
        and_(
            ScheduleEntry.lesson_date == today,
            ScheduleEntry.end_time <= current_time,
        ),
    )


def _completed_entries_query(
    user_id: int,
    semester_start: date,
    semester_end: date,
    today: date,
    current_time: time,
    subject_id: int | None = None,
) -> Select:
    """Build base query for completed schedule entries with absence status.

    Args:
        user_id: User ID for checking absences.
        semester_start: Semester start date.
        semester_end: Semester end date.
        today: Current date.
        current_time: Current time.
        subject_id: Optional filter by subject_id.

    Returns:
        SQLAlchemy select statement.
    """
    completed_filter = _get_completed_filter(today, current_time)

    query = (
        select(
            ScheduleEntry,
            Absence.id.label("absence_id"),
        )
        .outerjoin(
            Absence,
            and_(
                Absence.schedule_entry_id == ScheduleEntry.id,
                Absence.user_id == user_id,
            ),
        )
        .where(ScheduleEntry.lesson_date.isnot(None))
        .where(ScheduleEntry.lesson_date >= semester_start)
        .where(ScheduleEntry.lesson_date <= semester_end)
        .where(completed_filter)
        .order_by(ScheduleEntry.lesson_date.desc(), ScheduleEntry.start_time.desc())
    )

    if subject_id is not None:
        query = query.where(ScheduleEntry.subject_id == subject_id)

    return query


async def get_attendance_entries(
    db: AsyncSession,
    user_id: int,
    semester_id: int,
    subject_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Get completed schedule entries with attendance status for a semester.

    Args:
        db: Database session.
        user_id: Current user ID.
        semester_id: Semester ID (required).
        subject_id: Optional filter by subject.
        limit: Maximum number of entries to return.
        offset: Number of entries to skip.

    Returns:
        List of dicts with entry data and is_absent flag.

    Raises:
        ValueError: If semester not found or has no dates set.
    """
    # Get semester with dates
    semester = await db.get(Semester, semester_id)
    if semester is None:
        raise ValueError("Semester not found")
    if semester.start_date is None or semester.end_date is None:
        raise ValueError("Semester dates not set")

    # Get current time in local timezone
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    today = now.date()
    current_time = now.time()

    query = _completed_entries_query(
        user_id=user_id,
        semester_start=semester.start_date,
        semester_end=semester.end_date,
        today=today,
        current_time=current_time,
        subject_id=subject_id,
    )
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)

    entries = []
    for row in result.all():
        entry: ScheduleEntry = row[0]
        absence_id: int | None = row[1]
        entries.append(
            {
                "id": entry.id,
                "lesson_date": str(entry.lesson_date) if entry.lesson_date else None,
                "subject_name": entry.subject_name,
                "lesson_type": entry.lesson_type,
                "start_time": str(entry.start_time) if entry.start_time else None,
                "end_time": str(entry.end_time) if entry.end_time else None,
                "teacher_name": entry.teacher_name,
                "room": entry.room,
                "subject_id": entry.subject_id,
                "is_absent": absence_id is not None,
                "absence_id": absence_id,
            }
        )
    return entries


async def get_attendance_stats(
    db: AsyncSession,
    user_id: int,
    semester_id: int,
) -> dict:
    """Get overall attendance statistics plus per-subject breakdown for a semester.

    Uses planned_classes from Subject for total, and counts completed lessons
    for attendance calculation.

    Args:
        db: Database session.
        user_id: Current user ID.
        semester_id: Semester ID (required).

    Returns:
        Dict with total_planned, total_completed, absences, attended,
        attendance_percent, by_subject.

    Raises:
        ValueError: If semester not found or has no dates set.
    """
    # Get semester with dates
    semester = await db.get(Semester, semester_id)
    if semester is None:
        raise ValueError("Semester not found")
    if semester.start_date is None or semester.end_date is None:
        raise ValueError("Semester dates not set")

    # Get current time in local timezone
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    today = now.date()
    current_time = now.time()

    completed_filter = _get_completed_filter(today, current_time)

    # Get all subjects for semester with planned_classes
    subjects_result = await db.execute(
        select(Subject.id, Subject.name, Subject.planned_classes).where(
            Subject.semester_id == semester_id
        )
    )
    subjects = subjects_result.all()

    # Total planned classes from Subject.planned_classes
    total_planned = sum(s.planned_classes or 0 for s in subjects)

    # Build subject name to planned_classes mapping
    subject_planned: dict[str, int] = {}
    for s in subjects:
        if s.planned_classes:
            subject_planned[s.name] = s.planned_classes

    # Count completed lessons in semester
    total_completed_result = await db.execute(
        select(func.count(ScheduleEntry.id)).where(
            and_(
                ScheduleEntry.lesson_date.isnot(None),
                ScheduleEntry.lesson_date >= semester.start_date,
                ScheduleEntry.lesson_date <= semester.end_date,
                completed_filter,
            )
        )
    )
    total_completed = total_completed_result.scalar() or 0

    # Count absences for completed lessons in semester
    absences_result = await db.execute(
        select(func.count(Absence.id))
        .join(ScheduleEntry, Absence.schedule_entry_id == ScheduleEntry.id)
        .where(
            and_(
                Absence.user_id == user_id,
                ScheduleEntry.lesson_date >= semester.start_date,
                ScheduleEntry.lesson_date <= semester.end_date,
                completed_filter,
            )
        )
    )
    total_absences = absences_result.scalar() or 0

    # Attended = completed - absences
    attended = total_completed - total_absences

    # Calculate percentage based on total_planned (if set) or total_completed
    if total_planned > 0:
        percent = attended / total_planned * 100
    elif total_completed > 0:
        percent = attended / total_completed * 100
    else:
        percent = 0.0

    # Per-subject breakdown
    subject_stats_query = (
        select(
            ScheduleEntry.subject_name,
            ScheduleEntry.subject_id,
            func.count(ScheduleEntry.id).label("completed"),
            func.count(Absence.id).label("absent_count"),
        )
        .outerjoin(
            Absence,
            and_(
                Absence.schedule_entry_id == ScheduleEntry.id,
                Absence.user_id == user_id,
            ),
        )
        .where(
            and_(
                ScheduleEntry.lesson_date.isnot(None),
                ScheduleEntry.lesson_date >= semester.start_date,
                ScheduleEntry.lesson_date <= semester.end_date,
                completed_filter,
            )
        )
        .group_by(ScheduleEntry.subject_name, ScheduleEntry.subject_id)
        .order_by(ScheduleEntry.subject_name)
    )
    subject_result = await db.execute(subject_stats_query)

    by_subject = []
    for row in subject_result.all():
        subj_name = row[0]
        subj_id = row[1]
        subj_completed = row[2]
        subj_absent = row[3]
        subj_attended = subj_completed - subj_absent

        # Use planned_classes if available, otherwise use completed count
        subj_planned = subject_planned.get(subj_name, 0)
        if subj_planned > 0:
            subj_percent = subj_attended / subj_planned * 100
        elif subj_completed > 0:
            subj_percent = subj_attended / subj_completed * 100
        else:
            subj_percent = 0.0

        by_subject.append(
            {
                "subject_name": subj_name,
                "subject_id": subj_id,
                "planned_classes": subj_planned,
                "total_classes": subj_completed,  # completed lessons
                "absences": subj_absent,
                "attended": subj_attended,
                "attendance_percent": round(subj_percent, 1),
            }
        )

    return {
        "total_planned": total_planned,
        "total_completed": total_completed,
        "total_classes": total_completed,  # backwards compat
        "absences": total_absences,
        "attended": attended,
        "attendance_percent": round(percent, 1),
        "by_subject": by_subject,
    }


async def get_subject_attendance_stats(
    db: AsyncSession,
    user_id: int,
    subject_id: int,
    semester_id: int,
) -> dict | None:
    """Get attendance stats for a single subject in a semester.

    Args:
        db: Database session.
        user_id: Current user ID.
        subject_id: Subject ID.
        semester_id: Semester ID (required).

    Returns:
        Dict with subject stats or None if no entries found.

    Raises:
        ValueError: If semester not found or has no dates set.
    """
    # Get semester with dates
    semester = await db.get(Semester, semester_id)
    if semester is None:
        raise ValueError("Semester not found")
    if semester.start_date is None or semester.end_date is None:
        raise ValueError("Semester dates not set")

    # Get current time in local timezone
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    today = now.date()
    current_time = now.time()

    completed_filter = _get_completed_filter(today, current_time)

    # Get subject with planned_classes
    subject = await db.get(Subject, subject_id)
    if subject is None:
        return None

    total_result = await db.execute(
        select(
            ScheduleEntry.subject_name,
            func.count(ScheduleEntry.id),
        )
        .where(
            and_(
                ScheduleEntry.subject_id == subject_id,
                ScheduleEntry.lesson_date.isnot(None),
                ScheduleEntry.lesson_date >= semester.start_date,
                ScheduleEntry.lesson_date <= semester.end_date,
                completed_filter,
            )
        )
        .group_by(ScheduleEntry.subject_name)
    )
    total_row = total_result.one_or_none()
    if total_row is None:
        return None

    subject_name = total_row[0]
    completed_count = total_row[1]

    absences_result = await db.execute(
        select(func.count(Absence.id))
        .join(ScheduleEntry, Absence.schedule_entry_id == ScheduleEntry.id)
        .where(
            and_(
                Absence.user_id == user_id,
                ScheduleEntry.subject_id == subject_id,
                ScheduleEntry.lesson_date >= semester.start_date,
                ScheduleEntry.lesson_date <= semester.end_date,
                completed_filter,
            )
        )
    )
    absences = absences_result.scalar() or 0
    attended = completed_count - absences

    planned = subject.planned_classes or 0
    if planned > 0:
        percent = attended / planned * 100
    elif completed_count > 0:
        percent = attended / completed_count * 100
    else:
        percent = 0.0

    return {
        "subject_name": subject_name,
        "subject_id": subject_id,
        "planned_classes": planned,
        "total_classes": completed_count,
        "absences": absences,
        "attended": attended,
        "attendance_percent": round(percent, 1),
    }
