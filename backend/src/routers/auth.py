"""Authentication router."""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.auth import (
    AccessTokenResponse,
    RefreshRequest,
    TokenResponse,
)
from src.schemas.user import UserCreate, UserResponse
from src.services.auth import (
    login_user,
    refresh_access_token,
    register_user,
)
from src.utils.rate_limit import limiter

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new user."""
    return await register_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login and get access and refresh tokens."""
    return await login_user(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    request_data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> AccessTokenResponse:
    """Refresh access token using refresh token."""
    access_token = await refresh_access_token(db, request_data.refresh_token)
    return AccessTokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current authenticated user."""
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Logout current user.

    Note: With JWT, logout is typically handled client-side
    by removing the tokens. This endpoint is for API completeness.
    """
    return {"message": "Successfully logged out"}
