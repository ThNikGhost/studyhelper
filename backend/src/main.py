"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers import auth, semesters, subjects


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

app.include_router(api_v1)
