"""Tests for ecommercetools.intelligence.analyst"""

import pandas as pd
from ecommercetools.intelligence.analyst import compute_wow_diff


def _make_summary(week, country, sessions, revenue, transactions):
    return pd.DataFrame([{
        "week": week, "country": country,
        "sessions": sessions, "revenue": revenue,
        "transactions": transactions,
        "users": 100, "new_users": 50, "bounce_rate": 40.0,
        "avg_order_value": revenue / max(transactions, 1),
        "conversion_rate": transactions / max(sessions, 1) * 100,
    }])


def test_wow_diff_positive_sessions():
    current = _make_summary("2026-W09", "UK", sessions=1200, revenue=6000, transactions=60)
    previous = _make_summary("2026-W08", "UK", sessions=1000, revenue=5000, transactions=50)
    result = compute_wow_diff(current, previous)
    assert result["UK"]["sessions"] == 20.0  # +20%


def test_wow_diff_negative_revenue():
    current = _make_summary("2026-W09", "UK", sessions=1000, revenue=4000, transactions=40)
    previous = _make_summary("2026-W08", "UK", sessions=1000, revenue=5000, transactions=50)
    result = compute_wow_diff(current, previous)
    assert result["UK"]["revenue"] == -20.0  # -20%


def test_wow_diff_zero_previous_handled():
    current = _make_summary("2026-W09", "UK", sessions=100, revenue=0, transactions=0)
    previous = _make_summary("2026-W08", "UK", sessions=0, revenue=0, transactions=0)
    result = compute_wow_diff(current, previous)
    assert result["UK"]["sessions"] is None  # can't divide by zero


import tempfile
from pathlib import Path
from ecommercetools.intelligence.snapshots import save_snapshot
from ecommercetools.intelligence.analyst import detect_anomalies, analyse_week


def test_detect_anomalies_flags_large_swings():
    wow = {"UK": {"sessions": 20.0, "revenue": -18.0, "transactions": 5.0}}
    anomalies = detect_anomalies(wow, threshold=15.0)
    assert len(anomalies) == 2
    directions = {a["metric"]: a["direction"] for a in anomalies if a["country"] == "UK"}
    assert directions["sessions"] == "up"
    assert directions["revenue"] == "down"


def test_detect_anomalies_ignores_small_swings():
    wow = {"UK": {"sessions": 5.0, "revenue": -3.0}}
    anomalies = detect_anomalies(wow, threshold=15.0)
    assert anomalies == []


def test_analyse_week_returns_expected_keys():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for week, sessions, revenue in [
            ("2026-W05", 800, 4000), ("2026-W06", 900, 4500),
            ("2026-W07", 950, 4800), ("2026-W08", 1000, 5000),
            ("2026-W09", 1200, 6000),
        ]:
            df = _make_summary(week, "UK", sessions=sessions, revenue=revenue, transactions=sessions // 20)
            save_snapshot(df, week, "summary", base_dir=base)
        result = analyse_week("2026-W09", base_dir=base)
        assert "week" in result
        assert "vs_last_week" in result
        assert "anomalies" in result
        assert "winners" in result
        assert "losers" in result
