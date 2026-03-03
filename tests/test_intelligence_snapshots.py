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


import tempfile
from pathlib import Path
from ecommercetools.intelligence.snapshots import get_snapshot_dir, snapshot_exists


def test_get_snapshot_dir_returns_correct_path():
    base = Path("/tmp/reports")
    result = get_snapshot_dir("2026-W09", base_dir=base)
    assert result == Path("/tmp/reports/snapshots/2026-W09")


def test_snapshot_exists_false_when_dir_missing():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        assert snapshot_exists("2026-W09", base_dir=base) is False


def test_snapshot_exists_true_when_summary_parquet_present():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        snap_dir = base / "snapshots" / "2026-W09"
        snap_dir.mkdir(parents=True)
        (snap_dir / "summary.parquet").touch()
        assert snapshot_exists("2026-W09", base_dir=base) is True
