"""Extract belief statements from synthesis output.

Strategy: regex-first, Haiku fallback (temporary — plan to drop regex post-AWE).
Triple failure: regex fails → Haiku fails → skip silently, log, return empty list.
"""

import json
import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Counters for observability — log how often fallback triggers
_extraction_stats = {"regex_success": 0, "haiku_fallback": 0, "total_failure": 0}

# Confidence mapping from synthesis output
CONFIDENCE_MAP = {
    "high": 0.85,
    "moderate": 0.6,
    "low": 0.3,
}

# Barrier table row pattern: | # | Classification | Description |
# Matches rows like: | 1 | PROHIBITION | No Mexican license pathway... |
BARRIER_ROW_RE = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(PROHIBITION|REGULATORY[_ ]GAP|CONFLICT|ASYMMETRY)\s*\|\s*(.+?)\s*\|",
    re.MULTILINE | re.IGNORECASE,
)

# Record ID citations: [Record ID: 123]
RECORD_ID_RE = re.compile(r"\[Record ID:\s*(\d+)\]")

# Confidence level from synthesis output
CONFIDENCE_RE = re.compile(
    r"###?\s*Confidence:\s*(HIGH|MODERATE|LOW)", re.IGNORECASE
)


def extract_beliefs(
    answer: str,
    question: str,
    countries: list[str],
    execution_results: dict,
) -> list[dict]:
    """Parse synthesis answer into belief dicts ready for DB insertion.

    Returns list of dicts with keys matching Belief model fields.
    Returns empty list on failure (never raises).
    """
    if not answer or not countries:
        return []

    beliefs = _extract_via_regex(answer, question, countries)
    if beliefs:
        _extraction_stats["regex_success"] += 1
        _log_stats()
        return beliefs

    # Regex found nothing — try Haiku fallback
    logger.info("Regex extraction found no beliefs, trying Haiku fallback")
    try:
        beliefs = _extract_via_haiku(answer, question, countries)
        if beliefs:
            _extraction_stats["haiku_fallback"] += 1
            _log_stats()
            return beliefs
    except Exception as e:
        logger.warning(f"Haiku fallback failed: {e}")

    # Triple failure — skip silently
    _extraction_stats["total_failure"] += 1
    _log_stats()
    logger.warning("Belief extraction failed (regex + Haiku). Skipping.")
    return []


def _extract_via_regex(
    answer: str, question: str, countries: list[str]
) -> list[dict]:
    """Extract beliefs by parsing the barrier classification table."""
    rows = BARRIER_ROW_RE.findall(answer)
    if not rows:
        return []

    # Extract global confidence
    conf_match = CONFIDENCE_RE.search(answer)
    base_confidence = CONFIDENCE_MAP.get(
        conf_match.group(1).lower(), 0.6
    ) if conf_match else 0.6

    # Extract all record IDs cited in the full answer
    all_record_ids = [int(x) for x in RECORD_ID_RE.findall(answer)]

    # Determine country pair
    country = countries[0] if countries else "USA"
    country_secondary = countries[1] if len(countries) > 1 else None

    now = datetime.now(timezone.utc)
    beliefs = []

    for _num, classification, description in rows:
        # Normalize classification
        classification = classification.upper().replace(" ", "_")

        # Try to find record IDs near this barrier description in the text
        # Search in a window around the description text
        local_ids = _find_nearby_record_ids(answer, description)
        source_ids = local_ids if local_ids else all_record_ids[:5]

        beliefs.append({
            "statement_text": description.strip(),
            "confidence_score": base_confidence,
            "belief_type": "barrier",
            "classification": classification,
            "country": country,
            "country_secondary": country_secondary,
            "category": _infer_category(description),
            "agent_id": "policy_researcher",
            "source_record_ids": json.dumps(source_ids),
            "query_text": question,
            "status": "active",
            "created_at": now,
            "last_validated": now,
        })

    return beliefs


def _find_nearby_record_ids(full_text: str, description: str) -> list[int]:
    """Find Record IDs cited near a barrier description in the synthesis text."""
    # Find the description in the text
    desc_lower = description.lower().strip()
    text_lower = full_text.lower()
    pos = text_lower.find(desc_lower[:40])  # match first 40 chars
    if pos == -1:
        return []

    # Search in a 500-char window around the match
    start = max(0, pos - 200)
    end = min(len(full_text), pos + len(description) + 300)
    window = full_text[start:end]

    return [int(x) for x in RECORD_ID_RE.findall(window)]


def _infer_category(description: str) -> str:
    """Infer policy category from barrier description text."""
    desc = description.lower()
    if any(w in desc for w in ["licens", "credential", "cédula", "registration"]):
        return "medical_licensing"
    if any(w in desc for w in ["prescri", "drug", "substance", "pharmac", "dea", "cofepris"]):
        return "drug_regulation"
    if any(w in desc for w in ["privacy", "hipaa", "pipeda", "lfpdppp", "gdpr", "data"]):
        return "data_privacy"
    if any(w in desc for w in ["telehealth", "telemedicine", "virtual care", "remote"]):
        return "telehealth"
    if any(w in desc for w in ["reimburse", "billing", "insurance", "payment"]):
        return "insurance"
    if any(w in desc for w in ["liability", "malpractice", "negligence"]):
        return "medical_liability"
    if any(w in desc for w in ["trade", "usmca", "bilateral", "agreement"]):
        return "cross_border"
    return "cross_border"  # default for barrier beliefs


def _extract_via_haiku(
    answer: str, question: str, countries: list[str]
) -> list[dict]:
    """Use Haiku to extract beliefs as structured JSON. Fallback path."""
    import httpx
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY for Haiku fallback")
        return []

    prompt = f"""Extract barrier findings from this policy analysis as a JSON array.
Each barrier should have: statement_text, classification (PROHIBITION/REGULATORY_GAP/CONFLICT/ASYMMETRY), category, and source_record_ids (list of integers from [Record ID: N] citations).

Analysis text:
{answer[:4000]}

Return ONLY valid JSON array, no other text."""

    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    resp.raise_for_status()

    content = resp.json()["content"][0]["text"]
    # Extract JSON from response
    json_match = re.search(r"\[.*\]", content, re.DOTALL)
    if not json_match:
        return []

    raw_beliefs = json.loads(json_match.group())
    now = datetime.now(timezone.utc)
    country = countries[0] if countries else "USA"
    country_secondary = countries[1] if len(countries) > 1 else None

    beliefs = []
    for b in raw_beliefs:
        source_ids = b.get("source_record_ids", [])
        if not isinstance(source_ids, list):
            source_ids = []

        beliefs.append({
            "statement_text": b.get("statement_text", ""),
            "confidence_score": 0.6,
            "belief_type": "barrier",
            "classification": b.get("classification", "REGULATORY_GAP"),
            "country": country,
            "country_secondary": country_secondary,
            "category": b.get("category", "cross_border"),
            "agent_id": "policy_researcher",
            "source_record_ids": json.dumps(source_ids),
            "query_text": question,
            "status": "active",
            "created_at": now,
            "last_validated": now,
        })

    return beliefs


def _log_stats():
    """Log extraction method frequency for drift detection."""
    total = sum(_extraction_stats.values())
    if total > 0 and total % 10 == 0:
        logger.info(
            f"Belief extraction stats: regex={_extraction_stats['regex_success']}, "
            f"haiku={_extraction_stats['haiku_fallback']}, "
            f"failed={_extraction_stats['total_failure']} "
            f"(out of {total})"
        )


def get_extraction_stats() -> dict:
    """Return extraction stats for monitoring."""
    return dict(_extraction_stats)
