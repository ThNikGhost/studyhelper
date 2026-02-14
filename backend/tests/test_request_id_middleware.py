"""Tests for RequestIdMiddleware."""

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from src.logging_config import request_id_ctx
from src.middleware.request_id import RequestIdMiddleware


def _make_app() -> Starlette:
    """Create a minimal Starlette app with RequestIdMiddleware."""

    async def index(request: Request) -> JSONResponse:
        return JSONResponse({"request_id": request_id_ctx.get()})

    app = Starlette(routes=[Route("/", index)])
    app.add_middleware(RequestIdMiddleware)
    return app


@pytest.mark.asyncio
async def test_response_has_request_id() -> None:
    """Test that response includes X-Request-ID header."""
    app = _make_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200
    assert "x-request-id" in resp.headers
    assert len(resp.headers["x-request-id"]) == 12


@pytest.mark.asyncio
async def test_preserves_incoming_request_id() -> None:
    """Test that incoming X-Request-ID is preserved."""
    app = _make_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/", headers={"X-Request-ID": "custom-id-123"})

    assert resp.headers["x-request-id"] == "custom-id-123"
    body = resp.json()
    assert body["request_id"] == "custom-id-123"


@pytest.mark.asyncio
async def test_different_requests_get_different_ids() -> None:
    """Test that different requests get different auto-generated IDs."""
    app = _make_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp1 = await client.get("/")
        resp2 = await client.get("/")

    assert resp1.headers["x-request-id"] != resp2.headers["x-request-id"]
