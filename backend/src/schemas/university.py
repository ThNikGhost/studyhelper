"""University schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


# Department schemas
class DepartmentBase(BaseModel):
    """Base department schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Department name")
    short_name: str | None = Field(None, max_length=50, description="Short name")
    faculty: str | None = Field(None, max_length=200, description="Faculty name")
    building: str | None = Field(None, max_length=100, description="Building name")
    floor: int | None = Field(None, ge=0, le=50, description="Floor number")
    phone: str | None = Field(None, max_length=50, description="Phone number")
    email: EmailStr | None = Field(None, description="Email address")
    website: HttpUrl | None = Field(None, description="Website URL")
    notes: str | None = Field(None, description="Additional notes")


class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""

    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""

    name: str | None = Field(None, min_length=1, max_length=200)
    short_name: str | None = Field(None, max_length=50)
    faculty: str | None = Field(None, max_length=200)
    building: str | None = Field(None, max_length=100)
    floor: int | None = Field(None, ge=0, le=50)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = Field(None)
    website: HttpUrl | None = Field(None)
    notes: str | None = Field(None)


class DepartmentResponse(DepartmentBase):
    """Schema for department response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Building schemas
class BuildingBase(BaseModel):
    """Base building schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Building name")
    short_name: str | None = Field(None, max_length=50, description="Short name")
    address: str | None = Field(None, max_length=300, description="Address")
    floors: int | None = Field(None, ge=1, le=100, description="Number of floors")
    description: str | None = Field(None, description="Description")
    latitude: float | None = Field(None, ge=-90, le=90, description="Latitude")
    longitude: float | None = Field(None, ge=-180, le=180, description="Longitude")


class BuildingCreate(BuildingBase):
    """Schema for creating a building."""

    pass


class BuildingUpdate(BaseModel):
    """Schema for updating a building."""

    name: str | None = Field(None, min_length=1, max_length=200)
    short_name: str | None = Field(None, max_length=50)
    address: str | None = Field(None, max_length=300)
    floors: int | None = Field(None, ge=1, le=100)
    description: str | None = Field(None)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)


class BuildingResponse(BuildingBase):
    """Schema for building response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
