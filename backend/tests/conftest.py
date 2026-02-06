"""Pytest fixtures for testing."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import get_db
from src.main import app
from src.models.base import Base
from src.utils.rate_limit import limiter

# Use SQLite in-memory for tests (avoids Windows PostgreSQL issues)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def engine():
    """Create test database engine."""
    _engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Get a test database session."""
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session


@pytest.fixture
async def client(engine) -> AsyncClient:
    """Async HTTP client for testing."""
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """Test user registration data."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
    }


@pytest.fixture
def test_user_data_2() -> dict:
    """Second test user registration data."""
    return {
        "email": "test2@example.com",
        "password": "testpassword456",
        "name": "Test User 2",
    }


@pytest.fixture
async def registered_user(client: AsyncClient, test_user_data: dict) -> dict:
    """Register a user and return the response data."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    return response.json()


@pytest.fixture
async def auth_tokens(client: AsyncClient, test_user_data: dict) -> dict:
    """Register and login a user, return tokens."""
    await client.post("/api/v1/auth/register", json=test_user_data)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    return response.json()


@pytest.fixture
async def auth_headers(auth_tokens: dict) -> dict:
    """Get authorization headers with access token."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}
