"""Authentication service."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.auth import TokenResponse
from src.schemas.user import UserCreate
from src.services.user import (
    create_user,
    get_user_by_email,
    get_users_count,
)
from src.utils.exceptions import (
    CredentialsException,
    UserExistsException,
    UserLimitException,
)
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)

MAX_USERS = 2


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Register a new user with limit check."""
    # Check if user limit reached
    users_count = await get_users_count(db)
    if users_count >= MAX_USERS:
        raise UserLimitException()

    # Check if email already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise UserExistsException()

    # Create user
    return await create_user(db, user_data)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """Authenticate user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> TokenResponse:
    """Login user and return tokens."""
    user = await authenticate_user(db, email, password)
    if not user:
        raise CredentialsException(detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise CredentialsException(detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise CredentialsException(detail="Invalid refresh token")

    # Verify user still exists
    from src.services.user import get_user_by_id

    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise CredentialsException(detail="User not found")

    return create_access_token(data={"sub": str(user.id)})
