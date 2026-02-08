"""Attendance service — absences-only approach."""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import Select, and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.attendance import Absence
from src.models.schedule import ScheduleEntry

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

    absence = Absence(user_id=user_id, schedule_entry_id=schedule_entry_id)
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


def _past_entries_query(
    user_id: int,
    subject_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Select:
    """Build base query for past schedule entries with absence status.

    Args:
        user_id: User ID for checking absences.
        subject_id: Optional filter by subject_id.
        date_from: Optional start date.
        date_to: Optional end date.

    Returns:
        SQLAlchemy select statement.
    """
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
        .where(ScheduleEntry.lesson_date <= date.today())
        .order_by(ScheduleEntry.lesson_date.desc(), ScheduleEntry.start_time.desc())
    )

    if subject_id is not None:
        query = query.where(ScheduleEntry.subject_id == subject_id)
    if date_from is not None:
        query = query.where(ScheduleEntry.lesson_date >= date_from)
    if date_to is not None:
        query = query.where(ScheduleEntry.lesson_date <= date_to)

    return query


async def get_attendance_entries(
    db: AsyncSession,
    user_id: int,
    subject_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict]:
    """Get past schedule entries with attendance status.

    Args:
        db: Database session.
        user_id: Current user ID.
        subject_id: Optional filter by subject.
        date_from: Optional start date filter.
        date_to: Optional end date filter.

    Returns:
        List of dicts with entry data and is_absent flag.
    """
    query = _past_entries_query(user_id, subject_id, date_from, date_to)
    result = await db.execute(query)

    entries = []
    for row in result.all():
        entry: ScheduleEntry = row[0]
        absence_id: int | None = row[1]
        entries.append({
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
        })
    return entries


async def get_attendance_stats(
    db: AsyncSession,
    user_id: int,
) -> dict:
    """Get overall attendance statistics plus per-subject breakdown.

    Args:
        db: Database session.
        user_id: Current user ID.

    Returns:
        Dict with total_classes, absences, attended, attendance_percent, by_subject.
    """
    # Overall stats
    total_result = await db.execute(
        select(func.count(ScheduleEntry.id)).where(
            and_(
                ScheduleEntry.lesson_date.isnot(None),
                ScheduleEntry.lesson_date <= date.today(),
            )
        )
    )
    total_classes = total_result.scalar() or 0

    absences_result = await db.execute(
        select(func.count(Absence.id)).where(Absence.user_id == user_id)
    )
    total_absences = absences_result.scalar() or 0

    attended = total_classes - total_absences
    percent = (attended / total_classes * 100) if total_classes > 0 else 100.0

    # Per-subject breakdown
    subject_stats_query = (
        select(
            ScheduleEntry.subject_name,
            ScheduleEntry.subject_id,
            func.count(ScheduleEntry.id).label("total"),
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
                ScheduleEntry.lesson_date <= date.today(),
            )
        )
        .group_by(ScheduleEntry.subject_name, ScheduleEntry.subject_id)
        .order_by(ScheduleEntry.subject_name)
    )
    subject_result = await db.execute(subject_stats_query)

    by_subject = []
    for row in subject_result.all():
        subj_total = row[2]
        subj_absent = row[3]
        subj_attended = subj_total - subj_absent
        subj_percent = (subj_attended / subj_total * 100) if subj_total > 0 else 100.0
        by_subject.append({
            "subject_name": row[0],
            "subject_id": row[1],
            "total_classes": subj_total,
            "absences": subj_absent,
            "attended": subj_attended,
            "attendance_percent": round(subj_percent, 1),
        })

    return {
        "total_classes": total_classes,
        "absences": total_absences,
        "attended": attended,
        "attendance_percent": round(percent, 1),
        "by_subject": by_subject,
    }


async def get_subject_attendance_stats(
    db: AsyncSession,
    user_id: int,
    subject_id: int,
) -> dict | None:
    """Get attendance stats for a single subject.

    Args:
        db: Database session.
        user_id: Current user ID.
        subject_id: Subject ID.

    Returns:
        Dict with subject stats or None if no entries found.
    """
    total_result = await db.execute(
        select(
            ScheduleEntry.subject_name,
            func.count(ScheduleEntry.id),
        )
        .where(
            and_(
                ScheduleEntry.subject_id == subject_id,
                ScheduleEntry.lesson_date.isnot(None),
                ScheduleEntry.lesson_date <= date.today(),
            )
        )
        .group_by(ScheduleEntry.subject_name)
    )
    total_row = total_result.one_or_none()
    if total_row is None:
        return None

    subject_name = total_row[0]
    total_classes = total_row[1]

    absences_result = await db.execute(
        select(func.count(Absence.id))
        .join(ScheduleEntry, Absence.schedule_entry_id == ScheduleEntry.id)
        .where(
            and_(
                Absence.user_id == user_id,
                ScheduleEntry.subject_id == subject_id,
            )
        )
    )
    absences = absences_result.scalar() or 0
    attended = total_classes - absences
    percent = (attended / total_classes * 100) if total_classes > 0 else 100.0

    return {
        "subject_name": subject_name,
        "subject_id": subject_id,
        "total_classes": total_classes,
        "absences": absences,
        "attended": attended,
        "attendance_percent": round(percent, 1),
    }
