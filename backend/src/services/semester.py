"""Semester service."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.schedule import ScheduleEntry
from src.models.semester import Semester
from src.models.subject import Subject
from src.models.work import Work
from src.schemas.semester import (
    SemesterCreate,
    SemesterUpdate,
    TimelineDeadline,
    TimelineExam,
    TimelineResponse,
)


async def get_semesters(db: AsyncSession) -> list[Semester]:
    """Get all semesters ordered by year and number."""
    result = await db.execute(
        select(Semester).order_by(Semester.year_start.desc(), Semester.number.desc())
    )
    return list(result.scalars().all())


async def get_semester_by_id(db: AsyncSession, semester_id: int) -> Semester | None:
    """Get semester by ID."""
    result = await db.execute(select(Semester).where(Semester.id == semester_id))
    return result.scalar_one_or_none()


async def get_current_semester(db: AsyncSession) -> Semester | None:
    """Get current semester."""
    result = await db.execute(select(Semester).where(Semester.is_current.is_(True)))
    return result.scalar_one_or_none()


async def create_semester(db: AsyncSession, semester_data: SemesterCreate) -> Semester:
    """Create a new semester."""
    semester = Semester(
        number=semester_data.number,
        year_start=semester_data.year_start,
        year_end=semester_data.year_end,
        name=semester_data.name,
        start_date=semester_data.start_date,
        end_date=semester_data.end_date,
        is_current=False,
    )
    db.add(semester)
    await db.commit()
    await db.refresh(semester)
    return semester


async def update_semester(
    db: AsyncSession, semester: Semester, semester_data: SemesterUpdate
) -> Semester:
    """Update semester."""
    update_data = semester_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(semester, field, value)
    await db.commit()
    await db.refresh(semester)
    return semester


async def delete_semester(db: AsyncSession, semester: Semester) -> None:
    """Delete semester."""
    await db.delete(semester)
    await db.commit()


async def set_current_semester(db: AsyncSession, semester: Semester) -> Semester:
    """Set semester as current (only one can be current)."""
    # Atomically remove current flag from all semesters
    await db.execute(
        update(Semester).where(Semester.is_current.is_(True)).values(is_current=False)
    )

    # Set new current
    semester.is_current = True
    await db.commit()
    await db.refresh(semester)
    return semester


async def get_semester_timeline(
    db: AsyncSession, semester_id: int, user_id: int
) -> TimelineResponse | None:
    """Get aggregated timeline data for a semester.

    Args:
        db: Database session.
        semester_id: Semester ID.
        user_id: Current user ID for work status lookup.

    Returns:
        TimelineResponse with deadlines and exams, or None if semester not found.

    Raises:
        ValueError: If semester has no start_date or end_date.
    """
    semester = await get_semester_by_id(db, semester_id)
    if not semester:
        return None

    if not semester.start_date or not semester.end_date:
        msg = "Semester must have start_date and end_date for timeline"
        raise ValueError(msg)

    # Get subject IDs for this semester
    subjects_result = await db.execute(
        select(Subject).where(Subject.semester_id == semester_id)
    )
    subjects = list(subjects_result.scalars().all())
    subject_ids = [s.id for s in subjects]
    subject_name_map = {s.id: s.name for s in subjects}

    # Get works with deadlines for these subjects
    deadlines: list[TimelineDeadline] = []
    if subject_ids:
        works_query = (
            select(Work)
            .options(selectinload(Work.statuses))
            .where(
                Work.subject_id.in_(subject_ids),
                Work.deadline.isnot(None),
            )
            .order_by(Work.deadline)
        )
        works_result = await db.execute(works_query)
        works = list(works_result.scalars().all())

        for work in works:
            # Find status for this user
            user_status = None
            for ws in work.statuses:
                if ws.user_id == user_id:
                    user_status = ws.status
                    break

            deadlines.append(
                TimelineDeadline(
                    work_id=work.id,
                    title=work.title,
                    work_type=work.work_type,
                    deadline=work.deadline,
                    subject_name=subject_name_map.get(work.subject_id, ""),
                    subject_id=work.subject_id,
                    status=user_status,
                )
            )

    # Get exam schedule entries within semester date range
    exams_query = (
        select(ScheduleEntry)
        .where(
            ScheduleEntry.lesson_type == "exam",
            ScheduleEntry.lesson_date.isnot(None),
            ScheduleEntry.lesson_date >= semester.start_date,
            ScheduleEntry.lesson_date <= semester.end_date,
        )
        .order_by(ScheduleEntry.lesson_date, ScheduleEntry.start_time)
    )
    exams_result = await db.execute(exams_query)
    exam_entries = list(exams_result.scalars().all())

    exams = [
        TimelineExam(
            schedule_entry_id=e.id,
            subject_name=e.subject_name,
            lesson_date=e.lesson_date,
            start_time=e.start_time,
            end_time=e.end_time,
            room=e.room,
            teacher_name=e.teacher_name,
        )
        for e in exam_entries
    ]

    return TimelineResponse(
        semester=semester,
        deadlines=deadlines,
        exams=exams,
    )
