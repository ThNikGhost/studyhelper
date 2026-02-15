"""Telegram link service layer."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.telegram import TelegramLink

LINK_CODE_LENGTH = 6
LINK_CODE_TTL_MINUTES = 10


async def get_link_by_user(
    db: AsyncSession,
    user_id: int,
) -> TelegramLink | None:
    """Get telegram link for a user."""
    result = await db.execute(
        select(TelegramLink).where(TelegramLink.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_link_by_telegram_id(
    db: AsyncSession,
    telegram_id: int,
) -> TelegramLink | None:
    """Get telegram link by Telegram user ID."""
    result = await db.execute(
        select(TelegramLink).where(TelegramLink.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_link_by_code(
    db: AsyncSession,
    code: str,
) -> TelegramLink | None:
    """Get telegram link by link code (non-expired)."""
    now = datetime.now(UTC)
    result = await db.execute(
        select(TelegramLink).where(
            TelegramLink.link_code == code,
            TelegramLink.link_code_expires_at > now,
        )
    )
    return result.scalar_one_or_none()


async def generate_link_code(
    db: AsyncSession,
    user_id: int,
) -> TelegramLink:
    """Generate a 6-digit link code for user.

    Creates or updates the TelegramLink record. If the user already
    has a linked Telegram account, the existing link is preserved
    and a new code is generated alongside it.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        Updated TelegramLink with new code.
    """
    link = await get_link_by_user(db, user_id)
    code = secrets.token_hex(3).upper()[:LINK_CODE_LENGTH]
    expires_at = datetime.now(UTC) + timedelta(minutes=LINK_CODE_TTL_MINUTES)

    if link is None:
        link = TelegramLink(
            user_id=user_id,
            link_code=code,
            link_code_expires_at=expires_at,
        )
        db.add(link)
    else:
        link.link_code = code
        link.link_code_expires_at = expires_at

    await db.flush()
    await db.commit()
    await db.refresh(link)
    return link


async def complete_link(
    db: AsyncSession,
    link: TelegramLink,
    telegram_id: int,
    telegram_username: str | None,
) -> TelegramLink:
    """Complete the link process after user sends /link CODE in Telegram.

    Args:
        db: Database session.
        link: TelegramLink record found by code.
        telegram_id: Telegram user ID.
        telegram_username: Telegram username (without @).

    Returns:
        Updated TelegramLink.
    """
    link.telegram_id = telegram_id
    link.telegram_username = telegram_username
    link.link_code = None
    link.link_code_expires_at = None
    link.linked_at = datetime.now(UTC)
    await db.flush()
    await db.commit()
    await db.refresh(link)
    return link


async def unlink(
    db: AsyncSession,
    user_id: int,
) -> bool:
    """Remove telegram link for user.

    Returns:
        True if a link existed and was removed, False otherwise.
    """
    link = await get_link_by_user(db, user_id)
    if link is None:
        return False
    await db.delete(link)
    await db.commit()
    return True


async def update_notifications(
    db: AsyncSession,
    user_id: int,
    *,
    notify_deadlines: bool | None = None,
    morning_summary: bool | None = None,
) -> TelegramLink | None:
    """Update notification preferences.

    Args:
        db: Database session.
        user_id: User ID.
        notify_deadlines: New value for deadline alerts (or None to keep).
        morning_summary: New value for morning summary (or None to keep).

    Returns:
        Updated TelegramLink, or None if not linked.
    """
    link = await get_link_by_user(db, user_id)
    if link is None:
        return None

    if notify_deadlines is not None:
        link.notify_deadlines = notify_deadlines
    if morning_summary is not None:
        link.morning_summary = morning_summary

    await db.flush()
    await db.commit()
    await db.refresh(link)
    return link


async def get_all_linked_users(
    db: AsyncSession,
) -> list[TelegramLink]:
    """Get all users with linked Telegram accounts."""
    result = await db.execute(
        select(TelegramLink).where(TelegramLink.telegram_id.isnot(None))
    )
    return list(result.scalars().all())


async def get_users_with_morning_summary(
    db: AsyncSession,
) -> list[TelegramLink]:
    """Get all linked users who have morning summary enabled."""
    result = await db.execute(
        select(TelegramLink).where(
            TelegramLink.telegram_id.isnot(None),
            TelegramLink.morning_summary.is_(True),
        )
    )
    return list(result.scalars().all())


async def get_users_with_deadline_alerts(
    db: AsyncSession,
) -> list[TelegramLink]:
    """Get all linked users who have deadline alerts enabled."""
    result = await db.execute(
        select(TelegramLink).where(
            TelegramLink.telegram_id.isnot(None),
            TelegramLink.notify_deadlines.is_(True),
        )
    )
    return list(result.scalars().all())
