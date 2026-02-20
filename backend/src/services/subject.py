"""Subject service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.schedule import ScheduleEntry
from src.models.subject import Subject
from src.schemas.subject import SubjectCreate, SubjectUpdate


async def _get_subject_lesson_types(
    db: AsyncSession, subjects: list[Subject]
) -> dict[int, list[str]]:
    """Get unique lesson types per subject from schedule entries.

    Uses subject_name matching since subject_id is always NULL in ScheduleEntry.

    Args:
        db: Database session.
        subjects: List of Subject objects to get lesson types for.

    Returns:
        Dictionary mapping subject_id to list of lesson types.
    """
    if not subjects:
        return {}

    # Build map: subject_name → subject_id
    name_to_id = {s.name: s.id for s in subjects}

    # Query: get all (subject_name, lesson_type) pairs
    # Note: ScheduleEntry.subject_id is always NULL (parser doesn't fill it)
    # We fetch all entries and group/deduplicate in Python (works with both SQLite and PostgreSQL)
    query = (
        select(ScheduleEntry.subject_name, ScheduleEntry.lesson_type)
        .where(ScheduleEntry.subject_name.in_(list(name_to_id.keys())))
        .distinct()  # Get unique combinations
    )

    result = await db.execute(query)
    rows = result.all()

    # Group by subject_name → collect lesson_types
    types_by_name: dict[str, list[str]] = {}
    for subject_name, lesson_type in rows:
        if subject_name not in types_by_name:
            types_by_name[subject_name] = []
        types_by_name[subject_name].append(lesson_type)

    # Map back: subject_name → subject_id → lesson_types
    return {
        name_to_id[subject_name]: lesson_types
        for subject_name, lesson_types in types_by_name.items()
        if subject_name in name_to_id
    }


async def get_subjects(
    db: AsyncSession, semester_id: int | None = None
) -> list[Subject]:
    """Get all subjects, optionally filtered by semester."""
    query = select(Subject).options(selectinload(Subject.semester))

    if semester_id is not None:
        query = query.where(Subject.semester_id == semester_id)

    query = query.order_by(Subject.name)
    result = await db.execute(query)
    subjects = list(result.scalars().all())

    # Compute lesson_types for subjects
    if subjects:
        lesson_types_map = await _get_subject_lesson_types(db, subjects)

        # Attach lesson_types to subjects (temporary attribute for serialization)
        for subject in subjects:
            # Set computed attribute (not in DB, only for Pydantic serialization)
            subject.lesson_types = lesson_types_map.get(subject.id, [])

    return subjects


async def get_subject_by_id(
    db: AsyncSession, subject_id: int, with_semester: bool = False
) -> Subject | None:
    """Get subject by ID."""
    query = select(Subject).where(Subject.id == subject_id)

    if with_semester:
        query = query.options(selectinload(Subject.semester))

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_subject(db: AsyncSession, subject_data: SubjectCreate) -> Subject:
    """Create a new subject."""
    subject = Subject(
        name=subject_data.name,
        short_name=subject_data.short_name,
        description=subject_data.description,
        semester_id=subject_data.semester_id,
        planned_classes=subject_data.planned_classes,
    )
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return subject


async def update_subject(
    db: AsyncSession, subject: Subject, subject_data: SubjectUpdate
) -> Subject:
    """Update subject."""
    update_data = subject_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subject, field, value)
    await db.commit()
    await db.refresh(subject)
    return subject


async def delete_subject(db: AsyncSession, subject: Subject) -> None:
    """Delete subject."""
    await db.delete(subject)
    await db.commit()
