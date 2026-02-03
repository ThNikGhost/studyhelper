"""Tests for semester endpoints."""

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
def semester_data_2() -> dict:
    """Second sample semester data."""
    return {
        "number": 2,
        "year_start": 2024,
        "year_end": 2025,
        "name": "2 семестр 2024-2025",
    }


class TestGetSemesters:
    """Tests for GET /api/v1/semesters."""

    async def test_get_semesters_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting semesters when none exist."""
        response = await client.get("/api/v1/semesters", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_semesters_unauthorized(self, client: AsyncClient):
        """Test getting semesters without auth fails."""
        response = await client.get("/api/v1/semesters")

        assert response.status_code == 401


class TestCreateSemester:
    """Tests for POST /api/v1/semesters."""

    async def test_create_semester_success(
        self, client: AsyncClient, auth_headers: dict, semester_data: dict
    ):
        """Test successful semester creation."""
        response = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["number"] == semester_data["number"]
        assert data["year_start"] == semester_data["year_start"]
        assert data["year_end"] == semester_data["year_end"]
        assert data["name"] == semester_data["name"]
        assert data["is_current"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_semester_unauthorized(
        self, client: AsyncClient, semester_data: dict
    ):
        """Test creating semester without auth fails."""
        response = await client.post("/api/v1/semesters", json=semester_data)

        assert response.status_code == 401

    async def test_create_semester_invalid_number(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating semester with invalid number fails."""
        response = await client.post(
            "/api/v1/semesters",
            json={
                "number": 0,  # Invalid: must be >= 1
                "year_start": 2024,
                "year_end": 2025,
                "name": "Test",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_semester_invalid_year(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating semester with invalid year fails."""
        response = await client.post(
            "/api/v1/semesters",
            json={
                "number": 1,
                "year_start": 1999,  # Invalid: must be >= 2000
                "year_end": 2025,
                "name": "Test",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetSemester:
    """Tests for GET /api/v1/semesters/{id}."""

    async def test_get_semester_success(
        self, client: AsyncClient, auth_headers: dict, semester_data: dict
    ):
        """Test getting a semester by ID."""
        # Create semester first
        create_response = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )
        semester_id = create_response.json()["id"]

        # Get semester
        response = await client.get(
            f"/api/v1/semesters/{semester_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == semester_id
        assert data["name"] == semester_data["name"]

    async def test_get_semester_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent semester fails."""
        response = await client.get(
            "/api/v1/semesters/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateSemester:
    """Tests for PUT /api/v1/semesters/{id}."""

    async def test_update_semester_success(
        self, client: AsyncClient, auth_headers: dict, semester_data: dict
    ):
        """Test updating a semester."""
        # Create semester first
        create_response = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )
        semester_id = create_response.json()["id"]

        # Update semester
        response = await client.put(
            f"/api/v1/semesters/{semester_id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["number"] == semester_data["number"]

    async def test_update_semester_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent semester fails."""
        response = await client.put(
            "/api/v1/semesters/99999",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteSemester:
    """Tests for DELETE /api/v1/semesters/{id}."""

    async def test_delete_semester_success(
        self, client: AsyncClient, auth_headers: dict, semester_data: dict
    ):
        """Test deleting a semester."""
        # Create semester first
        create_response = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )
        semester_id = create_response.json()["id"]

        # Delete semester
        response = await client.delete(
            f"/api/v1/semesters/{semester_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(
            f"/api/v1/semesters/{semester_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_semester_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent semester fails."""
        response = await client.delete(
            "/api/v1/semesters/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGetCurrentSemester:
    """Tests for GET /api/v1/semesters/current."""

    async def test_get_current_semester_none(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting current semester when none is set."""
        response = await client.get(
            "/api/v1/semesters/current",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json() is None

    async def test_get_current_semester_success(
        self, client: AsyncClient, auth_headers: dict, semester_data: dict
    ):
        """Test getting current semester after setting one."""
        # Create and set as current
        create_response = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )
        semester_id = create_response.json()["id"]

        await client.put(
            f"/api/v1/semesters/{semester_id}/set-current",
            headers=auth_headers,
        )

        # Get current
        response = await client.get(
            "/api/v1/semesters/current",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == semester_id
        assert data["is_current"] is True


class TestSetCurrentSemester:
    """Tests for PUT /api/v1/semesters/{id}/set-current."""

    async def test_set_current_semester_success(
        self, client: AsyncClient, auth_headers: dict, semester_data: dict
    ):
        """Test setting a semester as current."""
        # Create semester
        create_response = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )
        semester_id = create_response.json()["id"]

        # Set as current
        response = await client.put(
            f"/api/v1/semesters/{semester_id}/set-current",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_current"] is True

    async def test_set_current_semester_switches(
        self,
        client: AsyncClient,
        auth_headers: dict,
        semester_data: dict,
        semester_data_2: dict,
    ):
        """Test that setting current removes previous current."""
        # Create two semesters
        resp1 = await client.post(
            "/api/v1/semesters",
            json=semester_data,
            headers=auth_headers,
        )
        semester1_id = resp1.json()["id"]

        resp2 = await client.post(
            "/api/v1/semesters",
            json=semester_data_2,
            headers=auth_headers,
        )
        semester2_id = resp2.json()["id"]

        # Set first as current
        await client.put(
            f"/api/v1/semesters/{semester1_id}/set-current",
            headers=auth_headers,
        )

        # Set second as current
        await client.put(
            f"/api/v1/semesters/{semester2_id}/set-current",
            headers=auth_headers,
        )

        # Check that only second is current
        resp1_after = await client.get(
            f"/api/v1/semesters/{semester1_id}",
            headers=auth_headers,
        )
        resp2_after = await client.get(
            f"/api/v1/semesters/{semester2_id}",
            headers=auth_headers,
        )

        assert resp1_after.json()["is_current"] is False
        assert resp2_after.json()["is_current"] is True

    async def test_set_current_semester_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test setting non-existent semester as current fails."""
        response = await client.put(
            "/api/v1/semesters/99999/set-current",
            headers=auth_headers,
        )

        assert response.status_code == 404
