"""Classmate service."""

from __future__ import annotations

from pydantic import HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.classmate import Classmate, ClassmateDetail
from src.schemas.classmate import (
    ClassmateCreate,
    ClassmateDetailUpsert,
    ClassmateUpdate,
)


def _url_to_str(url: HttpUrl | None) -> str | None:
    """Convert Pydantic HttpUrl to plain string for DB storage.

    Args:
        url: Pydantic HttpUrl instance or None.

    Returns:
        String representation of URL or None.
    """
    return str(url) if url else None


async def get_classmates(db: AsyncSession) -> list[Classmate]:
    """Get all classmates ordered by full name."""
    result = await db.execute(select(Classmate).order_by(Classmate.full_name))
    return list(result.scalars().all())


async def get_classmate_by_id(db: AsyncSession, classmate_id: int) -> Classmate | None:
    """Get classmate by ID."""
    result = await db.execute(select(Classmate).where(Classmate.id == classmate_id))
    return result.scalar_one_or_none()


async def get_classmate_with_details(
    db: AsyncSession, classmate_id: int, user_id: int
) -> tuple[Classmate, ClassmateDetail | None] | None:
    """Get classmate with per-user details.

    Args:
        db: Async database session.
        classmate_id: Classmate primary key.
        user_id: Current user primary key.

    Returns:
        Tuple of (Classmate, ClassmateDetail | None) or None if not found.
    """
    classmate = await get_classmate_by_id(db, classmate_id)
    if classmate is None:
        return None

    result = await db.execute(
        select(ClassmateDetail).where(
            ClassmateDetail.classmate_id == classmate_id,
            ClassmateDetail.user_id == user_id,
        )
    )
    detail = result.scalar_one_or_none()
    return classmate, detail


async def create_classmate(db: AsyncSession, data: ClassmateCreate) -> Classmate:
    """Create a new classmate."""
    classmate = Classmate(
        full_name=data.full_name,
        group_name=data.group_name,
        subgroup=data.subgroup,
    )
    db.add(classmate)
    await db.commit()
    await db.refresh(classmate)
    return classmate


async def update_classmate(
    db: AsyncSession, classmate: Classmate, data: ClassmateUpdate
) -> Classmate:
    """Update classmate base fields."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(classmate, field, value)
    await db.commit()
    await db.refresh(classmate)
    return classmate


async def delete_classmate(db: AsyncSession, classmate: Classmate) -> None:
    """Delete classmate."""
    await db.delete(classmate)
    await db.commit()


async def upsert_classmate_details(
    db: AsyncSession,
    classmate_id: int,
    user_id: int,
    data: ClassmateDetailUpsert,
) -> ClassmateDetail:
    """Create or update per-user classmate details.

    Args:
        db: Async database session.
        classmate_id: Classmate primary key.
        user_id: Current user primary key.
        data: Detail fields to set.

    Returns:
        Created or updated ClassmateDetail.
    """
    result = await db.execute(
        select(ClassmateDetail).where(
            ClassmateDetail.classmate_id == classmate_id,
            ClassmateDetail.user_id == user_id,
        )
    )
    detail = result.scalar_one_or_none()

    if detail is None:
        detail = ClassmateDetail(
            classmate_id=classmate_id,
            user_id=user_id,
            short_name=data.short_name,
            email=str(data.email) if data.email else None,
            phone=data.phone,
            telegram=data.telegram,
            vk=_url_to_str(data.vk),
            photo_url=data.photo_url,
            notes=data.notes,
        )
        db.add(detail)
    else:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "vk":
                value = _url_to_str(value)
            elif field == "email":
                value = str(value) if value else None
            setattr(detail, field, value)

    await db.commit()
    await db.refresh(detail)
    return detail
