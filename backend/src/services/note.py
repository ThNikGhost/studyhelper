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
) -> tuple[LessonNote, bool]:
    """Create or update a lesson note (upsert by subject_name).

    If schedule_entry_id is provided, auto-fills subject_name and lesson_date
    from the entry. If a note for the same (user_id, subject_name) already
    exists, updates its content (and optionally schedule_entry_id/lesson_date).

    Args:
        db: Database session.
        user_id: Current user ID.
        data: Note creation data.

    Returns:
        Tuple of (LessonNote, created) where created is True if new.

    Raises:
        ValueError: If schedule entry not found.
    """
    subject_name = data.subject_name
    lesson_date = data.lesson_date
    schedule_entry_id = data.schedule_entry_id

    if schedule_entry_id is not None:
        entry = await db.get(ScheduleEntry, schedule_entry_id)
        if entry is None:
            raise ValueError("Schedule entry not found")

        # Auto-fill from entry
        subject_name = entry.subject_name
        lesson_date = entry.lesson_date

    # Check for existing note by (user_id, subject_name)
    existing = await db.execute(
        select(LessonNote).where(
            and_(
                LessonNote.user_id == user_id,
                LessonNote.subject_name == subject_name,
            )
        )
    )
    note = existing.scalar_one_or_none()

    if note is not None:
        # Update existing note
        note.content = data.content
        if schedule_entry_id is not None:
            note.schedule_entry_id = schedule_entry_id
        if lesson_date is not None:
            note.lesson_date = lesson_date
        await db.flush()
        await db.commit()
        await db.refresh(note)
        return note, False

    # Create new note
    note = LessonNote(
        user_id=user_id,
        schedule_entry_id=schedule_entry_id,
        subject_name=subject_name,
        lesson_date=lesson_date,
        content=data.content,
    )
    db.add(note)
    await db.flush()
    await db.commit()
    await db.refresh(note)
    return note, True


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


async def get_note_for_subject(
    db: AsyncSession,
    user_id: int,
    subject_name: str,
) -> LessonNote | None:
    """Get a user's note for a specific subject.

    Args:
        db: Database session.
        user_id: Current user ID.
        subject_name: Subject name.

    Returns:
        LessonNote or None if not found.
    """
    result = await db.execute(
        select(LessonNote).where(
            and_(
                LessonNote.user_id == user_id,
                LessonNote.subject_name == subject_name,
            )
        )
    )
    return result.scalar_one_or_none()


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
