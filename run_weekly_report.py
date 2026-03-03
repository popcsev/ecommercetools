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

    countries = [c.strip() for c in args.countries.split(",")] if args.countries else None

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
