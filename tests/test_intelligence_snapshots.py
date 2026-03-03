"""Tests for ecommercetools.intelligence.snapshots"""

from datetime import date
from ecommercetools.intelligence.snapshots import get_week_label, get_week_date_range


def test_get_week_label_returns_iso_format():
    # Monday 2026-02-23 is week 9 of 2026
    result = get_week_label(date(2026, 2, 23))
    assert result == "2026-W09"


def test_get_week_label_pads_single_digit_week():
    result = get_week_label(date(2026, 1, 5))
    assert result == "2026-W02"


def test_get_week_date_range_returns_monday_to_sunday():
    start, end = get_week_date_range("2026-W09")
    assert start == date(2026, 2, 23)
    assert end == date(2026, 3, 1)


def test_get_week_date_range_week01():
    start, end = get_week_date_range("2026-W01")
    assert start == date(2025, 12, 29)
    assert end == date(2026, 1, 4)
