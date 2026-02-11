"""Subject service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.subject import Subject
from src.schemas.subject import SubjectCreate, SubjectUpdate


async def get_subjects(
    db: AsyncSession, semester_id: int | None = None
) -> list[Subject]:
    """Get all subjects, optionally filtered by semester."""
    query = select(Subject).options(selectinload(Subject.semester))

    if semester_id is not None:
        query = query.where(Subject.semester_id == semester_id)

    query = query.order_by(Subject.name)
    result = await db.execute(query)
    return list(result.scalars().all())


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
