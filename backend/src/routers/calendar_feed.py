"""Calendar feed router.

Endpoints for managing iCal feed subscriptions and serving .ics files.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user
from src.models.user import User
from src.schemas.calendar_feed import (
    CalendarFeedCreateResponse,
    CalendarFeedStatusResponse,
)
from src.services import calendar_feed as cal_service
from src.utils.rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_feed_url(token: str) -> str:
    """Build the public feed URL from a token."""
    return f"{settings.base_url}/api/v1/calendar/feed/{token}.ics"


@router.get("/status", response_model=CalendarFeedStatusResponse)
async def get_calendar_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarFeedStatusResponse:
    """Get calendar feed subscription status for current user."""
    feed = await cal_service.get_feed_by_user(db, current_user.id)
    if feed is None:
        return CalendarFeedStatusResponse(is_active=False)

    return CalendarFeedStatusResponse(
        is_active=True,
        feed_url=_build_feed_url(feed.token),
        last_accessed_at=feed.last_accessed_at,
        created_at=feed.created_at,
    )


@router.post("/enable", response_model=CalendarFeedCreateResponse)
async def enable_calendar_feed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarFeedCreateResponse:
    """Create or regenerate calendar feed URL."""
    feed = await cal_service.create_or_regenerate_feed(db, current_user.id)
    return CalendarFeedCreateResponse(feed_url=_build_feed_url(feed.token))


@router.delete("/disable", status_code=204)
async def disable_calendar_feed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Revoke calendar feed subscription."""
    removed = await cal_service.revoke_feed(db, current_user.id)
    if not removed:
        raise HTTPException(status_code=404, detail="No calendar feed found")


@router.get("/feed/{token}.ics")
@limiter.limit("30/minute")
async def get_calendar_feed(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Public .ics feed endpoint. No JWT required — authenticated by token in URL."""
    feed = await cal_service.get_feed_by_token(db, token)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")

    # Update last accessed timestamp
    await cal_service.update_last_accessed(db, feed)

    # Generate ICS
    ics_bytes = await cal_service.generate_ics(db, feed.user_id)

    return Response(
        content=ics_bytes,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Content-Disposition": "attachment; filename=studyhelper.ics",
        },
    )
