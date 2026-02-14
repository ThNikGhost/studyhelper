"""Tests for Prometheus metrics middleware and endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.metrics import SCHEDULE_SYNC_TOTAL
from src.middleware.prometheus import _normalize_path


class TestMetricsEndpoint:
    """Tests for /metrics endpoint."""

    @pytest.mark.asyncio
    async def test_metrics_returns_200(self) -> None:
        """Test /metrics endpoint returns 200."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/metrics")

        assert resp.status_code == 200
        assert "text/plain" in resp.headers["content-type"]

    @pytest.mark.asyncio
    async def test_metrics_contains_python_info(self) -> None:
        """Test metrics contain default python_info collector."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/metrics")

        assert "python_info" in resp.text

    @pytest.mark.asyncio
    async def test_metrics_contain_app_info(self) -> None:
        """Test metrics contain app_info gauge."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Trigger lifespan indirectly via a normal request
            resp = await client.get("/metrics")

        assert "app_info" in resp.text

    @pytest.mark.asyncio
    async def test_http_metrics_appear_after_request(self) -> None:
        """Test HTTP request metrics appear after making a request."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Make a request to generate metrics
            await client.get("/")
            resp = await client.get("/metrics")

        assert "http_requests_total" in resp.text
        assert "http_request_duration_seconds" in resp.text

    @pytest.mark.asyncio
    async def test_metrics_and_health_not_instrumented(self) -> None:
        """Test /metrics and /health are excluded from HTTP metrics."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.get("/metrics")
            await client.get("/health")
            resp = await client.get("/metrics")

        # These paths should not appear as instrumented paths
        lines = resp.text.split("\n")
        http_req_lines = [
            line
            for line in lines
            if line.startswith("http_requests_total") and "path=" in line
        ]
        paths_in_metrics = [
            line for line in http_req_lines if 'path="/metrics"' in line
        ]
        paths_in_health = [line for line in http_req_lines if 'path="/health"' in line]
        assert len(paths_in_metrics) == 0
        assert len(paths_in_health) == 0


class TestPathNormalization:
    """Tests for path normalization."""

    def test_numeric_id_replaced(self) -> None:
        """Test numeric path segments are replaced with {id}."""
        assert _normalize_path("/api/v1/subjects/5") == "/api/v1/subjects/{id}"

    def test_multiple_ids_replaced(self) -> None:
        """Test multiple numeric segments are replaced."""
        assert (
            _normalize_path("/api/v1/subjects/5/works/123")
            == "/api/v1/subjects/{id}/works/{id}"
        )

    def test_no_ids_unchanged(self) -> None:
        """Test paths without IDs are unchanged."""
        assert _normalize_path("/api/v1/subjects") == "/api/v1/subjects"

    def test_trailing_id(self) -> None:
        """Test trailing numeric segment."""
        assert _normalize_path("/api/v1/works/42") == "/api/v1/works/{id}"


class TestScheduleSyncMetrics:
    """Tests for schedule sync metric counters."""

    def test_sync_skipped_counter(self) -> None:
        """Test skipped counter can be incremented."""
        before = SCHEDULE_SYNC_TOTAL.labels(status="skipped")._value.get()
        SCHEDULE_SYNC_TOTAL.labels(status="skipped").inc()
        after = SCHEDULE_SYNC_TOTAL.labels(status="skipped")._value.get()
        assert after == before + 1

    def test_sync_success_counter(self) -> None:
        """Test success counter can be incremented."""
        before = SCHEDULE_SYNC_TOTAL.labels(status="success")._value.get()
        SCHEDULE_SYNC_TOTAL.labels(status="success").inc()
        after = SCHEDULE_SYNC_TOTAL.labels(status="success")._value.get()
        assert after == before + 1

    def test_sync_error_counter(self) -> None:
        """Test error counter can be incremented."""
        before = SCHEDULE_SYNC_TOTAL.labels(status="error")._value.get()
        SCHEDULE_SYNC_TOTAL.labels(status="error").inc()
        after = SCHEDULE_SYNC_TOTAL.labels(status="error")._value.get()
        assert after == before + 1
