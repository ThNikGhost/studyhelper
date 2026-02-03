"""University router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.university import (
    BuildingCreate,
    BuildingResponse,
    BuildingUpdate,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from src.services import university as university_service

router = APIRouter()


# Department endpoints
@router.get("/departments", response_model=list[DepartmentResponse])
async def get_departments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DepartmentResponse]:
    """Get all departments."""
    return await university_service.get_departments(db)


@router.post(
    "/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentResponse:
    """Create a new department."""
    return await university_service.create_department(db, data)


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentResponse:
    """Get a department by ID."""
    department = await university_service.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return department


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentResponse:
    """Update a department."""
    department = await university_service.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return await university_service.update_department(db, department, data)


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a department."""
    department = await university_service.get_department_by_id(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    await university_service.delete_department(db, department)


# Building endpoints
@router.get("/buildings", response_model=list[BuildingResponse])
async def get_buildings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BuildingResponse]:
    """Get all buildings."""
    return await university_service.get_buildings(db)


@router.post(
    "/buildings", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED
)
async def create_building(
    data: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BuildingResponse:
    """Create a new building."""
    return await university_service.create_building(db, data)


@router.get("/buildings/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BuildingResponse:
    """Get a building by ID."""
    building = await university_service.get_building_by_id(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    return building


@router.put("/buildings/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: int,
    data: BuildingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BuildingResponse:
    """Update a building."""
    building = await university_service.get_building_by_id(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    return await university_service.update_building(db, building, data)


@router.delete("/buildings/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_building(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a building."""
    building = await university_service.get_building_by_id(db, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found",
        )
    await university_service.delete_building(db, building)
