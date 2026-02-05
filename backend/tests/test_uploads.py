"""Tests for uploads router."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.config import settings


class TestUploadAvatar:
    """Tests for POST /api/v1/uploads/avatar."""

    @pytest.mark.asyncio
    async def test_upload_avatar_success(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test successful avatar upload."""
        # Create a simple image file
        image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/uploads/avatar",
                files={"file": ("test.png", io.BytesIO(image_content), "image/png")},
                headers=auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert "url" in data
        assert "filename" in data
        assert data["url"].startswith("/uploads/avatars/")
        assert data["filename"].endswith(".png")

    @pytest.mark.asyncio
    async def test_upload_avatar_jpeg(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test JPEG avatar upload."""
        image_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/uploads/avatar",
                files={"file": ("photo.jpg", io.BytesIO(image_content), "image/jpeg")},
                headers=auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"].endswith(".jpg")

    @pytest.mark.asyncio
    async def test_upload_avatar_webp(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test WebP avatar upload."""
        image_content = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/uploads/avatar",
                files={"file": ("photo.webp", io.BytesIO(image_content), "image/webp")},
                headers=auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"].endswith(".webp")

    @pytest.mark.asyncio
    async def test_upload_avatar_unauthorized(self, client: AsyncClient) -> None:
        """Test upload without authentication."""
        image_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        response = await client.post(
            "/api/v1/uploads/avatar",
            files={"file": ("test.png", io.BytesIO(image_content), "image/png")},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_avatar_invalid_type(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test upload with invalid file type."""
        response = await client.post(
            "/api/v1/uploads/avatar",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_avatar_too_large(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test upload with file too large."""
        # Create a file larger than 5MB
        large_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * (6 * 1024 * 1024)

        response = await client.post(
            "/api/v1/uploads/avatar",
            files={"file": ("large.png", io.BytesIO(large_content), "image/png")},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "too large" in response.json()["detail"]


class TestDeleteAvatar:
    """Tests for DELETE /api/v1/uploads/avatar/{filename}."""

    @pytest.mark.asyncio
    async def test_delete_avatar_success(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test successful avatar deletion."""
        # Create a test file
        avatars_dir = tmp_path / "avatars"
        avatars_dir.mkdir(parents=True)
        test_file = avatars_dir / "test123.png"
        test_file.write_bytes(b"test content")

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.delete(
                "/api/v1/uploads/avatar/test123.png",
                headers=auth_headers,
            )

        assert response.status_code == 204
        assert not test_file.exists()

    @pytest.mark.asyncio
    async def test_delete_avatar_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test deletion of non-existent file."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            # Create the avatars directory
            avatars_dir = tmp_path / "avatars"
            avatars_dir.mkdir(parents=True)

            response = await client.delete(
                "/api/v1/uploads/avatar/nonexistent.png",
                headers=auth_headers,
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_avatar_unauthorized(self, client: AsyncClient) -> None:
        """Test deletion without authentication."""
        response = await client.delete("/api/v1/uploads/avatar/test.png")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_avatar_path_traversal(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test path traversal prevention."""
        # FastAPI/Starlette normalizes the path, so ../.. is handled at router level
        # The filename with .. is rejected by our validation
        response = await client.delete(
            "/api/v1/uploads/avatar/..%2F..%2Fetc%2Fpasswd",
            headers=auth_headers,
        )

        # Should be rejected (400) or not found (404)
        assert response.status_code in (400, 404)

    @pytest.mark.asyncio
    async def test_delete_avatar_path_traversal_backslash(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test path traversal with backslash prevention."""
        response = await client.delete(
            "/api/v1/uploads/avatar/..\\..\\etc\\passwd",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Invalid filename" in response.json()["detail"]
