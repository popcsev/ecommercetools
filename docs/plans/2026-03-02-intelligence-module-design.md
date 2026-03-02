# Intelligence Module Design
**Date:** 2026-03-02
**Status:** Approved

## Overview

A new `ecommercetools/intelligence/` module that adds LLM-powered weekly reporting with persistent snapshot storage. Each Monday, a script pulls GA4 data, saves structured snapshots locally, runs trend analysis, and uses Claude (via GCP Vertex AI) to generate a narrative report in both Markdown and HTML. Over time, the growing snapshot history enables trend detection and natural language Q&A over past performance.

## Goals

- Automated weekly performance snapshots with persistent storage
- LLM-generated narrative summaries (executive summary + trend commentary)
- Anomaly and winner/loser detection across countries and channels
- Natural language Q&A over historical snapshots
- Clean extension point for transactional data (not yet available)

## Data Sources

- **Now:** GA4 (multi-country, using existing `ecommercetools/analytics/` module)
- **Later:** Transactional data (CSV or DB — placeholder hook in place from day one)

## LLM

Claude on GCP Vertex AI (Model Garden), authenticated via existing GCP service account credentials. Uses the `anthropic` SDK with `AnthropicVertex` client.

---

## Architecture

```
ecommercetools/intelligence/
├── __init__.py
├── snapshots.py      # Pulls GA4 data, saves weekly Parquet files
├── analyst.py        # Compares snapshots, detects trends & anomalies
├── narrator.py       # Calls Claude on Vertex AI, generates narrative
└── reporter.py       # Assembles Markdown + HTML output
```

### Entry Points

```bash
# Run the weekly report
python run_weekly_report.py --config ga4_properties.json --credentials service_account.json

# Ask a question about historical data
python ask.py "When did UK revenue last grow 3 weeks in a row?"
```

---

## Storage Layout

```
reports/
├── snapshots/
│   ├── 2026-W08/
│   │   ├── summary.parquet          # One row per country, aggregated
│   │   ├── traffic_detail.parquet   # Daily traffic breakdown
│   │   └── acquisition_detail.parquet  # Source/medium breakdown
│   └── 2026-W09/
│       └── ...
└── weekly/
    └── 2026-W09/
        ├── report.md
        └── report.html
```

---

## Component Details

### 1. `snapshots.py` — Data Collector

Pulls GA4 data for the previous week (Mon–Sun) and saves to disk.

**Behaviour:**
- Determines the previous week's date range automatically
- Queries GA4 for two datasets per country:
  - **Summary** — single aggregated row per country: sessions, users, new users, revenue, transactions, conversion rate, avg order value, bounce rate
  - **Detail** — daily traffic + acquisition by source/medium
- Saves as Parquet under `reports/snapshots/YYYY-Www/`
- Idempotent — skips if that week's snapshot already exists

**Summary schema (one row per country per week):**
```
week | country | sessions | users | new_users | revenue |
transactions | conversion_rate | avg_order_value | bounce_rate
```

**Transactional data hook:**
```python
def add_transactions(week: str, df: pd.DataFrame) -> pd.DataFrame:
    """Merge external transaction data into the week's summary.
    Implement when transactional data is available."""
    pass
```

---

### 2. `analyst.py` — Trend Analyst

Reads snapshots and computes structured comparisons for the LLM. Never calls the LLM directly — keeps the layer testable independently.

**Produces:**
- **Week-on-week diff** — absolute and % change vs previous week for every metric
- **4-week rolling average** — flags when current week is significantly above/below trend
- **Anomaly flags** — metrics with >15% swing flagged as `up`, `down`, or `stable`
- **Winner/loser summary** — top 3 improving and declining countries/channels

**Output structure:**
```python
{
  "week": "2026-W09",
  "date_range": {"start": "2026-02-23", "end": "2026-03-01"},
  "vs_last_week": {
    "UK": {"sessions": +12.3, "revenue": -4.1, ...},
    ...
  },
  "vs_4w_avg": {
    "UK": {"sessions": +2.1, ...},
    ...
  },
  "anomalies": [
    {"country": "UK", "metric": "revenue", "direction": "down", "pct": -18.2}
  ],
  "winners": [...],
  "losers": [...]
}
```

---

### 3. `narrator.py` — LLM Narrator

Calls Claude on Vertex AI with structured analyst output to generate written narrative.

**Authentication:**
```python
import anthropic
from google.auth import default

def get_vertex_client(project_id: str, region: str = "us-east5"):
    credentials, _ = default()
    return anthropic.AnthropicVertex(
        project_id=project_id,
        region=region,
        credentials=credentials
    )
```

**Three prompts:**

1. **Weekly narrative** — executive summary of what moved this week and what to watch
2. **Trend commentary** — fed last 8 weeks of summaries, identifies patterns and sustained shifts
3. **Q&A** — loads relevant snapshot Parquets into context, answers open-ended questions

---

### 4. `reporter.py` — Report Assembler

Combines metrics tables + LLM narrative into final output files.

**Markdown structure:**
```
# Weekly Performance Report — W09 2026

## Executive Summary
[LLM narrative]

## Key Metrics by Country
[Table: sessions, revenue, transactions, conv. rate, WoW delta]

## Anomalies & Watch Items
[Flagged metrics with direction indicators]

## Trend Commentary
[LLM narrative over last 8 weeks]

## Notes
[Data source, generation date, transactional data status]
```

**HTML** generated from Markdown — no extra templating dependency.

---

## Future Roadmap

See `ROADMAP.md` for tracked items. Key planned extensions:

- [ ] Move weekly trigger from manual script → GCP Cloud Scheduler + Cloud Run
- [ ] Connect transactional data source to snapshot collector
- [ ] Add Google Search Console as a data source
- [ ] Email/Slack delivery of the HTML report

---

## Dependencies

```
anthropic[vertex]
google-auth
pandas
pyarrow          # Parquet read/write
markdown         # Markdown → HTML conversion
```
