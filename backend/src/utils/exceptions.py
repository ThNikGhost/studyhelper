"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """Exception for invalid credentials."""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        """Initialize exception."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserLimitException(HTTPException):
    """Exception when user registration limit is reached."""

    def __init__(self) -> None:
        """Initialize exception."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Maximum number of users (2) reached. Registration is closed.",
        )


class UserExistsException(HTTPException):
    """Exception when user with email already exists."""

    def __init__(self) -> None:
        """Initialize exception."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


class NotFoundException(HTTPException):
    """Exception for resource not found."""

    def __init__(self, resource: str = "Resource") -> None:
        """Initialize exception."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
        )
