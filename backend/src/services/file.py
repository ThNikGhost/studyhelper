"""File service for study material management."""

import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.models.file import File

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


def save_file(content: bytes, extension: str) -> str:
    """Save file content to disk.

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


async def upload_file(
    db: AsyncSession,
    filename: str,
    stored_filename: str,
    mime_type: str,
    size: int,
    category: str,
    subject_id: int | None,
    user_id: int,
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
        uploaded_by=user_id,
    )
    db.add(file_record)
    await db.flush()
    await db.commit()
    await db.refresh(file_record, attribute_names=["subject"])
    return file_record


async def get_files(
    db: AsyncSession,
    subject_id: int | None = None,
    category: str | None = None,
) -> list[File]:
    """Get list of files with optional filtering.

    Args:
        db: Database session.
        subject_id: Filter by subject ID.
        category: Filter by category.

    Returns:
        List of File records with subject relationship loaded.
    """
    query = (
        select(File).options(joinedload(File.subject)).order_by(File.created_at.desc())
    )

    if subject_id is not None:
        query = query.where(File.subject_id == subject_id)
    if category is not None:
        query = query.where(File.category == category)

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
        select(File).options(joinedload(File.subject)).where(File.id == file_id)
    )
    return result.scalar_one_or_none()


async def delete_file(db: AsyncSession, file: File) -> None:
    """Delete a file from database and disk.

    Args:
        db: Database session.
        file: File record to delete.
    """
    # Delete from disk
    file_path = get_file_path(file.stored_filename)
    if file_path.exists():
        file_path.unlink()
        logger.info("Deleted file from disk: %s", file.stored_filename)

    # Delete from DB
    await db.delete(file)
    await db.commit()
