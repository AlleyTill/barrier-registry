"""
Tests for TASK-005: Agent framework.
Tests the framework structure and tools — does NOT require Ollama running.
"""

import pytest
from src.agents.framework import (
    search_policies, search_who_indicators, check_confidence,
    _parse_tool_call, TOOLS, SYSTEM_PROMPT, MAX_ITERATIONS_DEFAULT,
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

    def test_max_iterations_is_set(self):
        assert MAX_ITERATIONS_DEFAULT > 0
        assert MAX_ITERATIONS_DEFAULT <= 10  # Sanity check

    def test_system_prompt_has_key_rules(self):
        assert "NEVER answer from general knowledge" in SYSTEM_PROMPT
        assert "Record ID" in SYSTEM_PROMPT
        assert "I don't know" in SYSTEM_PROMPT
        assert "legal advice" in SYSTEM_PROMPT.lower()
        assert "confidence" in SYSTEM_PROMPT.lower()
