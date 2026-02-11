"""LK (личный кабинет) HTTP parser for OmGU eservice.

Handles OAuth2-based authentication and data fetching from student portal.
httpx.AsyncClient automatically persists cookies between requests.
Source: https://www.python-httpx.org/advanced/clients/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from src.parser.lk_exceptions import LkAuthError, LkDataError, LkSessionExpired

logger = logging.getLogger(__name__)

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT = 30


@dataclass
class LkStudentData:
    """Data extracted from LK /myStudents endpoint."""

    sessions: list[dict[str, Any]] = field(default_factory=list)
    sem_info: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)


class LkParser:
    """HTTP client for LK authentication and data fetching.

    httpx.AsyncClient automatically persists cookies between requests,
    so after login() the session is maintained for subsequent calls.

    Usage:
        async with LkParser() as parser:
            if await parser.login(email, password):
                data = await parser.fetch_student_data()
                print(data.sessions)

    Authentication flow:
        1. GET /dasext/login -> extract CSRF from X-CSRF-TOKEN header
        2. POST /dasext/login.do with credentials + CSRF
        3. httpx follows OAuth redirects automatically
        4. Session cookies are stored in client
    """

    BASE_URL = "https://eservice.omsu.ru"

    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        """Initialize parser.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> LkParser:
        """Create HTTP client with cookie persistence."""
        self._client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=self.timeout,
            # Cookies are persisted automatically within client instance
        )
        logger.info("LK HTTP client created")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("LK HTTP client closed")

    def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client, raising if not initialized."""
        if self._client is None:
            raise RuntimeError("LkParser must be used as async context manager")
        return self._client

    async def login(self, email: str, password: str) -> bool:
        """Authenticate to LK and establish session.

        Steps:
            1. GET /dasext/login -> extract CSRF from X-CSRF-TOKEN header
            2. POST /dasext/login.do with credentials + CSRF
            3. httpx follows OAuth redirects automatically
            4. Session cookies are stored in client

        Args:
            email: User email (without @eservice suffix).
            password: User password.

        Returns:
            True if authentication successful, False otherwise.

        Raises:
            LkAuthError: If CSRF token not found or critical error occurs.
        """
        client = self._get_client()

        try:
            # Step 1: Get login page and extract CSRF token
            logger.debug("Fetching login page for CSRF token")
            resp = await client.get(f"{self.BASE_URL}/dasext/login")

            csrf_token = resp.headers.get("X-CSRF-TOKEN")
            if not csrf_token:
                # Try to find in cookies as fallback
                csrf_token = resp.cookies.get("XSRF-TOKEN")

            if not csrf_token:
                raise LkAuthError("CSRF token not found in response headers or cookies")

            logger.debug("CSRF token obtained")

            # Step 2: Submit login form
            # Note: j_username format is email@eservice
            login_data = {
                "j_username": f"{email}@eservice",
                "j_password": password,
                "_csrf": csrf_token,
            }

            logger.debug("Submitting login form")
            resp = await client.post(
                f"{self.BASE_URL}/dasext/login.do",
                data=login_data,
            )

            # After redirects, check if we landed on sinfo (successful auth)
            final_url = str(resp.url)
            if "/sinfo/" in final_url:
                logger.info("LK authentication successful")
                return True

            # Check for error indicators in response
            if "error" in final_url.lower() or resp.status_code >= 400:
                logger.warning("LK authentication failed: %s", final_url)
                return False

            # Check response content for login form (still on login page = failed)
            if "j_password" in resp.text:
                logger.warning("LK authentication failed: still on login page")
                return False

            logger.info("LK authentication status unclear, assuming success")
            return True

        except httpx.RequestError as e:
            raise LkAuthError(f"Network error during authentication: {e}") from e

    async def fetch_student_data(self) -> LkStudentData:
        """Fetch student data from /sinfo/backend/myStudents.

        Returns:
            LkStudentData with sessions, sem_info, and summary.

        Raises:
            LkSessionExpired: If session has expired.
            LkDataError: If data format is unexpected.
        """
        client = self._get_client()

        try:
            logger.debug("Fetching student data from myStudents endpoint")
            resp = await client.get(f"{self.BASE_URL}/sinfo/backend/myStudents")

            # Check for redirect to login (session expired)
            if "/login" in str(resp.url):
                raise LkSessionExpired("Session expired, please re-authenticate")

            resp.raise_for_status()
            data = resp.json()

            logger.info("Student data fetched successfully")

            return LkStudentData(
                sessions=data.get("sessions", []),
                sem_info=data.get("semInfo", []),
                summary=data.get("summary", {}),
                raw_data=data,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise LkSessionExpired("Session expired (401)") from e
            raise LkDataError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise LkDataError(f"Network error: {e}") from e
        except (KeyError, TypeError, ValueError) as e:
            raise LkDataError(f"Invalid data format: {e}") from e

    async def check_session(self) -> bool:
        """Check if current session is valid.

        Returns:
            True if session is active, False otherwise.
        """
        client = self._get_client()

        try:
            resp = await client.get(f"{self.BASE_URL}/sinfo/backend/myStudents")
            return resp.status_code == 200 and "/login" not in str(resp.url)
        except httpx.RequestError:
            return False
