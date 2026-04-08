"""Belief confidence decay over time.

Half-life: 180 days. A belief at 0.85 decays to 0.425 after 6 months
without revalidation. Policy changes are quarterly/annual, so 6 months
is a reasonable point where an unvalidated belief should carry ~half weight.
"""

from datetime import datetime, timezone


HALF_LIFE_DAYS = 180
STALE_THRESHOLD = 0.2  # below this, belief should be marked stale


def decayed_confidence(
    original_confidence: float,
    created_at: datetime,
    now: datetime = None,
) -> float:
    """Apply time-based exponential decay to confidence score."""
    if now is None:
        now = datetime.now(timezone.utc)

    # Handle timezone-naive datetimes
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    days_elapsed = (now - created_at).total_seconds() / 86400
    if days_elapsed <= 0:
        return original_confidence

    return original_confidence * (0.5 ** (days_elapsed / HALF_LIFE_DAYS))


def is_stale(
    original_confidence: float,
    created_at: datetime,
    now: datetime = None,
) -> bool:
    """Check if a belief's decayed confidence has dropped below stale threshold."""
    return decayed_confidence(original_confidence, created_at, now) < STALE_THRESHOLD
