"""Tests for schedule endpoints."""


import pytest
from httpx import AsyncClient


@pytest.fixture
def schedule_entry_data() -> dict:
    """Sample schedule entry data."""
    return {
        "day_of_week": 1,  # Monday
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "subject_name": "Математический анализ",
        "lesson_type": "lecture",
        "teacher_name": "Иванов И.И.",
        "room": "301",
        "building": "Главный корпус",
        "group_name": "ММБ-101",
        "subgroup": 1,
    }


@pytest.fixture
def schedule_entry_data_2() -> dict:
    """Second sample schedule entry data."""
    return {
        "day_of_week": 1,  # Monday
        "start_time": "10:45:00",
        "end_time": "12:15:00",
        "subject_name": "Программирование",
        "lesson_type": "practice",
        "teacher_name": "Петров П.П.",
        "room": "418",
        "building": "Главный корпус",
    }


@pytest.fixture
def schedule_entry_odd_week() -> dict:
    """Schedule entry for odd week only."""
    return {
        "day_of_week": 2,  # Tuesday
        "start_time": "09:00:00",
        "end_time": "10:30:00",
        "week_type": "odd",
        "subject_name": "Физика",
        "lesson_type": "lab",
        "room": "205",
    }


class TestGetScheduleEntries:
    """Tests for GET /api/v1/schedule/entries."""

    async def test_get_entries_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting entries when none exist."""
        response = await client.get("/api/v1/schedule/entries", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_entries_unauthorized(self, client: AsyncClient):
        """Test getting entries without auth fails."""
        response = await client.get("/api/v1/schedule/entries")

        assert response.status_code == 401

    async def test_get_entries_returns_list(
        self, client: AsyncClient, auth_headers: dict, schedule_entry_data: dict
    ):
        """Test getting entries returns list."""
        await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_data,
            headers=auth_headers,
        )

        response = await client.get("/api/v1/schedule/entries", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["subject_name"] == schedule_entry_data["subject_name"]

    async def test_get_entries_filter_by_day(
        self,
        client: AsyncClient,
        auth_headers: dict,
        schedule_entry_data: dict,
        schedule_entry_odd_week: dict,
    ):
        """Test filtering entries by day of week."""
        # Create entries for different days
        await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_data,  # Monday
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_odd_week,  # Tuesday
            headers=auth_headers,
        )

        # Filter by Monday
        response = await client.get(
            "/api/v1/schedule/entries?day_of_week=1",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["day_of_week"] == 1


class TestCreateScheduleEntry:
    """Tests for POST /api/v1/schedule/entries."""

    async def test_create_entry_success(
        self, client: AsyncClient, auth_headers: dict, schedule_entry_data: dict
    ):
        """Test successful entry creation."""
        response = await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["day_of_week"] == schedule_entry_data["day_of_week"]
        assert data["subject_name"] == schedule_entry_data["subject_name"]
        assert data["lesson_type"] == schedule_entry_data["lesson_type"]
        assert data["teacher_name"] == schedule_entry_data["teacher_name"]
        assert data["room"] == schedule_entry_data["room"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_entry_minimal(self, client: AsyncClient, auth_headers: dict):
        """Test creating entry with only required fields."""
        response = await client.post(
            "/api/v1/schedule/entries",
            json={
                "day_of_week": 3,
                "start_time": "14:00:00",
                "end_time": "15:30:00",
                "subject_name": "Минимальный предмет",
                "lesson_type": "other",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["subject_name"] == "Минимальный предмет"
        assert data["teacher_name"] is None

    async def test_create_entry_with_week_type(
        self, client: AsyncClient, auth_headers: dict, schedule_entry_odd_week: dict
    ):
        """Test creating entry with week type."""
        response = await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_odd_week,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["week_type"] == "odd"

    async def test_create_entry_unauthorized(
        self, client: AsyncClient, schedule_entry_data: dict
    ):
        """Test creating entry without auth fails."""
        response = await client.post(
            "/api/v1/schedule/entries", json=schedule_entry_data
        )

        assert response.status_code == 401

    async def test_create_entry_invalid_day(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating entry with invalid day fails."""
        response = await client.post(
            "/api/v1/schedule/entries",
            json={
                "day_of_week": 8,  # Invalid: must be 1-7
                "start_time": "09:00:00",
                "end_time": "10:30:00",
                "subject_name": "Test",
                "lesson_type": "lecture",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_entry_invalid_lesson_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating entry with invalid lesson type fails."""
        response = await client.post(
            "/api/v1/schedule/entries",
            json={
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "10:30:00",
                "subject_name": "Test",
                "lesson_type": "invalid_type",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetScheduleEntry:
    """Tests for GET /api/v1/schedule/entries/{id}."""

    async def test_get_entry_success(
        self, client: AsyncClient, auth_headers: dict, schedule_entry_data: dict
    ):
        """Test getting an entry by ID."""
        create_response = await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_data,
            headers=auth_headers,
        )
        entry_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/schedule/entries/{entry_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry_id
        assert data["subject_name"] == schedule_entry_data["subject_name"]

    async def test_get_entry_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent entry fails."""
        response = await client.get(
            "/api/v1/schedule/entries/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateScheduleEntry:
    """Tests for PUT /api/v1/schedule/entries/{id}."""

    async def test_update_entry_success(
        self, client: AsyncClient, auth_headers: dict, schedule_entry_data: dict
    ):
        """Test updating an entry."""
        create_response = await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_data,
            headers=auth_headers,
        )
        entry_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/schedule/entries/{entry_id}",
            json={"room": "500", "notes": "Перенос занятия"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["room"] == "500"
        assert data["notes"] == "Перенос занятия"
        assert data["subject_name"] == schedule_entry_data["subject_name"]

    async def test_update_entry_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent entry fails."""
        response = await client.put(
            "/api/v1/schedule/entries/99999",
            json={"room": "123"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteScheduleEntry:
    """Tests for DELETE /api/v1/schedule/entries/{id}."""

    async def test_delete_entry_success(
        self, client: AsyncClient, auth_headers: dict, schedule_entry_data: dict
    ):
        """Test deleting an entry."""
        create_response = await client.post(
            "/api/v1/schedule/entries",
            json=schedule_entry_data,
            headers=auth_headers,
        )
        entry_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/schedule/entries/{entry_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/schedule/entries/{entry_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_entry_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent entry fails."""
        response = await client.delete(
            "/api/v1/schedule/entries/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestWeekSchedule:
    """Tests for GET /api/v1/schedule/week."""

    async def test_get_week_schedule_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting week schedule when empty."""
        response = await client.get("/api/v1/schedule/week", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "week_start" in data
        assert "week_end" in data
        assert "week_number" in data
        assert "is_odd_week" in data
        assert "days" in data
        assert len(data["days"]) == 7

    async def test_get_week_schedule_unauthorized(self, client: AsyncClient):
        """Test getting week schedule without auth fails."""
        response = await client.get("/api/v1/schedule/week")

        assert response.status_code == 401


class TestTodaySchedule:
    """Tests for GET /api/v1/schedule/today."""

    async def test_get_today_schedule(self, client: AsyncClient, auth_headers: dict):
        """Test getting today's schedule."""
        response = await client.get("/api/v1/schedule/today", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "day_of_week" in data
        assert "day_name" in data
        assert "entries" in data

    async def test_get_today_schedule_unauthorized(self, client: AsyncClient):
        """Test getting today's schedule without auth fails."""
        response = await client.get("/api/v1/schedule/today")

        assert response.status_code == 401


class TestCurrentLesson:
    """Tests for GET /api/v1/schedule/current."""

    async def test_get_current_lesson(self, client: AsyncClient, auth_headers: dict):
        """Test getting current lesson."""
        response = await client.get("/api/v1/schedule/current", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "current" in data
        assert "next" in data
        assert "time_until_next" in data

    async def test_get_current_lesson_unauthorized(self, client: AsyncClient):
        """Test getting current lesson without auth fails."""
        response = await client.get("/api/v1/schedule/current")

        assert response.status_code == 401


class TestRefreshSchedule:
    """Tests for POST /api/v1/schedule/refresh."""

    async def test_refresh_schedule_placeholder(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test refresh schedule placeholder endpoint."""
        response = await client.post("/api/v1/schedule/refresh", headers=auth_headers)

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"

    async def test_refresh_schedule_unauthorized(self, client: AsyncClient):
        """Test refresh schedule without auth fails."""
        response = await client.post("/api/v1/schedule/refresh")

        assert response.status_code == 401


class TestSnapshots:
    """Tests for snapshot endpoints."""

    async def test_get_snapshots_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting snapshots when empty."""
        response = await client.get("/api/v1/schedule/snapshots", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_latest_snapshot_none(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting latest snapshot when none exist."""
        response = await client.get(
            "/api/v1/schedule/snapshots/latest", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() is None
