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


class TestSettings:
    """Tests for PATCH /api/v1/auth/me/settings."""

    async def test_update_settings_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating all settings at once."""
        response = await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={
                "preferred_subgroup": 1,
                "preferred_pe_teacher": "Иванов И.И.",
                "theme_mode": "dark",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_subgroup"] == 1
        assert data["preferred_pe_teacher"] == "Иванов И.И."
        assert data["theme_mode"] == "dark"

    async def test_update_settings_partial(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating only some settings (partial update)."""
        # First, set all settings
        await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={
                "preferred_subgroup": 1,
                "preferred_pe_teacher": "Иванов И.И.",
                "theme_mode": "dark",
            },
        )

        # Now update only subgroup
        response = await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={"preferred_subgroup": 2},
        )

        assert response.status_code == 200
        data = response.json()
        # Updated field
        assert data["preferred_subgroup"] == 2
        # Other fields unchanged
        assert data["preferred_pe_teacher"] == "Иванов И.И."
        assert data["theme_mode"] == "dark"

    async def test_update_settings_null_values(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test clearing settings by setting them to null."""
        # Set a value first
        await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={"preferred_subgroup": 1},
        )

        # Clear it
        response = await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={"preferred_subgroup": None},
        )

        assert response.status_code == 200
        assert response.json()["preferred_subgroup"] is None

    async def test_update_settings_unauthorized(self, client: AsyncClient):
        """Test updating settings without auth fails."""
        response = await client.patch(
            "/api/v1/auth/me/settings",
            json={"preferred_subgroup": 1},
        )

        assert response.status_code == 401

    async def test_update_settings_invalid_theme_mode(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test invalid theme_mode value is rejected."""
        response = await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={"theme_mode": "invalid"},
        )

        assert response.status_code == 422

    async def test_settings_in_user_response(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test that settings are included in /me response."""
        # Set some settings
        await client.patch(
            "/api/v1/auth/me/settings",
            headers=auth_headers,
            json={"preferred_subgroup": 2, "theme_mode": "light"},
        )

        # Get user info
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["preferred_subgroup"] == 2
        assert data["theme_mode"] == "light"
        assert "preferred_pe_teacher" in data
