"""Tests for attendance (absences) endpoints."""

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


def _future_entry() -> dict:
    """Create a schedule entry with a future lesson_date."""
    tomorrow = str(date.today() + timedelta(days=1))
    return {
        "day_of_week": 3,
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "subject_name": "Физика",
        "lesson_type": "lecture",
        "lesson_date": tomorrow,
    }


async def _create_entry(
    client: AsyncClient, headers: dict[str, str], data: dict
) -> int:
    """Helper to create a schedule entry and return its ID."""
    resp = await client.post("/api/v1/schedule/entries", json=data, headers=headers)
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_semester_with_dates(
    client: AsyncClient, headers: dict[str, str]
) -> int:
    """Create a semester with start_date and end_date for testing."""
    start = date.today() - timedelta(days=30)
    end = date.today() + timedelta(days=30)
    resp = await client.post(
        "/api/v1/semesters",
        json={
            "number": 1,
            "year_start": 2025,
            "year_end": 2026,
            "name": "Test Semester",
            "start_date": str(start),
            "end_date": str(end),
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


class TestMarkAbsent:
    """Tests for POST /api/v1/attendance/mark-absent."""

    @pytest.mark.asyncio
    async def test_mark_absent_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test successfully marking a past lesson as absent."""
        entry_id = await _create_entry(client, auth_headers, _past_entry())

        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["schedule_entry_id"] == entry_id
        assert data["user_id"] is not None
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_mark_absent_duplicate_409(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test marking the same lesson absent twice returns 409."""
        entry_id = await _create_entry(client, auth_headers, _past_entry())

        await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )
        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 409
        assert "Already marked" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_absent_entry_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test marking a non-existent entry returns 404."""
        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": 99999},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_absent_future_lesson_400(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test marking a future lesson as absent returns 400."""
        entry_id = await _create_entry(client, auth_headers, _future_entry())

        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "future" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_absent_no_auth(self, client: AsyncClient) -> None:
        """Test marking absent without authentication returns 401."""
        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": 1},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_mark_absent_today_entry(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test marking today's lesson as absent succeeds."""
        today = str(date.today())
        entry_id = await _create_entry(
            client, auth_headers, _past_entry(lesson_date=today)
        )

        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_mark_absent_entry_without_date(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test marking an entry without lesson_date succeeds (no future check)."""
        entry_data = {
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "10:30:00",
            "subject_name": "Алгебра",
            "lesson_type": "lecture",
        }
        entry_id = await _create_entry(client, auth_headers, entry_data)

        response = await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 201


class TestMarkPresent:
    """Tests for POST /api/v1/attendance/mark-present."""

    @pytest.mark.asyncio
    async def test_mark_present_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test removing an absence record returns 204."""
        entry_id = await _create_entry(client, auth_headers, _past_entry())
        await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        response = await client.post(
            "/api/v1/attendance/mark-present",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_mark_present_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test removing non-existent absence returns 404."""
        entry_id = await _create_entry(client, auth_headers, _past_entry())

        response = await client.post(
            "/api/v1/attendance/mark-present",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_mark_present_no_auth(self, client: AsyncClient) -> None:
        """Test mark present without authentication returns 401."""
        response = await client.post(
            "/api/v1/attendance/mark-present",
            json={"schedule_entry_id": 1},
        )

        assert response.status_code == 401


class TestGetAttendance:
    """Tests for GET /api/v1/attendance/."""

    @pytest.mark.asyncio
    async def test_get_entries_requires_semester_id(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting entries without semester_id returns 422."""
        response = await client.get("/api/v1/attendance/", headers=auth_headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_entries_semester_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting entries with non-existent semester returns 404."""
        response = await client.get(
            "/api/v1/attendance/?semester_id=99999", headers=auth_headers
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_entries_semester_no_dates(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting entries with semester without dates returns 400."""
        sem_resp = await client.post(
            "/api/v1/semesters",
            json={
                "number": 1,
                "year_start": 2025,
                "year_end": 2026,
                "name": "No dates semester",
            },
            headers=auth_headers,
        )
        sem_id = sem_resp.json()["id"]

        response = await client.get(
            f"/api/v1/attendance/?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 400
        assert "dates not set" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_entries_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting entries when none exist in semester."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        response = await client.get(
            f"/api/v1/attendance/?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_entries_with_absences(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting entries with mixed attendance."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        entry1_id = await _create_entry(client, auth_headers, _past_entry())
        entry2_id = await _create_entry(
            client, auth_headers, _past_entry("Программирование")
        )

        # Mark entry1 as absent
        await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry1_id},
            headers=auth_headers,
        )

        response = await client.get(
            f"/api/v1/attendance/?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        entry1_data = next(e for e in data if e["id"] == entry1_id)
        entry2_data = next(e for e in data if e["id"] == entry2_id)
        assert entry1_data["is_absent"] is True
        assert entry2_data["is_absent"] is False

    @pytest.mark.asyncio
    async def test_get_entries_pagination(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test pagination with limit and offset."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        for i in range(5):
            await _create_entry(
                client,
                auth_headers,
                _past_entry(f"Subject {i}"),
            )

        response = await client.get(
            f"/api/v1/attendance/?semester_id={sem_id}&limit=2&offset=0",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        response2 = await client.get(
            f"/api/v1/attendance/?semester_id={sem_id}&limit=2&offset=2",
            headers=auth_headers,
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 2

    @pytest.mark.asyncio
    async def test_get_entries_no_auth(self, client: AsyncClient) -> None:
        """Test getting entries without authentication returns 401."""
        response = await client.get("/api/v1/attendance/?semester_id=1")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_entries_excludes_future(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that future entries are not returned."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        await _create_entry(client, auth_headers, _past_entry())
        await _create_entry(client, auth_headers, _future_entry())

        response = await client.get(
            f"/api/v1/attendance/?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["subject_name"] == "Математический анализ"


class TestGetStats:
    """Tests for GET /api/v1/attendance/stats."""

    @pytest.mark.asyncio
    async def test_stats_requires_semester_id(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats without semester_id returns 422."""
        response = await client.get("/api/v1/attendance/stats", headers=auth_headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_stats_semester_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats with non-existent semester returns 404."""
        response = await client.get(
            "/api/v1/attendance/stats?semester_id=99999", headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_stats_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats with no entries returns 0% attendance (no planned_classes)."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        response = await client.get(
            f"/api/v1/attendance/stats?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_planned"] == 0
        assert data["total_completed"] == 0
        assert data["total_classes"] == 0
        assert data["absences"] == 0
        assert data["attendance_percent"] == 0.0
        assert data["by_subject"] == []

    @pytest.mark.asyncio
    async def test_stats_all_present(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats when all lessons attended (no planned_classes set)."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        await _create_entry(client, auth_headers, _past_entry())
        await _create_entry(client, auth_headers, _past_entry("Физика"))

        response = await client.get(
            f"/api/v1/attendance/stats?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_completed"] == 2
        assert data["total_classes"] == 2
        assert data["absences"] == 0
        assert data["attended"] == 2
        assert data["attendance_percent"] == 100.0

    @pytest.mark.asyncio
    async def test_stats_with_absences(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats with some absences."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        entry1_id = await _create_entry(client, auth_headers, _past_entry())
        await _create_entry(client, auth_headers, _past_entry("Физика"))

        await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry1_id},
            headers=auth_headers,
        )

        response = await client.get(
            f"/api/v1/attendance/stats?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_completed"] == 2
        assert data["absences"] == 1
        assert data["attended"] == 1
        assert data["attendance_percent"] == 50.0

    @pytest.mark.asyncio
    async def test_stats_with_planned_classes(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats with planned_classes set on subject."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        # Create subject with planned_classes
        subj_resp = await client.post(
            "/api/v1/subjects",
            json={
                "name": "Алгебра",
                "semester_id": sem_id,
                "planned_classes": 32,
            },
            headers=auth_headers,
        )
        subj_id = subj_resp.json()["id"]

        # Create 2 past entries linked to subject
        for _ in range(2):
            await _create_entry(
                client,
                auth_headers,
                _past_entry("Алгебра", subject_id=subj_id),
            )

        response = await client.get(
            f"/api/v1/attendance/stats?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_planned"] == 32
        assert data["total_completed"] == 2
        assert data["attended"] == 2
        # 2 / 32 * 100 = 6.25%
        assert data["attendance_percent"] == 6.2

    @pytest.mark.asyncio
    async def test_stats_by_subject_breakdown(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test per-subject stats breakdown."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        entry_math = await _create_entry(client, auth_headers, _past_entry())
        await _create_entry(client, auth_headers, _past_entry("Физика"))

        await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_math},
            headers=auth_headers,
        )

        response = await client.get(
            f"/api/v1/attendance/stats?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["by_subject"]) == 2

        math_subj = next(
            s
            for s in data["by_subject"]
            if s["subject_name"] == "Математический анализ"
        )
        physics_subj = next(
            s for s in data["by_subject"] if s["subject_name"] == "Физика"
        )

        assert math_subj["total_classes"] == 1
        assert math_subj["absences"] == 1
        assert math_subj["attendance_percent"] == 0.0

        assert physics_subj["total_classes"] == 1
        assert physics_subj["absences"] == 0
        assert physics_subj["attendance_percent"] == 100.0

    @pytest.mark.asyncio
    async def test_stats_no_auth(self, client: AsyncClient) -> None:
        """Test stats without authentication returns 401."""
        response = await client.get("/api/v1/attendance/stats?semester_id=1")

        assert response.status_code == 401


class TestGetSubjectStats:
    """Tests for GET /api/v1/attendance/stats/{subject_id}."""

    @pytest.mark.asyncio
    async def test_subject_stats_requires_semester_id(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test subject stats without semester_id returns 422."""
        response = await client.get("/api/v1/attendance/stats/1", headers=auth_headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_subject_stats_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting stats for a specific subject with linked subject_id."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        subj_resp = await client.post(
            "/api/v1/subjects",
            json={"name": "Алгебра", "semester_id": sem_id, "planned_classes": 16},
            headers=auth_headers,
        )
        subj_id = subj_resp.json()["id"]

        # Create entries linked to this subject
        yesterday = str(date.today() - timedelta(days=1))
        entry_id = await _create_entry(
            client,
            auth_headers,
            _past_entry("Алгебра", subject_id=subj_id, lesson_date=yesterday),
        )

        await client.post(
            "/api/v1/attendance/mark-absent",
            json={"schedule_entry_id": entry_id},
            headers=auth_headers,
        )

        response = await client.get(
            f"/api/v1/attendance/stats/{subj_id}?semester_id={sem_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["subject_name"] == "Алгебра"
        assert data["planned_classes"] == 16
        assert data["total_classes"] == 1
        assert data["absences"] == 1
        assert data["attendance_percent"] == 0.0

    @pytest.mark.asyncio
    async def test_subject_stats_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test stats for subject with no entries returns 404."""
        sem_id = await _create_semester_with_dates(client, auth_headers)

        response = await client.get(
            f"/api/v1/attendance/stats/99999?semester_id={sem_id}", headers=auth_headers
        )

        assert response.status_code == 404
