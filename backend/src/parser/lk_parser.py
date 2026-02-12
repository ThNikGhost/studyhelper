"""LK (личный кабинет) HTTP parser for OmGU eservice.

Handles OAuth2-based authentication and data fetching from student portal.
httpx.AsyncClient automatically persists cookies between requests.
Source: https://www.python-httpx.org/advanced/clients/

OAuth2 Flow (discovered from HAR analysis):
    1. GET /sinfo/backend/ → 302 → /dasext/oauth/authorize?client_id=sinfo&...
    2. GET /dasext/oauth/authorize?... → 302 → /dasext/login
    3. POST /dasext/login.do with credentials → 302 → /dasext/oauth/authorize
    4. GET /dasext/oauth/authorize?... → 302 → /sinfo/backend/j_oauth_check?code=...
    5. GET /sinfo/backend/j_oauth_check?code=... → 302 → /sinfo/backend/
    6. Now /sinfo/backend/myStudents returns 200 with data
"""

from __future__ import annotations

import logging
import re
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

    Authentication flow (OAuth2):
        1. GET /sinfo/backend/ triggers OAuth redirect chain
        2. On login page, extract CSRF and POST credentials
        3. Follow redirects back through OAuth to /sinfo/
        4. Session cookies for /sinfo/ are now valid
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
            follow_redirects=False,  # Manual redirect handling for OAuth flow
            timeout=self.timeout,
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

    async def _follow_redirects(
        self, resp: httpx.Response, max_redirects: int = 10
    ) -> httpx.Response:
        """Follow redirects manually, preserving cookies.

        Args:
            resp: Initial response.
            max_redirects: Maximum number of redirects to follow.

        Returns:
            Final response after all redirects.
        """
        client = self._get_client()
        redirects = 0

        while resp.is_redirect and redirects < max_redirects:
            location = resp.headers.get("location", "")
            if not location:
                break

            # Handle relative URLs
            if location.startswith("/"):
                location = f"{self.BASE_URL}{location}"
            elif not location.startswith("http"):
                # Relative to current path
                base = str(resp.url).rsplit("/", 1)[0]
                location = f"{base}/{location}"

            # Handle HTTP->HTTPS upgrade
            if location.startswith("http://eservice.omsu.ru"):
                location = location.replace("http://", "https://")

            logger.debug("Following redirect to: %s", location)
            resp = await client.get(location)
            redirects += 1

        return resp

    async def login(self, email: str, password: str) -> bool:
        """Authenticate to LK via OAuth2 flow and establish session.

        OAuth2 Flow:
            1. GET /sinfo/backend/ → triggers OAuth redirect
            2. Follow redirects to /dasext/login
            3. Extract CSRF, POST credentials
            4. Follow redirects back to /sinfo/ with OAuth code
            5. Session is now valid for /sinfo/backend/*

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
            # Step 1: Initiate OAuth flow by accessing /sinfo/backend/
            logger.debug("Initiating OAuth flow via /sinfo/backend/")
            resp = await client.get(f"{self.BASE_URL}/sinfo/backend/")

            # Follow redirects until we reach login page
            while resp.is_redirect:
                location = resp.headers.get("location", "")
                if "/dasext/login" in location and "oauth" not in location.lower():
                    # We've reached the login page
                    break
                resp = await self._follow_redirects(resp, max_redirects=1)

            # Final redirect to login page
            if resp.is_redirect:
                location = resp.headers.get("location", "")
                if location.startswith("/"):
                    location = f"{self.BASE_URL}{location}"
                resp = await client.get(location)

            # Step 2: Extract CSRF token from login page
            logger.debug("Fetching login page for CSRF token")
            csrf_token = resp.headers.get("X-CSRF-TOKEN")
            if not csrf_token:
                csrf_token = resp.cookies.get("XSRF-TOKEN")

            if not csrf_token:
                # Try to extract from HTML
                match = re.search(r'name="_csrf"\s+value="([^"]+)"', resp.text)
                if match:
                    csrf_token = match.group(1)

            if not csrf_token:
                raise LkAuthError("CSRF token not found in response headers or cookies")

            logger.debug("CSRF token obtained")

            # Step 3: Submit login form
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

            # Step 4: Follow all redirects through OAuth back to /sinfo/
            resp = await self._follow_redirects(resp, max_redirects=10)

            final_url = str(resp.url)
            logger.debug("Final URL after login: %s", final_url)

            # Check if we landed on sinfo (successful auth)
            if "/sinfo/" in final_url and "/login" not in final_url:
                logger.info("LK authentication successful")
                return True

            # Check for error indicators
            if "error" in final_url.lower() or resp.status_code >= 400:
                logger.warning("LK authentication failed: %s", final_url)
                return False

            # Check if still on login page
            if "j_password" in resp.text or "/dasext/login" in final_url:
                logger.warning("LK authentication failed: still on login page")
                return False

            # If we're on eservice.omsu.ru root, try to access sinfo again
            if final_url.rstrip("/") == self.BASE_URL:
                logger.debug("On root page, verifying sinfo access")
                return await self.check_session()

            logger.info("LK authentication completed, verifying session")
            return await self.check_session()

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

            # Follow redirects if any
            if resp.is_redirect:
                resp = await self._follow_redirects(resp)

            # Check for redirect to login (session expired)
            final_url = str(resp.url)
            if "/login" in final_url or "/oauth/authorize" in final_url:
                raise LkSessionExpired("Session expired, please re-authenticate")

            if resp.status_code == 401:
                raise LkSessionExpired("Session expired (401)")

            resp.raise_for_status()

            # Parse JSON response
            try:
                data = resp.json()
            except Exception as e:
                logger.error("Failed to parse JSON response: %s", resp.text[:500])
                raise LkDataError(f"Invalid JSON response: {e}") from e

            logger.info("Student data fetched successfully")
            logger.debug(
                "Response type: %s, keys: %s",
                type(data).__name__,
                list(data.keys()) if isinstance(data, dict) else f"list[{len(data)}]",
            )

            # API returns a list with one student object
            if isinstance(data, list):
                if len(data) == 0:
                    logger.warning("API returned empty list")
                    return LkStudentData()
                # Take first student from the list
                student = data[0]
                logger.debug(
                    "Extracted student data, keys: %s",
                    list(student.keys())
                    if isinstance(student, dict)
                    else type(student).__name__,
                )
            else:
                student = data

            return LkStudentData(
                sessions=student.get("sessions", []),
                sem_info=student.get("semInfo", []),
                summary=student.get("summary", {}),
                raw_data=student,
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

            # Follow redirects
            if resp.is_redirect:
                resp = await self._follow_redirects(resp)

            final_url = str(resp.url)

            # Session is valid if we get 200 and not redirected to login/oauth
            return (
                resp.status_code == 200
                and "/login" not in final_url
                and "/oauth/authorize" not in final_url
            )
        except httpx.RequestError:
            return False
