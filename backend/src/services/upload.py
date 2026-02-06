"""Upload service for file management."""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from src.config import settings

# Magic bytes for image format validation
_IMAGE_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".png": (b"\x89PNG",),
    ".webp": (b"RIFF",),
}

CHUNK_SIZE = 8192


def get_upload_dir() -> Path:
    """Get and create upload directory for avatars.

    Returns:
        Path to the avatars upload directory.
    """
    upload_path = Path(settings.upload_dir) / "avatars"
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def validate_image_content(content: bytes) -> str | None:
    """Validate image content by checking magic bytes.

    Args:
        content: Raw file bytes to validate.

    Returns:
        Detected file extension (e.g. '.jpg') or None if invalid.
    """
    for ext, signatures in _IMAGE_SIGNATURES.items():
        for sig in signatures:
            if content[: len(sig)] == sig:
                # Additional check for WEBP: must have WEBP at offset 8
                if ext == ".webp" and content[8:12] != b"WEBP":
                    continue
                return ext
    return None


async def read_upload_streaming(file: UploadFile) -> bytes:
    """Read uploaded file in chunks with size validation.

    Args:
        file: The uploaded file.

    Returns:
        File content as bytes.

    Raises:
        HTTPException: If file exceeds maximum size.
    """
    max_size = settings.max_upload_size_mb * 1024 * 1024
    chunks: list[bytes] = []
    total_size = 0

    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
            )
        chunks.append(chunk)

    return b"".join(chunks)


def save_avatar(content: bytes, extension: str) -> str:
    """Save avatar content to disk.

    Args:
        content: Image bytes to save.
        extension: File extension (e.g. '.jpg').

    Returns:
        Generated unique filename.
    """
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_filename

    with open(file_path, "wb") as f:
        f.write(content)

    return unique_filename


def delete_avatar_file(filename: str) -> bool:
    """Delete an avatar file safely with path traversal protection.

    Args:
        filename: The filename to delete.

    Returns:
        True if file was deleted, False if not found.

    Raises:
        HTTPException: If filename attempts path traversal.
    """
    upload_dir = get_upload_dir()
    file_path = (upload_dir / filename).resolve()

    # Path traversal protection: ensure resolved path is within upload_dir
    if not str(file_path).startswith(str(upload_dir.resolve())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    if not file_path.exists():
        return False

    file_path.unlink()
    return True
