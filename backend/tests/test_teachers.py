"""Tests for teacher endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
def teacher_data() -> dict:
    """Sample teacher data."""
    return {
        "full_name": "Иванов Иван Иванович",
        "short_name": "Иванов И.И.",
        "email": "ivanov@omsu.ru",
        "phone": "+7-900-123-45-67",
        "department": "Кафедра информатики",
        "position": "Доцент",
        "office": "418",
        "notes": "Консультации по вторникам",
    }


@pytest.fixture
def teacher_data_2() -> dict:
    """Second sample teacher data."""
    return {
        "full_name": "Петров Петр Петрович",
        "short_name": "Петров П.П.",
        "email": "petrov@omsu.ru",
        "department": "Кафедра математики",
        "position": "Профессор",
    }


class TestGetTeachers:
    """Tests for GET /api/v1/teachers."""

    async def test_get_teachers_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting teachers when none exist."""
        response = await client.get("/api/v1/teachers", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_teachers_unauthorized(self, client: AsyncClient):
        """Test getting teachers without auth fails."""
        response = await client.get("/api/v1/teachers")

        assert response.status_code == 401

    async def test_get_teachers_returns_list(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test getting teachers returns list."""
        # Create teacher first
        await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )

        response = await client.get("/api/v1/teachers", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["full_name"] == teacher_data["full_name"]

    async def test_get_teachers_ordered_by_name(
        self,
        client: AsyncClient,
        auth_headers: dict,
        teacher_data: dict,
        teacher_data_2: dict,
    ):
        """Test teachers are ordered by full_name."""
        # Create teachers (Иванов before Петров alphabetically)
        await client.post(
            "/api/v1/teachers",
            json=teacher_data_2,  # Петров
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/teachers",
            json=teacher_data,  # Иванов
            headers=auth_headers,
        )

        response = await client.get("/api/v1/teachers", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should be ordered alphabetically by full_name
        assert data[0]["full_name"] == "Иванов Иван Иванович"
        assert data[1]["full_name"] == "Петров Петр Петрович"


class TestCreateTeacher:
    """Tests for POST /api/v1/teachers."""

    async def test_create_teacher_success(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test successful teacher creation."""
        response = await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == teacher_data["full_name"]
        assert data["short_name"] == teacher_data["short_name"]
        assert data["email"] == teacher_data["email"]
        assert data["phone"] == teacher_data["phone"]
        assert data["department"] == teacher_data["department"]
        assert data["position"] == teacher_data["position"]
        assert data["office"] == teacher_data["office"]
        assert data["notes"] == teacher_data["notes"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_teacher_minimal(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating teacher with only required fields."""
        response = await client.post(
            "/api/v1/teachers",
            json={"full_name": "Минимальный Преподаватель"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "Минимальный Преподаватель"
        assert data["short_name"] is None
        assert data["email"] is None

    async def test_create_teacher_unauthorized(
        self, client: AsyncClient, teacher_data: dict
    ):
        """Test creating teacher without auth fails."""
        response = await client.post("/api/v1/teachers", json=teacher_data)

        assert response.status_code == 401

    async def test_create_teacher_empty_name(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating teacher with empty name fails."""
        response = await client.post(
            "/api/v1/teachers",
            json={"full_name": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_teacher_name_too_long(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating teacher with name too long fails."""
        response = await client.post(
            "/api/v1/teachers",
            json={"full_name": "A" * 201},  # max is 200
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_teacher_invalid_email(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating teacher with invalid email fails."""
        response = await client.post(
            "/api/v1/teachers",
            json={"full_name": "Test Teacher", "email": "not-an-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetTeacher:
    """Tests for GET /api/v1/teachers/{id}."""

    async def test_get_teacher_success(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test getting a teacher by ID."""
        # Create teacher first
        create_response = await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )
        teacher_id = create_response.json()["id"]

        # Get teacher
        response = await client.get(
            f"/api/v1/teachers/{teacher_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == teacher_id
        assert data["full_name"] == teacher_data["full_name"]
        assert data["email"] == teacher_data["email"]

    async def test_get_teacher_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent teacher fails."""
        response = await client.get(
            "/api/v1/teachers/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_teacher_unauthorized(self, client: AsyncClient):
        """Test getting teacher without auth fails."""
        response = await client.get("/api/v1/teachers/1")

        assert response.status_code == 401


class TestUpdateTeacher:
    """Tests for PUT /api/v1/teachers/{id}."""

    async def test_update_teacher_success(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test updating a teacher."""
        # Create teacher first
        create_response = await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )
        teacher_id = create_response.json()["id"]

        # Update teacher
        response = await client.put(
            f"/api/v1/teachers/{teacher_id}",
            json={"position": "Профессор", "office": "500"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["position"] == "Профессор"
        assert data["office"] == "500"
        # Other fields should remain unchanged
        assert data["full_name"] == teacher_data["full_name"]
        assert data["email"] == teacher_data["email"]

    async def test_update_teacher_full_name(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test updating teacher's full name."""
        # Create teacher
        create_response = await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )
        teacher_id = create_response.json()["id"]

        # Update full name
        response = await client.put(
            f"/api/v1/teachers/{teacher_id}",
            json={"full_name": "Новое Имя Преподавателя"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["full_name"] == "Новое Имя Преподавателя"

    async def test_update_teacher_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent teacher fails."""
        response = await client.put(
            "/api/v1/teachers/99999",
            json={"position": "New Position"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_teacher_invalid_email(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test updating teacher with invalid email fails."""
        # Create teacher
        create_response = await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )
        teacher_id = create_response.json()["id"]

        # Update with invalid email
        response = await client.put(
            f"/api/v1/teachers/{teacher_id}",
            json={"email": "invalid-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestDeleteTeacher:
    """Tests for DELETE /api/v1/teachers/{id}."""

    async def test_delete_teacher_success(
        self, client: AsyncClient, auth_headers: dict, teacher_data: dict
    ):
        """Test deleting a teacher."""
        # Create teacher first
        create_response = await client.post(
            "/api/v1/teachers",
            json=teacher_data,
            headers=auth_headers,
        )
        teacher_id = create_response.json()["id"]

        # Delete teacher
        response = await client.delete(
            f"/api/v1/teachers/{teacher_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(
            f"/api/v1/teachers/{teacher_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_teacher_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent teacher fails."""
        response = await client.delete(
            "/api/v1/teachers/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_delete_teacher_unauthorized(self, client: AsyncClient):
        """Test deleting teacher without auth fails."""
        response = await client.delete("/api/v1/teachers/1")

        assert response.status_code == 401
