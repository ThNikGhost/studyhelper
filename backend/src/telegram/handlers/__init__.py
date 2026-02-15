"""Telegram bot handlers registration."""

from __future__ import annotations

from aiogram import Dispatcher

from src.telegram.handlers.academics import router as academics_router
from src.telegram.handlers.schedule import router as schedule_router
from src.telegram.handlers.settings import router as settings_router
from src.telegram.handlers.start import router as start_router


def register_all_handlers(dp: Dispatcher) -> None:
    """Register all handler routers with the dispatcher."""
    dp.include_router(start_router)
    dp.include_router(schedule_router)
    dp.include_router(academics_router)
    dp.include_router(settings_router)
