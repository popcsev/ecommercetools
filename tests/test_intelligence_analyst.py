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
