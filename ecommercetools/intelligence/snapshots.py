"""Collect and persist weekly GA4 snapshots as Parquet files."""

from datetime import date, timedelta
import pandas as pd
from pathlib import Path
from typing import Tuple


def get_week_label(d: date) -> str:
    """Return ISO week label like '2026-W09' for a given date."""
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def get_week_date_range(week_label: str) -> Tuple[date, date]:
    """Return (monday, sunday) for a given week label like '2026-W09'."""
    year, week = int(week_label[:4]), int(week_label[6:])
    monday = date.fromisocalendar(year, week, 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


def get_snapshot_dir(week_label: str, base_dir: Path = REPORTS_DIR) -> Path:
    """Return path to snapshot directory for a given week."""
    return base_dir / "snapshots" / week_label


def snapshot_exists(week_label: str, base_dir: Path = REPORTS_DIR) -> bool:
    """Return True if summary snapshot already exists for this week."""
    return (get_snapshot_dir(week_label, base_dir) / "summary.parquet").exists()


def collect_weekly_snapshot(*args, **kwargs):
    pass
