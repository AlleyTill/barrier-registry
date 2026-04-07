"""
Tests for TASK-005: Agent framework.
Tests the framework structure and tools — does NOT require Ollama running.
"""

import pytest
from src.agents.framework import (
    search_policies, search_policies_semantic, search_who_indicators,
    check_confidence, list_categories,
    _parse_tool_call, TOOLS, SYNTHESIZE_PROMPT, PLAN_PROMPT,
    _get_available_categories, _validate_plan, _detect_countries,
    REQUIRED_CATEGORIES, _filter_by_specialty, _detect_question_specialties,
    _tag_specialties, MAX_RECORDS_PER_CATEGORY, SPECIALTY_MAP,
    COUNTRY_CONTEXT, CROSS_BORDER_PROMPT,
    _is_cross_border, _get_country_counts, _build_cross_border_section,
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


class TestSpecialtyFiltering:
    """Test the two-pass specialty filtering for large result sets (NCD flooding fix)."""

    def test_specialty_map_covers_all_areas(self):
        """Map must cover enough specialties that every NCD can be tagged."""
        expected = [
            "cardiovascular", "oncology", "respiratory", "neurology",
            "musculoskeletal", "renal_urological", "endocrine_metabolic",
            "gastrointestinal", "ophthalmology", "hematology",
            "infectious_disease", "pain_rehabilitation", "diagnostic_imaging",
            "behavioral_health", "wound_skin", "general_preventive",
            "laboratory_diagnostics", "dme_assistive", "surgical_procedures",
            "immunology", "therapies_rehab", "administrative",
        ]
        for s in expected:
            assert s in SPECIALTY_MAP, f"Missing specialty: {s}"

    def test_every_ncd_is_tagged(self):
        """CRITICAL: Every single NCD must map to at least one specialty.
        Untagged NCDs cause garbage results via fallback."""
        ncds = search_policies(country="USA", category="national_coverage_determination")
        untagged = [r for r in ncds if not _tag_specialties(r)]
        assert len(untagged) == 0, (
            f"{len(untagged)} NCDs have no specialty tag: "
            + ", ".join(f"ID:{r['record_id']} {r['title'][:40]}" for r in untagged[:5])
        )

    def test_tag_specialties_cardiac(self):
        record = {"title": "Cardiac Contractility Modulation (CCM) for Heart Failure", "summary": ""}
        tags = _tag_specialties(record)
        assert "cardiovascular" in tags

    def test_tag_specialties_cancer(self):
        record = {"title": "Anti-Cancer Chemotherapy for Colorectal Cancer", "summary": ""}
        tags = _tag_specialties(record)
        assert "oncology" in tags

    def test_tag_specialties_diabetes(self):
        record = {"title": "Blood Glucose Testing", "summary": "diabetes management"}
        tags = _tag_specialties(record)
        assert "endocrine_metabolic" in tags

    def test_detect_question_specialties_heart(self):
        specs = _detect_question_specialties("What does Medicare cover for heart failure treatment?")
        assert "cardiovascular" in specs

    def test_detect_question_specialties_none_for_telehealth(self):
        specs = _detect_question_specialties("What are the telehealth licensing rules between US and Canada?")
        # Telehealth policy questions don't map to a medical specialty
        assert len(specs) == 0

    def test_filter_telehealth_returns_zero_ncds(self):
        """Telehealth policy question has NO medical specialty — must return 0 NCDs, not garbage."""
        ncds = search_policies(country="USA", category="national_coverage_determination")
        if len(ncds) <= MAX_RECORDS_PER_CATEGORY:
            pytest.skip("Not enough NCDs to trigger filtering")
        filtered = _filter_by_specialty(ncds, "What are the telehealth rules between US and Canada?")
        assert len(filtered) == 0, (
            f"Telehealth question returned {len(filtered)} NCDs — should be 0. "
            f"First result: {filtered[0]['title'] if filtered else 'N/A'}"
        )

    def test_filter_heart_failure_returns_only_cardiovascular(self):
        """Heart failure question must return cardiovascular NCDs — verify content, not just count."""
        ncds = search_policies(country="USA", category="national_coverage_determination")
        if len(ncds) <= MAX_RECORDS_PER_CATEGORY:
            pytest.skip("Not enough NCDs to trigger filtering")
        filtered = _filter_by_specialty(ncds, "What does Medicare cover for heart failure treatment?")
        assert len(filtered) > 0
        assert len(filtered) < len(ncds)
        # Every returned record must actually be tagged cardiovascular
        for r in filtered:
            tags = _tag_specialties(r)
            assert "cardiovascular" in tags, (
                f"Record ID:{r['record_id']} '{r['title']}' returned for heart failure "
                f"but tagged as {tags}, not cardiovascular"
            )

    def test_filter_diabetes_returns_only_endocrine(self):
        """Diabetes question must return endocrine/metabolic NCDs — verify each record."""
        ncds = search_policies(country="USA", category="national_coverage_determination")
        if len(ncds) <= MAX_RECORDS_PER_CATEGORY:
            pytest.skip("Not enough NCDs to trigger filtering")
        filtered = _filter_by_specialty(ncds, "What are Medicare coverage rules for diabetes management and insulin pumps?")
        assert len(filtered) > 0
        assert len(filtered) < 50
        # Verify specific expected records are present
        titles = [r["title"].lower() for r in filtered]
        assert any("glucose" in t for t in titles), "Missing blood glucose testing NCD"
        assert any("insulin" in t for t in titles), "Missing insulin-related NCD"
        # Every returned record must be tagged endocrine_metabolic
        for r in filtered:
            tags = _tag_specialties(r)
            assert "endocrine_metabolic" in tags, (
                f"Record ID:{r['record_id']} '{r['title']}' returned for diabetes "
                f"but tagged as {tags}, not endocrine_metabolic"
            )


class TestSemanticSearch:
    """Test the RAG/semantic search pipeline (requires Ollama + Qdrant populated)."""

    def test_semantic_search_tool_registered(self):
        assert "search_policies_semantic" in TOOLS

    def test_semantic_search_returns_records_with_scores(self):
        """Semantic search must return real records with valid similarity scores."""
        results = search_policies_semantic("telehealth licensing", country="USA", limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "record_id" in r
            assert "country" in r
            assert "title" in r
            assert "similarity_score" in r
            assert 0 <= r["similarity_score"] <= 1, f"Score {r['similarity_score']} out of range"
            assert r["country"] == "USA"

    def test_semantic_privacy_returns_privacy_records(self):
        """Privacy query must return actual data_privacy records — verify by category and title."""
        results = search_policies_semantic("patient health information privacy protection", country="CAN", limit=5)
        assert len(results) > 0
        # Top result should be a privacy record
        assert results[0]["category"] == "data_privacy", (
            f"Top result for privacy query is '{results[0]['title']}' "
            f"in category '{results[0]['category']}', expected data_privacy"
        )
        # At least 3 of top 5 should be data_privacy
        privacy_count = sum(1 for r in results if r["category"] == "data_privacy")
        assert privacy_count >= 3, f"Only {privacy_count}/5 results are data_privacy records"

    def test_semantic_finds_controlled_substances_without_exact_keyword(self):
        """CORE RAG VALUE: 'narcotics' keyword returns 0, but semantic finds controlled substance records.
        Verify the actual records found are about controlled substances, not random noise."""
        keyword_results = search_policies(country="CAN", category="cross_border", keyword="narcotics")
        assert len(keyword_results) == 0, "Keyword 'narcotics' should find nothing — that's the point"

        semantic_results = search_policies_semantic(
            "importing narcotics and controlled drugs across Canadian border", country="CAN", limit=10
        )
        assert len(semantic_results) > 0

        # Verify the results are actually about controlled substances / drug importation
        relevant_terms = ["controlled", "substance", "drug", "import", "export", "medication", "prescri"]
        relevant_count = 0
        for r in semantic_results:
            text = f"{r['title']} {r['summary']}".lower()
            if any(term in text for term in relevant_terms):
                relevant_count += 1

        assert relevant_count >= 3, (
            f"Only {relevant_count}/{len(semantic_results)} semantic results are actually about "
            f"controlled substances. Results: {[r['title'][:50] for r in semantic_results]}"
        )

    def test_semantic_respects_country_filter(self):
        results = search_policies_semantic("telehealth regulations", country="CAN", limit=10)
        for r in results:
            assert r["country"] == "CAN", f"Record '{r['title']}' has country={r['country']}, expected CAN"

    def test_semantic_cross_country_without_filter(self):
        """Without country filter, should return results from multiple countries."""
        results = search_policies_semantic("telehealth licensing barriers", limit=20)
        countries = set(r["country"] for r in results)
        assert len(countries) > 1, (
            f"Cross-country semantic search only returned {countries}. "
            f"Expected multiple countries."
        )


class TestCrossBorderDetection:
    """Test cross-border detection, prompt assembly, and country context."""

    def test_is_cross_border_true_for_two_countries(self):
        """Records from 2 countries = cross-border."""
        results = {
            "all_records": [
                {"country": "USA", "record_id": 1},
                {"country": "CAN", "record_id": 2},
            ]
        }
        assert _is_cross_border(results) is True

    def test_is_cross_border_false_for_single_country(self):
        """Records from 1 country = not cross-border."""
        results = {
            "all_records": [
                {"country": "USA", "record_id": 1},
                {"country": "USA", "record_id": 2},
            ]
        }
        assert _is_cross_border(results) is False

    def test_is_cross_border_false_for_empty(self):
        """No records = not cross-border."""
        assert _is_cross_border({"all_records": []}) is False
        assert _is_cross_border({}) is False

    def test_is_cross_border_true_for_three_countries(self):
        """Records from 3 countries = cross-border."""
        results = {
            "all_records": [
                {"country": "USA", "record_id": 1},
                {"country": "CAN", "record_id": 2},
                {"country": "MEX", "record_id": 3},
            ]
        }
        assert _is_cross_border(results) is True

    def test_get_country_counts(self):
        records = [
            {"country": "USA"}, {"country": "USA"}, {"country": "USA"},
            {"country": "CAN"},
        ]
        counts = _get_country_counts(records)
        assert counts["USA"] == 3
        assert counts["CAN"] == 1

    def test_country_context_covers_all_db_countries(self):
        """COUNTRY_CONTEXT must have an entry for every country in the database."""
        categories = _get_available_categories()
        for country in categories:
            assert country in COUNTRY_CONTEXT, (
                f"COUNTRY_CONTEXT missing entry for {country} — "
                f"the synthesis prompt won't have jurisdictional context for this country"
            )

    def test_cross_border_prompt_has_barrier_classifications(self):
        """The cross-border prompt must instruct barrier classification."""
        for term in ["PROHIBITION", "REGULATORY GAP", "CONFLICT", "ASYMMETRY"]:
            assert term in CROSS_BORDER_PROMPT, f"CROSS_BORDER_PROMPT missing '{term}'"

    def test_cross_border_prompt_has_barrier_summary_table(self):
        """Must instruct a barrier summary table."""
        assert "Barrier Summary" in CROSS_BORDER_PROMPT

    def test_build_cross_border_section_includes_countries(self):
        """Built section must name the actual countries."""
        results = {
            "all_records": [
                {"country": "USA", "record_id": 1, "title": "t", "summary": "s"},
                {"country": "CAN", "record_id": 2, "title": "t", "summary": "s"},
            ]
        }
        section = _build_cross_border_section(results)
        assert "USA" in section
        assert "CAN" in section

    def test_build_cross_border_section_flags_asymmetry(self):
        """When one country has 4x+ more records, flag asymmetry."""
        records = [{"country": "USA", "record_id": i} for i in range(20)]
        records.append({"country": "CAN", "record_id": 100})
        results = {"all_records": records}
        section = _build_cross_border_section(results)
        assert "asymmetry" in section.lower()
        assert "CAN" in section

    def test_synthesize_prompt_requires_foundational_legislation(self):
        """Prompt must instruct citing foundational/primary legislation."""
        assert "foundational" in SYNTHESIZE_PROMPT.lower()
        assert "primary legislation" in SYNTHESIZE_PROMPT.lower()

    def test_synthesize_prompt_requires_exact_language_counts(self):
        """Prompt must tell LLM to count only cited records, not estimate."""
        assert "do not estimate" in SYNTHESIZE_PROMPT.lower() or "exact numbers" in SYNTHESIZE_PROMPT.lower()

    def test_build_cross_border_section_no_asymmetry_when_balanced(self):
        """Balanced records should not trigger asymmetry warning."""
        records = [{"country": "USA", "record_id": i} for i in range(5)]
        records += [{"country": "CAN", "record_id": i + 10} for i in range(4)]
        results = {"all_records": records}
        section = _build_cross_border_section(results)
        assert "roughly balanced" in section.lower()

    def test_build_cross_border_section_includes_country_context(self):
        """Built section must include jurisdictional context for each country."""
        results = {
            "all_records": [
                {"country": "USA", "record_id": 1},
                {"country": "MEX", "record_id": 2},
            ]
        }
        section = _build_cross_border_section(results)
        assert "HIPAA" in section  # US context
        assert "COFEPRIS" in section  # Mexico context
        assert "PIPEDA" not in section  # Canada context should NOT be included


class TestCrossBorderComparison:
    """Test that the database has sufficient data for cross-border comparison."""

    def test_us_and_canada_both_have_telehealth(self):
        us = search_policies(country="USA", category="telehealth")
        can = search_policies(country="CAN", category="telehealth")
        assert len(us) >= 3, f"USA telehealth: only {len(us)} records"
        assert len(can) >= 3, f"CAN telehealth: only {len(can)} records"

    def test_us_and_canada_both_have_licensing(self):
        us = search_policies(country="USA", category="medical_licensing")
        can = search_policies(country="CAN", category="medical_licensing")
        assert len(us) >= 2, f"USA licensing: only {len(us)} records"
        assert len(can) >= 3, f"CAN licensing: only {len(can)} records"

    def test_us_and_canada_both_have_privacy(self):
        us = search_policies(country="USA", category="data_privacy")
        can = search_policies(country="CAN", category="data_privacy")
        assert len(us) >= 1, f"USA privacy: only {len(us)} records"
        assert len(can) >= 3, f"CAN privacy: only {len(can)} records"

    def test_validate_plan_injects_for_both_countries_on_cross_border(self):
        """A US-Canada question must get required categories for BOTH countries."""
        categories = _get_available_categories()
        plan = [{"country": "USA", "category": "telehealth"}]
        valid = _validate_plan(plan, categories, question="US doctor telehealth to Canada")
        usa_cats = [s["category"] for s in valid if s["country"] == "USA"]
        can_cats = [s["category"] for s in valid if s["country"] == "CAN"]
        assert "telehealth" in can_cats, "CAN telehealth not injected"
        assert "medical_licensing" in can_cats, "CAN medical_licensing not injected"
        assert "data_privacy" in can_cats, "CAN data_privacy not injected"
        assert "medical_licensing" in usa_cats, "USA medical_licensing not injected"

    def test_detect_countries_us_mexico(self):
        available = ["USA", "CAN", "MEX", "GBR"]
        countries = _detect_countries("What stops a US doctor from telehealth in Mexico?", available)
        assert "USA" in countries
        assert "MEX" in countries

    def test_canada_has_medical_liability(self):
        """Canada must have medical liability records for cross-border comparison."""
        results = search_policies(country="CAN", category="medical_liability")
        assert len(results) >= 3, f"CAN medical_liability: only {len(results)} records, need >= 3"
        # Verify content: at least one record mentions CMPA
        titles = " ".join(r["title"] for r in results).lower()
        assert "cmpa" in titles or "liability" in titles, (
            "medical_liability records should reference CMPA or liability"
        )

    def test_canada_has_clinical_standards(self):
        """Canada must have clinical standards records."""
        results = search_policies(country="CAN", category="clinical_standards")
        assert len(results) >= 3, f"CAN clinical_standards: only {len(results)} records, need >= 3"

    def test_canada_telehealth_province_coverage(self):
        """Telehealth records must reference at least 8 provinces."""
        results = search_policies(country="CAN", category="telehealth")
        text = " ".join(f"{r['title']} {r['summary']}" for r in results).lower()
        provinces_found = []
        province_markers = {
            "ON": ["ontario", "cpso"],
            "BC": ["british columbia", "cpsbc"],
            "AB": ["alberta", "cpsa"],
            "QC": ["quebec", "québec", "cmq"],
            "SK": ["saskatchewan", "cpss"],
            "MB": ["manitoba", "cpsm"],
            "NS": ["nova scotia", "cpsns"],
            "NB": ["new brunswick", "cpsnb"],
            "PE": ["prince edward island", "cpspei", "pei"],
            "NL": ["newfoundland", "cpsnl"],
        }
        for code, markers in province_markers.items():
            if any(m in text for m in markers):
                provinces_found.append(code)
        assert len(provinces_found) >= 8, (
            f"Only {len(provinces_found)} provinces found in telehealth records: "
            f"{provinces_found}. Need >= 8 for cross-border coverage."
        )

    def test_canada_has_digital_health(self):
        """Canada must have digital health records."""
        results = search_policies(country="CAN", category="digital_health")
        assert len(results) >= 3, f"CAN digital_health: only {len(results)} records, need >= 3"

    def test_canada_has_health_workforce(self):
        """Canada must have health workforce records."""
        results = search_policies(country="CAN", category="health_workforce")
        assert len(results) >= 2, f"CAN health_workforce: only {len(results)} records, need >= 2"

    def test_detect_countries_all_three(self):
        available = ["USA", "CAN", "MEX", "GBR"]
        countries = _detect_countries(
            "Compare telehealth rules across US, Canada, and Mexico", available
        )
        assert "USA" in countries
        assert "CAN" in countries
        assert "MEX" in countries

    def test_validate_plan_injects_for_three_countries(self):
        """A US-Canada-Mexico question must get required categories for ALL THREE."""
        categories = _get_available_categories()
        plan = [{"country": "USA", "category": "telehealth"}]
        valid = _validate_plan(plan, categories,
            question="Compare telehealth rules across US, Canada, and Mexico")
        usa_cats = [s["category"] for s in valid if s["country"] == "USA"]
        can_cats = [s["category"] for s in valid if s["country"] == "CAN"]
        mex_cats = [s["category"] for s in valid if s["country"] == "MEX"]
        # All three countries must have required categories
        assert len(usa_cats) >= 1, "USA must have categories"
        assert len(can_cats) >= 3, f"CAN only has {len(can_cats)} categories, need >= 3"
        assert len(mex_cats) >= 3, f"MEX only has {len(mex_cats)} categories, need >= 3"
        # Telehealth must be in all three
        assert "telehealth" in can_cats, "CAN missing telehealth"
        assert "telehealth" in mex_cats, "MEX missing telehealth"

    def test_three_way_cross_border_detection(self):
        """Three countries in records = cross-border."""
        results = {
            "all_records": [
                {"country": "USA", "record_id": 1},
                {"country": "CAN", "record_id": 2},
                {"country": "MEX", "record_id": 3},
            ]
        }
        assert _is_cross_border(results) is True
        counts = _get_country_counts(results["all_records"])
        assert len(counts) == 3

    def test_detect_countries_handles_punctuation(self):
        """US followed by comma, period, or question mark must still match."""
        available = ["USA", "CAN", "MEX", "GBR"]
        for q in [
            "US, Canada",
            "US. Canada.",
            "What about the US?",
            "US and Canada and Mexico!",
            "telehealth in the US; what about Canada?",
        ]:
            countries = _detect_countries(q, available)
            assert "USA" in countries, f"Failed to detect USA in: '{q}'"
