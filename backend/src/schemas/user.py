"""User schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

VALID_LESSON_TYPES = {
    "lecture",
    "practice",
    "lab",
    "seminar",
    "exam",
    "consultation",
    "other",
}


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
    hidden_subjects: dict[str, list[str] | None] | None = None

    @field_validator("hidden_subjects")
    @classmethod
    def validate_hidden_subjects(
        cls, v: dict[str, list[str] | None] | None
    ) -> dict[str, list[str] | None] | None:
        """Validate hidden_subjects dict format.

        Keys must be stringified positive integers (subject IDs).
        Values must be null (hide all) or list of valid lesson types.
        Empty list is normalized to null (hide all).
        Max 100 entries.
        """
        if v is None:
            return v
        cleaned: dict[str, list[str] | None] = {}
        for key, types in v.items():
            # Key must be a positive integer string
            try:
                sid = int(key)
            except (ValueError, TypeError):
                continue
            if sid <= 0:
                continue
            # Normalize value
            if types is None or (isinstance(types, list) and len(types) == 0):
                cleaned[str(sid)] = None
            elif isinstance(types, list):
                valid = list(dict.fromkeys(t for t in types if t in VALID_LESSON_TYPES))
                cleaned[str(sid)] = valid if valid else None
            else:
                continue
        if len(cleaned) > 100:
            cleaned = dict(list(cleaned.items())[:100])
        return cleaned or None


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    avatar_url: str | None
    preferred_subgroup: int | None
    preferred_pe_teacher: str | None
    theme_mode: str | None
    hidden_subjects: dict[str, list[str] | None] | None
    created_at: datetime
    updated_at: datetime
