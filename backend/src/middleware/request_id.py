"""Request ID middleware for tracing requests through logs."""

from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.logging_config import request_id_ctx


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to each request.

    - Uses incoming X-Request-ID header if present.
    - Otherwise generates a short uuid4 hex (12 chars).
    - Sets the ID in ContextVar for structured logging.
    - Adds X-Request-ID to response headers.
    """

    async def dispatch(self, request: Request, call_next: ...) -> Response:
        """Process request with ID tracking."""
        rid = request.headers.get("x-request-id") or uuid4().hex[:12]
        token = request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            request_id_ctx.reset(token)
