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
import re
import sys
from pathlib import Path
from ecommercetools.intelligence.snapshots import REPORTS_DIR, load_snapshot
from ecommercetools.intelligence.narrator import answer_question


def load_all_snapshots(base_dir: Path, max_weeks: int = 12) -> list:
    """Load summary snapshots from all available weeks, newest first."""
    snap_base = base_dir / "snapshots"
    if not snap_base.exists():
        return []
    _WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")
    week_dirs = sorted(
        (d for d in snap_base.iterdir() if d.is_dir() and _WEEK_RE.match(d.name)),
        reverse=True,
    )[:max_weeks]
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
        print("No snapshots found. Run run_weekly_report.py first to collect data.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(snapshots)} records across {args.weeks} weeks.\n")
    answer = answer_question(args.question, snapshots, project_id=args.project, region=args.region)
    print(f"Answer:\n{answer}")


if __name__ == "__main__":
    main()
