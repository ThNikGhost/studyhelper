"""Tests for lesson notes endpoints."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


def _past_entry(subject_name: str = "Математический анализ", **kwargs) -> dict:
    """Create a schedule entry with a past lesson_date."""
    yesterday = str(date.today() - timedelta(days=1))
    data = {
        "day_of_week": 1,
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "subject_name": subject_name,
        "lesson_type": "lecture",
        "lesson_date": yesterday,
    }
    data.update(kwargs)
    return data


async def _create_entry(
    client: AsyncClient, headers: dict[str, str], data: dict
) -> int:
    """Helper to create a schedule entry and return its ID."""
    resp = await client.post("/api/v1/schedule/entries", json=data, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_note(
    client: AsyncClient,
    headers: dict[str, str],
    entry_id: int | None = None,
    subject_name: str = "Математический анализ",
    content: str = "Тестовая заметка",
    lesson_date: str | None = None,
) -> dict:
    """Helper to create or upsert a note via API."""
    body: dict = {"subject_name": subject_name, "content": content}
    if entry_id is not None:
        body["schedule_entry_id"] = entry_id
    if lesson_date is not None:
        body["lesson_date"] = lesson_date
    resp = await client.post("/api/v1/notes/", json=body, headers=headers)
    assert resp.status_code in (200, 201)
    return resp.json()


class TestCreateNote:
    """Tests for POST /api/v1/notes/."""

    @pytest.mark.asyncio
    async def test_create_note_standalone(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test creating a standalone note (no schedule entry)."""
        response = await client.post(
            "/api/v1/notes/",
            json={
                "subject_name": "Физика",
                "content": "Запомнить формулу F=ma",
                "lesson_date": str(date.today()),
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["subject_name"] == "Физика"
        assert data["content"] == "Запомнить формулу F=ma"
        assert data["schedule_entry_id"] is None
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_create_note_for_entry(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test creating a note linked to a schedule entry."""
        entry_id = await _create_entry(client, auth_headers, _past_entry("Физика"))

        response = await client.post(
            "/api/v1/notes/",
            json={
                "schedule_entry_id": entry_id,
                "subject_name": "ignored",
                "content": "Заметка к паре",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["schedule_entry_id"] == entry_id
        # subject_name auto-filled from entry
        assert data["subject_name"] == "Физика"

    @pytest.mark.asyncio
    async def test_upsert_updates_existing_note(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test upsert: second POST with same subject updates content (200)."""
        await _create_note(client, auth_headers, content="Первый вариант")

        response = await client.post(
            "/api/v1/notes/",
            json={
                "subject_name": "Математический анализ",
                "content": "Обновлённый текст",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Обновлённый текст"
        assert data["subject_name"] == "Математический анализ"

    @pytest.mark.asyncio
    async def test_upsert_via_entry_updates_existing(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test upsert via entry: updates existing note for same subject."""
        entry_id = await _create_entry(client, auth_headers, _past_entry())
        await _create_note(client, auth_headers, entry_id=entry_id, content="Первая")

        # Create second entry for same subject
        entry_id_2 = await _create_entry(
            client,
            auth_headers,
            _past_entry(start_time="11:00:00", end_time="12:30:00"),
        )
        response = await client.post(
            "/api/v1/notes/",
            json={
                "schedule_entry_id": entry_id_2,
                "subject_name": "X",
                "content": "Обновлённая",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Обновлённая"
        assert data["schedule_entry_id"] == entry_id_2

    @pytest.mark.asyncio
    async def test_create_note_entry_not_found_404(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test 404 when entry does not exist."""
        response = await client.post(
            "/api/v1/notes/",
            json={
                "schedule_entry_id": 99999,
                "subject_name": "X",
                "content": "Заметка",
            },
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_note_content_too_long(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test validation error when content exceeds 2000 chars."""
        response = await client.post(
            "/api/v1/notes/",
            json={
                "subject_name": "X",
                "content": "a" * 2001,
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_note_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.post(
            "/api/v1/notes/",
            json={"subject_name": "X", "content": "test"},
        )
        assert response.status_code == 401


class TestGetNotes:
    """Tests for GET /api/v1/notes/."""

    @pytest.mark.asyncio
    async def test_get_notes_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test empty notes list."""
        response = await client.get("/api/v1/notes/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_notes_with_data(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting notes list."""
        await _create_note(client, auth_headers, content="Заметка 1")
        await _create_note(
            client, auth_headers, content="Заметка 2", subject_name="Физика"
        )

        response = await client.get("/api/v1/notes/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_notes_filter_date(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test filtering notes by date range."""
        yesterday = str(date.today() - timedelta(days=1))
        tomorrow = str(date.today() + timedelta(days=1))
        await _create_note(client, auth_headers, content="Вчера", lesson_date=yesterday)
        await _create_note(
            client,
            auth_headers,
            content="Завтра",
            subject_name="Физика",
            lesson_date=tomorrow,
        )

        response = await client.get(
            "/api/v1/notes/",
            params={"date_from": yesterday, "date_to": yesterday},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Вчера"

    @pytest.mark.asyncio
    async def test_get_notes_filter_subject(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test filtering notes by subject name."""
        await _create_note(client, auth_headers, content="Матан")
        await _create_note(client, auth_headers, content="Физ", subject_name="Физика")

        response = await client.get(
            "/api/v1/notes/",
            params={"subject_name": "Физика"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Физ"

    @pytest.mark.asyncio
    async def test_get_notes_search(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test searching notes by content."""
        await _create_note(client, auth_headers, content="Formula F=ma")
        await _create_note(
            client, auth_headers, content="Homework task", subject_name="Физика"
        )

        response = await client.get(
            "/api/v1/notes/",
            params={"search": "Formula"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Formula" in data[0]["content"]


class TestGetNoteForEntry:
    """Tests for GET /api/v1/notes/entry/{schedule_entry_id}."""

    @pytest.mark.asyncio
    async def test_get_note_for_entry_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting a note by schedule entry ID."""
        entry_id = await _create_entry(client, auth_headers, _past_entry())
        await _create_note(client, auth_headers, entry_id=entry_id, content="Тест")

        response = await client.get(
            f"/api/v1/notes/entry/{entry_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Тест"

    @pytest.mark.asyncio
    async def test_get_note_for_entry_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test 404 when no note for entry."""
        response = await client.get("/api/v1/notes/entry/99999", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_note_for_entry_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.get("/api/v1/notes/entry/1")
        assert response.status_code == 401


class TestGetNoteForSubject:
    """Tests for GET /api/v1/notes/subject/{subject_name}."""

    @pytest.mark.asyncio
    async def test_get_note_for_subject_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting a note by subject name."""
        await _create_note(
            client, auth_headers, subject_name="Физика", content="Заметка по физике"
        )

        response = await client.get(
            "/api/v1/notes/subject/Физика", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Заметка по физике"
        assert response.json()["subject_name"] == "Физика"

    @pytest.mark.asyncio
    async def test_get_note_for_subject_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test 404 when no note for subject."""
        response = await client.get(
            "/api/v1/notes/subject/Несуществующий", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_note_for_subject_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.get("/api/v1/notes/subject/Физика")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_note_for_subject_url_encoded(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting a note with URL-encoded Cyrillic subject name."""
        await _create_note(
            client,
            auth_headers,
            subject_name="Математический анализ",
            content="Матан",
        )

        # URL with encoded Cyrillic
        response = await client.get(
            "/api/v1/notes/subject/%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9%20%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Матан"


class TestUpdateNote:
    """Tests for PUT /api/v1/notes/{note_id}."""

    @pytest.mark.asyncio
    async def test_update_note_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test successfully updating a note."""
        note = await _create_note(client, auth_headers, content="Старый текст")

        response = await client.put(
            f"/api/v1/notes/{note['id']}",
            json={"content": "Новый текст"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["content"] == "Новый текст"

    @pytest.mark.asyncio
    async def test_update_note_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test 404 when note does not exist."""
        response = await client.put(
            "/api/v1/notes/99999",
            json={"content": "test"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_note_content_too_long(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test validation error when updated content exceeds 2000 chars."""
        note = await _create_note(client, auth_headers, content="Текст")

        response = await client.put(
            f"/api/v1/notes/{note['id']}",
            json={"content": "a" * 2001},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_note_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.put("/api/v1/notes/1", json={"content": "test"})
        assert response.status_code == 401


class TestDeleteNote:
    """Tests for DELETE /api/v1/notes/{note_id}."""

    @pytest.mark.asyncio
    async def test_delete_note_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test successfully deleting a note."""
        note = await _create_note(client, auth_headers, content="Удалить")

        response = await client.delete(
            f"/api/v1/notes/{note['id']}", headers=auth_headers
        )
        assert response.status_code == 204

        # Verify deletion
        response = await client.get("/api/v1/notes/", headers=auth_headers)
        assert len(response.json()) == 0

    @pytest.mark.asyncio
    async def test_delete_note_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test 404 when note does not exist."""
        response = await client.delete("/api/v1/notes/99999", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_note_no_auth(self, client: AsyncClient) -> None:
        """Test 401 without authentication."""
        response = await client.delete("/api/v1/notes/1")
        assert response.status_code == 401
