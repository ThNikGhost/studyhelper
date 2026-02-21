"""Classmate schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ClassmateCreate(BaseModel):
    """Schema for creating a classmate (base fields only)."""

    full_name: str = Field(..., min_length=1, max_length=200, description="Full name")
    group_name: str | None = Field(None, max_length=50, description="Group name")
    subgroup: int | None = Field(None, ge=1, le=10, description="Subgroup number")


class ClassmateUpdate(BaseModel):
    """Schema for updating a classmate (base fields only)."""

    full_name: str | None = Field(None, min_length=1, max_length=200)
    group_name: str | None = Field(None, max_length=50)
    subgroup: int | None = Field(None, ge=1, le=10)


class ClassmateDetailUpsert(BaseModel):
    """Schema for upserting per-user classmate details."""

    short_name: str | None = Field(
        None, max_length=100, description="Short/display name"
    )
    email: EmailStr | None = Field(None, description="Email address")
    phone: str | None = Field(None, max_length=50, description="Phone number")
    telegram: str | None = Field(None, max_length=100, description="Telegram username")
    vk: HttpUrl | None = Field(None, description="VK profile URL")
    photo_url: str | None = Field(None, max_length=500, description="Photo URL or path")
    notes: str | None = Field(None, max_length=2000, description="Additional notes")


class ClassmateDetailResponse(BaseModel):
    """Schema for per-user classmate detail response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    classmate_id: int
    user_id: int
    short_name: str | None
    email: str | None
    phone: str | None
    telegram: str | None
    vk: str | None
    photo_url: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ClassmateListResponse(BaseModel):
    """Schema for classmate list item (base fields only)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    group_name: str | None
    subgroup: int | None
    created_at: datetime
    updated_at: datetime


class ClassmateDetailedResponse(ClassmateListResponse):
    """Schema for single classmate with per-user details."""

    details: ClassmateDetailResponse | None
