"""Belief CRUD, staleness management, and supersession logic."""

import json
import logging
from datetime import datetime, timezone

from src.database.models import Belief, get_session

logger = logging.getLogger(__name__)


def store_beliefs(beliefs: list[dict], db_path: str = "data/policies.db") -> list[int]:
    """Store belief dicts in the database. Returns list of new belief IDs."""
    if not beliefs:
        return []

    session = get_session(db_path)
    new_ids = []
    try:
        for b in beliefs:
            # Check for existing belief to supersede
            existing = _find_duplicate(session, b)
            if existing:
                existing.status = "superseded"
                existing.superseded_by = None  # will be set after insert

            belief = Belief(
                statement_text=b["statement_text"],
                confidence_score=b["confidence_score"],
                belief_type=b["belief_type"],
                classification=b.get("classification"),
                country=b["country"],
                country_secondary=b.get("country_secondary"),
                category=b.get("category"),
                agent_id=b.get("agent_id", "policy_researcher"),
                source_record_ids=b["source_record_ids"],
                query_text=b.get("query_text"),
                status="active",
                created_at=b.get("created_at", datetime.now(timezone.utc)),
                last_validated=b.get("last_validated", datetime.now(timezone.utc)),
            )
            session.add(belief)
            session.flush()  # get the ID

            if existing:
                existing.superseded_by = belief.id

            new_ids.append(belief.id)

        session.commit()
        logger.info(f"Stored {len(new_ids)} beliefs")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to store beliefs: {e}")
        raise
    finally:
        session.close()

    return new_ids


def get_active_beliefs(
    country: str = None,
    country_secondary: str = None,
    category: str = None,
    db_path: str = "data/policies.db",
) -> list[dict]:
    """Retrieve active beliefs, optionally filtered by country/category."""
    session = get_session(db_path)
    try:
        query = session.query(Belief).filter(Belief.status == "active")

        if country:
            query = query.filter(
                (Belief.country == country) | (Belief.country_secondary == country)
            )
        if country_secondary:
            query = query.filter(
                (Belief.country == country_secondary)
                | (Belief.country_secondary == country_secondary)
            )
        if category:
            query = query.filter(Belief.category == category)

        beliefs = query.order_by(Belief.confidence_score.desc()).all()

        return [
            {
                "id": b.id,
                "statement_text": b.statement_text,
                "confidence_score": b.confidence_score,
                "belief_type": b.belief_type,
                "classification": b.classification,
                "country": b.country,
                "country_secondary": b.country_secondary,
                "category": b.category,
                "source_record_ids": json.loads(b.source_record_ids),
                "query_text": b.query_text,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "last_validated": b.last_validated.isoformat() if b.last_validated else None,
            }
            for b in beliefs
        ]
    finally:
        session.close()


def mark_stale(belief_id: int, db_path: str = "data/policies.db"):
    """Mark a belief as stale."""
    session = get_session(db_path)
    try:
        belief = session.get(Belief, belief_id)
        if belief:
            belief.status = "stale"
            session.commit()
            logger.info(f"Belief {belief_id} marked stale")
    finally:
        session.close()


def supersede(old_id: int, new_id: int, db_path: str = "data/policies.db"):
    """Mark old belief as superseded by new belief."""
    session = get_session(db_path)
    try:
        old = session.get(Belief, old_id)
        if old:
            old.status = "superseded"
            old.superseded_by = new_id
            session.commit()
            logger.info(f"Belief {old_id} superseded by {new_id}")
    finally:
        session.close()


def mark_stale_by_record(
    record_id: int, db_path: str = "data/policies.db"
) -> list[int]:
    """Mark all beliefs that cite a given record ID as stale.
    Used when a PolicyUpdate modifies or removes a source record."""
    session = get_session(db_path)
    staled = []
    try:
        active = session.query(Belief).filter(Belief.status == "active").all()
        for belief in active:
            source_ids = json.loads(belief.source_record_ids)
            if record_id in source_ids:
                belief.status = "stale"
                staled.append(belief.id)
        if staled:
            session.commit()
            logger.info(
                f"Marked {len(staled)} beliefs stale due to record {record_id} update"
            )
    finally:
        session.close()
    return staled


def prune_beliefs(
    max_per_category: int = 50, db_path: str = "data/policies.db"
) -> int:
    """Remove lowest-confidence beliefs when count exceeds threshold.
    SALT-inspired memory bound."""
    session = get_session(db_path)
    pruned = 0
    try:
        # Get categories with too many active beliefs
        from sqlalchemy import func

        counts = (
            session.query(Belief.category, func.count(Belief.id))
            .filter(Belief.status == "active")
            .group_by(Belief.category)
            .having(func.count(Belief.id) > max_per_category)
            .all()
        )

        for category, count in counts:
            excess = count - max_per_category
            to_prune = (
                session.query(Belief)
                .filter(Belief.status == "active", Belief.category == category)
                .order_by(Belief.confidence_score.asc())
                .limit(excess)
                .all()
            )
            for belief in to_prune:
                session.delete(belief)
                pruned += 1

        if pruned:
            session.commit()
            logger.info(f"Pruned {pruned} low-confidence beliefs")
    finally:
        session.close()
    return pruned


def get_belief_count(db_path: str = "data/policies.db") -> dict:
    """Return belief counts by status for monitoring."""
    session = get_session(db_path)
    try:
        from sqlalchemy import func

        counts = (
            session.query(Belief.status, func.count(Belief.id))
            .group_by(Belief.status)
            .all()
        )
        return {status: count for status, count in counts}
    finally:
        session.close()


def _find_duplicate(session, belief_dict: dict):
    """Find an existing active belief that the new one would supersede.
    Match: same country pair + category + classification."""
    return (
        session.query(Belief)
        .filter(
            Belief.status == "active",
            Belief.country == belief_dict["country"],
            Belief.country_secondary == belief_dict.get("country_secondary"),
            Belief.category == belief_dict.get("category"),
            Belief.classification == belief_dict.get("classification"),
        )
        .first()
    )
