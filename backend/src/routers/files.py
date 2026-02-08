"""File management router."""

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.models.subject import Subject
from src.models.user import User
from src.schemas.file import FileCategory, FileListResponse, FileResponse
from src.services.file import (
    delete_file,
    get_file_by_id,
    get_file_path,
    get_files,
    save_file,
    upload_file,
)
from src.services.upload import read_upload_streaming, validate_file_content

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED
)
async def upload_study_file(
    file: UploadFile,
    category: FileCategory = Form(...),
    subject_id: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Upload a study file.

    Args:
        file: The file to upload (multipart/form-data).
        category: File category (textbook, lecture, etc.).
        subject_id: Optional subject ID to associate with.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        FileResponse with uploaded file details.
    """
    # Validate MIME type
    if file.content_type not in settings.allowed_file_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(settings.allowed_file_extensions)}",
        )

    # Validate category
    try:
        FileCategory(category)
    except ValueError as err:
        valid = [c.value for c in FileCategory]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Valid: {', '.join(valid)}",
        ) from err

    # Validate subject exists if provided
    if subject_id is not None:
        result = await db.execute(select(Subject).where(Subject.id == subject_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found",
            )

    # Read file with streaming size check
    content = await read_upload_streaming(file, max_size_mb=settings.max_file_size_mb)

    # Get extension from original filename
    original_filename = file.filename or "unnamed"
    extension = Path(original_filename).suffix.lower()

    # Validate extension
    ext_without_dot = extension.lstrip(".")
    if ext_without_dot not in settings.allowed_file_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed: {', '.join(settings.allowed_file_extensions)}",
        )

    # Validate magic bytes
    if not validate_file_content(content, extension):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match expected format",
        )

    # Save to disk
    stored_filename = save_file(content, extension)

    # Save to DB
    file_record = await upload_file(
        db=db,
        filename=original_filename,
        stored_filename=stored_filename,
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        category=category,
        subject_id=subject_id,
        user_id=current_user.id,
    )

    return FileResponse(
        id=file_record.id,
        filename=file_record.filename,
        stored_filename=file_record.stored_filename,
        mime_type=file_record.mime_type,
        size=file_record.size,
        category=file_record.category,
        subject_id=file_record.subject_id,
        subject_name=file_record.subject.name if file_record.subject else None,
        uploaded_by=file_record.uploaded_by,
        created_at=file_record.created_at,
    )


@router.get("/", response_model=list[FileListResponse])
async def list_files(
    subject_id: int | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FileListResponse]:
    """List files with optional filtering.

    Args:
        subject_id: Filter by subject ID.
        category: Filter by category.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        List of files.
    """
    files = await get_files(db, subject_id=subject_id, category=category)
    return [
        FileListResponse(
            id=f.id,
            filename=f.filename,
            mime_type=f.mime_type,
            size=f.size,
            category=f.category,
            subject_id=f.subject_id,
            subject_name=f.subject.name if f.subject else None,
            uploaded_by=f.uploaded_by,
            created_at=f.created_at,
        )
        for f in files
    ]


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Download a file by ID.

    Args:
        file_id: File ID.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        StreamingResponse with file content.
    """
    file_record = await get_file_by_id(db, file_id)
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    file_path = get_file_path(file_record.stored_filename)
    if not file_path.exists():
        logger.error("File on disk missing: %s", file_record.stored_filename)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    def iterfile():
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    # RFC 5987 encoded filename for Content-Disposition
    safe_filename = file_record.filename.encode("ascii", errors="ignore").decode()
    return StreamingResponse(
        iterfile(),
        media_type=file_record.mime_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{safe_filename}\"; filename*=UTF-8''{file_record.filename}",
            "Content-Length": str(file_record.size),
        },
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a file.

    Args:
        file_id: File ID.
        db: Database session.
        current_user: Authenticated user.
    """
    file_record = await get_file_by_id(db, file_id)
    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    await delete_file(db, file_record)
