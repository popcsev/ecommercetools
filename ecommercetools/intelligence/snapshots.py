"""Collect and persist weekly GA4 snapshots as Parquet files."""

from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd


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


def save_snapshot(df: pd.DataFrame, week_label: str, name: str, base_dir: Path = REPORTS_DIR) -> Path:
    """Save a DataFrame as a Parquet file in the week's snapshot directory."""
    snap_dir = get_snapshot_dir(week_label, base_dir)
    snap_dir.mkdir(parents=True, exist_ok=True)
    path = snap_dir / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def load_snapshot(week_label: str, name: str, base_dir: Path = REPORTS_DIR) -> pd.DataFrame:
    """Load a Parquet snapshot by week label and name."""
    path = get_snapshot_dir(week_label, base_dir) / f"{name}.parquet"
    return pd.DataFrame(pd.read_parquet(path))


def add_transactions(week_label: str, df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder: merge external transactional data into the summary.
    Implement when transactional data is available."""
    return df


def collect_weekly_snapshot(
    credentials_path: str,
    config_path: str,
    week_label: Optional[str] = None,
    base_dir: Path = REPORTS_DIR,
    countries: Optional[List[str]] = None,
) -> str:
    """Pull GA4 data for the previous week and save as Parquet snapshots.

    Args:
        credentials_path: Path to GCP service account JSON.
        config_path: Path to GA4 property config JSON.
        week_label: ISO week label e.g. '2026-W09'. Defaults to previous week.
        base_dir: Root directory for reports storage.
        countries: Optional list of countries to query. Defaults to all in config.

    Returns:
        week_label that was collected.
    """
    from ecommercetools.analytics.ga4 import query_ga4_multi_country

    if week_label is None:
        today = date.today()
        last_monday = today - timedelta(days=today.weekday() + 7)
        week_label = get_week_label(last_monday)

    if snapshot_exists(week_label, base_dir):
        print(f"Snapshot for {week_label} already exists, skipping.")
        return week_label

    start, end = get_week_date_range(week_label)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    # --- Summary snapshot ---
    summary_df = query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_str,
        end_date=end_str,
        dimensions=[],
        metrics=[
            "sessions", "totalUsers", "newUsers", "bounceRate",
            "transactions", "totalRevenue", "averagePurchaseRevenue",
        ],
        countries=countries,
    )
    summary_df["week"] = week_label
    summary_df.rename(columns={
        "country_label": "country",
        "totalUsers": "users",
        "newUsers": "new_users",
        "totalRevenue": "revenue",
        "averagePurchaseRevenue": "avg_order_value",
    }, inplace=True)
    summary_df["conversion_rate"] = (
        (summary_df["transactions"] / summary_df["sessions"].replace(0, float("nan"))) * 100
    ).fillna(0.0).round(2)
    summary_df = add_transactions(week_label, summary_df)
    save_snapshot(summary_df, week_label, "summary", base_dir)

    # --- Traffic detail snapshot ---
    traffic_df = query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_str,
        end_date=end_str,
        dimensions=["date"],
        metrics=["sessions", "totalUsers", "newUsers", "screenPageViews", "bounceRate"],
        countries=countries,
    )
    traffic_df["week"] = week_label
    save_snapshot(traffic_df, week_label, "traffic_detail", base_dir)

    # --- Acquisition detail snapshot ---
    acq_df = query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_str,
        end_date=end_str,
        dimensions=["sessionSource", "sessionMedium"],
        metrics=["sessions", "totalUsers", "conversions", "engagementRate"],
        countries=countries,
    )
    acq_df["week"] = week_label
    save_snapshot(acq_df, week_label, "acquisition_detail", base_dir)

    print(f"Snapshot saved for {week_label} ({start_str} to {end_str})")
    return week_label
