"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: str | None = None
    avatar_url: str | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime
