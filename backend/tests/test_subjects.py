"""Tests for subject endpoints."""

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
    """Sample subject data without semester_id."""
    return {
        "name": "Математический анализ",
        "short_name": "Матанализ",
        "description": "Изучение пределов, производных и интегралов",
    }


@pytest.fixture
def subject_data_2() -> dict:
    """Second sample subject data without semester_id."""
    return {
        "name": "Линейная алгебра",
        "short_name": "Линал",
        "description": "Изучение матриц и векторов",
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


class TestGetSubjects:
    """Tests for GET /api/v1/subjects."""

    async def test_get_subjects_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting subjects when none exist."""
        response = await client.get("/api/v1/subjects", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_subjects_unauthorized(self, client: AsyncClient):
        """Test getting subjects without auth fails."""
        response = await client.get("/api/v1/subjects")

        assert response.status_code == 401

    async def test_get_subjects_filtered_by_semester(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test filtering subjects by semester."""
        # Create a subject
        subject_data["semester_id"] = semester["id"]
        await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )

        # Get subjects filtered by semester
        response = await client.get(
            f"/api/v1/subjects?semester_id={semester['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == subject_data["name"]

    async def test_get_subjects_filter_returns_empty_for_other_semester(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test filtering returns empty for non-matching semester."""
        # Create a subject
        subject_data["semester_id"] = semester["id"]
        await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )

        # Get subjects for non-existent semester
        response = await client.get(
            "/api/v1/subjects?semester_id=99999",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() == []


class TestCreateSubject:
    """Tests for POST /api/v1/subjects."""

    async def test_create_subject_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test successful subject creation."""
        subject_data["semester_id"] = semester["id"]
        response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == subject_data["name"]
        assert data["short_name"] == subject_data["short_name"]
        assert data["description"] == subject_data["description"]
        assert data["semester_id"] == semester["id"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_subject_minimal(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
    ):
        """Test creating subject with only required fields."""
        response = await client.post(
            "/api/v1/subjects",
            json={"name": "Test Subject", "semester_id": semester["id"]},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Subject"
        assert data["short_name"] is None
        assert data["description"] is None

    async def test_create_subject_unauthorized(
        self, client: AsyncClient, subject_data: dict
    ):
        """Test creating subject without auth fails."""
        subject_data["semester_id"] = 1
        response = await client.post("/api/v1/subjects", json=subject_data)

        assert response.status_code == 401

    async def test_create_subject_nonexistent_semester(
        self, client: AsyncClient, auth_headers: dict, subject_data: dict
    ):
        """Test creating subject with non-existent semester fails."""
        subject_data["semester_id"] = 99999
        response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "semester" in response.json()["detail"].lower()

    async def test_create_subject_empty_name(
        self, client: AsyncClient, auth_headers: dict, semester: dict
    ):
        """Test creating subject with empty name fails."""
        response = await client.post(
            "/api/v1/subjects",
            json={"name": "", "semester_id": semester["id"]},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetSubject:
    """Tests for GET /api/v1/subjects/{id}."""

    async def test_get_subject_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test getting a subject by ID."""
        # Create subject first
        subject_data["semester_id"] = semester["id"]
        create_response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )
        subject_id = create_response.json()["id"]

        # Get subject
        response = await client.get(
            f"/api/v1/subjects/{subject_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == subject_id
        assert data["name"] == subject_data["name"]

    async def test_get_subject_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent subject fails."""
        response = await client.get(
            "/api/v1/subjects/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateSubject:
    """Tests for PUT /api/v1/subjects/{id}."""

    async def test_update_subject_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test updating a subject."""
        # Create subject first
        subject_data["semester_id"] = semester["id"]
        create_response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )
        subject_id = create_response.json()["id"]

        # Update subject
        response = await client.put(
            f"/api/v1/subjects/{subject_id}",
            json={"name": "Updated Name", "short_name": "Upd"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["short_name"] == "Upd"
        # Original description should remain
        assert data["description"] == subject_data["description"]

    async def test_update_subject_change_semester(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test updating a subject's semester."""
        # Create another semester
        semester2_response = await client.post(
            "/api/v1/semesters",
            json={
                "number": 2,
                "year_start": 2024,
                "year_end": 2025,
                "name": "2 семестр 2024-2025",
            },
            headers=auth_headers,
        )
        semester2_id = semester2_response.json()["id"]

        # Create subject in first semester
        subject_data["semester_id"] = semester["id"]
        create_response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )
        subject_id = create_response.json()["id"]

        # Update subject to second semester
        response = await client.put(
            f"/api/v1/subjects/{subject_id}",
            json={"semester_id": semester2_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["semester_id"] == semester2_id

    async def test_update_subject_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent subject fails."""
        response = await client.put(
            "/api/v1/subjects/99999",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_subject_nonexistent_semester(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test updating subject to non-existent semester fails."""
        # Create subject first
        subject_data["semester_id"] = semester["id"]
        create_response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )
        subject_id = create_response.json()["id"]

        # Try to update to non-existent semester
        response = await client.put(
            f"/api/v1/subjects/{subject_id}",
            json={"semester_id": 99999},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "semester" in response.json()["detail"].lower()


class TestDeleteSubject:
    """Tests for DELETE /api/v1/subjects/{id}."""

    async def test_delete_subject_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test deleting a subject."""
        # Create subject first
        subject_data["semester_id"] = semester["id"]
        create_response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )
        subject_id = create_response.json()["id"]

        # Delete subject
        response = await client.delete(
            f"/api/v1/subjects/{subject_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(
            f"/api/v1/subjects/{subject_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_subject_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent subject fails."""
        response = await client.delete(
            "/api/v1/subjects/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestSemesterSubjectsCascade:
    """Test cascade delete of subjects when semester is deleted."""

    async def test_deleting_semester_deletes_subjects(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester: dict,
        subject_data: dict,
    ):
        """Test that deleting a semester also deletes its subjects."""
        # Create subject
        subject_data["semester_id"] = semester["id"]
        create_response = await client.post(
            "/api/v1/subjects",
            json=subject_data,
            headers=auth_headers,
        )
        subject_id = create_response.json()["id"]

        # Delete semester
        await client.delete(
            f"/api/v1/semesters/{semester['id']}",
            headers=auth_headers,
        )

        # Subject should also be deleted
        get_response = await client.get(
            f"/api/v1/subjects/{subject_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404
