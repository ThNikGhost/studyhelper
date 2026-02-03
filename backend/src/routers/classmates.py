"""Classmates router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.classmate import ClassmateCreate, ClassmateResponse, ClassmateUpdate
from src.services import classmate as classmate_service

router = APIRouter()


@router.get("", response_model=list[ClassmateResponse])
async def get_classmates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClassmateResponse]:
    """Get all classmates."""
    return await classmate_service.get_classmates(db)


@router.post("", response_model=ClassmateResponse, status_code=status.HTTP_201_CREATED)
async def create_classmate(
    data: ClassmateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateResponse:
    """Create a new classmate."""
    return await classmate_service.create_classmate(db, data)


@router.get("/{classmate_id}", response_model=ClassmateResponse)
async def get_classmate(
    classmate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateResponse:
    """Get a classmate by ID."""
    classmate = await classmate_service.get_classmate_by_id(db, classmate_id)
    if not classmate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classmate not found",
        )
    return classmate


@router.put("/{classmate_id}", response_model=ClassmateResponse)
async def update_classmate(
    classmate_id: int,
    data: ClassmateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateResponse:
    """Update a classmate."""
    classmate = await classmate_service.get_classmate_by_id(db, classmate_id)
    if not classmate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classmate not found",
        )
    return await classmate_service.update_classmate(db, classmate, data)


@router.delete("/{classmate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_classmate(
    classmate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a classmate."""
    classmate = await classmate_service.get_classmate_by_id(db, classmate_id)
    if not classmate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classmate not found",
        )
    await classmate_service.delete_classmate(db, classmate)
