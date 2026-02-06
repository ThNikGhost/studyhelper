"""File upload router."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.config import settings
from src.dependencies import get_current_user
from src.models.user import User
from src.services.upload import (
    delete_avatar_file,
    read_upload_streaming,
    save_avatar,
    validate_image_content,
)

router = APIRouter()


class UploadResponse(BaseModel):
    """Response schema for file upload."""

    url: str
    filename: str


@router.post(
    "/avatar", response_model=UploadResponse, status_code=status.HTTP_201_CREATED
)
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
    # Validate content type header
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_image_types)}",
        )

    # Read file with streaming size check
    content = await read_upload_streaming(file)

    # Validate actual file content via magic bytes
    detected_ext = validate_image_content(content)
    if detected_ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file content",
        )

    # Save file
    unique_filename = save_avatar(content, detected_ext)
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
        HTTPException: If file not found or invalid filename.
    """
    deleted = delete_avatar_file(filename)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
