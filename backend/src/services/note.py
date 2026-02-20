"""Lesson note service — CRUD for shared notes on schedule entries."""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.note import LessonNote
from src.models.schedule import ScheduleEntry
from src.schemas.note import LessonNoteCreate

logger = logging.getLogger(__name__)


async def create_note(
    db: AsyncSession,
    user_id: int,
    data: LessonNoteCreate,
) -> tuple[LessonNote, bool]:
    """Create or update a shared lesson note (upsert by subject_name).

    If schedule_entry_id is provided, auto-fills subject_name and lesson_date
    from the entry. If a note for the same subject_name already exists (from any
    user), updates its content and records user_id as the last editor.

    Args:
        db: Database session.
        user_id: Current user ID (becomes last editor).
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

    # Check for existing note by subject_name (shared across all users)
    existing = await db.execute(
        select(LessonNote)
        .where(LessonNote.subject_name == subject_name)
        .options(selectinload(LessonNote.user))
    )
    note = existing.scalar_one_or_none()

    if note is not None:
        # Update existing note, record last editor
        note.content = data.content
        note.user_id = user_id
        if schedule_entry_id is not None:
            note.schedule_entry_id = schedule_entry_id
        if lesson_date is not None:
            note.lesson_date = lesson_date
        await db.flush()
        await db.commit()
        await db.refresh(note)
        # Reload user relationship after refresh
        await db.refresh(note, attribute_names=["user"])
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
    await db.refresh(note, attribute_names=["user"])
    return note, True


async def update_note(
    db: AsyncSession,
    user_id: int,
    note_id: int,
    content: str,
) -> LessonNote | None:
    """Update a shared lesson note content.

    Any authenticated user can update any note.
    user_id is recorded as the last editor.

    Args:
        db: Database session.
        user_id: Current user ID (becomes last editor).
        note_id: Note ID to update.
        content: New content.

    Returns:
        Updated LessonNote or None if not found.
    """
    note = await db.get(LessonNote, note_id, options=[selectinload(LessonNote.user)])
    if note is None:
        return None

    note.content = content
    note.user_id = user_id
    await db.flush()
    await db.commit()
    await db.refresh(note)
    await db.refresh(note, attribute_names=["user"])
    return note


async def delete_note(
    db: AsyncSession,
    note_id: int,
) -> bool:
    """Delete a shared lesson note.

    Any authenticated user can delete any note.

    Args:
        db: Database session.
        note_id: Note ID to delete.

    Returns:
        True if deleted, False if not found.
    """
    note = await db.get(LessonNote, note_id)
    if note is None:
        return False

    await db.delete(note)
    await db.commit()
    return True


async def get_notes(
    db: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    subject_name: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[LessonNote]:
    """Get shared lesson notes with optional filters and pagination.

    Args:
        db: Database session.
        date_from: Optional start date filter.
        date_to: Optional end date filter.
        subject_name: Optional subject name filter.
        search: Optional text search in content.
        limit: Maximum number of results.
        offset: Number of results to skip.

    Returns:
        List of matching LessonNote objects.
    """
    query = (
        select(LessonNote)
        .options(selectinload(LessonNote.user))
        .order_by(LessonNote.updated_at.desc())
    )

    if date_from is not None:
        query = query.where(LessonNote.lesson_date >= date_from)
    if date_to is not None:
        query = query.where(LessonNote.lesson_date <= date_to)
    if subject_name is not None:
        query = query.where(LessonNote.subject_name == subject_name)
    if search is not None:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.where(LessonNote.content.ilike(f"%{escaped}%", escape="\\"))

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_note_for_subject(
    db: AsyncSession,
    subject_name: str,
) -> LessonNote | None:
    """Get the shared note for a specific subject.

    Args:
        db: Database session.
        subject_name: Subject name.

    Returns:
        LessonNote or None if not found.
    """
    result = await db.execute(
        select(LessonNote)
        .where(LessonNote.subject_name == subject_name)
        .options(selectinload(LessonNote.user))
    )
    return result.scalar_one_or_none()


async def get_note_for_entry(
    db: AsyncSession,
    schedule_entry_id: int,
) -> LessonNote | None:
    """Get the shared note for a specific schedule entry (by subject_name).

    Args:
        db: Database session.
        schedule_entry_id: Schedule entry ID.

    Returns:
        LessonNote or None if not found.
    """
    entry = await db.get(ScheduleEntry, schedule_entry_id)
    if entry is None:
        return None

    result = await db.execute(
        select(LessonNote)
        .where(LessonNote.subject_name == entry.subject_name)
        .options(selectinload(LessonNote.user))
    )
    return result.scalar_one_or_none()
