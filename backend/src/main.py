"""FastAPI application entry point."""

import logging
import sys

# Fix for asyncpg on Windows - use SelectorEventLoop instead of ProactorEventLoop
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.config import settings
from src.routers import (
    attendance,
    auth,
    classmates,
    files,
    notes,
    schedule,
    semesters,
    subjects,
    teachers,
    university,
    uploads,
    works,
)
from src.utils.rate_limit import limiter

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure structured logging based on debug mode."""
    log_level = logging.DEBUG if settings.debug else logging.INFO
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    logging.basicConfig(level=log_level, format=log_format, force=True)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: ...) -> Response:
        """Add security headers to the response."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    setup_logging()
    logger.info("StudyHelper API starting up")
    yield
    # Shutdown
    logger.info("StudyHelper API shutting down")


app = FastAPI(
    title="StudyHelper API",
    description="Backend API for StudyHelper PWA",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions without leaking stack traces."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "StudyHelper API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# API v1 router
api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1.include_router(semesters.router, prefix="/semesters", tags=["Semesters"])
api_v1.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_v1.include_router(works.router, prefix="/works", tags=["Works"])
api_v1.include_router(teachers.router, prefix="/teachers", tags=["Teachers"])
api_v1.include_router(university.router, prefix="/university", tags=["University"])
api_v1.include_router(classmates.router, prefix="/classmates", tags=["Classmates"])
api_v1.include_router(schedule.router, prefix="/schedule", tags=["Schedule"])
api_v1.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
api_v1.include_router(files.router, prefix="/files", tags=["Files"])
api_v1.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_v1.include_router(notes.router, prefix="/notes", tags=["Notes"])

app.include_router(api_v1)

# Mount static files for uploads
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
