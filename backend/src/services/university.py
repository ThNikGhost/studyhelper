"""University service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.university import Building, Department
from src.schemas.university import (
    BuildingCreate,
    BuildingUpdate,
    DepartmentCreate,
    DepartmentUpdate,
)


# Department operations
async def get_departments(db: AsyncSession) -> list[Department]:
    """Get all departments ordered by name."""
    result = await db.execute(select(Department).order_by(Department.name))
    return list(result.scalars().all())


async def get_department_by_id(db: AsyncSession, department_id: int) -> Department | None:
    """Get department by ID."""
    result = await db.execute(select(Department).where(Department.id == department_id))
    return result.scalar_one_or_none()


async def create_department(db: AsyncSession, data: DepartmentCreate) -> Department:
    """Create a new department."""
    department = Department(
        name=data.name,
        short_name=data.short_name,
        faculty=data.faculty,
        building=data.building,
        floor=data.floor,
        phone=data.phone,
        email=data.email,
        website=str(data.website) if data.website else None,
        notes=data.notes,
    )
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return department


async def update_department(
    db: AsyncSession, department: Department, data: DepartmentUpdate
) -> Department:
    """Update department."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "website" and value is not None:
            value = str(value)
        setattr(department, field, value)
    await db.commit()
    await db.refresh(department)
    return department


async def delete_department(db: AsyncSession, department: Department) -> None:
    """Delete department."""
    await db.delete(department)
    await db.commit()


# Building operations
async def get_buildings(db: AsyncSession) -> list[Building]:
    """Get all buildings ordered by name."""
    result = await db.execute(select(Building).order_by(Building.name))
    return list(result.scalars().all())


async def get_building_by_id(db: AsyncSession, building_id: int) -> Building | None:
    """Get building by ID."""
    result = await db.execute(select(Building).where(Building.id == building_id))
    return result.scalar_one_or_none()


async def create_building(db: AsyncSession, data: BuildingCreate) -> Building:
    """Create a new building."""
    building = Building(
        name=data.name,
        short_name=data.short_name,
        address=data.address,
        floors=data.floors,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(building)
    await db.commit()
    await db.refresh(building)
    return building


async def update_building(
    db: AsyncSession, building: Building, data: BuildingUpdate
) -> Building:
    """Update building."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(building, field, value)
    await db.commit()
    await db.refresh(building)
    return building


async def delete_building(db: AsyncSession, building: Building) -> None:
    """Delete building."""
    await db.delete(building)
    await db.commit()
