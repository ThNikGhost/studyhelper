"""Tests for Telegram REST API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def tg_auth_headers(client: AsyncClient, test_user_data: dict) -> dict:
    """Register, login, and return auth headers."""
    await client.post("/api/v1/auth/register", json=test_user_data)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


class TestTelegramStatus:
    """Tests for GET /api/v1/telegram/status."""

    async def test_status_not_linked(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """Should return not linked when no link exists."""
        response = await client.get(
            "/api/v1/telegram/status",
            headers=tg_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_linked"] is False
        assert data["link_code"] is None

    async def test_status_unauthorized(self, client: AsyncClient) -> None:
        """Should return 401 without auth."""
        response = await client.get("/api/v1/telegram/status")
        assert response.status_code == 401


class TestGenerateLinkCode:
    """Tests for POST /api/v1/telegram/link-code."""

    async def test_generates_code(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """Should generate a 6-char link code."""
        response = await client.post(
            "/api/v1/telegram/link-code",
            headers=tg_auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "link_code" in data
        assert len(data["link_code"]) == 6
        assert "expires_at" in data

    async def test_status_shows_code(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """After generating code, status should show it."""
        await client.post(
            "/api/v1/telegram/link-code",
            headers=tg_auth_headers,
        )
        response = await client.get(
            "/api/v1/telegram/status",
            headers=tg_auth_headers,
        )
        data = response.json()
        assert data["link_code"] is not None
        assert data["is_linked"] is False


class TestUnlink:
    """Tests for DELETE /api/v1/telegram/link."""

    async def test_unlink_not_found(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """Should return 404 when no link exists."""
        response = await client.delete(
            "/api/v1/telegram/link",
            headers=tg_auth_headers,
        )
        assert response.status_code == 404

    async def test_unlink_with_code(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """Should delete link even if only code was generated (not fully linked)."""
        await client.post(
            "/api/v1/telegram/link-code",
            headers=tg_auth_headers,
        )
        response = await client.delete(
            "/api/v1/telegram/link",
            headers=tg_auth_headers,
        )
        assert response.status_code == 204


class TestUpdateNotifications:
    """Tests for PATCH /api/v1/telegram/notifications."""

    async def test_update_no_link(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """Should return 404 when no link exists."""
        response = await client.patch(
            "/api/v1/telegram/notifications",
            headers=tg_auth_headers,
            json={"notify_deadlines": False},
        )
        assert response.status_code == 404

    async def test_update_with_link(
        self, client: AsyncClient, tg_auth_headers: dict
    ) -> None:
        """Should update notifications when link exists."""
        await client.post(
            "/api/v1/telegram/link-code",
            headers=tg_auth_headers,
        )
        response = await client.patch(
            "/api/v1/telegram/notifications",
            headers=tg_auth_headers,
            json={"notify_deadlines": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notify_deadlines"] is False
        assert data["morning_summary"] is True


class TestWebhook:
    """Tests for POST /api/v1/telegram/webhook."""

    async def test_webhook_no_bot(self, client: AsyncClient) -> None:
        """Should return 503 when bot is not initialized."""
        response = await client.post(
            "/api/v1/telegram/webhook",
            json={"update_id": 123},
        )
        assert response.status_code == 503
