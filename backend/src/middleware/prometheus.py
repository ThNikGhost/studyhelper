"""Prometheus metrics middleware for automatic HTTP instrumentation."""

from __future__ import annotations

import re
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
)

# Replace numeric path segments with {id} to prevent cardinality explosion
_ID_PATTERN = re.compile(r"/\d+(?=/|$)")

# Paths to exclude from instrumentation
_EXCLUDED_PATHS = frozenset({"/metrics", "/health"})


def _normalize_path(path: str) -> str:
    """Normalize URL path by replacing numeric IDs with {id}.

    Args:
        path: Raw request path.

    Returns:
        Normalized path string.
    """
    return _ID_PATTERN.sub("/{id}", path)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Collect HTTP request metrics for Prometheus.

    Records request count, duration histogram, and in-progress gauge.
    Excludes /metrics and /health from instrumentation.
    """

    async def dispatch(self, request: Request, call_next: ...) -> Response:
        """Instrument HTTP request with Prometheus metrics."""
        path = request.url.path
        if path in _EXCLUDED_PATHS:
            return await call_next(request)

        method = request.method
        normalized = _normalize_path(path)

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method).inc()
        start = time.perf_counter()

        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            status = "500"
            raise
        finally:
            duration = time.perf_counter() - start
            HTTP_REQUESTS_TOTAL.labels(
                method=method, path=normalized, status_code=status
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method, path=normalized
            ).observe(duration)
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method).dec()

        return response
