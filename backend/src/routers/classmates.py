"""Classmates router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.classmate import (
    ClassmateCreate,
    ClassmateDetailedResponse,
    ClassmateDetailResponse,
    ClassmateDetailUpsert,
    ClassmateListResponse,
    ClassmateUpdate,
)
from src.services import classmate as classmate_service

router = APIRouter()


def _build_detailed_response(classmate, detail) -> ClassmateDetailedResponse:
    """Build ClassmateDetailedResponse from model instances."""
    data = {
        "id": classmate.id,
        "full_name": classmate.full_name,
        "group_name": classmate.group_name,
        "subgroup": classmate.subgroup,
        "created_at": classmate.created_at,
        "updated_at": classmate.updated_at,
        "details": ClassmateDetailResponse.model_validate(detail) if detail else None,
    }
    return ClassmateDetailedResponse.model_validate(data)


@router.get("", response_model=list[ClassmateListResponse])
async def get_classmates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClassmateListResponse]:
    """Get all classmates (base fields only)."""
    return await classmate_service.get_classmates(db)


@router.post(
    "", response_model=ClassmateDetailedResponse, status_code=status.HTTP_201_CREATED
)
async def create_classmate(
    data: ClassmateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateDetailedResponse:
    """Create a new classmate."""
    classmate = await classmate_service.create_classmate(db, data)
    return _build_detailed_response(classmate, None)


@router.get("/{classmate_id}", response_model=ClassmateDetailedResponse)
async def get_classmate(
    classmate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateDetailedResponse:
    """Get a classmate by ID with current user's details."""
    result = await classmate_service.get_classmate_with_details(
        db, classmate_id, current_user.id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classmate not found",
        )
    classmate, detail = result
    return _build_detailed_response(classmate, detail)


@router.put("/{classmate_id}", response_model=ClassmateDetailedResponse)
async def update_classmate(
    classmate_id: int,
    data: ClassmateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateDetailedResponse:
    """Update a classmate's base fields."""
    result = await classmate_service.get_classmate_with_details(
        db, classmate_id, current_user.id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classmate not found",
        )
    classmate, detail = result
    classmate = await classmate_service.update_classmate(db, classmate, data)
    return _build_detailed_response(classmate, detail)


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


@router.put("/{classmate_id}/details", response_model=ClassmateDetailResponse)
async def upsert_classmate_details(
    classmate_id: int,
    data: ClassmateDetailUpsert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClassmateDetailResponse:
    """Create or update per-user details for a classmate."""
    classmate = await classmate_service.get_classmate_by_id(db, classmate_id)
    if not classmate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classmate not found",
        )
    detail = await classmate_service.upsert_classmate_details(
        db, classmate_id, current_user.id, data
    )
    return ClassmateDetailResponse.model_validate(detail)
