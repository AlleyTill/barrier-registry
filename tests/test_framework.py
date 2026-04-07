"""
Tests for TASK-005: Agent framework.
Tests the framework structure and tools — does NOT require Ollama running.
"""

import pytest
from src.agents.framework import (
    search_policies, search_who_indicators, check_confidence, list_categories,
    _parse_tool_call, TOOLS, SYNTHESIZE_PROMPT, PLAN_PROMPT,
    _get_available_categories, _validate_plan, _detect_countries,
    REQUIRED_CATEGORIES,
)


class TestTools:
    """Test that database tools return correct data."""

    def test_search_policies_returns_list(self):
        results = search_policies(country="USA")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_policies_has_required_fields(self):
        results = search_policies(country="USA", keyword="telehealth")
        assert len(results) > 0
        record = results[0]
        assert "record_id" in record
        assert "country" in record
        assert "title" in record
        assert "source_url" in record
        assert "verification_status" in record

    def test_search_policies_filters_by_country(self):
        results = search_policies(country="USA")
        for r in results:
            assert r["country"] == "USA"

    def test_search_policies_excludes_failed(self):
        results = search_policies()
        for r in results:
            assert r["verification_status"] != "failed"

    def test_search_policies_keyword_search(self):
        results = search_policies(keyword="telehealth")
        assert len(results) > 0
        # At least one result should mention telehealth
        found = any("telehealth" in (r["title"] + r["summary"]).lower() for r in results)
        assert found

    def test_search_who_indicators_returns_list(self):
        results = search_who_indicators(country="USA")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_who_indicators_has_fields(self):
        results = search_who_indicators(country="USA")
        record = results[0]
        assert "id" in record
        assert "country" in record
        assert "indicator" in record

    def test_check_confidence_sufficient(self):
        records = search_policies(country="USA", keyword="telehealth")
        result = check_confidence(records)
        assert result["can_answer"] is True
        assert result["level"] in ("sufficient", "thin")

    def test_check_confidence_no_data(self):
        result = check_confidence([])
        assert result["can_answer"] is False
        assert result["level"] == "no_data"

    def test_list_categories_returns_list(self):
        results = list_categories()
        assert isinstance(results, list)
        assert len(results) > 0
        assert "category" in results[0]
        assert "count" in results[0]

    def test_list_categories_filters_by_country(self):
        all_cats = list_categories()
        usa_cats = list_categories(country="USA")
        # USA should have fewer or equal categories than all
        assert len(usa_cats) <= len(all_cats)


class TestToolParsing:
    """Test that tool call JSON parsing works correctly."""

    def test_parse_valid_tool_call(self):
        text = '{"tool": "search_policies", "args": {"country": "USA"}}'
        result = _parse_tool_call(text)
        assert result is not None
        assert result[0] == "search_policies"
        assert result[1]["country"] == "USA"

    def test_parse_tool_call_with_surrounding_text(self):
        text = 'I should search for US policies.\n{"tool": "search_policies", "args": {"keyword": "telehealth"}}\nLet me check.'
        result = _parse_tool_call(text)
        assert result is not None
        assert result[0] == "search_policies"

    def test_parse_no_tool_call(self):
        text = "FINAL ANSWER: Here is what I found..."
        result = _parse_tool_call(text)
        assert result is None

    def test_parse_invalid_json(self):
        text = '{"tool": broken json}'
        result = _parse_tool_call(text)
        assert result is None


class TestFrameworkConfig:
    """Test framework configuration is correct."""

    def test_all_tools_registered(self):
        assert "search_policies" in TOOLS
        assert "search_who_indicators" in TOOLS
        assert "check_confidence" in TOOLS
        assert "list_categories" in TOOLS

    def test_synthesize_prompt_has_key_rules(self):
        assert "NEVER answer from general knowledge" in SYNTHESIZE_PROMPT
        assert "Record ID" in SYNTHESIZE_PROMPT
        assert "I don't know" in SYNTHESIZE_PROMPT
        assert "legal advice" in SYNTHESIZE_PROMPT.lower()
        assert "confidence" in SYNTHESIZE_PROMPT.lower()

    def test_plan_prompt_has_key_rules(self):
        assert "ONLY use category names" in PLAN_PROMPT
        assert "cross-border" in PLAN_PROMPT.lower()
        assert "JSON" in PLAN_PROMPT

    def test_get_available_categories(self):
        cats = _get_available_categories()
        assert isinstance(cats, dict)
        assert "USA" in cats
        assert "CAN" in cats
        assert len(cats["USA"]) > 0

    def test_validate_plan_rejects_invalid_country(self):
        categories = {"USA": ["telehealth"], "CAN": ["telehealth"]}
        plan = [{"country": "ZZZ", "category": "telehealth"}]
        valid = _validate_plan(plan, categories, question="test")
        # May still inject required categories for countries detected in question
        assert not any(s["country"] == "ZZZ" for s in valid)

    def test_validate_plan_rejects_invalid_category(self):
        categories = {"USA": ["telehealth"], "CAN": ["telehealth"]}
        plan = [{"country": "USA", "category": "fake_category"}]
        valid = _validate_plan(plan, categories, question="test")
        assert not any(s["category"] == "fake_category" for s in valid)

    def test_validate_plan_accepts_valid_search(self):
        categories = {"USA": ["telehealth"], "CAN": ["telehealth"]}
        plan = [{"country": "USA", "category": "telehealth"}]
        valid = _validate_plan(plan, categories, question="test")
        assert any(s["country"] == "USA" and s["category"] == "telehealth" for s in valid)

    def test_validate_plan_deduplicates(self):
        categories = {"USA": ["telehealth"]}
        plan = [
            {"country": "USA", "category": "telehealth"},
            {"country": "USA", "category": "telehealth"},
        ]
        valid = _validate_plan(plan, categories, question="test")
        telehealth_count = sum(1 for s in valid if s["category"] == "telehealth")
        assert telehealth_count == 1

    def test_validate_plan_injects_required_drug_regulation(self):
        """drug_regulation must be searched even if planner omits it."""
        categories = {"CAN": ["telehealth", "drug_regulation", "medical_licensing"]}
        plan = [{"country": "CAN", "category": "telehealth"}]
        valid = _validate_plan(plan, categories, question="telehealth in Canada")
        cats = [s["category"] for s in valid]
        assert "drug_regulation" in cats

    def test_validate_plan_injects_cross_border_variants(self):
        """cross_border and cross_border_health are equivalent — inject whichever exists."""
        categories = {"MEX": ["telehealth", "cross_border_health"]}
        plan = [{"country": "MEX", "category": "telehealth"}]
        valid = _validate_plan(plan, categories, question="telehealth in Mexico")
        cats = [s["category"] for s in valid]
        assert "cross_border_health" in cats

    def test_validate_plan_no_duplicate_injection(self):
        """Don't inject a required category if the planner already included it."""
        categories = {"USA": ["telehealth", "drug_regulation"]}
        plan = [
            {"country": "USA", "category": "telehealth"},
            {"country": "USA", "category": "drug_regulation"},
        ]
        valid = _validate_plan(plan, categories, question="US telehealth")
        drug_count = sum(1 for s in valid if s["category"] == "drug_regulation")
        assert drug_count == 1

    def test_detect_countries_us_canada(self):
        available = ["USA", "CAN", "MEX", "GBR"]
        countries = _detect_countries("US doctor telehealth to Canada", available)
        assert "USA" in countries
        assert "CAN" in countries
        assert "MEX" not in countries

    def test_detect_countries_mexico(self):
        available = ["USA", "CAN", "MEX", "GBR"]
        countries = _detect_countries("barriers for telehealth in Mexico", available)
        assert "MEX" in countries
