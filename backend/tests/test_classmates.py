"""Tests for classmate endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
def classmate_data() -> dict:
    """Sample classmate data."""
    return {
        "full_name": "Сидоров Сидор Сидорович",
        "short_name": "Сидоров С.С.",
        "email": "sidorov@example.com",
        "phone": "+7-900-111-22-33",
        "telegram": "@sidorov",
        "vk": "https://vk.com/sidorov",
        "group_name": "ММБ-101",
        "subgroup": 1,
        "notes": "Староста группы",
    }


@pytest.fixture
def classmate_data_2() -> dict:
    """Second sample classmate data."""
    return {
        "full_name": "Козлова Мария Ивановна",
        "short_name": "Козлова М.И.",
        "email": "kozlova@example.com",
        "group_name": "ММБ-101",
        "subgroup": 2,
    }


class TestGetClassmates:
    """Tests for GET /api/v1/classmates."""

    async def test_get_classmates_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting classmates when none exist."""
        response = await client.get("/api/v1/classmates", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_classmates_unauthorized(self, client: AsyncClient):
        """Test getting classmates without auth fails."""
        response = await client.get("/api/v1/classmates")

        assert response.status_code == 401

    async def test_get_classmates_returns_list(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test getting classmates returns list."""
        await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )

        response = await client.get("/api/v1/classmates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["full_name"] == classmate_data["full_name"]

    async def test_get_classmates_ordered_by_name(
        self,
        client: AsyncClient,
        auth_headers: dict,
        classmate_data: dict,
        classmate_data_2: dict,
    ):
        """Test classmates are ordered by full_name."""
        # Create classmates (Козлова before Сидоров alphabetically)
        await client.post(
            "/api/v1/classmates",
            json=classmate_data,  # Сидоров
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/classmates",
            json=classmate_data_2,  # Козлова
            headers=auth_headers,
        )

        response = await client.get("/api/v1/classmates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["full_name"] == "Козлова Мария Ивановна"
        assert data[1]["full_name"] == "Сидоров Сидор Сидорович"


class TestCreateClassmate:
    """Tests for POST /api/v1/classmates."""

    async def test_create_classmate_success(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test successful classmate creation."""
        response = await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == classmate_data["full_name"]
        assert data["short_name"] == classmate_data["short_name"]
        assert data["email"] == classmate_data["email"]
        assert data["phone"] == classmate_data["phone"]
        assert data["telegram"] == classmate_data["telegram"]
        assert data["group_name"] == classmate_data["group_name"]
        assert data["subgroup"] == classmate_data["subgroup"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_classmate_minimal(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating classmate with only required fields."""
        response = await client.post(
            "/api/v1/classmates",
            json={"full_name": "Минимальный Одногруппник"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Минимальный Одногруппник"
        assert data["short_name"] is None
        assert data["email"] is None

    async def test_create_classmate_unauthorized(
        self, client: AsyncClient, classmate_data: dict
    ):
        """Test creating classmate without auth fails."""
        response = await client.post("/api/v1/classmates", json=classmate_data)

        assert response.status_code == 401

    async def test_create_classmate_empty_name(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating classmate with empty name fails."""
        response = await client.post(
            "/api/v1/classmates",
            json={"full_name": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_classmate_invalid_email(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating classmate with invalid email fails."""
        response = await client.post(
            "/api/v1/classmates",
            json={"full_name": "Test", "email": "invalid-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_classmate_invalid_subgroup(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating classmate with invalid subgroup fails."""
        response = await client.post(
            "/api/v1/classmates",
            json={"full_name": "Test", "subgroup": 0},  # Invalid: must be >= 1
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetClassmate:
    """Tests for GET /api/v1/classmates/{id}."""

    async def test_get_classmate_success(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test getting a classmate by ID."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )
        classmate_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/classmates/{classmate_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == classmate_id
        assert data["full_name"] == classmate_data["full_name"]

    async def test_get_classmate_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent classmate fails."""
        response = await client.get(
            "/api/v1/classmates/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_classmate_unauthorized(self, client: AsyncClient):
        """Test getting classmate without auth fails."""
        response = await client.get("/api/v1/classmates/1")

        assert response.status_code == 401


class TestUpdateClassmate:
    """Tests for PUT /api/v1/classmates/{id}."""

    async def test_update_classmate_success(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test updating a classmate."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )
        classmate_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/classmates/{classmate_id}",
            json={"telegram": "@new_telegram", "subgroup": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["telegram"] == "@new_telegram"
        assert data["subgroup"] == 2
        assert data["full_name"] == classmate_data["full_name"]

    async def test_update_classmate_full_name(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test updating classmate's full name."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )
        classmate_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/classmates/{classmate_id}",
            json={"full_name": "Новое Имя"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["full_name"] == "Новое Имя"

    async def test_update_classmate_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent classmate fails."""
        response = await client.put(
            "/api/v1/classmates/99999",
            json={"notes": "Updated notes"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_classmate_invalid_email(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test updating classmate with invalid email fails."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )
        classmate_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/classmates/{classmate_id}",
            json={"email": "invalid-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestDeleteClassmate:
    """Tests for DELETE /api/v1/classmates/{id}."""

    async def test_delete_classmate_success(
        self, client: AsyncClient, auth_headers: dict, classmate_data: dict
    ):
        """Test deleting a classmate."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_data,
            headers=auth_headers,
        )
        classmate_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/classmates/{classmate_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/classmates/{classmate_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_classmate_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent classmate fails."""
        response = await client.delete(
            "/api/v1/classmates/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_delete_classmate_unauthorized(self, client: AsyncClient):
        """Test deleting classmate without auth fails."""
        response = await client.delete("/api/v1/classmates/1")

        assert response.status_code == 401
