"""Teacher schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TeacherBase(BaseModel):
    """Base teacher schema."""

    full_name: str = Field(..., min_length=1, max_length=200, description="Full name")
    short_name: str | None = Field(None, max_length=100, description="Short name")
    email: EmailStr | None = Field(None, description="Email address")
    phone: str | None = Field(None, max_length=50, description="Phone number")
    department: str | None = Field(None, max_length=200, description="Department")
    position: str | None = Field(None, max_length=200, description="Position/title")
    office: str | None = Field(None, max_length=100, description="Office location")
    notes: str | None = Field(None, description="Additional notes")


class TeacherCreate(TeacherBase):
    """Schema for creating a teacher."""

    pass


class TeacherUpdate(BaseModel):
    """Schema for updating a teacher."""

    full_name: str | None = Field(None, min_length=1, max_length=200)
    short_name: str | None = Field(None, max_length=100)
    email: EmailStr | None = Field(None)
    phone: str | None = Field(None, max_length=50)
    department: str | None = Field(None, max_length=200)
    position: str | None = Field(None, max_length=200)
    office: str | None = Field(None, max_length=100)
    notes: str | None = Field(None)


class TeacherResponse(TeacherBase):
    """Schema for teacher response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
