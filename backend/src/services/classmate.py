"""Classmate service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.classmate import Classmate
from src.schemas.classmate import ClassmateCreate, ClassmateUpdate


async def get_classmates(db: AsyncSession) -> list[Classmate]:
    """Get all classmates ordered by full name."""
    result = await db.execute(select(Classmate).order_by(Classmate.full_name))
    return list(result.scalars().all())


async def get_classmate_by_id(db: AsyncSession, classmate_id: int) -> Classmate | None:
    """Get classmate by ID."""
    result = await db.execute(select(Classmate).where(Classmate.id == classmate_id))
    return result.scalar_one_or_none()


async def create_classmate(db: AsyncSession, data: ClassmateCreate) -> Classmate:
    """Create a new classmate."""
    classmate = Classmate(
        full_name=data.full_name,
        short_name=data.short_name,
        email=data.email,
        phone=data.phone,
        telegram=data.telegram,
        vk=str(data.vk) if data.vk else None,
        photo_url=str(data.photo_url) if data.photo_url else None,
        group_name=data.group_name,
        subgroup=data.subgroup,
        notes=data.notes,
    )
    db.add(classmate)
    await db.commit()
    await db.refresh(classmate)
    return classmate


async def update_classmate(
    db: AsyncSession, classmate: Classmate, data: ClassmateUpdate
) -> Classmate:
    """Update classmate."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ("vk", "photo_url") and value is not None:
            value = str(value)
        setattr(classmate, field, value)
    await db.commit()
    await db.refresh(classmate)
    return classmate


async def delete_classmate(db: AsyncSession, classmate: Classmate) -> None:
    """Delete classmate."""
    await db.delete(classmate)
    await db.commit()
