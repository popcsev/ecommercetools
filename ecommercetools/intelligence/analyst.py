"""Compare weekly snapshots and detect trends and anomalies."""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

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
            if prev_val == 0:
                diffs[metric] = None
            else:
                diffs[metric] = round((cur_val - prev_val) / abs(prev_val) * 100, 1)
        result[country] = diffs
    return result


def analyse_week(*args, **kwargs):
    pass
