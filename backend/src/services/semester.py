"""Semester service."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.semester import Semester
from src.schemas.semester import SemesterCreate, SemesterUpdate


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
