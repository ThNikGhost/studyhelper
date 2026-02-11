"""Tests for health endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "StudyHelper API"
    assert "version" in data


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    """Test health check endpoint returns status and dependency checks."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "redis" in data
    assert data["db"] is True  # DB should be reachable in tests
