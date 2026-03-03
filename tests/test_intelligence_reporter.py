"""Tests for ecommercetools.intelligence.reporter"""
import tempfile
from pathlib import Path
from ecommercetools.intelligence.reporter import build_anomalies_section, build_metrics_table, generate_report


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


def test_build_anomalies_section_with_anomalies():
    analysis = _sample_analysis()
    analysis["anomalies"] = [
        {"country": "UK", "metric": "revenue", "direction": "down", "pct": -18.2}
    ]
    result = build_anomalies_section(analysis)
    assert "UK" in result
    assert "-18.2%" in result
    assert "🔴" in result
