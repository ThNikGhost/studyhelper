"""File upload router."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.config import settings
from src.dependencies import get_current_user
from src.models.user import User

router = APIRouter()


class UploadResponse(BaseModel):
    """Response schema for file upload."""

    url: str
    filename: str


def get_upload_dir() -> Path:
    """Get and create upload directory."""
    upload_path = Path(settings.upload_dir) / "avatars"
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


@router.post("/avatar", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    """Upload an avatar image.

    Args:
        file: The image file to upload.
        current_user: The authenticated user.

    Returns:
        UploadResponse with the URL of the uploaded file.

    Raises:
        HTTPException: If file type is not allowed or file is too large.
    """
    # Validate content type
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_image_types)}",
        )

    # Read file and check size
    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes

    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    # Generate unique filename
    ext = Path(file.filename or "image.jpg").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"

    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Save file
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as f:
        f.write(content)

    # Return URL (relative to static files mount)
    url = f"/uploads/avatars/{unique_filename}"

    return UploadResponse(url=url, filename=unique_filename)


@router.delete("/avatar/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    filename: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an avatar image.

    Args:
        filename: The filename to delete.
        current_user: The authenticated user.

    Raises:
        HTTPException: If file not found.
    """
    # Validate filename (prevent path traversal)
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    upload_dir = get_upload_dir()
    file_path = upload_dir / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    file_path.unlink()
