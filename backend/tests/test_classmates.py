"""Tests for classmate endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.fixture
def classmate_base_data() -> dict:
    """Sample classmate base data."""
    return {
        "full_name": "Сидоров Сидор Сидорович",
        "group_name": "ММБ-101",
        "subgroup": 1,
    }


@pytest.fixture
def classmate_base_data_2() -> dict:
    """Second sample classmate base data."""
    return {
        "full_name": "Козлова Мария Ивановна",
        "group_name": "ММБ-101",
        "subgroup": 2,
    }


@pytest.fixture
def details_data() -> dict:
    """Sample classmate detail data."""
    return {
        "short_name": "Сидоров С.С.",
        "email": "sidorov@example.com",
        "phone": "+7-900-111-22-33",
        "telegram": "@sidorov",
        "vk": "https://vk.com/sidorov",
        "notes": "Староста группы",
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
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test getting classmates returns list with base fields only."""
        await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )

        response = await client.get("/api/v1/classmates", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["full_name"] == classmate_base_data["full_name"]
        # List response should not contain details
        assert "details" not in data[0]
        assert "email" not in data[0]
        assert "phone" not in data[0]

    async def test_get_classmates_ordered_by_name(
        self,
        client: AsyncClient,
        auth_headers: dict,
        classmate_base_data: dict,
        classmate_base_data_2: dict,
    ):
        """Test classmates are ordered by full_name."""
        await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,  # Сидоров
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/classmates",
            json=classmate_base_data_2,  # Козлова
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
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test successful classmate creation."""
        response = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == classmate_base_data["full_name"]
        assert data["group_name"] == classmate_base_data["group_name"]
        assert data["subgroup"] == classmate_base_data["subgroup"]
        assert data["details"] is None
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
        assert data["group_name"] is None
        assert data["details"] is None

    async def test_create_classmate_unauthorized(
        self, client: AsyncClient, classmate_base_data: dict
    ):
        """Test creating classmate without auth fails."""
        response = await client.post("/api/v1/classmates", json=classmate_base_data)

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

    async def test_create_classmate_invalid_subgroup(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating classmate with invalid subgroup fails."""
        response = await client.post(
            "/api/v1/classmates",
            json={"full_name": "Test", "subgroup": 0},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetClassmate:
    """Tests for GET /api/v1/classmates/{id}."""

    async def test_get_classmate_success(
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test getting a classmate by ID returns base fields and details."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
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
        assert data["full_name"] == classmate_base_data["full_name"]
        assert "details" in data
        assert data["details"] is None

    async def test_get_classmate_with_details(
        self,
        client: AsyncClient,
        auth_headers: dict,
        classmate_base_data: dict,
        details_data: dict,
    ):
        """Test getting a classmate returns per-user details when present."""
        create_resp = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_resp.json()["id"]

        await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json=details_data,
            headers=auth_headers,
        )

        response = await client.get(
            f"/api/v1/classmates/{classmate_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["details"] is not None
        assert data["details"]["email"] == details_data["email"]
        assert data["details"]["phone"] == details_data["phone"]

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
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test updating a classmate's base fields."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/classmates/{classmate_id}",
            json={"subgroup": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["subgroup"] == 2
        assert data["full_name"] == classmate_base_data["full_name"]

    async def test_update_classmate_full_name(
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test updating classmate's full name."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
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
            json={"group_name": "ИВТ-202"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteClassmate:
    """Tests for DELETE /api/v1/classmates/{id}."""

    async def test_delete_classmate_success(
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test deleting a classmate."""
        create_response = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
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


class TestUpsertDetails:
    """Tests for PATCH /api/v1/classmates/{id}/details."""

    async def test_create_details_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        classmate_base_data: dict,
        details_data: dict,
    ):
        """Test creating details for a classmate."""
        create_resp = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json=details_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == details_data["email"]
        assert data["phone"] == details_data["phone"]
        assert data["telegram"] == details_data["telegram"]
        assert data["notes"] == details_data["notes"]
        assert data["classmate_id"] == classmate_id
        assert "id" in data

    async def test_update_details_idempotent(
        self,
        client: AsyncClient,
        auth_headers: dict,
        classmate_base_data: dict,
        details_data: dict,
    ):
        """Test that repeated PATCH upserts details (idempotent)."""
        create_resp = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_resp.json()["id"]

        await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json=details_data,
            headers=auth_headers,
        )
        response = await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json={"phone": "+7-000-000-00-00"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["phone"] == "+7-000-000-00-00"

    async def test_upsert_details_classmate_not_found(
        self, client: AsyncClient, auth_headers: dict, details_data: dict
    ):
        """Test upserting details for non-existent classmate fails."""
        response = await client.patch(
            "/api/v1/classmates/99999/details",
            json=details_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_upsert_details_unauthorized(
        self, client: AsyncClient, details_data: dict
    ):
        """Test upserting details without auth fails."""
        response = await client.patch("/api/v1/classmates/1/details", json=details_data)

        assert response.status_code == 401

    async def test_upsert_details_invalid_email(
        self, client: AsyncClient, auth_headers: dict, classmate_base_data: dict
    ):
        """Test upserting details with invalid email fails."""
        create_resp = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json={"email": "not-an-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_details_per_user_isolation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        auth_headers_user2: dict,
        classmate_base_data: dict,
        details_data: dict,
    ):
        """Test that details are isolated per user."""
        create_resp = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_resp.json()["id"]

        # User 1 sets details
        await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json=details_data,
            headers=auth_headers,
        )

        # User 2 sees no details
        response = await client.get(
            f"/api/v1/classmates/{classmate_id}",
            headers=auth_headers_user2,
        )

        assert response.status_code == 200
        assert response.json()["details"] is None

    async def test_upsert_details_partial(
        self,
        client: AsyncClient,
        auth_headers: dict,
        classmate_base_data: dict,
    ):
        """Test upserting details with partial fields."""
        create_resp = await client.post(
            "/api/v1/classmates",
            json=classmate_base_data,
            headers=auth_headers,
        )
        classmate_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/classmates/{classmate_id}/details",
            json={"phone": "+7-999-999-99-99"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "+7-999-999-99-99"
        assert data["email"] is None
        assert data["telegram"] is None
