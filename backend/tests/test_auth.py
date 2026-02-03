"""Tests for authentication endpoints."""

from httpx import AsyncClient


class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    async def test_register_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    async def test_register_duplicate_email(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test registration with existing email fails."""
        await client.post("/api/v1/auth/register", json=test_user_data)
        response = await client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code in (400, 409)
        assert "email" in response.json()["detail"].lower()

    async def test_register_max_users_limit(
        self, client: AsyncClient, test_user_data: dict, test_user_data_2: dict
    ):
        """Test that only 2 users can be registered (pair mode)."""
        # Register first user
        response1 = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201

        # Register second user
        response2 = await client.post("/api/v1/auth/register", json=test_user_data_2)
        assert response2.status_code == 201

        # Third user should fail
        third_user = {
            "email": "third@example.com",
            "password": "password123",
            "name": "Third User",
        }
        response3 = await client.post("/api/v1/auth/register", json=third_user)
        assert response3.status_code == 403
        detail = response3.json()["detail"].lower()
        assert "maximum" in detail or "limit" in detail

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "invalid-email", "password": "password123", "name": "Test"},
        )

        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password fails."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "short", "name": "Test"},
        )

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Test successful login."""
        await client.post("/api/v1/auth/register", json=test_user_data)
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Test login with wrong password fails."""
        await client.post("/api/v1/auth/register", json=test_user_data)
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": test_user_data["email"], "password": "wrongpassword"},
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == 401


class TestMe:
    """Tests for GET /api/v1/auth/me."""

    async def test_me_success(
        self, client: AsyncClient, auth_headers: dict, test_user_data: dict
    ):
        """Test getting current user info."""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]

    async def test_me_no_token(self, client: AsyncClient):
        """Test getting user info without token fails."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_me_invalid_token(self, client: AsyncClient):
        """Test getting user info with invalid token fails."""
        response = await client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


class TestRefresh:
    """Tests for POST /api/v1/auth/refresh."""

    async def test_refresh_success(self, client: AsyncClient, auth_tokens: dict):
        """Test successful token refresh."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401

    async def test_refresh_with_access_token(
        self, client: AsyncClient, auth_tokens: dict
    ):
        """Test refresh with access token (not refresh) fails."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["access_token"]},
        )

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/v1/auth/logout."""

    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful logout."""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    async def test_logout_no_token(self, client: AsyncClient):
        """Test logout without token fails."""
        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 401
