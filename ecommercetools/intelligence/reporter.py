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
