"""Classmate schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ClassmateBase(BaseModel):
    """Base classmate schema."""

    full_name: str = Field(..., min_length=1, max_length=200, description="Full name")
    short_name: str | None = Field(None, max_length=100, description="Short name")
    email: EmailStr | None = Field(None, description="Email address")
    phone: str | None = Field(None, max_length=50, description="Phone number")
    telegram: str | None = Field(None, max_length=100, description="Telegram username")
    vk: HttpUrl | None = Field(None, description="VK profile URL")
    photo_url: str | None = Field(None, max_length=500, description="Photo URL or path")
    group_name: str | None = Field(None, max_length=50, description="Group name")
    subgroup: int | None = Field(None, ge=1, le=10, description="Subgroup number")
    notes: str | None = Field(None, max_length=2000, description="Additional notes")


class ClassmateCreate(ClassmateBase):
    """Schema for creating a classmate."""

    pass


class ClassmateUpdate(BaseModel):
    """Schema for updating a classmate."""

    full_name: str | None = Field(None, min_length=1, max_length=200)
    short_name: str | None = Field(None, max_length=100)
    email: EmailStr | None = Field(None)
    phone: str | None = Field(None, max_length=50)
    telegram: str | None = Field(None, max_length=100)
    vk: HttpUrl | None = Field(None)
    photo_url: str | None = Field(None, max_length=500)
    group_name: str | None = Field(None, max_length=50)
    subgroup: int | None = Field(None, ge=1, le=10)
    notes: str | None = Field(None, max_length=2000)


class ClassmateResponse(ClassmateBase):
    """Schema for classmate response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
