"""Tests for structured logging configuration."""

import json
import logging

import pytest

from src.logging_config import add_request_id, request_id_ctx, setup_logging


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_production_json_output(self, capfd: pytest.CaptureFixture) -> None:
        """Test production mode outputs valid JSON."""
        setup_logging(debug=False)
        test_logger = logging.getLogger("test.production")
        test_logger.info("test message")

        captured = capfd.readouterr()
        line = captured.err.strip()
        parsed = json.loads(line)
        assert parsed["event"] == "test message"
        assert parsed["level"] == "info"
        assert "timestamp" in parsed

    def test_development_console_output(self, capfd: pytest.CaptureFixture) -> None:
        """Test development mode outputs human-readable text (not JSON)."""
        setup_logging(debug=True)
        test_logger = logging.getLogger("test.development")
        test_logger.info("dev message")

        captured = capfd.readouterr()
        line = captured.err.strip()
        # Console output should NOT be valid JSON
        with pytest.raises(json.JSONDecodeError):
            json.loads(line)
        assert "dev message" in line

    def test_debug_level_in_debug_mode(self) -> None:
        """Test root logger level is DEBUG when debug=True."""
        setup_logging(debug=True)
        assert logging.getLogger().level == logging.DEBUG

    def test_info_level_in_production(self) -> None:
        """Test root logger level is INFO when debug=False."""
        setup_logging(debug=False)
        assert logging.getLogger().level == logging.INFO

    def test_stdlib_logger_produces_structured_output(
        self, capfd: pytest.CaptureFixture
    ) -> None:
        """Test stdlib logger is intercepted by structlog."""
        setup_logging(debug=False)
        stdlib_logger = logging.getLogger("some.stdlib.module")
        stdlib_logger.warning("stdlib warning")

        captured = capfd.readouterr()
        parsed = json.loads(captured.err.strip())
        assert parsed["event"] == "stdlib warning"
        assert parsed["level"] == "warning"
        assert parsed["logger"] == "some.stdlib.module"

    def test_noisy_loggers_silenced(self) -> None:
        """Test that noisy loggers are set to WARNING."""
        setup_logging(debug=False)
        for name in ("uvicorn.access", "httpx", "httpcore", "apscheduler"):
            assert logging.getLogger(name).level == logging.WARNING


class TestAddRequestId:
    """Tests for add_request_id processor."""

    def test_adds_request_id_from_contextvar(self) -> None:
        """Test request_id is added when ContextVar is set."""
        token = request_id_ctx.set("abc123")
        try:
            event_dict: dict = {"event": "test"}
            result = add_request_id(None, "", event_dict)  # type: ignore[arg-type]
            assert result["request_id"] == "abc123"
        finally:
            request_id_ctx.reset(token)

    def test_no_request_id_when_contextvar_not_set(self) -> None:
        """Test request_id is absent when ContextVar is None."""
        event_dict: dict = {"event": "test"}
        result = add_request_id(None, "", event_dict)  # type: ignore[arg-type]
        assert "request_id" not in result
