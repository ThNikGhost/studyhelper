"""OmGU schedule parser using Playwright."""

from __future__ import annotations

import asyncio
import logging
import sys
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from playwright.async_api import Browser, Page, Playwright, async_playwright

from src.config import settings
from src.parser.data_mapper import DataMapper
from src.parser.exceptions import (
    DataExtractionError,
    ElementNotFoundError,
    PageLoadError,
)
from src.parser.hash_utils import compute_schedule_hash
from src.schemas.schedule import ScheduleEntryCreate

logger = logging.getLogger(__name__)

# Default timeout for page operations (ms)
DEFAULT_TIMEOUT = 30000

# Selectors for schedule elements (based on eservice.omsu.ru structure)
SELECTORS = {
    # Schedule table container
    "schedule_container": ".schedule-table, .table-schedule, [class*='schedule']",
    # Individual lesson/entry
    "lesson_entry": ".lesson-item, .schedule-item, tr.lesson, [class*='lesson']",
    # Day header
    "day_header": ".day-header, th.day, [class*='day-name']",
    # Time cell
    "time_cell": ".time, .lesson-time, td.time",
    # Subject name
    "subject": ".subject, .lesson-name, .discipline",
    # Teacher name
    "teacher": ".teacher, .lecturer, .prepod",
    # Room/location
    "location": ".room, .audience, .location, .aud",
    # Lesson type
    "lesson_type": ".type, .lesson-type, [class*='type']",
    # Week type (odd/even)
    "week_type": ".week-type, .week, [class*='week']",
}


@dataclass
class ParseResult:
    """Result of schedule parsing."""

    entries: list[ScheduleEntryCreate] = field(default_factory=list)
    raw_data: list[dict[str, Any]] = field(default_factory=list)
    content_hash: str = ""
    source_url: str = ""
    parsed_date: date = field(default_factory=date.today)
    errors: list[str] = field(default_factory=list)

    @property
    def entries_count(self) -> int:
        """Get number of parsed entries."""
        return len(self.entries)

    @property
    def has_errors(self) -> bool:
        """Check if parsing had errors."""
        return len(self.errors) > 0


class OmsuScheduleParser:
    """Playwright-based parser for OmGU schedule website.

    Usage:
        async with OmsuScheduleParser() as parser:
            result = await parser.parse()
            for entry in result.entries:
                print(entry.subject_name)
    """

    def __init__(
        self,
        url: str | None = None,
        headless: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize parser.

        Args:
            url: Schedule URL. Defaults to settings.schedule_url.
            headless: Run browser in headless mode.
            timeout: Page operation timeout in milliseconds.
        """
        self.url = url or settings.schedule_url
        self.headless = headless
        self.timeout = timeout
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def __aenter__(self) -> OmsuScheduleParser:
        """Start Playwright and launch browser."""
        # Set Windows event loop policy if needed
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._page = await self._browser.new_page()
        self._page.set_default_timeout(self.timeout)

        logger.info("Playwright browser started (headless=%s)", self.headless)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Close browser and stop Playwright."""
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

        logger.info("Playwright browser closed")

    async def parse(self, url: str | None = None) -> ParseResult:
        """Parse schedule from URL.

        Args:
            url: URL to parse. Defaults to instance URL.

        Returns:
            ParseResult with parsed entries and metadata.

        Raises:
            PageLoadError: If page fails to load.
            ElementNotFoundError: If schedule container not found.
            DataExtractionError: If data extraction fails.
        """
        if self._page is None:
            raise RuntimeError("Parser not initialized. Use 'async with' context.")

        target_url = url or self.url
        logger.info("Parsing schedule from: %s", target_url)

        result = ParseResult(source_url=target_url, parsed_date=date.today())

        try:
            # Load page
            await self._load_page(target_url)

            # Wait for schedule to render
            await self._wait_for_schedule()

            # Extract raw data
            raw_entries = await self._extract_schedule_data()
            result.raw_data = raw_entries

            # Map to schema objects
            for raw in raw_entries:
                try:
                    entry = DataMapper.map_raw_entry(raw)
                    result.entries.append(entry)
                except Exception as e:
                    error_msg = f"Failed to map entry: {e}"
                    logger.warning(error_msg)
                    result.errors.append(error_msg)

            # Compute hash
            result.content_hash = compute_schedule_hash(raw_entries)

            logger.info(
                "Parsed %d entries (hash: %s...)",
                len(result.entries),
                result.content_hash[:8],
            )

        except PageLoadError:
            raise
        except ElementNotFoundError:
            raise
        except Exception as e:
            raise DataExtractionError(f"Failed to extract schedule: {e}") from e

        return result

    async def _load_page(self, url: str) -> None:
        """Load page and wait for network idle.

        Args:
            url: URL to load.

        Raises:
            PageLoadError: If page fails to load.
        """
        if self._page is None:
            raise RuntimeError("Page not initialized")

        try:
            response = await self._page.goto(url, wait_until="networkidle")
            if response and not response.ok:
                raise PageLoadError(
                    f"Page returned status {response.status}: {response.status_text}"
                )
            logger.debug("Page loaded: %s", url)
        except Exception as e:
            if isinstance(e, PageLoadError):
                raise
            raise PageLoadError(f"Failed to load page: {e}") from e

    async def _wait_for_schedule(self) -> None:
        """Wait for schedule container to appear.

        Raises:
            ElementNotFoundError: If schedule container not found.
        """
        if self._page is None:
            raise RuntimeError("Page not initialized")

        # Try multiple selectors
        selectors_to_try = [
            ".schedule-table",
            ".table-schedule",
            "table.schedule",
            "[class*='schedule']",
            ".timetable",
            "table",  # Fallback to any table
        ]

        for selector in selectors_to_try:
            try:
                await self._page.wait_for_selector(selector, timeout=5000)
                logger.debug("Found schedule container: %s", selector)
                return
            except Exception:
                continue

        raise ElementNotFoundError(
            "Schedule container not found. The page structure may have changed."
        )

    async def _extract_schedule_data(self) -> list[dict[str, Any]]:
        """Extract schedule data from page.

        Returns:
            List of raw entry dictionaries.

        Note:
            This method uses JavaScript evaluation to extract data from the page.
            The extraction logic may need adjustment based on actual site structure.
        """
        if self._page is None:
            raise RuntimeError("Page not initialized")

        # JavaScript to extract schedule data
        # This is a generic extraction that tries multiple approaches
        extract_script = """
        () => {
            const entries = [];

            // Try to find schedule rows/items
            const rows = document.querySelectorAll(
                'tr, .lesson-item, .schedule-item, [class*="lesson"], [class*="pair"]'
            );

            for (const row of rows) {
                // Skip header rows
                if (row.querySelector('th')) continue;

                // Try to extract data
                const getText = (selectors) => {
                    for (const sel of selectors) {
                        const el = row.querySelector(sel);
                        if (el && el.textContent.trim()) {
                            return el.textContent.trim();
                        }
                    }
                    return '';
                };

                const subject = getText([
                    '.subject', '.discipline', '.lesson-name',
                    '[class*="subject"]', '[class*="discipline"]',
                    'td:nth-child(2)', 'td:nth-child(3)'
                ]);

                if (!subject) continue;

                const entry = {
                    subject_name: subject,
                    start_time: getText(['.time-start', '.start', '[class*="time"]']),
                    end_time: getText(['.time-end', '.end']),
                    teacher_name: getText([
                        '.teacher', '.lecturer', '.prepod',
                        '[class*="teacher"]', '[class*="prepod"]'
                    ]),
                    location: getText([
                        '.room', '.audience', '.location', '.aud',
                        '[class*="room"]', '[class*="aud"]'
                    ]),
                    lesson_type: getText([
                        '.type', '.lesson-type', '[class*="type"]'
                    ]),
                    week_type: getText([
                        '.week-type', '.week', '[class*="week"]'
                    ]),
                    day_of_week: getText([
                        '.day', '.day-name', '[class*="day"]'
                    ]),
                    subgroup: getText(['.subgroup', '[class*="subgroup"]']),
                    group_name: getText(['.group', '[class*="group"]']),
                };

                // Try to get time from combined cell
                const timeCell = row.querySelector('.time, td:first-child');
                if (timeCell && !entry.start_time) {
                    const timeText = timeCell.textContent.trim();
                    const timeMatch = timeText.match(/(\\d{1,2}[:.:]\\d{2})\\s*[-–]\\s*(\\d{1,2}[:.:]\\d{2})/);
                    if (timeMatch) {
                        entry.start_time = timeMatch[1];
                        entry.end_time = timeMatch[2];
                    }
                }

                entries.push(entry);
            }

            return entries;
        }
        """

        try:
            raw_entries = await self._page.evaluate(extract_script)
            logger.debug("Extracted %d raw entries", len(raw_entries))
            return raw_entries
        except Exception as e:
            logger.error("Failed to extract data: %s", e)
            return []

    async def get_page_html(self) -> str:
        """Get current page HTML for debugging.

        Returns:
            Page HTML content.
        """
        if self._page is None:
            raise RuntimeError("Page not initialized")
        return await self._page.content()

    async def screenshot(self, path: str) -> None:
        """Take screenshot of current page.

        Args:
            path: Path to save screenshot.
        """
        if self._page is None:
            raise RuntimeError("Page not initialized")
        await self._page.screenshot(path=path, full_page=True)
        logger.info("Screenshot saved: %s", path)
