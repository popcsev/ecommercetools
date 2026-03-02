# Intelligence Module Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build `ecommercetools/intelligence/` — a module that saves weekly GA4 snapshots locally, runs trend/anomaly analysis, and uses Claude on GCP Vertex AI to generate Markdown + HTML reports with Q&A over history.

**Architecture:** Four components (`snapshots`, `analyst`, `narrator`, `reporter`) plus two entry-point scripts (`run_weekly_report.py`, `ask.py`). Data is stored as Parquet files under `reports/snapshots/YYYY-Www/`. LLM calls go to Claude via `anthropic.AnthropicVertex`, authenticated with the existing GCP service account.

**Tech Stack:** `pandas`, `pyarrow`, `anthropic[vertex]`, `google-auth`, `markdown`, existing `ecommercetools.analytics.ga4` module.

---

## Task 1: Add dependencies

**Files:**
- Modify: `requirements.txt`

**Step 1: Add new dependencies**

Append to `requirements.txt`:
```
anthropic[vertex]>=0.40.0
google-auth>=2.0.0
pyarrow>=14.0.0
markdown>=3.5.0
```

**Step 2: Install them**

```bash
pip install "anthropic[vertex]>=0.40.0" "google-auth>=2.0.0" "pyarrow>=14.0.0" "markdown>=3.5.0"
```

Expected: all packages install without errors.

**Step 3: Commit**

```bash
git add requirements.txt
git commit -m "feat: add intelligence module dependencies"
```

---

## Task 2: Create module skeleton

**Files:**
- Create: `ecommercetools/intelligence/__init__.py`
- Create: `ecommercetools/intelligence/snapshots.py`
- Create: `ecommercetools/intelligence/analyst.py`
- Create: `ecommercetools/intelligence/narrator.py`
- Create: `ecommercetools/intelligence/reporter.py`
- Create: `tests/test_intelligence_snapshots.py`
- Create: `tests/test_intelligence_analyst.py`
- Create: `tests/test_intelligence_reporter.py`

**Step 1: Create the package**

`ecommercetools/intelligence/__init__.py`:
```python
from .snapshots import collect_weekly_snapshot, get_week_label, get_week_date_range
from .analyst import analyse_week
from .narrator import generate_narrative, answer_question
from .reporter import generate_report
```

**Step 2: Create empty module files with docstrings only**

`ecommercetools/intelligence/snapshots.py`:
```python
"""Collect and persist weekly GA4 snapshots as Parquet files."""
```

`ecommercetools/intelligence/analyst.py`:
```python
"""Compare weekly snapshots and detect trends and anomalies."""
```

`ecommercetools/intelligence/narrator.py`:
```python
"""Generate LLM narrative using Claude on GCP Vertex AI."""
```

`ecommercetools/intelligence/reporter.py`:
```python
"""Assemble Markdown and HTML reports from analysis and narrative."""
```

**Step 3: Create empty test files**

`tests/test_intelligence_snapshots.py`:
```python
"""Tests for ecommercetools.intelligence.snapshots"""
```

`tests/test_intelligence_analyst.py`:
```python
"""Tests for ecommercetools.intelligence.analyst"""
```

`tests/test_intelligence_reporter.py`:
```python
"""Tests for ecommercetools.intelligence.reporter"""
```

**Step 4: Verify import works**

```bash
python -c "from ecommercetools.intelligence import snapshots"
```

Expected: no errors.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/ tests/test_intelligence_*.py
git commit -m "feat: add intelligence module skeleton"
```

---

## Task 3: `snapshots.py` — week label helpers

**Files:**
- Modify: `ecommercetools/intelligence/snapshots.py`
- Modify: `tests/test_intelligence_snapshots.py`

**Step 1: Write failing tests**

In `tests/test_intelligence_snapshots.py`:
```python
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
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_intelligence_snapshots.py -v
```

Expected: FAIL with `ImportError`.

**Step 3: Implement**

In `ecommercetools/intelligence/snapshots.py`:
```python
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
```

**Step 4: Run to verify they pass**

```bash
pytest tests/test_intelligence_snapshots.py -v
```

Expected: 4 PASSED.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/snapshots.py tests/test_intelligence_snapshots.py
git commit -m "feat: add week label helpers to snapshots"
```

---

## Task 4: `snapshots.py` — snapshot paths and idempotency check

**Files:**
- Modify: `ecommercetools/intelligence/snapshots.py`
- Modify: `tests/test_intelligence_snapshots.py`

**Step 1: Write failing tests**

Append to `tests/test_intelligence_snapshots.py`:
```python
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
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_intelligence_snapshots.py::test_get_snapshot_dir_returns_correct_path -v
```

Expected: FAIL with `ImportError`.

**Step 3: Implement**

Append to `ecommercetools/intelligence/snapshots.py`:
```python

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


def get_snapshot_dir(week_label: str, base_dir: Path = REPORTS_DIR) -> Path:
    """Return path to snapshot directory for a given week."""
    return base_dir / "snapshots" / week_label


def snapshot_exists(week_label: str, base_dir: Path = REPORTS_DIR) -> bool:
    """Return True if summary snapshot already exists for this week."""
    return (get_snapshot_dir(week_label, base_dir) / "summary.parquet").exists()
```

**Step 4: Run to verify they pass**

```bash
pytest tests/test_intelligence_snapshots.py -v
```

Expected: all PASSED.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/snapshots.py tests/test_intelligence_snapshots.py
git commit -m "feat: add snapshot path helpers and idempotency check"
```

---

## Task 5: `snapshots.py` — GA4 collection and save

**Files:**
- Modify: `ecommercetools/intelligence/snapshots.py`

**Note:** This task integrates with the live GA4 API so it is not unit-tested directly. The helpers it calls (`query_ga4_multi_country`) are already tested upstream. We test the save/load round-trip instead.

**Step 1: Write a save/load round-trip test**

Append to `tests/test_intelligence_snapshots.py`:
```python
from ecommercetools.intelligence.snapshots import save_snapshot, load_snapshot


def test_save_and_load_snapshot_round_trip():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        df = pd.DataFrame({
            "week": ["2026-W09"],
            "country": ["UK"],
            "sessions": [1000],
            "revenue": [5000.0],
        })
        save_snapshot(df, "2026-W09", "summary", base_dir=base)
        result = load_snapshot("2026-W09", "summary", base_dir=base)
        assert list(result["country"]) == ["UK"]
        assert result["sessions"].iloc[0] == 1000
```

**Step 2: Run to verify it fails**

```bash
pytest tests/test_intelligence_snapshots.py::test_save_and_load_snapshot_round_trip -v
```

Expected: FAIL with `ImportError`.

**Step 3: Implement save/load and collect_weekly_snapshot**

Append to `ecommercetools/intelligence/snapshots.py`:
```python

from ecommercetools.analytics.ga4 import query_ga4_multi_country


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
    week_label: str = None,
    base_dir: Path = REPORTS_DIR,
    countries: list = None,
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
    if summary_df["sessions"].sum() > 0:
        summary_df["conversion_rate"] = (
            summary_df["transactions"] / summary_df["sessions"] * 100
        ).round(2)
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
```

**Step 4: Run all snapshot tests**

```bash
pytest tests/test_intelligence_snapshots.py -v
```

Expected: all PASSED.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/snapshots.py tests/test_intelligence_snapshots.py
git commit -m "feat: implement GA4 collection and snapshot persistence"
```

---

## Task 6: `analyst.py` — week-on-week diff

**Files:**
- Modify: `ecommercetools/intelligence/analyst.py`
- Modify: `tests/test_intelligence_analyst.py`

**Step 1: Write failing tests**

In `tests/test_intelligence_analyst.py`:
```python
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
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_intelligence_analyst.py -v
```

Expected: FAIL with `ImportError`.

**Step 3: Implement**

In `ecommercetools/intelligence/analyst.py`:
```python
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
```

**Step 4: Run to verify they pass**

```bash
pytest tests/test_intelligence_analyst.py -v
```

Expected: all PASSED.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/analyst.py tests/test_intelligence_analyst.py
git commit -m "feat: add week-on-week diff to analyst"
```

---

## Task 7: `analyst.py` — anomaly detection and full analyse_week

**Files:**
- Modify: `ecommercetools/intelligence/analyst.py`
- Modify: `tests/test_intelligence_analyst.py`

**Step 1: Write failing tests**

Append to `tests/test_intelligence_analyst.py`:
```python
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
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_intelligence_analyst.py -v
```

Expected: FAIL with `ImportError`.

**Step 3: Implement**

Append to `ecommercetools/intelligence/analyst.py`:
```python
from ecommercetools.intelligence.snapshots import load_snapshot, REPORTS_DIR


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

    year, wnum = int(week_label[:4]), int(week_label[6:])
    prev_week = f"{year}-W{wnum - 1:02d}" if wnum > 1 else f"{year - 1}-W52"

    try:
        previous = load_snapshot(prev_week, "summary", base_dir)
        wow = compute_wow_diff(current, previous)
    except FileNotFoundError:
        wow = {}

    # Load up to 8 weeks of history for rolling context
    history = []
    for offset in range(1, 9):
        w = wnum - offset
        y = year
        if w < 1:
            w += 52
            y -= 1
        wlabel = f"{y}-W{w:02d}"
        try:
            history.append(load_snapshot(wlabel, "summary", base_dir))
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

    from datetime import date
    from ecommercetools.intelligence.snapshots import get_week_date_range
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
```

**Step 4: Run all analyst tests**

```bash
pytest tests/test_intelligence_analyst.py -v
```

Expected: all PASSED.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/analyst.py tests/test_intelligence_analyst.py
git commit -m "feat: add anomaly detection and full analyse_week"
```

---

## Task 8: `narrator.py` — Vertex AI client and weekly narrative

**Files:**
- Modify: `ecommercetools/intelligence/narrator.py`

**Note:** Narrator makes live LLM calls so we do not unit test it. Manual verification is described below.

**Step 1: Implement narrator**

In `ecommercetools/intelligence/narrator.py`:
```python
"""Generate LLM narrative using Claude on GCP Vertex AI."""

import json
from typing import Dict, Any


MODEL = "claude-sonnet-4-6@20251001"


def _get_client(project_id: str, region: str = "us-east5"):
    """Create AnthropicVertex client using default GCP credentials."""
    import anthropic
    from google.auth import default
    from google.auth.transport.requests import Request

    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())

    return anthropic.AnthropicVertex(
        project_id=project_id,
        region=region,
    )


def _call(client, prompt: str, max_tokens: int = 1024) -> str:
    """Make a single call to Claude and return the text response."""
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_narrative(analysis: Dict[str, Any], project_id: str, region: str = "us-east5") -> Dict[str, str]:
    """Generate executive summary and trend commentary from analysis dict.

    Args:
        analysis: Output from analyst.analyse_week()
        project_id: GCP project ID for Vertex AI
        region: Vertex AI region

    Returns:
        dict with keys 'executive_summary' and 'trend_commentary'
    """
    client = _get_client(project_id, region)

    summary_prompt = f"""You are an ecommerce analytics expert. Below is weekly performance data.
Write a concise executive summary (3-4 sentences) highlighting what moved, any notable anomalies, and one thing to watch next week.
Be specific with numbers. Do not use filler phrases.

Data:
{json.dumps(analysis, indent=2)}
"""

    trend_prompt = f"""You are an ecommerce analytics expert. Below is {analysis['history_weeks']} weeks of historical performance data plus this week's results.
Write a brief trend commentary (3-4 sentences) identifying any patterns, sustained shifts, or seasonality.
Be specific. Do not repeat the executive summary.

Current week: {analysis['week']}
History data:
{json.dumps(analysis['history_summary'], indent=2)}
Current summary:
{json.dumps(analysis['current_summary'], indent=2)}
"""

    return {
        "executive_summary": _call(client, summary_prompt),
        "trend_commentary": _call(client, trend_prompt),
    }


def answer_question(question: str, snapshots_data: list, project_id: str, region: str = "us-east5") -> str:
    """Answer a natural language question about historical snapshot data.

    Args:
        question: User's question e.g. "When did UK revenue last grow 3 weeks in a row?"
        snapshots_data: List of summary dicts loaded from all available snapshots
        project_id: GCP project ID
        region: Vertex AI region

    Returns:
        str: Claude's answer
    """
    client = _get_client(project_id, region)

    prompt = f"""You are an ecommerce analytics expert with access to weekly performance snapshots.
Answer the following question using only the data provided. Be specific and cite weeks/numbers.
If you cannot answer from the data, say so clearly.

Question: {question}

Data (weekly snapshots, oldest first):
{json.dumps(snapshots_data, indent=2)}
"""
    return _call(client, prompt, max_tokens=512)
```

**Step 2: Smoke test (requires valid GCP credentials)**

```bash
python -c "
from ecommercetools.intelligence.narrator import _get_client
client = _get_client('YOUR_PROJECT_ID')
print('Vertex AI client created OK')
"
```

Expected: prints confirmation without error. If credentials fail, ensure `GOOGLE_APPLICATION_CREDENTIALS` env var points to your service account JSON.

**Step 3: Commit**

```bash
git add ecommercetools/intelligence/narrator.py
git commit -m "feat: implement Claude Vertex AI narrator"
```

---

## Task 9: `reporter.py` — Markdown and HTML assembly

**Files:**
- Modify: `ecommercetools/intelligence/reporter.py`
- Modify: `tests/test_intelligence_reporter.py`

**Step 1: Write failing tests**

In `tests/test_intelligence_reporter.py`:
```python
import tempfile
from pathlib import Path
from ecommercetools.intelligence.reporter import build_metrics_table, generate_report


def _sample_analysis():
    return {
        "week": "2026-W09",
        "date_range": {"start": "2026-02-23", "end": "2026-03-01"},
        "current_summary": [
            {"country": "UK", "sessions": 1200, "revenue": 6000.0,
             "transactions": 60, "conversion_rate": 5.0, "users": 900},
        ],
        "vs_last_week": {"UK": {"sessions": 20.0, "revenue": 20.0}},
        "anomalies": [],
        "winners": [{"country": "UK", "metric": "sessions", "pct": 20.0}],
        "losers": [],
        "history_weeks": 0,
    }


def _sample_narrative():
    return {
        "executive_summary": "Traffic grew 20% WoW driven by UK.",
        "trend_commentary": "Steady growth over 4 weeks.",
    }


def test_build_metrics_table_contains_country():
    table = build_metrics_table(_sample_analysis())
    assert "UK" in table
    assert "1,200" in table  # sessions formatted


def test_generate_report_creates_md_and_html():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        generate_report(_sample_analysis(), _sample_narrative(), base_dir=base)
        md_path = base / "weekly" / "2026-W09" / "report.md"
        html_path = base / "weekly" / "2026-W09" / "report.html"
        assert md_path.exists()
        assert html_path.exists()


def test_generate_report_md_contains_executive_summary():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        generate_report(_sample_analysis(), _sample_narrative(), base_dir=base)
        md = (base / "weekly" / "2026-W09" / "report.md").read_text()
        assert "Traffic grew 20%" in md


def test_generate_report_html_is_valid():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        generate_report(_sample_analysis(), _sample_narrative(), base_dir=base)
        html = (base / "weekly" / "2026-W09" / "report.html").read_text()
        assert "<html>" in html
        assert "UK" in html
```

**Step 2: Run to verify they fail**

```bash
pytest tests/test_intelligence_reporter.py -v
```

Expected: FAIL with `ImportError`.

**Step 3: Implement**

In `ecommercetools/intelligence/reporter.py`:
```python
"""Assemble Markdown and HTML reports from analysis and narrative."""

from datetime import date
from pathlib import Path
from typing import Dict, Any
import markdown as md_lib

REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"


def build_metrics_table(analysis: Dict[str, Any]) -> str:
    """Build a Markdown table of key metrics per country."""
    rows = ["| Country | Sessions | Revenue | Transactions | Conv. Rate | WoW Sessions |",
            "|---------|----------|---------|-------------|------------|-------------|"]

    for row in analysis["current_summary"]:
        country = row["country"]
        sessions = f"{int(row.get('sessions', 0)):,}"
        revenue = f"£{float(row.get('revenue', 0)):,.0f}"
        transactions = f"{int(row.get('transactions', 0)):,}"
        conv = f"{float(row.get('conversion_rate', 0)):.2f}%"
        wow_sessions = analysis["vs_last_week"].get(country, {}).get("sessions")
        wow_str = f"{wow_sessions:+.1f}%" if wow_sessions is not None else "n/a"
        rows.append(f"| {country} | {sessions} | {revenue} | {transactions} | {conv} | {wow_str} |")

    return "\n".join(rows)


def build_anomalies_section(analysis: Dict[str, Any]) -> str:
    """Build anomalies list for the report."""
    if not analysis["anomalies"]:
        return "_No significant anomalies this week._"
    lines = []
    for a in analysis["anomalies"]:
        icon = "🟢" if a["direction"] == "up" else "🔴"
        lines.append(f"- {icon} **{a['country']}** {a['metric']} {a['pct']:+.1f}% vs last week")
    return "\n".join(lines)


def build_markdown(analysis: Dict[str, Any], narrative: Dict[str, str]) -> str:
    """Assemble the full Markdown report."""
    week = analysis["week"]
    start = analysis["date_range"]["start"]
    end = analysis["date_range"]["end"]
    generated = date.today().isoformat()

    return f"""# Weekly Performance Report — {week}

## Executive Summary

{narrative['executive_summary']}

## Key Metrics by Country

{build_metrics_table(analysis)}

## Anomalies & Watch Items

{build_anomalies_section(analysis)}

## Trend Commentary

{narrative['trend_commentary']}

---

_Data source: GA4 | Period: {start} to {end} | Generated: {generated} | Transactional data: not yet connected_
"""


def generate_report(
    analysis: Dict[str, Any],
    narrative: Dict[str, str],
    base_dir: Path = REPORTS_DIR,
) -> Dict[str, Path]:
    """Write Markdown and HTML report files for the given week.

    Returns:
        dict with 'md' and 'html' Path keys.
    """
    week = analysis["week"]
    out_dir = base_dir / "weekly" / week
    out_dir.mkdir(parents=True, exist_ok=True)

    markdown_content = build_markdown(analysis, narrative)

    md_path = out_dir / "report.md"
    md_path.write_text(markdown_content, encoding="utf-8")

    html_body = md_lib.markdown(markdown_content, extensions=["tables"])
    html_content = f"""<html>
<head>
<meta charset="utf-8">
<title>Weekly Report {week}</title>
<style>
  body {{ font-family: sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #f4f4f4; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    html_path = out_dir / "report.html"
    html_path.write_text(html_content, encoding="utf-8")

    return {"md": md_path, "html": html_path}
```

**Step 4: Run all reporter tests**

```bash
pytest tests/test_intelligence_reporter.py -v
```

Expected: all PASSED.

**Step 5: Commit**

```bash
git add ecommercetools/intelligence/reporter.py tests/test_intelligence_reporter.py
git commit -m "feat: implement Markdown and HTML report assembly"
```

---

## Task 10: Entry point — `run_weekly_report.py`

**Files:**
- Create: `run_weekly_report.py`

**Step 1: Implement**

```python
#!/usr/bin/env python
"""Run the weekly intelligence report.

Usage:
    python run_weekly_report.py \\
        --credentials service_account.json \\
        --config ga4_properties.json \\
        --project YOUR_GCP_PROJECT_ID

Optional:
    --week 2026-W09       Override week (default: previous week)
    --region us-east5     Vertex AI region (default: us-east5)
    --countries UK,DE     Comma-separated country filter
"""

import argparse
from ecommercetools.intelligence.snapshots import collect_weekly_snapshot
from ecommercetools.intelligence.analyst import analyse_week
from ecommercetools.intelligence.narrator import generate_narrative
from ecommercetools.intelligence.reporter import generate_report


def main():
    parser = argparse.ArgumentParser(description="Run weekly ecommerce intelligence report")
    parser.add_argument("--credentials", required=True, help="Path to GCP service account JSON")
    parser.add_argument("--config", required=True, help="Path to GA4 property config JSON")
    parser.add_argument("--project", required=True, help="GCP project ID for Vertex AI")
    parser.add_argument("--week", default=None, help="Week label e.g. 2026-W09 (default: previous week)")
    parser.add_argument("--region", default="us-east5", help="Vertex AI region")
    parser.add_argument("--countries", default=None, help="Comma-separated country list")
    args = parser.parse_args()

    countries = args.countries.split(",") if args.countries else None

    print("Step 1/4: Collecting GA4 snapshot...")
    week_label = collect_weekly_snapshot(
        credentials_path=args.credentials,
        config_path=args.config,
        week_label=args.week,
        countries=countries,
    )

    print("Step 2/4: Analysing snapshot...")
    analysis = analyse_week(week_label)

    print("Step 3/4: Generating LLM narrative...")
    narrative = generate_narrative(analysis, project_id=args.project, region=args.region)

    print("Step 4/4: Writing report...")
    paths = generate_report(analysis, narrative)

    print(f"\nDone! Report saved:")
    print(f"  Markdown: {paths['md']}")
    print(f"  HTML:     {paths['html']}")


if __name__ == "__main__":
    main()
```

**Step 2: Smoke test (dry run — no credentials needed)**

```bash
python run_weekly_report.py --help
```

Expected: prints usage without errors.

**Step 3: Commit**

```bash
git add run_weekly_report.py
git commit -m "feat: add run_weekly_report.py entry point"
```

---

## Task 11: Entry point — `ask.py`

**Files:**
- Create: `ask.py`

**Step 1: Implement**

```python
#!/usr/bin/env python
"""Ask a natural language question about historical weekly snapshot data.

Usage:
    python ask.py "When did UK revenue last grow 3 weeks in a row?" \\
        --project YOUR_GCP_PROJECT_ID

Optional:
    --region us-east5     Vertex AI region (default: us-east5)
    --weeks 12            How many weeks of history to load (default: 12)
"""

import argparse
from pathlib import Path
from ecommercetools.intelligence.snapshots import REPORTS_DIR, load_snapshot
from ecommercetools.intelligence.narrator import answer_question


def load_all_snapshots(base_dir: Path, max_weeks: int = 12) -> list:
    """Load summary snapshots from all available weeks, newest first."""
    snap_base = base_dir / "snapshots"
    if not snap_base.exists():
        return []
    week_dirs = sorted(snap_base.iterdir(), reverse=True)[:max_weeks]
    records = []
    for d in week_dirs:
        if d.is_dir():
            try:
                df = load_snapshot(d.name, "summary", base_dir=base_dir)
                records.extend(df.to_dict(orient="records"))
            except Exception:
                pass
    return records


def main():
    parser = argparse.ArgumentParser(description="Q&A over historical weekly snapshots")
    parser.add_argument("question", help="Natural language question about your data")
    parser.add_argument("--project", required=True, help="GCP project ID for Vertex AI")
    parser.add_argument("--region", default="us-east5", help="Vertex AI region")
    parser.add_argument("--weeks", type=int, default=12, help="Weeks of history to load")
    args = parser.parse_args()

    print(f"Loading up to {args.weeks} weeks of snapshot history...")
    snapshots = load_all_snapshots(REPORTS_DIR, max_weeks=args.weeks)

    if not snapshots:
        print("No snapshots found. Run run_weekly_report.py first to collect data.")
        return

    print(f"Loaded {len(snapshots)} records across {args.weeks} weeks.\n")
    answer = answer_question(args.question, snapshots, project_id=args.project, region=args.region)
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
```

**Step 2: Smoke test**

```bash
python ask.py --help
```

Expected: prints usage without errors.

**Step 3: Commit**

```bash
git add ask.py
git commit -m "feat: add ask.py Q&A entry point"
```

---

## Task 12: Run all tests and final check

**Step 1: Run full test suite**

```bash
pytest tests/test_intelligence_snapshots.py tests/test_intelligence_analyst.py tests/test_intelligence_reporter.py -v
```

Expected: all PASSED.

**Step 2: Verify imports are clean**

```bash
python -c "from ecommercetools.intelligence import snapshots, analyst, reporter, narrator; print('All imports OK')"
```

Expected: `All imports OK`

**Step 3: Add `reports/` to .gitignore**

Append to `.gitignore`:
```
reports/
```

```bash
git add .gitignore
git commit -m "chore: ignore reports/ directory from git"
```

**Step 4: Final commit**

```bash
git add -A
git status
```

Confirm only expected files are staged, then:

```bash
git commit -m "feat: complete intelligence module implementation"
```
