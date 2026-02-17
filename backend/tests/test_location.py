"""Tests for location formatting utility."""

from __future__ import annotations

import pytest

from src.utils.location import _clean_building, _clean_room, format_location


class TestCleanBuilding:
    """Tests for _clean_building."""

    def test_strips_korpus_prefix(self) -> None:
        assert _clean_building("Корпус 1") == "1"
        assert _clean_building("корпус 2") == "2"
        assert _clean_building("Корпус 10") == "10"

    def test_strips_korpus_suffix(self) -> None:
        assert _clean_building("1 корпус") == "1"
        assert _clean_building("2 Корпус") == "2"

    def test_strips_parentheses(self) -> None:
        assert _clean_building("(4)") == "4"
        assert _clean_building("(6") == "6"
        assert _clean_building("6)") == "6"

    def test_plain_number(self) -> None:
        assert _clean_building("4") == "4"
        assert _clean_building("10") == "10"

    def test_none_and_empty(self) -> None:
        assert _clean_building(None) is None
        assert _clean_building("") is None
        assert _clean_building("  ") is None

    def test_non_standard(self) -> None:
        assert _clean_building("Спортзал") == "Спортзал"


class TestCleanRoom:
    """Tests for _clean_room."""

    def test_plain_number(self) -> None:
        assert _clean_room("301") == "301"
        assert _clean_room("101а") == "101а"

    def test_strips_parentheses(self) -> None:
        assert _clean_room("113)") == "113"

    def test_extracts_number_from_zal(self) -> None:
        assert _clean_room("113) Спортивный зал") == "113"
        assert _clean_room("115 Тренажерный зал") == "115"

    def test_zal_without_number(self) -> None:
        assert _clean_room("Спортивный зал") is None

    def test_none_and_empty(self) -> None:
        assert _clean_room(None) is None
        assert _clean_room("") is None


class TestFormatLocation:
    """Tests for format_location."""

    def test_building_and_room(self) -> None:
        assert format_location("4", "101") == "4-101"
        assert format_location("6", "113") == "6-113"

    def test_korpus_prefix(self) -> None:
        assert format_location("Корпус 2", "201") == "2-201"
        assert format_location("корпус 1", "301") == "1-301"

    def test_korpus_suffix(self) -> None:
        assert format_location("1 корпус", "301") == "1-301"

    def test_parentheses(self) -> None:
        assert format_location("(6", "113) Спортивный зал") == "6-113"

    def test_room_only(self) -> None:
        assert format_location(None, "301") == "301"

    def test_building_only(self) -> None:
        assert format_location("4", None) == "4"
        assert format_location("Корпус 2", None) == "2"

    def test_both_none(self) -> None:
        assert format_location(None, None) is None

    @pytest.mark.parametrize(
        ("building", "room", "expected"),
        [
            ("Корпус 1", "101", "1-101"),
            ("1 корпус", "301", "1-301"),
            ("корпус 3", "201", "3-201"),
            ("(6", "113) Спортивный зал", "6-113"),
            ("4", "320", "4-320"),
            (None, "301", "301"),
            ("Спортзал", None, "Спортзал"),
            (None, None, None),
        ],
    )
    def test_various_formats(
        self,
        building: str | None,
        room: str | None,
        expected: str | None,
    ) -> None:
        assert format_location(building, room) == expected
