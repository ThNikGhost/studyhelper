"""Tests for university endpoints."""

import pytest
from httpx import AsyncClient


# Department fixtures
@pytest.fixture
def department_data() -> dict:
    """Sample department data."""
    return {
        "name": "Кафедра информатики и вычислительной техники",
        "short_name": "ИВТ",
        "faculty": "Факультет компьютерных наук",
        "building": "Главный корпус",
        "floor": 4,
        "phone": "+7-381-2-67-03-00",
        "email": "ivt@omsu.ru",
        "website": "https://ivt.omsu.ru",
        "notes": "Прием по понедельникам",
    }


@pytest.fixture
def department_data_2() -> dict:
    """Second sample department data."""
    return {
        "name": "Кафедра математики",
        "short_name": "Мат",
        "faculty": "Факультет математики",
    }


# Building fixtures
@pytest.fixture
def building_data() -> dict:
    """Sample building data."""
    return {
        "name": "Главный корпус ОмГУ",
        "short_name": "ГК",
        "address": "пр. Мира, 55А, Омск, 644077",
        "floors": 5,
        "description": "Главный учебный корпус университета",
        "latitude": 54.9893,
        "longitude": 73.3686,
    }


@pytest.fixture
def building_data_2() -> dict:
    """Second sample building data."""
    return {
        "name": "Корпус естественных наук",
        "short_name": "КЕН",
        "address": "пр. Мира, 55",
        "floors": 4,
    }


class TestGetDepartments:
    """Tests for GET /api/v1/university/departments."""

    async def test_get_departments_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting departments when none exist."""
        response = await client.get(
            "/api/v1/university/departments", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_departments_unauthorized(self, client: AsyncClient):
        """Test getting departments without auth fails."""
        response = await client.get("/api/v1/university/departments")

        assert response.status_code == 401

    async def test_get_departments_returns_list(
        self, client: AsyncClient, auth_headers: dict, department_data: dict
    ):
        """Test getting departments returns list."""
        await client.post(
            "/api/v1/university/departments",
            json=department_data,
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/university/departments", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == department_data["name"]


class TestCreateDepartment:
    """Tests for POST /api/v1/university/departments."""

    async def test_create_department_success(
        self, client: AsyncClient, auth_headers: dict, department_data: dict
    ):
        """Test successful department creation."""
        response = await client.post(
            "/api/v1/university/departments",
            json=department_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == department_data["name"]
        assert data["short_name"] == department_data["short_name"]
        assert data["faculty"] == department_data["faculty"]
        assert data["floor"] == department_data["floor"]
        assert data["email"] == department_data["email"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_department_minimal(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating department with only required fields."""
        response = await client.post(
            "/api/v1/university/departments",
            json={"name": "Минимальная кафедра"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Минимальная кафедра"
        assert data["short_name"] is None

    async def test_create_department_unauthorized(
        self, client: AsyncClient, department_data: dict
    ):
        """Test creating department without auth fails."""
        response = await client.post(
            "/api/v1/university/departments", json=department_data
        )

        assert response.status_code == 401

    async def test_create_department_empty_name(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating department with empty name fails."""
        response = await client.post(
            "/api/v1/university/departments",
            json={"name": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_department_invalid_email(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating department with invalid email fails."""
        response = await client.post(
            "/api/v1/university/departments",
            json={"name": "Test", "email": "invalid-email"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetDepartment:
    """Tests for GET /api/v1/university/departments/{id}."""

    async def test_get_department_success(
        self, client: AsyncClient, auth_headers: dict, department_data: dict
    ):
        """Test getting a department by ID."""
        create_response = await client.post(
            "/api/v1/university/departments",
            json=department_data,
            headers=auth_headers,
        )
        department_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/university/departments/{department_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == department_id
        assert data["name"] == department_data["name"]

    async def test_get_department_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent department fails."""
        response = await client.get(
            "/api/v1/university/departments/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateDepartment:
    """Tests for PUT /api/v1/university/departments/{id}."""

    async def test_update_department_success(
        self, client: AsyncClient, auth_headers: dict, department_data: dict
    ):
        """Test updating a department."""
        create_response = await client.post(
            "/api/v1/university/departments",
            json=department_data,
            headers=auth_headers,
        )
        department_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/university/departments/{department_id}",
            json={"floor": 5, "notes": "Updated notes"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["floor"] == 5
        assert data["notes"] == "Updated notes"
        assert data["name"] == department_data["name"]

    async def test_update_department_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent department fails."""
        response = await client.put(
            "/api/v1/university/departments/99999",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteDepartment:
    """Tests for DELETE /api/v1/university/departments/{id}."""

    async def test_delete_department_success(
        self, client: AsyncClient, auth_headers: dict, department_data: dict
    ):
        """Test deleting a department."""
        create_response = await client.post(
            "/api/v1/university/departments",
            json=department_data,
            headers=auth_headers,
        )
        department_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/university/departments/{department_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/university/departments/{department_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_department_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent department fails."""
        response = await client.delete(
            "/api/v1/university/departments/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestGetBuildings:
    """Tests for GET /api/v1/university/buildings."""

    async def test_get_buildings_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting buildings when none exist."""
        response = await client.get(
            "/api/v1/university/buildings", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_buildings_unauthorized(self, client: AsyncClient):
        """Test getting buildings without auth fails."""
        response = await client.get("/api/v1/university/buildings")

        assert response.status_code == 401

    async def test_get_buildings_returns_list(
        self, client: AsyncClient, auth_headers: dict, building_data: dict
    ):
        """Test getting buildings returns list."""
        await client.post(
            "/api/v1/university/buildings",
            json=building_data,
            headers=auth_headers,
        )

        response = await client.get(
            "/api/v1/university/buildings", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == building_data["name"]


class TestCreateBuilding:
    """Tests for POST /api/v1/university/buildings."""

    async def test_create_building_success(
        self, client: AsyncClient, auth_headers: dict, building_data: dict
    ):
        """Test successful building creation."""
        response = await client.post(
            "/api/v1/university/buildings",
            json=building_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == building_data["name"]
        assert data["short_name"] == building_data["short_name"]
        assert data["address"] == building_data["address"]
        assert data["floors"] == building_data["floors"]
        assert data["latitude"] == building_data["latitude"]
        assert data["longitude"] == building_data["longitude"]
        assert "id" in data

    async def test_create_building_minimal(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating building with only required fields."""
        response = await client.post(
            "/api/v1/university/buildings",
            json={"name": "Минимальный корпус"},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Минимальный корпус"
        assert data["floors"] is None

    async def test_create_building_unauthorized(
        self, client: AsyncClient, building_data: dict
    ):
        """Test creating building without auth fails."""
        response = await client.post("/api/v1/university/buildings", json=building_data)

        assert response.status_code == 401

    async def test_create_building_empty_name(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating building with empty name fails."""
        response = await client.post(
            "/api/v1/university/buildings",
            json={"name": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_building_invalid_latitude(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating building with invalid latitude fails."""
        response = await client.post(
            "/api/v1/university/buildings",
            json={"name": "Test", "latitude": 100},  # Invalid: must be -90 to 90
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetBuilding:
    """Tests for GET /api/v1/university/buildings/{id}."""

    async def test_get_building_success(
        self, client: AsyncClient, auth_headers: dict, building_data: dict
    ):
        """Test getting a building by ID."""
        create_response = await client.post(
            "/api/v1/university/buildings",
            json=building_data,
            headers=auth_headers,
        )
        building_id = create_response.json()["id"]

        response = await client.get(
            f"/api/v1/university/buildings/{building_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == building_id
        assert data["name"] == building_data["name"]

    async def test_get_building_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent building fails."""
        response = await client.get(
            "/api/v1/university/buildings/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUpdateBuilding:
    """Tests for PUT /api/v1/university/buildings/{id}."""

    async def test_update_building_success(
        self, client: AsyncClient, auth_headers: dict, building_data: dict
    ):
        """Test updating a building."""
        create_response = await client.post(
            "/api/v1/university/buildings",
            json=building_data,
            headers=auth_headers,
        )
        building_id = create_response.json()["id"]

        response = await client.put(
            f"/api/v1/university/buildings/{building_id}",
            json={"floors": 6, "description": "Updated description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["floors"] == 6
        assert data["description"] == "Updated description"
        assert data["name"] == building_data["name"]

    async def test_update_building_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent building fails."""
        response = await client.put(
            "/api/v1/university/buildings/99999",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteBuilding:
    """Tests for DELETE /api/v1/university/buildings/{id}."""

    async def test_delete_building_success(
        self, client: AsyncClient, auth_headers: dict, building_data: dict
    ):
        """Test deleting a building."""
        create_response = await client.post(
            "/api/v1/university/buildings",
            json=building_data,
            headers=auth_headers,
        )
        building_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/v1/university/buildings/{building_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = await client.get(
            f"/api/v1/university/buildings/{building_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    async def test_delete_building_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent building fails."""
        response = await client.delete(
            "/api/v1/university/buildings/99999",
            headers=auth_headers,
        )

        assert response.status_code == 404
