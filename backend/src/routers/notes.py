"""Notes router — CRUD for lesson notes."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.note import LessonNoteCreate, LessonNoteResponse, LessonNoteUpdate
from src.services import note as note_service

router = APIRouter()


@router.post(
    "/",
    response_model=LessonNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    data: LessonNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonNoteResponse:
    """Create a new lesson note.

    Args:
        data: Note creation data.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Created note.
    """
    try:
        note = await note_service.create_note(db, current_user.id, data)
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=msg
            ) from e
        if "already exists" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from e

    return LessonNoteResponse.model_validate(note)


@router.get("/", response_model=list[LessonNoteResponse])
async def get_notes(
    date_from: date | None = Query(None, description="Start date filter"),
    date_to: date | None = Query(None, description="End date filter"),
    subject_name: str | None = Query(None, description="Filter by subject name"),
    search: str | None = Query(None, description="Search in content"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LessonNoteResponse]:
    """Get lesson notes with optional filters.

    Args:
        date_from: Optional start date.
        date_to: Optional end date.
        subject_name: Optional subject name filter.
        search: Optional text search.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        List of matching notes.
    """
    notes = await note_service.get_notes(
        db, current_user.id, date_from, date_to, subject_name, search
    )
    return [LessonNoteResponse.model_validate(n) for n in notes]


@router.get("/entry/{schedule_entry_id}", response_model=LessonNoteResponse)
async def get_note_for_entry(
    schedule_entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonNoteResponse:
    """Get note for a specific schedule entry.

    Args:
        schedule_entry_id: Schedule entry ID.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Note for the entry.
    """
    note = await note_service.get_note_for_entry(db, current_user.id, schedule_entry_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found for this entry",
        )
    return LessonNoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=LessonNoteResponse)
async def update_note(
    note_id: int,
    data: LessonNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonNoteResponse:
    """Update a lesson note.

    Args:
        note_id: Note ID.
        data: Updated content.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Updated note.
    """
    note = await note_service.update_note(db, current_user.id, note_id, data.content)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return LessonNoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a lesson note.

    Args:
        note_id: Note ID.
        db: Database session.
        current_user: Authenticated user.
    """
    deleted = await note_service.delete_note(db, current_user.id, note_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
