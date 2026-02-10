"""Tests for schedule auto-sync scheduler."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from redis.exceptions import LockNotOwnedError


@pytest.fixture(autouse=True)
def _reset_scheduler_globals():
    """Reset module-level globals before each test."""
    import src.scheduler as mod

    mod._scheduler = None
    mod._redis = None
    yield
    mod._scheduler = None
    mod._redis = None


class TestSyncScheduleWithLock:
    """Tests for _sync_schedule_with_lock."""

    @pytest.mark.asyncio
    async def test_acquires_lock_and_runs_sync(self):
        """Sync acquires Redis lock and calls sync_schedule."""
        mock_lock = AsyncMock()
        mock_lock.acquire = AsyncMock(return_value=True)
        mock_lock.release = AsyncMock()

        mock_redis = AsyncMock()
        mock_redis.lock = MagicMock(return_value=mock_lock)

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_session_maker = MagicMock(return_value=mock_session)

        sync_result = {
            "success": True,
            "changed": True,
            "entries_count": 100,
            "message": "ok",
        }

        with (
            patch(
                "src.scheduler._get_redis",
                new_callable=AsyncMock,
                return_value=mock_redis,
            ),
            patch("src.scheduler.get_session_maker", return_value=mock_session_maker),
            patch(
                "src.services.schedule.sync_schedule",
                new_callable=AsyncMock,
                return_value=sync_result,
            ) as mock_sync,
        ):
            from src.scheduler import _sync_schedule_with_lock

            await _sync_schedule_with_lock()

            mock_lock.acquire.assert_awaited_once()
            mock_sync.assert_awaited_once_with(mock_session)
            mock_lock.release.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_when_lock_held(self):
        """Sync is skipped when another worker holds the lock."""
        mock_lock = AsyncMock()
        mock_lock.acquire = AsyncMock(return_value=False)

        mock_redis = AsyncMock()
        mock_redis.lock = MagicMock(return_value=mock_lock)

        with (
            patch(
                "src.scheduler._get_redis",
                new_callable=AsyncMock,
                return_value=mock_redis,
            ),
            patch(
                "src.services.schedule.sync_schedule",
                new_callable=AsyncMock,
            ) as mock_sync,
        ):
            from src.scheduler import _sync_schedule_with_lock

            await _sync_schedule_with_lock()

            mock_lock.acquire.assert_awaited_once()
            mock_sync.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_lock_released_on_error(self):
        """Lock is released even if sync_schedule raises an exception."""
        mock_lock = AsyncMock()
        mock_lock.acquire = AsyncMock(return_value=True)
        mock_lock.release = AsyncMock()

        mock_redis = AsyncMock()
        mock_redis.lock = MagicMock(return_value=mock_lock)

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_session_maker = MagicMock(return_value=mock_session)

        with (
            patch(
                "src.scheduler._get_redis",
                new_callable=AsyncMock,
                return_value=mock_redis,
            ),
            patch("src.scheduler.get_session_maker", return_value=mock_session_maker),
            patch(
                "src.services.schedule.sync_schedule",
                new_callable=AsyncMock,
                side_effect=RuntimeError("Network error"),
            ),
        ):
            from src.scheduler import _sync_schedule_with_lock

            await _sync_schedule_with_lock()

            mock_lock.release.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_lock_expired_before_release(self):
        """LockNotOwnedError is caught when TTL expires before release."""
        mock_lock = AsyncMock()
        mock_lock.acquire = AsyncMock(return_value=True)
        mock_lock.release = AsyncMock(side_effect=LockNotOwnedError("expired"))

        mock_redis = AsyncMock()
        mock_redis.lock = MagicMock(return_value=mock_lock)

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_session_maker = MagicMock(return_value=mock_session)

        sync_result = {"success": True, "changed": False, "entries_count": 50}

        with (
            patch(
                "src.scheduler._get_redis",
                new_callable=AsyncMock,
                return_value=mock_redis,
            ),
            patch("src.scheduler.get_session_maker", return_value=mock_session_maker),
            patch(
                "src.services.schedule.sync_schedule",
                new_callable=AsyncMock,
                return_value=sync_result,
            ),
        ):
            from src.scheduler import _sync_schedule_with_lock

            # Should not raise — LockNotOwnedError is handled
            await _sync_schedule_with_lock()

            mock_lock.release.assert_awaited_once()


class TestGetRedis:
    """Tests for _get_redis."""

    @pytest.mark.asyncio
    async def test_creates_new_client(self):
        """Creates a new Redis client when none exists."""
        mock_client = AsyncMock()

        with patch("src.scheduler.Redis") as mock_redis_cls:
            mock_redis_cls.from_url = MagicMock(return_value=mock_client)

            from src.scheduler import _get_redis

            result = await _get_redis()

            assert result is mock_client
            mock_redis_cls.from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_reuses_existing_client(self):
        """Reuses cached client if ping succeeds."""
        import src.scheduler as mod

        mock_client = AsyncMock()
        mock_client.ping = AsyncMock(return_value=True)
        mod._redis = mock_client

        with patch("src.scheduler.Redis") as mock_redis_cls:
            from src.scheduler import _get_redis

            result = await _get_redis()

            assert result is mock_client
            mock_redis_cls.from_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_reconnects_on_dead_connection(self):
        """Recreates client when ping fails (connection lost)."""
        import src.scheduler as mod

        dead_client = AsyncMock()
        dead_client.ping = AsyncMock(side_effect=ConnectionError("gone"))
        dead_client.aclose = AsyncMock()
        mod._redis = dead_client

        new_client = AsyncMock()

        with patch("src.scheduler.Redis") as mock_redis_cls:
            mock_redis_cls.from_url = MagicMock(return_value=new_client)

            from src.scheduler import _get_redis

            result = await _get_redis()

            assert result is new_client
            dead_client.aclose.assert_awaited_once()
            mock_redis_cls.from_url.assert_called_once()


class TestStartScheduler:
    """Tests for start_scheduler."""

    @pytest.mark.asyncio
    async def test_disabled_does_not_start(self):
        """Scheduler does not start when schedule_sync_enabled is False."""
        with patch("src.scheduler.settings") as mock_settings:
            mock_settings.schedule_sync_enabled = False

            import src.scheduler as mod
            from src.scheduler import start_scheduler

            await start_scheduler()

            assert mod._scheduler is None

    @pytest.mark.asyncio
    async def test_creates_job_when_enabled(self):
        """Scheduler creates an interval job when enabled."""
        with patch("src.scheduler.settings") as mock_settings:
            mock_settings.schedule_sync_enabled = True
            mock_settings.schedule_update_interval_hours = 6

            import src.scheduler as mod
            from src.scheduler import start_scheduler

            await start_scheduler()

            assert mod._scheduler is not None
            jobs = mod._scheduler.get_jobs()
            assert len(jobs) == 1
            assert jobs[0].id == "schedule_auto_sync"
            assert jobs[0].misfire_grace_time == 3600

            # Cleanup
            mod._scheduler.shutdown(wait=False)
            mod._scheduler = None


class TestStopScheduler:
    """Tests for stop_scheduler."""

    @pytest.mark.asyncio
    async def test_stop_shuts_down_scheduler_and_redis(self):
        """stop_scheduler shuts down scheduler and closes Redis."""
        import src.scheduler as mod

        mock_scheduler = MagicMock()
        mock_redis = AsyncMock()

        mod._scheduler = mock_scheduler
        mod._redis = mock_redis

        from src.scheduler import stop_scheduler

        await stop_scheduler()

        mock_scheduler.shutdown.assert_called_once_with(wait=False)
        mock_redis.aclose.assert_awaited_once()
        assert mod._scheduler is None
        assert mod._redis is None

    @pytest.mark.asyncio
    async def test_stop_when_nothing_running(self):
        """stop_scheduler is safe when nothing is running."""
        import src.scheduler as mod

        mod._scheduler = None
        mod._redis = None

        from src.scheduler import stop_scheduler

        await stop_scheduler()

        assert mod._scheduler is None
        assert mod._redis is None
