"""User service for database operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.user import UserCreate
from src.utils.security import hash_password


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users_count(db: AsyncSession) -> int:
    """Get total number of users."""
    result = await db.execute(select(func.count(User.id)))
    return result.scalar_one()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user."""
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
