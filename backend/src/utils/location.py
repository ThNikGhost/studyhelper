"""Location formatting utility."""

from __future__ import annotations


def format_location(building: str | None, room: str | None) -> str | None:
    """Build compact location string like '1-101'.

    Strips 'Корпус ' / 'корпус ' prefix from building for compact format.

    Args:
        building: Building name (e.g. "Корпус 1").
        room: Room number (e.g. "101").

    Returns:
        Compact location string or None if both are absent.
    """
    b = building
    if b:
        b = b.removeprefix("Корпус ").removeprefix("корпус ")
    if b and room:
        return f"{b}-{room}"
    return room or b or None
