"""File service for study material management."""

import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.models.file import File
from src.schemas.file import FileUpdateRequest

logger = logging.getLogger(__name__)


def get_file_storage_dir() -> Path:
    """Get and create storage directory for study files.

    Returns:
        Path to the files upload directory.
    """
    upload_path = Path(settings.upload_dir) / "files"
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def get_file_path(stored_filename: str) -> Path:
    """Get safe file path with path traversal protection.

    Args:
        stored_filename: The stored filename (UUID-based).

    Returns:
        Resolved path to the file.

    Raises:
        HTTPException: If filename attempts path traversal.
    """
    storage_dir = get_file_storage_dir()
    file_path = (storage_dir / stored_filename).resolve()

    if not str(file_path).startswith(str(storage_dir.resolve())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    return file_path


def _save_file_sync(content: bytes, extension: str) -> str:
    """Save file content to disk (synchronous).

    Args:
        content: File bytes to save.
        extension: File extension (e.g. '.pdf').

    Returns:
        Generated unique stored filename.
    """
    stored_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = get_file_path(stored_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    return stored_filename


async def save_file(content: bytes, extension: str) -> str:
    """Save file content to disk without blocking the event loop.

    Args:
        content: File bytes to save.
        extension: File extension (e.g. '.pdf').

    Returns:
        Generated unique stored filename.
    """
    return await asyncio.to_thread(_save_file_sync, content, extension)


async def upload_file(
    db: AsyncSession,
    filename: str,
    stored_filename: str,
    mime_type: str,
    size: int,
    category: str,
    subject_id: int | None,
    user_id: int,
    work_id: int | None = None,
) -> File:
    """Create a file record in the database.

    Args:
        db: Database session.
        filename: Original filename.
        stored_filename: UUID filename on disk.
        mime_type: MIME type of the file.
        size: File size in bytes.
        category: File category.
        subject_id: Optional subject FK.
        user_id: Uploader user ID.
        work_id: Optional work FK.

    Returns:
        Created File record.
    """
    file_record = File(
        filename=filename,
        stored_filename=stored_filename,
        mime_type=mime_type,
        size=size,
        category=category,
        subject_id=subject_id,
        work_id=work_id,
        uploaded_by=user_id,
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record, attribute_names=["subject", "work"])
    return file_record


async def get_files(
    db: AsyncSession,
    subject_id: int | None = None,
    work_id: int | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[File]:
    """Get list of files with optional filtering and pagination.

    Args:
        db: Database session.
        subject_id: Filter by subject ID.
        work_id: Filter by work ID.
        category: Filter by category.
        limit: Maximum number of results.
        offset: Number of results to skip.

    Returns:
        List of File records with subject and work relationships loaded.
    """
    query = (
        select(File)
        .options(joinedload(File.subject), joinedload(File.work))
        .order_by(File.created_at.desc())
    )

    if subject_id is not None:
        query = query.where(File.subject_id == subject_id)
    if work_id is not None:
        query = query.where(File.work_id == work_id)
    if category is not None:
        query = query.where(File.category == category)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_file_by_id(db: AsyncSession, file_id: int) -> File | None:
    """Get a single file by ID.

    Args:
        db: Database session.
        file_id: File ID.

    Returns:
        File record or None.
    """
    result = await db.execute(
        select(File)
        .options(joinedload(File.subject), joinedload(File.work))
        .where(File.id == file_id)
    )
    return result.scalar_one_or_none()


async def update_file(
    db: AsyncSession,
    file: File,
    data: FileUpdateRequest,
) -> File:
    """Update file metadata (category and/or work attachment).

    Args:
        db: Database session.
        file: File record to update.
        data: Update payload with optional category and work_id.
            category is guaranteed non-null by schema validator when present.
            work_id=null means detach; work existence must be validated by caller.

    Returns:
        Updated File record.
    """
    if "category" in data.model_fields_set:
        assert data.category is not None
        file.category = data.category

    if "filename" in data.model_fields_set:
        assert data.filename is not None
        file.filename = data.filename.strip()

    if "work_id" in data.model_fields_set:
        file.work_id = data.work_id

    await db.commit()
    await db.refresh(file, attribute_names=["subject", "work"])
    return file


def _delete_file_from_disk(stored_filename: str) -> bool:
    """Delete a file from disk (synchronous).

    Args:
        stored_filename: The stored filename to delete.

    Returns:
        True if file was deleted, False if not found.
    """
    file_path = get_file_path(stored_filename)
    if file_path.exists():
        file_path.unlink()
        return True
    return False


async def delete_file(db: AsyncSession, file: File) -> None:
    """Delete a file from database and disk.

    Args:
        db: Database session.
        file: File record to delete.
    """
    # Delete from disk (non-blocking)
    deleted = await asyncio.to_thread(_delete_file_from_disk, file.stored_filename)
    if deleted:
        logger.info("Deleted file from disk: %s", file.stored_filename)

    # Delete from DB
    await db.delete(file)
    await db.commit()
