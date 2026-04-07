"""
TASK-003: TDD Tests for Agent Quality

These tests define what the agent MUST do BEFORE we build it.
The agent passes when all these tests pass.

Based on Human Quality Parameters:
1. Grounding — every claim cites a record ID
2. Coverage — finds relevant records, flags when thin
3. Faithfulness — doesn't exaggerate or reinterpret
4. Staleness — warns about old records
5. Refusal — says "I don't know" properly when data is missing
6. Translation — flags non-English sources
"""

import pytest
import re
from src.database.models import HealthPolicy, WHOIndicator, get_session, init_db
from src.validation.thresholds import evaluate_answer_confidence


# --- FIXTURES ---

@pytest.fixture
def session():
    init_db()
    s = get_session()
    yield s
    s.close()


# --- THRESHOLD TESTS ---

class TestThresholds:
    """Test that the threshold system correctly classifies data availability."""

    def test_no_data_returns_cannot_answer(self, session):
        """Zero records = agent must refuse to answer."""
        records = session.query(HealthPolicy).filter(
            HealthPolicy.country == "JPN"  # Japan not in our DB
        ).all()
        result = evaluate_answer_confidence(records, "Japan healthcare")
        assert result.level == "no_data"
        assert result.can_answer is False
        assert result.record_count == 0

    def test_thin_data_returns_caveat(self, session):
        """1-2 records = agent can answer but must caveat."""
        # Find a topic with very few records
        records = session.query(HealthPolicy).filter(
            HealthPolicy.title.like("%dental%")
        ).all()
        result = evaluate_answer_confidence(records, "dental policy")
        # Should be either no_data or thin — both are correct for sparse topics
        assert result.level in ("no_data", "thin")
        if result.level == "thin":
            assert result.can_answer is True
            assert any("coverage may be incomplete" in c for c in result.caveats)

    def test_sufficient_data_returns_can_answer(self, session):
        """3+ records = agent can answer normally."""
        records = session.query(HealthPolicy).filter(
            HealthPolicy.country == "USA",
            HealthPolicy.category == "telehealth",
        ).all()
        result = evaluate_answer_confidence(records, "US telehealth")
        assert result.level == "sufficient"
        assert result.can_answer is True
        assert result.record_count >= 3

    def test_unverified_records_get_caveat(self, session):
        """Unverified records should trigger a caveat."""
        records = session.query(HealthPolicy).filter(
            HealthPolicy.country == "USA",
            HealthPolicy.category == "telehealth",
        ).all()
        result = evaluate_answer_confidence(records, "US telehealth")
        # All our records are currently unverified
        assert any("not been independently verified" in c for c in result.caveats)

    def test_non_english_records_get_translation_caveat(self, session):
        """Non-English source records should trigger translation warning."""
        records = session.query(HealthPolicy).filter(
            HealthPolicy.country == "MEX",
        ).all()
        result = evaluate_answer_confidence(records, "Mexico healthcare")
        assert any("machine-translated" in c for c in result.caveats)

    def test_failed_verification_records_excluded(self, session):
        """Records with verification_status='failed' should be excluded."""
        # Get a record and mark it failed
        record = session.query(HealthPolicy).first()
        original_status = record.verification_status
        record.verification_status = "failed"
        session.flush()

        records = [record]
        result = evaluate_answer_confidence(records, "test")
        assert result.record_count == 0
        assert result.level == "no_data"

        # Restore
        record.verification_status = original_status
        session.flush()


# --- DATABASE INTEGRITY TESTS ---

class TestDatabaseIntegrity:
    """Test that the database has the data we expect."""

    def test_us_has_policy_records(self, session):
        count = session.query(HealthPolicy).filter_by(country="USA").count()
        assert count > 0, "US should have policy records"

    def test_canada_has_policy_records(self, session):
        count = session.query(HealthPolicy).filter_by(country="CAN").count()
        assert count > 0, "Canada should have policy records"

    def test_mexico_has_policy_records(self, session):
        count = session.query(HealthPolicy).filter_by(country="MEX").count()
        assert count > 0, "Mexico should have policy records"

    def test_all_policies_have_source_url(self, session):
        """Every policy record must have a source URL."""
        no_url = session.query(HealthPolicy).filter(
            (HealthPolicy.source_url == None) | (HealthPolicy.source_url == "")
        ).count()
        assert no_url == 0, f"{no_url} records have no source URL"

    def test_all_policies_have_title(self, session):
        """Every policy record must have a title."""
        no_title = session.query(HealthPolicy).filter(
            (HealthPolicy.title == None) | (HealthPolicy.title == "")
        ).count()
        assert no_title == 0, f"{no_title} records have no title"

    def test_all_policies_have_country(self, session):
        """Every policy record must have a valid country code."""
        valid_countries = {"USA", "CAN", "MEX", "GBR"}
        invalid = session.query(HealthPolicy).filter(
            ~HealthPolicy.country.in_(valid_countries)
        ).count()
        assert invalid == 0, f"{invalid} records have invalid country codes"

    def test_who_data_exists_for_all_countries(self, session):
        """WHO indicator data should exist for US, Canada, and Mexico."""
        for country in ["USA", "CAN", "MEX"]:
            count = session.query(WHOIndicator).filter_by(country=country).count()
            assert count > 0, f"No WHO data for {country}"


# --- AGENT OUTPUT FORMAT TESTS ---
# These test the FORMAT the agent must output in.
# They will be applied to actual agent output once built.

class TestAgentOutputFormat:
    """Tests that define the required format of agent responses.
    These are templates — actual agent tests will inherit from these.
    """

    def _check_record_ids_cited(self, answer_text: str) -> list:
        """Extract all [Record ID: X] citations from an answer."""
        # Matches: [Record ID: 362] or [Record ID: 356, 357] or [Record ID: 362, language: Spanish...]
        pattern = r'\[Record ID:\s*([\d,\s]+)'
        matches = re.findall(pattern, answer_text)
        ids = []
        for match in matches:
            # Extract just the numbers before any non-digit-comma content
            nums = re.findall(r'\d+', match)
            ids.extend([int(n) for n in nums])
        return ids

    def _check_inferences_labeled(self, answer_text: str) -> bool:
        """Check that inferences are explicitly labeled."""
        has_inference = "inference" in answer_text.lower() or "infer" in answer_text.lower()
        # If the answer makes claims beyond record data, it should label them
        return True  # Will be validated manually until agent exists

    def _check_gaps_listed(self, answer_text: str) -> bool:
        """Check that the answer lists what it doesn't know."""
        return "does not have" in answer_text.lower() or "gap" in answer_text.lower() or "i don't know" in answer_text.lower()

    def test_baseline_answer_has_record_ids(self):
        """The human baseline must cite record IDs."""
        with open("tests/human_baseline_001.md", "r") as f:
            answer = f.read()
        ids = self._check_record_ids_cited(answer)
        assert len(ids) > 0, "Baseline answer must cite at least one record ID"
        assert len(ids) >= 10, f"Baseline cites {len(ids)} records, expected at least 10"

    def test_baseline_answer_labels_inferences(self):
        """The human baseline must label all inferences."""
        with open("tests/human_baseline_001.md", "r") as f:
            answer = f.read()
        # Count "Inference" labels
        inference_count = answer.lower().count("*inference")
        assert inference_count >= 5, f"Found {inference_count} labeled inferences, expected at least 5"

    def test_baseline_answer_lists_gaps(self):
        """The human baseline must list what it doesn't know."""
        with open("tests/human_baseline_001.md", "r") as f:
            answer = f.read()
        assert self._check_gaps_listed(answer), "Baseline must list data gaps"

    def test_baseline_answer_has_confidence_level(self):
        """The human baseline must state a confidence level."""
        with open("tests/human_baseline_001.md", "r") as f:
            answer = f.read()
        assert "confidence:" in answer.lower(), "Baseline must state confidence level"

    def test_baseline_answer_flags_translations(self):
        """The human baseline must flag non-English sources."""
        with open("tests/human_baseline_001.md", "r") as f:
            answer = f.read()
        assert "spanish" in answer.lower() or "machine-translated" in answer.lower(), \
            "Baseline must flag non-English sources"


class TestBaseline002USCanada:
    """Tests for human baseline #002: US doctor telehealth to Canada."""

    def _check_record_ids_cited(self, answer_text: str) -> list:
        pattern = r'\[Record ID:\s*([\d,\s]+)'
        matches = re.findall(pattern, answer_text)
        ids = []
        for match in matches:
            nums = re.findall(r'\d+', match)
            ids.extend([int(n) for n in nums])
        return ids

    def test_baseline_002_has_record_ids(self):
        """US-Canada baseline must cite record IDs from both countries."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        ids = self._check_record_ids_cited(answer)
        assert len(ids) >= 20, f"Baseline 002 cites {len(ids)} records, expected at least 20"

    def test_baseline_002_cites_both_countries(self):
        """Baseline must cite records from BOTH USA and Canada."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        ids = self._check_record_ids_cited(answer)
        # Verify cited IDs include records from both countries
        session = get_session()
        countries = set()
        for rid in set(ids):
            record = session.query(HealthPolicy).filter_by(id=rid).first()
            if record:
                countries.add(record.country)
        session.close()
        assert "USA" in countries, "Baseline 002 must cite US records"
        assert "CAN" in countries, "Baseline 002 must cite Canadian records"

    def test_baseline_002_labels_inferences(self):
        """US-Canada baseline must label all inferences."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        inference_count = answer.lower().count("*inference")
        assert inference_count >= 5, f"Found {inference_count} labeled inferences, expected at least 5"

    def test_baseline_002_lists_gaps(self):
        """Must list what the database does NOT have."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        assert "does not have" in answer.lower() or "gap" in answer.lower()

    def test_baseline_002_has_confidence_level(self):
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        assert "confidence:" in answer.lower()

    def test_baseline_002_flags_translations(self):
        """Must flag French-language Quebec sources."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        assert "french" in answer.lower() or "machine-translated" in answer.lower(), \
            "Baseline must flag French-language sources"

    def test_baseline_002_covers_licensing_barrier(self):
        """Must address the core licensing barrier (provincial fragmentation)."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        assert "provincial" in answer.lower()
        assert "college of physicians" in answer.lower() or "cpso" in answer.lower()

    def test_baseline_002_covers_liability_barrier(self):
        """Must address the CMPA protection gap."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        assert "cmpa" in answer.lower()
        assert "liability" in answer.lower() or "medico-legal" in answer.lower()

    def test_baseline_002_covers_privacy_barrier(self):
        """Must address dual privacy compliance (HIPAA + PIPEDA)."""
        with open("tests/human_baseline_002.md", "r") as f:
            answer = f.read()
        assert "hipaa" in answer.lower()
        assert "pipeda" in answer.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
