"""Tests for retry utilities."""

import httpx
import pytest

from src.parser.retry import (
    RetryConfig,
    calculate_delay,
    is_retryable_exception,
    is_retryable_status,
    retry_async,
    with_retry,
)


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 30.0
        assert config.exponential_base == 2.0

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=60.0,
            exponential_base=3.0,
        )
        assert config.max_attempts == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 60.0
        assert config.exponential_base == 3.0


class TestCalculateDelay:
    """Tests for calculate_delay function."""

    def test_exponential_backoff(self) -> None:
        """Test exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=30.0)

        assert calculate_delay(0, config) == 1.0  # 1 * 2^0 = 1
        assert calculate_delay(1, config) == 2.0  # 1 * 2^1 = 2
        assert calculate_delay(2, config) == 4.0  # 1 * 2^2 = 4
        assert calculate_delay(3, config) == 8.0  # 1 * 2^3 = 8

    def test_max_delay_capped(self) -> None:
        """Test that delay is capped at max_delay."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=5.0)

        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0
        assert calculate_delay(3, config) == 5.0  # Capped at max_delay
        assert calculate_delay(10, config) == 5.0  # Still capped


class TestIsRetryableException:
    """Tests for is_retryable_exception function."""

    def test_timeout_exception(self) -> None:
        """Test TimeoutException is retryable."""
        exc = httpx.TimeoutException("timeout")
        assert is_retryable_exception(exc) is True

    def test_connect_error(self) -> None:
        """Test ConnectError is retryable."""
        exc = httpx.ConnectError("connection failed")
        assert is_retryable_exception(exc) is True

    def test_read_error(self) -> None:
        """Test ReadError is retryable."""
        exc = httpx.ReadError("read failed")
        assert is_retryable_exception(exc) is True

    def test_http_status_error_not_retryable(self) -> None:
        """Test HTTPStatusError is not retryable by exception type."""
        # HTTPStatusError requires a response object
        request = httpx.Request("GET", "http://example.com")
        response = httpx.Response(500, request=request)
        exc = httpx.HTTPStatusError("error", request=request, response=response)
        assert is_retryable_exception(exc) is False

    def test_generic_exception_not_retryable(self) -> None:
        """Test generic Exception is not retryable."""
        exc = ValueError("some error")
        assert is_retryable_exception(exc) is False


class TestIsRetryableStatus:
    """Tests for is_retryable_status function."""

    def test_retryable_statuses(self) -> None:
        """Test 502, 503, 504, 429 are retryable."""
        assert is_retryable_status(502) is True
        assert is_retryable_status(503) is True
        assert is_retryable_status(504) is True
        assert is_retryable_status(429) is True

    def test_non_retryable_statuses(self) -> None:
        """Test other status codes are not retryable."""
        assert is_retryable_status(200) is False
        assert is_retryable_status(400) is False
        assert is_retryable_status(401) is False
        assert is_retryable_status(404) is False
        assert is_retryable_status(500) is False


class TestRetryAsync:
    """Tests for retry_async function."""

    async def test_success_on_first_attempt(self) -> None:
        """Test successful execution on first attempt."""
        call_count = 0

        async def successful_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_async(successful_func)
        assert result == "success"
        assert call_count == 1

    async def test_retry_on_timeout(self) -> None:
        """Test retry on timeout exception."""
        call_count = 0

        async def failing_then_success() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("timeout")
            return "success"

        config = RetryConfig(max_attempts=3, base_delay=0.01)
        result = await retry_async(failing_then_success, config=config)
        assert result == "success"
        assert call_count == 2

    async def test_all_retries_fail(self) -> None:
        """Test that exception is raised after all retries fail."""
        call_count = 0

        async def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise httpx.TimeoutException("timeout")

        config = RetryConfig(max_attempts=3, base_delay=0.01)
        with pytest.raises(httpx.TimeoutException):
            await retry_async(always_fail, config=config)
        assert call_count == 3

    async def test_non_retryable_exception_not_retried(self) -> None:
        """Test non-retryable exceptions are raised immediately."""
        call_count = 0

        async def raise_value_error() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("not retryable")

        config = RetryConfig(max_attempts=3, base_delay=0.01)
        with pytest.raises(ValueError):
            await retry_async(raise_value_error, config=config)
        assert call_count == 1  # No retry

    async def test_with_arguments(self) -> None:
        """Test retry_async passes arguments correctly."""

        async def add(a: int, b: int) -> int:
            return a + b

        result = await retry_async(add, 2, 3)
        assert result == 5

    async def test_with_kwargs(self) -> None:
        """Test retry_async passes kwargs correctly."""

        async def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = await retry_async(greet, "World", greeting="Hi")
        assert result == "Hi, World!"


class TestWithRetryDecorator:
    """Tests for with_retry decorator."""

    async def test_decorated_function_success(self) -> None:
        """Test decorated function executes successfully."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.01))
        async def my_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await my_func()
        assert result == "success"
        assert call_count == 1

    async def test_decorated_function_retry(self) -> None:
        """Test decorated function retries on failure."""
        call_count = 0

        @with_retry(RetryConfig(max_attempts=3, base_delay=0.01))
        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.ConnectError("connection refused")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 2
