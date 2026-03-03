"""Compare weekly snapshots and detect trends and anomalies."""

from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from ecommercetools.intelligence.snapshots import load_snapshot, REPORTS_DIR, get_week_date_range, get_week_label

METRICS = ["sessions", "users", "revenue", "transactions", "conversion_rate", "avg_order_value"]


def compute_wow_diff(current: pd.DataFrame, previous: pd.DataFrame) -> Dict[str, Dict[str, Optional[float]]]:
    """Compute % change per metric per country between two summary DataFrames.

    Returns:
        dict: {country: {metric: pct_change or None if previous == 0}}
    """
    result = {}
    for _, cur_row in current.iterrows():
        country = cur_row["country"]
        prev_rows = previous[previous["country"] == country]
        if prev_rows.empty:
            continue
        prev_row = prev_rows.iloc[0]
        diffs = {}
        for metric in METRICS:
            if metric not in cur_row or metric not in prev_row:
                continue
            prev_val = prev_row[metric]
            cur_val = cur_row[metric]
            if prev_val == 0 or pd.isna(prev_val):
                diffs[metric] = None
            else:
                diffs[metric] = round((cur_val - prev_val) / abs(prev_val) * 100, 1)
        result[country] = diffs
    return result


def detect_anomalies(wow: Dict, threshold: float = 15.0) -> list:
    """Flag metrics where % change exceeds threshold.

    Returns:
        list of dicts: [{country, metric, direction, pct}]
    """
    anomalies = []
    for country, metrics in wow.items():
        for metric, pct in metrics.items():
            if pct is None:
                continue
            if abs(pct) >= threshold:
                anomalies.append({
                    "country": country,
                    "metric": metric,
                    "direction": "up" if pct > 0 else "down",
                    "pct": pct,
                })
    return anomalies


def analyse_week(week_label: str, base_dir: Path = REPORTS_DIR, anomaly_threshold: float = 15.0) -> Dict[str, Any]:
    """Load snapshots for this week and recent history, compute full analysis.

    Returns structured dict consumed by narrator.py.
    """
    current = load_snapshot(week_label, "summary", base_dir)

    current_start, _ = get_week_date_range(week_label)
    prev_start = current_start - timedelta(days=7)
    prev_week = get_week_label(prev_start)

    try:
        previous = load_snapshot(prev_week, "summary", base_dir)
        wow = compute_wow_diff(current, previous)
    except FileNotFoundError:
        wow = {}

    # Load up to 8 weeks of history for rolling context
    history = []
    for offset in range(1, 9):
        hist_start = current_start - timedelta(days=7 * offset)
        hist_label = get_week_label(hist_start)
        try:
            history.append(load_snapshot(hist_label, "summary", base_dir))
        except FileNotFoundError:
            break

    anomalies = detect_anomalies(wow, threshold=anomaly_threshold)

    # Winners = countries with biggest positive sessions WoW
    # Losers = countries with biggest negative sessions WoW
    sorted_wow = sorted(
        [(c, m.get("sessions")) for c, m in wow.items() if m.get("sessions") is not None],
        key=lambda x: x[1],
        reverse=True,
    )
    winners = [{"country": c, "metric": "sessions", "pct": p} for c, p in sorted_wow[:3] if p > 0]
    losers = [{"country": c, "metric": "sessions", "pct": p} for c, p in sorted_wow[-3:] if p < 0]

    start, end = get_week_date_range(week_label)

    return {
        "week": week_label,
        "date_range": {"start": str(start), "end": str(end)},
        "current_summary": current.to_dict(orient="records"),
        "vs_last_week": wow,
        "history_weeks": len(history),
        "history_summary": pd.concat(history).to_dict(orient="records") if history else [],
        "anomalies": anomalies,
        "winners": winners,
        "losers": losers,
    }
