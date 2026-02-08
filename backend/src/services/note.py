"""Lesson note service — CRUD for user notes on schedule entries."""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.note import LessonNote
from src.models.schedule import ScheduleEntry
from src.schemas.note import LessonNoteCreate

logger = logging.getLogger(__name__)


async def create_note(
    db: AsyncSession,
    user_id: int,
    data: LessonNoteCreate,
) -> LessonNote:
    """Create a new lesson note.

    If schedule_entry_id is provided, auto-fills subject_name and lesson_date
    from the entry. Also checks for duplicate (user+entry).

    Args:
        db: Database session.
        user_id: Current user ID.
        data: Note creation data.

    Returns:
        Created LessonNote.

    Raises:
        ValueError: If entry not found or duplicate note exists.
    """
    subject_name = data.subject_name
    lesson_date = data.lesson_date

    if data.schedule_entry_id is not None:
        entry = await db.get(ScheduleEntry, data.schedule_entry_id)
        if entry is None:
            raise ValueError("Schedule entry not found")

        # Auto-fill from entry
        subject_name = entry.subject_name
        lesson_date = entry.lesson_date

        # Check for duplicate
        existing = await db.execute(
            select(LessonNote).where(
                and_(
                    LessonNote.user_id == user_id,
                    LessonNote.schedule_entry_id == data.schedule_entry_id,
                )
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise ValueError("Note already exists for this entry")

    note = LessonNote(
        user_id=user_id,
        schedule_entry_id=data.schedule_entry_id,
        subject_name=subject_name,
        lesson_date=lesson_date,
        content=data.content,
    )
    db.add(note)
    await db.flush()
    await db.commit()
    await db.refresh(note)
    return note


async def update_note(
    db: AsyncSession,
    user_id: int,
    note_id: int,
    content: str,
) -> LessonNote | None:
    """Update a lesson note content.

    Args:
        db: Database session.
        user_id: Current user ID (ownership check).
        note_id: Note ID to update.
        content: New content.

    Returns:
        Updated LessonNote or None if not found/not owned.
    """
    note = await db.get(LessonNote, note_id)
    if note is None or note.user_id != user_id:
        return None

    note.content = content
    await db.flush()
    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(
    db: AsyncSession,
    user_id: int,
    note_id: int,
) -> bool:
    """Delete a lesson note.

    Args:
        db: Database session.
        user_id: Current user ID (ownership check).
        note_id: Note ID to delete.

    Returns:
        True if deleted, False if not found/not owned.
    """
    note = await db.get(LessonNote, note_id)
    if note is None or note.user_id != user_id:
        return False

    await db.delete(note)
    await db.commit()
    return True


async def get_notes(
    db: AsyncSession,
    user_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    subject_name: str | None = None,
    search: str | None = None,
) -> list[LessonNote]:
    """Get lesson notes with optional filters.

    Args:
        db: Database session.
        user_id: Current user ID.
        date_from: Optional start date filter.
        date_to: Optional end date filter.
        subject_name: Optional subject name filter.
        search: Optional text search in content.

    Returns:
        List of matching LessonNote objects.
    """
    query = (
        select(LessonNote)
        .where(LessonNote.user_id == user_id)
        .order_by(LessonNote.updated_at.desc())
    )

    if date_from is not None:
        query = query.where(LessonNote.lesson_date >= date_from)
    if date_to is not None:
        query = query.where(LessonNote.lesson_date <= date_to)
    if subject_name is not None:
        query = query.where(LessonNote.subject_name == subject_name)
    if search is not None:
        query = query.where(LessonNote.content.ilike(f"%{search}%"))

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_note_for_entry(
    db: AsyncSession,
    user_id: int,
    schedule_entry_id: int,
) -> LessonNote | None:
    """Get a user's note for a specific schedule entry.

    Args:
        db: Database session.
        user_id: Current user ID.
        schedule_entry_id: Schedule entry ID.

    Returns:
        LessonNote or None if not found.
    """
    result = await db.execute(
        select(LessonNote).where(
            and_(
                LessonNote.user_id == user_id,
                LessonNote.schedule_entry_id == schedule_entry_id,
            )
        )
    )
    return result.scalar_one_or_none()
