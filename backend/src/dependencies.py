"""FastAPI dependencies."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.user import User
from src.services.user import get_user_by_id
from src.utils.exceptions import CredentialsException
from src.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency for getting current authenticated user."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise CredentialsException()

    user_id = payload.get("sub")
    if not user_id:
        raise CredentialsException()

    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise CredentialsException()

    return user
