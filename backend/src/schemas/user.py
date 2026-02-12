"""User schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    name: str | None = None
    avatar_url: str | None = None


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings (synced across devices)."""

    preferred_subgroup: int | None = None
    preferred_pe_teacher: str | None = Field(None, max_length=200)
    theme_mode: Literal["light", "dark", "system"] | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    avatar_url: str | None
    preferred_subgroup: int | None
    preferred_pe_teacher: str | None
    theme_mode: str | None
    created_at: datetime
    updated_at: datetime
