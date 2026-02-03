"""Teacher service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.teacher import Teacher
from src.schemas.teacher import TeacherCreate, TeacherUpdate


async def get_teachers(db: AsyncSession) -> list[Teacher]:
    """Get all teachers ordered by full name."""
    result = await db.execute(select(Teacher).order_by(Teacher.full_name))
    return list(result.scalars().all())


async def get_teacher_by_id(db: AsyncSession, teacher_id: int) -> Teacher | None:
    """Get teacher by ID."""
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    return result.scalar_one_or_none()


async def create_teacher(db: AsyncSession, teacher_data: TeacherCreate) -> Teacher:
    """Create a new teacher."""
    teacher = Teacher(
        full_name=teacher_data.full_name,
        short_name=teacher_data.short_name,
        email=teacher_data.email,
        phone=teacher_data.phone,
        department=teacher_data.department,
        position=teacher_data.position,
        office=teacher_data.office,
        notes=teacher_data.notes,
    )
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def update_teacher(
    db: AsyncSession, teacher: Teacher, teacher_data: TeacherUpdate
) -> Teacher:
    """Update teacher."""
    update_data = teacher_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(teacher, field, value)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def delete_teacher(db: AsyncSession, teacher: Teacher) -> None:
    """Delete teacher."""
    await db.delete(teacher)
    await db.commit()
