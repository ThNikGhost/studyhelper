"""Widget router.

Endpoints for managing widget API keys and serving next lesson data.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.widget import (
    NextLessonResponse,
    TodayScheduleResponse,
    WidgetApiKeyCreateResponse,
    WidgetApiKeyStatusResponse,
)
from src.services import widget as widget_service
from src.utils.rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_widget_url(token: str) -> str:
    """Build the public widget URL from a token."""
    return f"{settings.base_url}/api/v1/widget/next-lesson?api_key={token}"


@router.get("/status", response_model=WidgetApiKeyStatusResponse)
async def get_widget_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WidgetApiKeyStatusResponse:
    """Get widget API key status for current user."""
    key = await widget_service.get_key_by_user(db, current_user.id)
    if key is None:
        return WidgetApiKeyStatusResponse(is_active=False)

    return WidgetApiKeyStatusResponse(
        is_active=True,
        api_key=key.token,
        widget_url=_build_widget_url(key.token),
        last_used_at=key.last_used_at,
        created_at=key.created_at,
    )


@router.post("/enable", response_model=WidgetApiKeyCreateResponse)
async def enable_widget(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WidgetApiKeyCreateResponse:
    """Create or regenerate widget API key."""
    key = await widget_service.create_or_regenerate_key(db, current_user.id)
    return WidgetApiKeyCreateResponse(
        api_key=key.token,
        widget_url=_build_widget_url(key.token),
    )


@router.delete("/disable", status_code=204)
async def disable_widget(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Revoke widget API key."""
    removed = await widget_service.revoke_key(db, current_user.id)
    if not removed:
        raise HTTPException(status_code=404, detail="No widget API key found")


@router.get("/next-lesson", response_model=NextLessonResponse)
@limiter.limit("60/minute")
async def get_next_lesson(
    request: Request,
    api_key: str = Query(..., description="Widget API key"),
    db: AsyncSession = Depends(get_db),
) -> NextLessonResponse:
    """Public next lesson endpoint. Authenticated by API key in query parameter."""
    result = await widget_service.get_next_lesson_by_token(db, api_key)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return result


@router.get("/today", response_model=TodayScheduleResponse)
@limiter.limit("60/minute")
async def get_today_schedule(
    request: Request,
    api_key: str = Query(..., description="Widget API key"),
    db: AsyncSession = Depends(get_db),
) -> TodayScheduleResponse:
    """Public today schedule endpoint. Returns all lessons for today + first future lesson."""
    result = await widget_service.get_today_schedule_by_token(db, api_key)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return result
