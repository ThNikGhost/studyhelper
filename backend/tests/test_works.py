"""Tests for work endpoints."""

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient


@pytest.fixture
def semester_data() -> dict:
    """Sample semester data."""
    return {
        "number": 1,
        "year_start": 2024,
        "year_end": 2025,
        "name": "1 семестр 2024-2025",
    }


@pytest.fixture
def subject_data() -> dict:
    """Sample subject data."""
    return {
        "name": "Математический анализ",
        "short_name": "Матан",
    }


@pytest.fixture
def work_data() -> dict:
    """Sample work data without subject_id."""
    return {
        "title": "Лабораторная работа №1",
        "description": "Исследование пределов",
        "work_type": "lab",
        "deadline": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
        "max_grade": 100,
    }


@pytest.fixture
def work_data_2() -> dict:
    """Second sample work data without subject_id."""
    return {
        "title": "Домашняя работа №1",
        "description": "Задачи на производные",
        "work_type": "homework",
        "max_grade": 50,
    }


@pytest.fixture
async def semester(client: AsyncClient, auth_headers: dict, semester_data: dict):
    """Create a semester and return it."""
    response = await client.post(
        "/api/v1/semesters",
        json=semester_data,
        headers=auth_headers,
    )
    return response.json()


@pytest.fixture
async def subject(
    client: AsyncClient, auth_headers: dict, semester: dict, subject_data: dict
):
    """Create a subject and return it."""
    subject_data["semester_id"] = semester["id"]
    response = await client.post(
        "/api/v1/subjects",
        json=subject_data,
        headers=auth_headers,
    )
    return response.json()


class TestGetWorks:
    """Tests for GET /api/v1/works."""

    async def test_get_works_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting works when none exist."""
        response = await client.get("/api/v1/works", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_works_unauthorized(self, client: AsyncClient):
        """Test getting works without auth fails."""
        response = await client.get("/api/v1/works")

        assert response.status_code == 401

    async def test_get_works_filtered_by_subject(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test filtering works by subject."""
        # Create a work
        work_data["subject_id"] = subject["id"]
        await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )

        # Get works filtered by subject
        response = await client.get(
            f"/api/v1/works?subject_id={subject['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == work_data["title"]


class TestCreateWork:
    """Tests for POST /api/v1/works."""

    async def test_create_work_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test successful work creation."""
        work_data["subject_id"] = subject["id"]
        response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == work_data["title"]
        assert data["description"] == work_data["description"]
        assert data["work_type"] == work_data["work_type"]
        assert data["max_grade"] == work_data["max_grade"]
        assert data["subject_id"] == subject["id"]
        assert "id" in data
        assert "my_status" in data
        assert data["my_status"]["status"] == "not_started"

    async def test_create_work_minimal(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
    ):
        """Test creating work with only required fields."""
        response = await client.post(
            "/api/v1/works",
            json={
                "title": "Test Work",
                "work_type": "other",
                "subject_id": subject["id"],
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Work"
        assert data["description"] is None
        assert data["deadline"] is None
        assert data["max_grade"] is None

    async def test_create_work_unauthorized(self, client: AsyncClient, work_data: dict):
        """Test creating work without auth fails."""
        work_data["subject_id"] = 1
        response = await client.post("/api/v1/works", json=work_data)

        assert response.status_code == 401

    async def test_create_work_nonexistent_subject(
        self, client: AsyncClient, auth_headers: dict, work_data: dict
    ):
        """Test creating work with non-existent subject fails."""
        work_data["subject_id"] = 99999
        response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "subject" in response.json()["detail"].lower()


class TestGetWork:
    """Tests for GET /api/v1/works/{id}."""

    async def test_get_work_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test getting a work by ID."""
        # Create work first
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Get work
        response = await client.get(
            f"/api/v1/works/{work_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == work_id
        assert data["title"] == work_data["title"]
        assert "my_status" in data

    async def test_get_work_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent work fails."""
        response = await client.get(
            "/api/v1/works/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateWork:
    """Tests for PUT /api/v1/works/{id}."""

    async def test_update_work_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test updating a work."""
        # Create work first
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Update work
        response = await client.put(
            f"/api/v1/works/{work_id}",
            json={"title": "Updated Title", "max_grade": 150},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["max_grade"] == 150
        assert data["description"] == work_data["description"]

    async def test_update_work_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating non-existent work fails."""
        response = await client.put(
            "/api/v1/works/99999",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteWork:
    """Tests for DELETE /api/v1/works/{id}."""

    async def test_delete_work_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test deleting a work."""
        # Create work first
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Delete work
        response = await client.delete(
            f"/api/v1/works/{work_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(
            f"/api/v1/works/{work_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_work_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent work fails."""
        response = await client.delete(
            "/api/v1/works/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateWorkStatus:
    """Tests for PUT /api/v1/works/{id}/status."""

    async def test_update_work_status_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test updating work status."""
        # Create work first
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Update status
        response = await client.put(
            f"/api/v1/works/{work_id}/status",
            json={"status": "in_progress", "notes": "Started working"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["notes"] == "Started working"

    async def test_update_work_status_with_grade(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test updating work status with grade."""
        # Create work first
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Update status to graded
        response = await client.put(
            f"/api/v1/works/{work_id}/status",
            json={"status": "graded", "grade": 85},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "graded"
        assert data["grade"] == 85

    async def test_update_work_status_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating status of non-existent work fails."""
        response = await client.put(
            "/api/v1/works/99999/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGetWorkStatusHistory:
    """Tests for GET /api/v1/works/{id}/history."""

    async def test_get_work_status_history_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test getting work status history."""
        # Create work first
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Update status a few times
        await client.put(
            f"/api/v1/works/{work_id}/status",
            json={"status": "in_progress"},
            headers=auth_headers,
        )
        await client.put(
            f"/api/v1/works/{work_id}/status",
            json={"status": "completed"},
            headers=auth_headers,
        )

        # Get history
        response = await client.get(
            f"/api/v1/works/{work_id}/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Should have 3 entries: initial, in_progress, completed
        assert len(data) >= 2
        # Most recent first
        assert data[0]["new_status"] == "completed"
        assert data[0]["old_status"] == "in_progress"

    async def test_get_work_status_history_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting history of non-existent work fails."""
        response = await client.get(
            "/api/v1/works/99999/history",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGetUpcomingWorks:
    """Tests for GET /api/v1/works/upcoming."""

    async def test_get_upcoming_works_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test getting upcoming works."""
        # Create work with deadline
        work_data["subject_id"] = subject["id"]
        work_data["deadline"] = (datetime.now(UTC) + timedelta(days=3)).isoformat()
        await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )

        # Get upcoming
        response = await client.get(
            "/api/v1/works/upcoming",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == work_data["title"]
        assert "subject_name" in data[0]
        assert "my_status" in data[0]

    async def test_get_upcoming_works_excludes_past_deadlines(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
    ):
        """Test that past deadlines are not included."""
        # Create work with past deadline
        await client.post(
            "/api/v1/works",
            json={
                "title": "Past Work",
                "work_type": "homework",
                "subject_id": subject["id"],
                "deadline": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
            },
            headers=auth_headers,
        )

        # Get upcoming
        response = await client.get(
            "/api/v1/works/upcoming",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []


class TestSubjectWorks:
    """Tests for GET /api/v1/subjects/{id}/works."""

    async def test_get_subject_works_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test getting works for a subject."""
        # Create work
        work_data["subject_id"] = subject["id"]
        await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )

        # Get subject works
        response = await client.get(
            f"/api/v1/subjects/{subject['id']}/works",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == work_data["title"]
        assert "my_status" in data[0]

    async def test_get_subject_works_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting works for non-existent subject fails."""
        response = await client.get(
            "/api/v1/subjects/99999/works",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSubjectWorksCascade:
    """Test cascade delete of works when subject is deleted."""

    async def test_deleting_subject_deletes_works(
        self,
        client: AsyncClient,
        auth_headers: dict,
        subject: dict,
        work_data: dict,
    ):
        """Test that deleting a subject also deletes its works."""
        # Create work
        work_data["subject_id"] = subject["id"]
        create_response = await client.post(
            "/api/v1/works",
            json=work_data,
            headers=auth_headers,
        )
        work_id = create_response.json()["id"]

        # Delete subject
        await client.delete(
            f"/api/v1/subjects/{subject['id']}",
            headers=auth_headers,
        )

        # Work should also be deleted
        get_response = await client.get(
            f"/api/v1/works/{work_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
