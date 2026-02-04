"""Hash utilities for schedule change detection."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_schedule_hash(entries: list[dict[str, Any]]) -> str:
    """Compute SHA-256 hash of schedule entries for change detection.

    Args:
        entries: List of schedule entry dictionaries.

    Returns:
        SHA-256 hash string (64 characters).

    Note:
        Entries are sorted by day_of_week and start_time before hashing
        to ensure consistent hash for same schedule data.
    """
    if not entries:
        return hashlib.sha256(b"").hexdigest()

    # Sort entries by day and time for consistent ordering
    sorted_entries = sorted(
        entries,
        key=lambda e: (
            e.get("day_of_week", 0),
            str(e.get("start_time", "")),
            e.get("subject_name", ""),
        ),
    )

    # Create canonical JSON representation
    canonical = json.dumps(sorted_entries, sort_keys=True, ensure_ascii=False)

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
