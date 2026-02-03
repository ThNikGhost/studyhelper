"""FastAPI application entry point."""

import sys

# Fix for asyncpg on Windows - use SelectorEventLoop instead of ProactorEventLoop
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers import (
    auth,
    classmates,
    schedule,
    semesters,
    subjects,
    teachers,
    university,
    works,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="StudyHelper API",
    description="Backend API for StudyHelper PWA",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(api_v1)
