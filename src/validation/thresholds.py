"""
TASK-002: Insufficient Data Thresholds

These thresholds define when an agent should say "I don't know" vs. answer,
and when to add caveats to answers. Used by all agents.
"""

from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class AnswerConfidence:
    """Result of evaluating whether we have enough data to answer."""
    level: str  # "sufficient", "thin", "insufficient", "no_data"
    record_count: int
    caveats: list[str]
    can_answer: bool


# --- THRESHOLDS ---

# Records found
NO_DATA_THRESHOLD = 0          # Zero records = "I don't know"
THIN_DATA_THRESHOLD = 2        # 1-2 records = answer with "coverage may be incomplete" caveat
SUFFICIENT_THRESHOLD = 3       # 3+ records = answer normally

# Staleness (years since last_updated)
STALE_WARNING_YEARS = 2        # Records older than 2 years get a staleness warning
STALE_EXCLUDE_YEARS = 5        # Records older than 5 years are excluded from answers (but noted)

# Verification status
TRUSTED_STATUSES = ["machine_verified", "user_verified"]
UNTRUSTED_STATUSES = ["unverified"]
EXCLUDED_STATUSES = ["failed"]

# Translation
NEEDS_TRANSLATION_WARNING = True  # Always flag non-English source records


def evaluate_answer_confidence(
    records: list,
    query_topic: str = "",
) -> AnswerConfidence:
    """
    Evaluate whether we have enough data to answer a query.

    Args:
        records: List of HealthPolicy records matching the query
        query_topic: What was asked (for caveat messages)

    Returns:
        AnswerConfidence with level, count, caveats, and can_answer flag
    """
    caveats = []

    # Filter out excluded records
    active_records = [
        r for r in records
        if getattr(r, "verification_status", "unverified") not in EXCLUDED_STATUSES
    ]

    # Check for stale records
    now = datetime.now(timezone.utc)
    stale_records = []
    very_stale_records = []

    for r in active_records:
        last_updated = getattr(r, "last_updated", None)
        if last_updated:
            try:
                # Handle multiple date formats in our data
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y"]:
                    try:
                        dt = datetime.strptime(str(last_updated).strip(), fmt)
                        age_years = (now.year - dt.year)
                        if age_years >= STALE_EXCLUDE_YEARS:
                            very_stale_records.append(r)
                        elif age_years >= STALE_WARNING_YEARS:
                            stale_records.append(r)
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

    # Remove very stale from active
    active_ids = {id(r) for r in active_records} - {id(r) for r in very_stale_records}
    active_records = [r for r in active_records if id(r) in active_ids]

    # Check unverified records
    unverified = [
        r for r in active_records
        if getattr(r, "verification_status", "unverified") in UNTRUSTED_STATUSES
    ]

    # Check non-English records
    non_english = [
        r for r in active_records
        if getattr(r, "original_language", "en") != "en"
    ]

    # Build caveats
    if stale_records:
        caveats.append(
            f"{len(stale_records)} record(s) are {STALE_WARNING_YEARS}+ years old — verify they are still current."
        )

    if very_stale_records:
        caveats.append(
            f"{len(very_stale_records)} record(s) excluded from answer (older than {STALE_EXCLUDE_YEARS} years). "
            f"Titles: {', '.join(r.title[:50] for r in very_stale_records)}"
        )

    if unverified:
        caveats.append(
            f"{len(unverified)} record(s) have not been independently verified."
        )

    if non_english and NEEDS_TRANSLATION_WARNING:
        caveats.append(
            f"{len(non_english)} record(s) are from non-English sources. "
            f"Summaries are machine-translated — verify with original text."
        )

    # Determine confidence level
    count = len(active_records)

    if count == NO_DATA_THRESHOLD:
        return AnswerConfidence(
            level="no_data",
            record_count=0,
            caveats=caveats + [f"No records found matching '{query_topic}'. This may be a gap in our database, not evidence that no policy exists."],
            can_answer=False,
        )
    elif count < SUFFICIENT_THRESHOLD:
        caveats.append(
            f"Only {count} record(s) found on this topic — coverage may be incomplete."
        )
        return AnswerConfidence(
            level="thin",
            record_count=count,
            caveats=caveats,
            can_answer=True,  # Can answer, but with caveats
        )
    else:
        return AnswerConfidence(
            level="sufficient",
            record_count=count,
            caveats=caveats,
            can_answer=True,
        )
