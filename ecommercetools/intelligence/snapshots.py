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


def collect_weekly_snapshot(*args, **kwargs):
    pass
