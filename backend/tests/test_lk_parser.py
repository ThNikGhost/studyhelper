"""Tests for LK parser HTTP client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.parser.lk_exceptions import LkAuthError, LkDataError, LkSessionExpired
from src.parser.lk_parser import LkParser, LkStudentData


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
    async def test_login_success(self) -> None:
        """Test successful login flow."""
        async with LkParser() as parser:
            # Mock HTTP responses
            with patch.object(parser._client, "get") as mock_get:
                with patch.object(parser._client, "post") as mock_post:
                    # Mock GET /dasext/login response
                    mock_login_page = MagicMock()
                    mock_login_page.headers = {"X-CSRF-TOKEN": "test-csrf-token"}
                    mock_get.return_value = mock_login_page

                    # Mock POST /dasext/login.do response (redirected to /sinfo/)
                    mock_login_resp = MagicMock()
                    mock_login_resp.url = "https://eservice.omsu.ru/sinfo/dashboard"
                    mock_login_resp.status_code = 200
                    mock_login_resp.text = "<html>Dashboard</html>"
                    mock_post.return_value = mock_login_resp

                    result = await parser.login("test@omsu.ru", "password123")

                    assert result is True
                    mock_get.assert_called_once()
                    mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_csrf_not_found(self) -> None:
        """Test login fails when CSRF token not found."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                # No CSRF token in response
                mock_login_page = MagicMock()
                mock_login_page.headers = {}
                mock_login_page.cookies = {}
                mock_get.return_value = mock_login_page

                with pytest.raises(LkAuthError, match="CSRF"):
                    await parser.login("test@omsu.ru", "password123")

    @pytest.mark.asyncio
    async def test_login_csrf_from_cookies(self) -> None:
        """Test CSRF token from cookies fallback."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                with patch.object(parser._client, "post") as mock_post:
                    # CSRF in cookies, not header
                    mock_login_page = MagicMock()
                    mock_login_page.headers = {}
                    mock_login_page.cookies = {"XSRF-TOKEN": "cookie-csrf-token"}
                    mock_get.return_value = mock_login_page

                    mock_login_resp = MagicMock()
                    mock_login_resp.url = "https://eservice.omsu.ru/sinfo/"
                    mock_login_resp.status_code = 200
                    mock_login_resp.text = ""
                    mock_post.return_value = mock_login_resp

                    result = await parser.login("test@omsu.ru", "password123")
                    assert result is True

    @pytest.mark.asyncio
    async def test_login_failed_still_on_login_page(self) -> None:
        """Test login fails when still on login page."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                with patch.object(parser._client, "post") as mock_post:
                    mock_login_page = MagicMock()
                    mock_login_page.headers = {"X-CSRF-TOKEN": "test-csrf"}
                    mock_get.return_value = mock_login_page

                    # Still on login page (contains j_password)
                    mock_login_resp = MagicMock()
                    mock_login_resp.url = "https://eservice.omsu.ru/dasext/login"
                    mock_login_resp.status_code = 200
                    mock_login_resp.text = '<input name="j_password">'
                    mock_post.return_value = mock_login_resp

                    result = await parser.login("test@omsu.ru", "wrongpass")
                    assert result is False

    @pytest.mark.asyncio
    async def test_login_network_error(self) -> None:
        """Test login handles network errors."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_get.side_effect = httpx.RequestError("Network error")

                with pytest.raises(LkAuthError, match="Network error"):
                    await parser.login("test@omsu.ru", "password123")

    @pytest.mark.asyncio
    async def test_fetch_student_data_success(self) -> None:
        """Test successful data fetch."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.url = "https://eservice.omsu.ru/sinfo/backend/myStudents"
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "sessions": [{"number": "5", "entries": []}],
                    "semInfo": [{"semester": 5, "discipline": "Math"}],
                    "summary": {"name": "Test Student"},
                }
                mock_resp.raise_for_status = MagicMock()
                mock_get.return_value = mock_resp

                data = await parser.fetch_student_data()

                assert isinstance(data, LkStudentData)
                assert len(data.sessions) == 1
                assert len(data.sem_info) == 1
                assert data.summary["name"] == "Test Student"

    @pytest.mark.asyncio
    async def test_fetch_student_data_session_expired_redirect(self) -> None:
        """Test session expired detection via redirect."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.url = "https://eservice.omsu.ru/dasext/login"
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with pytest.raises(LkSessionExpired):
                    await parser.fetch_student_data()

    @pytest.mark.asyncio
    async def test_fetch_student_data_401(self) -> None:
        """Test session expired detection via 401."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.status_code = 401
                mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "401",
                    request=MagicMock(),
                    response=MagicMock(status_code=401),
                )
                mock_get.return_value = mock_resp

                with pytest.raises(LkSessionExpired):
                    await parser.fetch_student_data()

    @pytest.mark.asyncio
    async def test_fetch_student_data_network_error(self) -> None:
        """Test data fetch handles network errors."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_get.side_effect = httpx.RequestError("Network error")

                with pytest.raises(LkDataError, match="Network error"):
                    await parser.fetch_student_data()

    @pytest.mark.asyncio
    async def test_check_session_valid(self) -> None:
        """Test check_session returns True for valid session."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.url = "https://eservice.omsu.ru/sinfo/backend/myStudents"
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                result = await parser.check_session()
                assert result is True

    @pytest.mark.asyncio
    async def test_check_session_expired(self) -> None:
        """Test check_session returns False for expired session."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.url = "https://eservice.omsu.ru/dasext/login"
                mock_resp.status_code = 302
                mock_get.return_value = mock_resp

                result = await parser.check_session()
                assert result is False

    @pytest.mark.asyncio
    async def test_check_session_network_error(self) -> None:
        """Test check_session returns False on network error."""
        async with LkParser() as parser:
            with patch.object(parser._client, "get") as mock_get:
                mock_get.side_effect = httpx.RequestError("Network error")

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
