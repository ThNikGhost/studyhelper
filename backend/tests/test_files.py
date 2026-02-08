"""Tests for file management router."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.config import settings


async def _create_semester(client: AsyncClient, headers: dict[str, str]) -> int:
    """Helper to create a semester and return its ID."""
    resp = await client.post(
        "/api/v1/semesters",
        json={
            "number": 1,
            "year_start": 2025,
            "year_end": 2026,
            "name": "1 семестр 2025-2026",
        },
        headers=headers,
    )
    return resp.json()["id"]


async def _create_subject(
    client: AsyncClient, headers: dict[str, str], semester_id: int
) -> int:
    """Helper to create a subject and return its ID."""
    resp = await client.post(
        "/api/v1/subjects",
        json={"name": "Математика", "semester_id": semester_id},
        headers=headers,
    )
    return resp.json()["id"]


def _pdf_content() -> bytes:
    """Minimal valid PDF magic bytes."""
    return b"%PDF-1.4 test content" + b"\x00" * 100


def _png_content() -> bytes:
    """Minimal valid PNG magic bytes."""
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def _docx_content() -> bytes:
    """Minimal valid DOCX (ZIP) magic bytes."""
    return b"PK\x03\x04" + b"\x00" * 100


def _gif_content() -> bytes:
    """Minimal valid GIF magic bytes."""
    return b"GIF89a" + b"\x00" * 100


class TestUploadFile:
    """Tests for POST /api/v1/files/upload."""

    @pytest.mark.asyncio
    async def test_upload_pdf_success(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test successful PDF upload."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("notes.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lecture"},
                headers=auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "notes.pdf"
        assert data["category"] == "lecture"
        assert data["mime_type"] == "application/pdf"
        assert data["subject_id"] is None
        assert data["size"] > 0

    @pytest.mark.asyncio
    async def test_upload_with_subject(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test upload linked to a subject."""
        semester_id = await _create_semester(client, auth_headers)
        subject_id = await _create_subject(client, auth_headers, semester_id)

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("hw.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "problem_set", "subject_id": str(subject_id)},
                headers=auth_headers,
            )

        assert response.status_code == 201
        data = response.json()
        assert data["subject_id"] == subject_id
        assert data["subject_name"] == "Математика"

    @pytest.mark.asyncio
    async def test_upload_docx(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test DOCX upload."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": (
                        "doc.docx",
                        io.BytesIO(_docx_content()),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
                data={"category": "lecture"},
                headers=auth_headers,
            )

        assert response.status_code == 201
        assert response.json()["filename"] == "doc.docx"

    @pytest.mark.asyncio
    async def test_upload_image(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test image file upload."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={"file": ("photo.png", io.BytesIO(_png_content()), "image/png")},
                data={"category": "cheatsheet"},
                headers=auth_headers,
            )

        assert response.status_code == 201
        assert response.json()["mime_type"] == "image/png"

    @pytest.mark.asyncio
    async def test_upload_gif(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test GIF file upload."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={"file": ("anim.gif", io.BytesIO(_gif_content()), "image/gif")},
                data={"category": "other"},
                headers=auth_headers,
            )

        assert response.status_code == 201
        assert response.json()["mime_type"] == "image/gif"

    @pytest.mark.asyncio
    async def test_upload_invalid_type_exe(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that exe files are rejected."""
        response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": (
                    "virus.exe",
                    io.BytesIO(b"MZ" + b"\x00" * 100),
                    "application/x-msdownload",
                )
            },
            data={"category": "other"},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_too_large(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test that files over 50MB are rejected."""
        large_content = b"%PDF-1.4" + b"\x00" * (51 * 1024 * 1024)

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("huge.pdf", io.BytesIO(large_content), "application/pdf")
                },
                data={"category": "textbook"},
                headers=auth_headers,
            )

        assert response.status_code == 400
        assert "too large" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_invalid_magic_bytes(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test that files with wrong magic bytes are rejected."""
        fake_pdf = b"NOT_A_PDF_CONTENT" + b"\x00" * 100

        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={"file": ("fake.pdf", io.BytesIO(fake_pdf), "application/pdf")},
                data={"category": "textbook"},
                headers=auth_headers,
            )

        assert response.status_code == 400
        assert "content does not match" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_unauthorized(self, client: AsyncClient) -> None:
        """Test upload without authentication."""
        response = await client.post(
            "/api/v1/files/upload",
            files={
                "file": ("notes.pdf", io.BytesIO(_pdf_content()), "application/pdf")
            },
            data={"category": "lecture"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_nonexistent_subject(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test upload with non-existent subject ID."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            response = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("notes.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lecture", "subject_id": "99999"},
                headers=auth_headers,
            )

        assert response.status_code == 404
        assert "Subject not found" in response.json()["detail"]


class TestListFiles:
    """Tests for GET /api/v1/files/."""

    @pytest.mark.asyncio
    async def test_list_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test listing files when none exist."""
        response = await client.get("/api/v1/files/", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_list_all(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test listing all files."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("a.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lecture"},
                headers=auth_headers,
            )
            await client.post(
                "/api/v1/files/upload",
                files={"file": ("b.png", io.BytesIO(_png_content()), "image/png")},
                data={"category": "cheatsheet"},
                headers=auth_headers,
            )

        response = await client.get("/api/v1/files/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_list_filter_by_subject(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test filtering files by subject."""
        semester_id = await _create_semester(client, auth_headers)
        subject_id = await _create_subject(client, auth_headers, semester_id)

        with patch.object(settings, "upload_dir", str(tmp_path)):
            await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("subj.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lecture", "subject_id": str(subject_id)},
                headers=auth_headers,
            )
            await client.post(
                "/api/v1/files/upload",
                files={
                    "file": (
                        "no_subj.pdf",
                        io.BytesIO(_pdf_content()),
                        "application/pdf",
                    )
                },
                data={"category": "other"},
                headers=auth_headers,
            )

        response = await client.get(
            f"/api/v1/files/?subject_id={subject_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["filename"] == "subj.pdf"

    @pytest.mark.asyncio
    async def test_list_filter_by_category(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test filtering files by category."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("lec.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lecture"},
                headers=auth_headers,
            )
            await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("lab.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lab"},
                headers=auth_headers,
            )

        response = await client.get(
            "/api/v1/files/?category=lecture", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "lecture"

    @pytest.mark.asyncio
    async def test_list_unauthorized(self, client: AsyncClient) -> None:
        """Test listing files without authentication."""
        response = await client.get("/api/v1/files/")

        assert response.status_code == 401


class TestDownloadFile:
    """Tests for GET /api/v1/files/{file_id}/download."""

    @pytest.mark.asyncio
    async def test_download_success(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test successful file download with Content-Disposition."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            upload_resp = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("notes.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "lecture"},
                headers=auth_headers,
            )
            file_id = upload_resp.json()["id"]

            response = await client.get(
                f"/api/v1/files/{file_id}/download", headers=auth_headers
            )

        assert response.status_code == 200
        assert "notes.pdf" in response.headers.get("content-disposition", "")
        assert response.headers.get("content-type") == "application/pdf"

    @pytest.mark.asyncio
    async def test_download_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test download of non-existent file."""
        response = await client.get(
            "/api/v1/files/99999/download", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_download_unauthorized(self, client: AsyncClient) -> None:
        """Test download without authentication."""
        response = await client.get("/api/v1/files/1/download")

        assert response.status_code == 401


class TestDeleteFile:
    """Tests for DELETE /api/v1/files/{file_id}."""

    @pytest.mark.asyncio
    async def test_delete_success(
        self, client: AsyncClient, auth_headers: dict[str, str], tmp_path: Path
    ) -> None:
        """Test successful file deletion removes DB record and disk file."""
        with patch.object(settings, "upload_dir", str(tmp_path)):
            upload_resp = await client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("del.pdf", io.BytesIO(_pdf_content()), "application/pdf")
                },
                data={"category": "other"},
                headers=auth_headers,
            )
            file_id = upload_resp.json()["id"]
            stored = upload_resp.json()["stored_filename"]

            # Verify file exists on disk
            file_on_disk = tmp_path / "files" / stored
            assert file_on_disk.exists()

            response = await client.delete(
                f"/api/v1/files/{file_id}", headers=auth_headers
            )

        assert response.status_code == 204

        # Verify file removed from disk
        assert not file_on_disk.exists()

        # Verify file removed from DB (list should be empty)
        with patch.object(settings, "upload_dir", str(tmp_path)):
            list_resp = await client.get("/api/v1/files/", headers=auth_headers)
        assert len(list_resp.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test deletion of non-existent file."""
        response = await client.delete("/api/v1/files/99999", headers=auth_headers)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_unauthorized(self, client: AsyncClient) -> None:
        """Test deletion without authentication."""
        response = await client.delete("/api/v1/files/1")

        assert response.status_code == 401
