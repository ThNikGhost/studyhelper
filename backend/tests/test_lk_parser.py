"""Tests for LK parser HTTP client.

Uses respx for transport-level HTTP mocking (replaces MagicMock approach
that caused deadlocks in CI).
"""

import httpx
import pytest
import respx
from httpx import Response

from src.parser.lk_exceptions import LkAuthError, LkDataError, LkSessionExpired
from src.parser.lk_parser import LkParser, LkStudentData

BASE_URL = "https://eservice.omsu.ru"


class TestLkParser:
    """Tests for LkParser class."""

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test parser works as async context manager."""
        async with LkParser() as parser:
            assert parser._client is not None

        # After exit, client should be closed
        assert parser._client is None

    @pytest.mark.asyncio
    async def test_get_client_without_context_manager(self) -> None:
        """Test error when not used as context manager."""
        parser = LkParser()

        with pytest.raises(RuntimeError, match="context manager"):
            parser._get_client()

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_success(self) -> None:
        """Test successful login flow."""
        # Step 1: GET /sinfo/backend/ — initial OAuth entry point
        respx.get(f"{BASE_URL}/sinfo/backend/").mock(
            return_value=Response(200, headers={"X-CSRF-TOKEN": "test-csrf-token"})
        )
        # Step 2: POST /dasext/login.do — submit credentials, get redirect
        respx.post(f"{BASE_URL}/dasext/login.do").mock(
            return_value=Response(
                302,
                headers={"Location": f"{BASE_URL}/sinfo/dashboard"},
            )
        )
        # Step 3: Follow redirect to dashboard
        respx.get(f"{BASE_URL}/sinfo/dashboard").mock(
            return_value=Response(200, text="<html>Dashboard</html>")
        )

        async with LkParser() as parser:
            result = await parser.login("test@omsu.ru", "password123")

        assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_csrf_not_found(self) -> None:
        """Test login fails when CSRF token not found."""
        # No CSRF token in response headers or cookies
        respx.get(f"{BASE_URL}/sinfo/backend/").mock(
            return_value=Response(200, text="<html>No CSRF here</html>")
        )

        async with LkParser() as parser:
            with pytest.raises(LkAuthError, match="CSRF"):
                await parser.login("test@omsu.ru", "password123")

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_csrf_from_cookies(self) -> None:
        """Test CSRF token from cookies fallback."""
        # CSRF in cookies, not header
        respx.get(f"{BASE_URL}/sinfo/backend/").mock(
            return_value=Response(
                200,
                text="<html>Login</html>",
                headers={"Set-Cookie": "XSRF-TOKEN=cookie-csrf-token; Path=/"},
            )
        )
        respx.post(f"{BASE_URL}/dasext/login.do").mock(
            return_value=Response(302, headers={"Location": f"{BASE_URL}/sinfo/"})
        )
        respx.get(f"{BASE_URL}/sinfo/").mock(
            return_value=Response(200, text="<html>Home</html>")
        )
        # check_session call after landing on root
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            return_value=Response(200, text="{}")
        )

        async with LkParser() as parser:
            result = await parser.login("test@omsu.ru", "password123")

        assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_failed_still_on_login_page(self) -> None:
        """Test login fails when still on login page."""
        respx.get(f"{BASE_URL}/sinfo/backend/").mock(
            return_value=Response(200, headers={"X-CSRF-TOKEN": "test-csrf"})
        )
        # Login fails — response is 200 with login form (not redirect)
        respx.post(f"{BASE_URL}/dasext/login.do").mock(
            return_value=Response(
                200,
                text='<input name="j_password">',
                headers={"Location": ""},
            )
        )

        async with LkParser() as parser:
            result = await parser.login("test@omsu.ru", "wrongpass")

        assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_login_network_error(self) -> None:
        """Test login handles network errors."""
        respx.get(f"{BASE_URL}/sinfo/backend/").mock(
            side_effect=httpx.ConnectError("Network error")
        )

        async with LkParser() as parser:
            with pytest.raises(LkAuthError, match="Network error"):
                await parser.login("test@omsu.ru", "password123")

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_student_data_success(self) -> None:
        """Test successful data fetch."""
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            return_value=Response(
                200,
                json={
                    "sessions": [{"number": "5", "entries": []}],
                    "semInfo": [{"semester": 5, "discipline": "Math"}],
                    "summary": {"name": "Test Student"},
                },
            )
        )

        async with LkParser() as parser:
            data = await parser.fetch_student_data()

        assert isinstance(data, LkStudentData)
        assert len(data.sessions) == 1
        assert len(data.sem_info) == 1
        assert data.summary["name"] == "Test Student"

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_student_data_session_expired_redirect(self) -> None:
        """Test session expired detection via redirect."""
        # First call returns redirect to login
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            return_value=Response(
                302,
                headers={"Location": f"{BASE_URL}/dasext/login"},
            )
        )
        # Follow redirect to login page
        respx.get(f"{BASE_URL}/dasext/login").mock(
            return_value=Response(200, text="<html>Login</html>")
        )

        async with LkParser() as parser:
            with pytest.raises(LkSessionExpired):
                await parser.fetch_student_data()

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_student_data_401(self) -> None:
        """Test session expired detection via 401."""
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            return_value=Response(401, text="Unauthorized")
        )

        async with LkParser() as parser:
            with pytest.raises(LkSessionExpired):
                await parser.fetch_student_data()

    @pytest.mark.asyncio
    @respx.mock
    async def test_fetch_student_data_network_error(self) -> None:
        """Test data fetch handles network errors.

        Uses httpx.RequestError (base class) which is NOT in RETRYABLE_EXCEPTIONS,
        so retry logic does not kick in (no asyncio.sleep delays).
        """
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            side_effect=httpx.RequestError("Network error")
        )

        async with LkParser() as parser:
            with pytest.raises(LkDataError, match="Network error"):
                await parser.fetch_student_data()

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_session_valid(self) -> None:
        """Test check_session returns True for valid session."""
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            return_value=Response(200, json={"sessions": []})
        )

        async with LkParser() as parser:
            result = await parser.check_session()

        assert result is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_session_expired(self) -> None:
        """Test check_session returns False for expired session."""
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            return_value=Response(
                302,
                headers={"Location": f"{BASE_URL}/dasext/login"},
            )
        )
        respx.get(f"{BASE_URL}/dasext/login").mock(
            return_value=Response(200, text="<html>Login</html>")
        )

        async with LkParser() as parser:
            result = await parser.check_session()

        assert result is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_check_session_network_error(self) -> None:
        """Test check_session returns False on network error."""
        respx.get(f"{BASE_URL}/sinfo/backend/myStudents").mock(
            side_effect=httpx.ConnectError("Network error")
        )

        async with LkParser() as parser:
            result = await parser.check_session()

        assert result is False


class TestLkStudentData:
    """Tests for LkStudentData dataclass."""

    def test_default_values(self) -> None:
        """Test default empty values."""
        data = LkStudentData()

        assert data.sessions == []
        assert data.sem_info == []
        assert data.summary == {}
        assert data.raw_data == {}

    def test_with_data(self) -> None:
        """Test with actual data."""
        data = LkStudentData(
            sessions=[{"number": "5"}],
            sem_info=[{"semester": 5}],
            summary={"name": "Test"},
            raw_data={"full": "data"},
        )

        assert len(data.sessions) == 1
        assert len(data.sem_info) == 1
        assert data.summary["name"] == "Test"
        assert data.raw_data["full"] == "data"
