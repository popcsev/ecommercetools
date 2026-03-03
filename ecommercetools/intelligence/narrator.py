"""Generate LLM narrative using Claude on GCP Vertex AI."""

import json
from typing import Dict, Any


MODEL = "claude-sonnet-4-6"


def _get_client(project_id: str, region: str = "global"):
    """Create AnthropicVertex client using default GCP credentials."""
    import anthropic
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
    if not message.content:
        raise RuntimeError(f"Claude returned empty content. Stop reason: {message.stop_reason}")
    return message.content[0].text


def generate_narrative(analysis: Dict[str, Any], project_id: str, region: str = "global") -> Dict[str, str]:
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

Week: {analysis['week']} ({analysis['date_range']['start']} to {analysis['date_range']['end']})
Current metrics by country:
{json.dumps(analysis['current_summary'], indent=2)}
Week-on-week changes (%):
{json.dumps(analysis['vs_last_week'], indent=2)}
Anomalies:
{json.dumps(analysis['anomalies'], indent=2)}
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


def answer_question(question: str, snapshots_data: list, project_id: str, region: str = "global") -> str:
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
