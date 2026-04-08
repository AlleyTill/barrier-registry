"""Tests for the SALT-inspired belief layer.

Tests verify DATA CONTENT, not just counts (per project test quality standard).
"""

import json
import os
import pytest
from datetime import datetime, timezone, timedelta

from src.database.models import Belief, HealthPolicy, init_db, get_session, Base, get_engine
from src.beliefs.extractor import (
    extract_beliefs,
    _extract_via_regex,
    _infer_category,
    BARRIER_ROW_RE,
    RECORD_ID_RE,
    CONFIDENCE_RE,
)
from src.beliefs.aging import decayed_confidence, is_stale, HALF_LIFE_DAYS
from src.beliefs.manager import (
    store_beliefs,
    get_active_beliefs,
    mark_stale,
    supersede,
    mark_stale_by_record,
    get_belief_count,
)


# --- Test database setup ---

TEST_DB = "data/test_beliefs.db"


@pytest.fixture
def test_db():
    """Create a clean test database with beliefs table."""
    engine = init_db(TEST_DB)
    yield TEST_DB
    # Cleanup
    session = get_session(TEST_DB)
    session.query(Belief).delete()
    session.commit()
    session.close()


# === TestBeliefModel ===


class TestBeliefModel:
    """Test Belief table creation and basic CRUD."""

    def test_belief_table_created(self, test_db):
        """init_db creates the beliefs table alongside existing tables."""
        engine = get_engine(test_db)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert "beliefs" in tables
        assert "health_policies" in tables  # existing table still there

    def test_create_belief(self, test_db):
        """Can create a belief with all required fields."""
        session = get_session(test_db)
        belief = Belief(
            statement_text="Provincial licensure required for cross-border telehealth",
            confidence_score=0.85,
            belief_type="barrier",
            classification="PROHIBITION",
            country="USA",
            country_secondary="CAN",
            category="medical_licensing",
            source_record_ids="[12, 45, 78]",
            query_text="What barriers exist for US-Canada telehealth?",
        )
        session.add(belief)
        session.commit()

        fetched = session.query(Belief).first()
        assert fetched.statement_text == "Provincial licensure required for cross-border telehealth"
        assert fetched.confidence_score == 0.85
        assert fetched.belief_type == "barrier"
        assert fetched.classification == "PROHIBITION"
        assert fetched.country == "USA"
        assert fetched.country_secondary == "CAN"
        assert fetched.status == "active"
        session.close()

    def test_source_record_ids_json(self, test_db):
        """source_record_ids stores and retrieves as valid JSON list."""
        session = get_session(test_db)
        ids = [12, 45, 78, 373]
        belief = Belief(
            statement_text="Test belief",
            confidence_score=0.6,
            belief_type="barrier",
            country="USA",
            source_record_ids=json.dumps(ids),
        )
        session.add(belief)
        session.commit()

        fetched = session.query(Belief).first()
        parsed = json.loads(fetched.source_record_ids)
        assert parsed == [12, 45, 78, 373]
        assert all(isinstance(x, int) for x in parsed)
        session.close()

    def test_default_status_is_active(self, test_db):
        """New beliefs default to 'active' status."""
        session = get_session(test_db)
        belief = Belief(
            statement_text="Test",
            confidence_score=0.5,
            belief_type="barrier",
            country="USA",
            source_record_ids="[]",
        )
        session.add(belief)
        session.commit()
        assert session.query(Belief).first().status == "active"
        session.close()

    def test_bilateral_pair(self, test_db):
        """Beliefs store bilateral country pairs correctly."""
        session = get_session(test_db)
        belief = Belief(
            statement_text="US-MEX prescribing conflict",
            confidence_score=0.7,
            belief_type="barrier",
            classification="CONFLICT",
            country="USA",
            country_secondary="MEX",
            source_record_ids="[100, 200]",
        )
        session.add(belief)
        session.commit()

        fetched = session.query(Belief).first()
        assert fetched.country == "USA"
        assert fetched.country_secondary == "MEX"
        session.close()


# === TestBeliefExtraction ===


# Sample synthesis output mimicking real cross-border analysis
SAMPLE_CROSS_BORDER_OUTPUT = """
## Cross-Border Barrier Analysis: USA — Canada

### 1. Medical Licensing
- **USA:** Interstate Medical Licensure Compact (IMLC) allows multi-state licensing [Record ID: 374]
- **CAN:** Provincial licensing required; CPSO governs Ontario [Record ID: 400]
- **Barrier:** US license not recognized in any Canadian province

### Barrier Classifications
| # | Classification | Description |
|---|---------------|-------------|
| 1 | PROHIBITION | Provincial licensure required, no reciprocity with US |
| 2 | REGULATORY GAP | No CAN-US licensing compact exists |
| 3 | CONFLICT | Dual privacy compliance required (HIPAA + PIPEDA) |
| 4 | PROHIBITION | Cannot prescribe controlled substances without CDSA authorization |
| 5 | ASYMMETRY | No provincial health plan reimbursement for foreign providers |

Records cited: [Record ID: 374] [Record ID: 400] [Record ID: 375] [Record ID: 410] [Record ID: 371]

### Confidence: HIGH
58 records available across both countries.
"""

SAMPLE_SINGLE_COUNTRY = """
## US Federal Rules for Controlled Substances

The Ryan Haight Act requires in-person evaluation. [Record ID: 373]
DEA temporary extension through Dec 31, 2026. [Record ID: 371]

### Confidence: HIGH
"""


class TestBeliefExtraction:
    """Test parsing synthesis output into beliefs."""

    def test_extracts_barriers_from_table(self):
        """Regex extracts all barrier rows from classification table."""
        beliefs = _extract_via_regex(
            SAMPLE_CROSS_BORDER_OUTPUT, "test query", ["USA", "CAN"]
        )
        assert len(beliefs) == 5
        assert beliefs[0]["classification"] == "PROHIBITION"
        assert beliefs[1]["classification"] == "REGULATORY_GAP"
        assert beliefs[2]["classification"] == "CONFLICT"
        assert beliefs[3]["classification"] == "PROHIBITION"
        assert beliefs[4]["classification"] == "ASYMMETRY"

    def test_belief_statements_match_descriptions(self):
        """Extracted statement text matches the barrier description."""
        beliefs = _extract_via_regex(
            SAMPLE_CROSS_BORDER_OUTPUT, "test query", ["USA", "CAN"]
        )
        assert "Provincial licensure" in beliefs[0]["statement_text"]
        assert "licensing compact" in beliefs[1]["statement_text"]
        assert "privacy" in beliefs[2]["statement_text"].lower()

    def test_country_pair_set_correctly(self):
        """Both countries from the query are stored on each belief."""
        beliefs = _extract_via_regex(
            SAMPLE_CROSS_BORDER_OUTPUT, "test query", ["USA", "CAN"]
        )
        for b in beliefs:
            assert b["country"] == "USA"
            assert b["country_secondary"] == "CAN"

    def test_confidence_extracted(self):
        """Confidence level maps to numeric score."""
        beliefs = _extract_via_regex(
            SAMPLE_CROSS_BORDER_OUTPUT, "test query", ["USA", "CAN"]
        )
        # HIGH → 0.85
        assert all(b["confidence_score"] == 0.85 for b in beliefs)

    def test_record_ids_extracted(self):
        """Source record IDs are parsed from [Record ID: N] citations."""
        beliefs = _extract_via_regex(
            SAMPLE_CROSS_BORDER_OUTPUT, "test query", ["USA", "CAN"]
        )
        # At least some beliefs should have record IDs
        all_ids = set()
        for b in beliefs:
            ids = json.loads(b["source_record_ids"])
            all_ids.update(ids)
        # These IDs appear in the sample output
        assert 374 in all_ids or 400 in all_ids or 375 in all_ids

    def test_no_beliefs_from_single_country(self):
        """Single-country output with no barrier table returns empty list."""
        beliefs = _extract_via_regex(
            SAMPLE_SINGLE_COUNTRY, "test query", ["USA"]
        )
        assert beliefs == []

    def test_extract_beliefs_returns_empty_on_empty_input(self):
        """Empty input returns empty list, never raises."""
        assert extract_beliefs("", "test", ["USA"], {}) == []
        assert extract_beliefs(None, "test", ["USA"], {}) == []
        assert extract_beliefs("some text", "test", [], {}) == []

    def test_all_beliefs_have_required_fields(self):
        """Every extracted belief has all fields needed for DB insertion."""
        beliefs = _extract_via_regex(
            SAMPLE_CROSS_BORDER_OUTPUT, "test query", ["USA", "CAN"]
        )
        required = [
            "statement_text", "confidence_score", "belief_type",
            "country", "source_record_ids", "status",
        ]
        for b in beliefs:
            for field in required:
                assert field in b, f"Missing field: {field}"
            assert b["source_record_ids"]  # not empty string
            assert b["status"] == "active"
            assert b["belief_type"] == "barrier"


# === TestCategoryInference ===


class TestCategoryInference:
    """Test category inference from barrier descriptions."""

    def test_licensing_keywords(self):
        assert _infer_category("Provincial licensure required") == "medical_licensing"
        assert _infer_category("Cédula Profesional needed") == "medical_licensing"

    def test_drug_keywords(self):
        assert _infer_category("Cannot prescribe controlled substances") == "drug_regulation"
        assert _infer_category("COFEPRIS approval needed") == "drug_regulation"

    def test_privacy_keywords(self):
        assert _infer_category("HIPAA + PIPEDA dual compliance") == "data_privacy"

    def test_telehealth_keywords(self):
        assert _infer_category("No telehealth framework in Mexico") == "telehealth"

    def test_default_is_cross_border(self):
        assert _infer_category("Unrecognizable barrier text") == "cross_border"


# === TestRegexPatterns ===


class TestRegexPatterns:
    """Test the regex patterns used for extraction."""

    def test_barrier_row_pattern(self):
        """Matches standard barrier table rows."""
        row = "| 1 | PROHIBITION | No license reciprocity |"
        match = BARRIER_ROW_RE.search(row)
        assert match
        assert match.group(2) == "PROHIBITION"
        assert "No license reciprocity" in match.group(3)

    def test_barrier_row_regulatory_gap(self):
        """Matches REGULATORY GAP with space."""
        row = "| 2 | REGULATORY GAP | No bilateral agreement |"
        match = BARRIER_ROW_RE.search(row)
        assert match
        assert "REGULATORY" in match.group(2)

    def test_record_id_pattern(self):
        """Extracts record IDs from citation format."""
        text = "This is relevant [Record ID: 373] and also [Record ID: 400]."
        ids = RECORD_ID_RE.findall(text)
        assert ids == ["373", "400"]

    def test_confidence_pattern(self):
        text = "### Confidence: HIGH\n58 records available."
        match = CONFIDENCE_RE.search(text)
        assert match
        assert match.group(1) == "HIGH"


# === TestBeliefAging ===


class TestBeliefAging:
    """Test confidence decay math."""

    def test_no_decay_at_creation(self):
        """Confidence unchanged at time of creation."""
        now = datetime.now(timezone.utc)
        assert decayed_confidence(0.85, now, now) == 0.85

    def test_half_life_decay(self):
        """Confidence halves after HALF_LIFE_DAYS."""
        created = datetime(2026, 1, 1, tzinfo=timezone.utc)
        later = created + timedelta(days=HALF_LIFE_DAYS)
        result = decayed_confidence(0.85, created, later)
        assert abs(result - 0.425) < 0.001

    def test_double_half_life(self):
        """Confidence quarters after 2x half-life."""
        created = datetime(2026, 1, 1, tzinfo=timezone.utc)
        later = created + timedelta(days=HALF_LIFE_DAYS * 2)
        result = decayed_confidence(0.85, created, later)
        assert abs(result - 0.2125) < 0.001

    def test_stale_after_sufficient_time(self):
        """Belief becomes stale when decayed below threshold."""
        created = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # At ~2.1 half-lives, 0.85 drops below 0.2
        later = created + timedelta(days=400)
        assert is_stale(0.85, created, later)

    def test_not_stale_when_fresh(self):
        """Fresh belief is not stale."""
        now = datetime.now(timezone.utc)
        assert not is_stale(0.85, now, now)

    def test_low_confidence_stales_faster(self):
        """Low initial confidence becomes stale sooner."""
        created = datetime(2026, 1, 1, tzinfo=timezone.utc)
        # 0.3 * 0.5^(150/180) = 0.3 * 0.56 = 0.168 — below 0.2 threshold
        after_150_days = created + timedelta(days=150)
        assert is_stale(0.3, created, after_150_days)
        # 0.85 at 150 days: 0.85 * 0.56 = 0.476 — still well above 0.2
        assert not is_stale(0.85, created, after_150_days)


# === TestBeliefManager ===


class TestBeliefManager:
    """Test belief storage, retrieval, and lifecycle management."""

    def test_store_and_retrieve(self, test_db):
        """Stored beliefs can be retrieved with correct content."""
        beliefs = [
            {
                "statement_text": "No US-CAN licensing compact exists",
                "confidence_score": 0.85,
                "belief_type": "barrier",
                "classification": "REGULATORY_GAP",
                "country": "USA",
                "country_secondary": "CAN",
                "category": "medical_licensing",
                "source_record_ids": json.dumps([374, 400]),
                "query_text": "US-CAN telehealth barriers?",
            }
        ]
        ids = store_beliefs(beliefs, test_db)
        assert len(ids) == 1

        active = get_active_beliefs(country="USA", db_path=test_db)
        assert len(active) == 1
        assert active[0]["statement_text"] == "No US-CAN licensing compact exists"
        assert active[0]["classification"] == "REGULATORY_GAP"
        assert active[0]["source_record_ids"] == [374, 400]

    def test_filter_by_country(self, test_db):
        """get_active_beliefs filters by country correctly."""
        beliefs = [
            {
                "statement_text": "US-CAN barrier",
                "confidence_score": 0.8,
                "belief_type": "barrier",
                "country": "USA",
                "country_secondary": "CAN",
                "source_record_ids": "[1]",
            },
            {
                "statement_text": "US-MEX barrier",
                "confidence_score": 0.7,
                "belief_type": "barrier",
                "country": "USA",
                "country_secondary": "MEX",
                "source_record_ids": "[2]",
            },
        ]
        store_beliefs(beliefs, test_db)

        can_beliefs = get_active_beliefs(country="CAN", db_path=test_db)
        assert len(can_beliefs) == 1
        assert can_beliefs[0]["statement_text"] == "US-CAN barrier"

        mex_beliefs = get_active_beliefs(country="MEX", db_path=test_db)
        assert len(mex_beliefs) == 1
        assert mex_beliefs[0]["statement_text"] == "US-MEX barrier"

    def test_mark_stale(self, test_db):
        """Stale beliefs don't appear in active queries."""
        beliefs = [
            {
                "statement_text": "Will become stale",
                "confidence_score": 0.5,
                "belief_type": "barrier",
                "country": "USA",
                "source_record_ids": "[1]",
            }
        ]
        ids = store_beliefs(beliefs, test_db)
        mark_stale(ids[0], test_db)

        active = get_active_beliefs(country="USA", db_path=test_db)
        assert len(active) == 0

    def test_supersede(self, test_db):
        """Superseded beliefs point to their replacement."""
        old = [
            {
                "statement_text": "Old belief",
                "confidence_score": 0.5,
                "belief_type": "barrier",
                "country": "USA",
                "source_record_ids": "[1]",
            }
        ]
        new = [
            {
                "statement_text": "New belief",
                "confidence_score": 0.8,
                "belief_type": "barrier",
                "country": "USA",
                "source_record_ids": "[1, 2]",
            }
        ]
        old_ids = store_beliefs(old, test_db)
        new_ids = store_beliefs(new, test_db)
        supersede(old_ids[0], new_ids[0], test_db)

        active = get_active_beliefs(country="USA", db_path=test_db)
        assert len(active) == 1
        assert active[0]["statement_text"] == "New belief"

    def test_mark_stale_by_record(self, test_db):
        """Beliefs citing an updated record get marked stale."""
        beliefs = [
            {
                "statement_text": "Cites record 373",
                "confidence_score": 0.85,
                "belief_type": "barrier",
                "country": "USA",
                "category": "drug_regulation",
                "source_record_ids": json.dumps([373, 374]),
            },
            {
                "statement_text": "Does not cite 373",
                "confidence_score": 0.7,
                "belief_type": "barrier",
                "country": "USA",
                "category": "data_privacy",
                "source_record_ids": json.dumps([400, 410]),
            },
        ]
        store_beliefs(beliefs, test_db)

        staled = mark_stale_by_record(373, test_db)
        assert len(staled) == 1

        active = get_active_beliefs(country="USA", db_path=test_db)
        assert len(active) == 1
        assert active[0]["statement_text"] == "Does not cite 373"

    def test_store_empty_list(self, test_db):
        """Storing empty list returns empty, no errors."""
        ids = store_beliefs([], test_db)
        assert ids == []

    def test_belief_count(self, test_db):
        """get_belief_count returns counts by status."""
        categories = ["medical_licensing", "data_privacy", "drug_regulation"]
        beliefs = [
            {
                "statement_text": f"Belief {i}",
                "confidence_score": 0.5,
                "belief_type": "barrier",
                "country": "USA",
                "category": categories[i],
                "source_record_ids": "[1]",
            }
            for i in range(3)
        ]
        ids = store_beliefs(beliefs, test_db)
        mark_stale(ids[0], test_db)

        counts = get_belief_count(test_db)
        assert counts.get("active", 0) == 2
        assert counts.get("stale", 0) == 1

    def test_auto_supersede_duplicate(self, test_db):
        """Storing a belief with same country+category+classification supersedes existing."""
        first = [
            {
                "statement_text": "Original finding",
                "confidence_score": 0.6,
                "belief_type": "barrier",
                "classification": "PROHIBITION",
                "country": "USA",
                "country_secondary": "CAN",
                "category": "medical_licensing",
                "source_record_ids": "[374]",
            }
        ]
        second = [
            {
                "statement_text": "Updated finding with more detail",
                "confidence_score": 0.85,
                "belief_type": "barrier",
                "classification": "PROHIBITION",
                "country": "USA",
                "country_secondary": "CAN",
                "category": "medical_licensing",
                "source_record_ids": "[374, 400]",
            }
        ]
        store_beliefs(first, test_db)
        store_beliefs(second, test_db)

        active = get_active_beliefs(country="USA", db_path=test_db)
        assert len(active) == 1
        assert active[0]["statement_text"] == "Updated finding with more detail"
        assert active[0]["confidence_score"] == 0.85
