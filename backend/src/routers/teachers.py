"""Teachers router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_user, get_db
from src.models.user import User
from src.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from src.services import teacher as teacher_service

router = APIRouter()


@router.get("", response_model=list[TeacherResponse])
async def get_teachers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TeacherResponse]:
    """Get all teachers."""
    return await teacher_service.get_teachers(db)


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeacherResponse:
    """Create a new teacher."""
    return await teacher_service.create_teacher(db, teacher_data)


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeacherResponse:
    """Get a teacher by ID."""
    teacher = await teacher_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )
    return teacher


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeacherResponse:
    """Update a teacher."""
    teacher = await teacher_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )
    return await teacher_service.update_teacher(db, teacher, teacher_data)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a teacher."""
    teacher = await teacher_service.get_teacher_by_id(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )
    await teacher_service.delete_teacher(db, teacher)
