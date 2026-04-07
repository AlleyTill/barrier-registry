"""
Global Healthcare Barrier Registry — Streamlit Frontend

Provides a web interface for querying cross-border healthcare policy barriers.
Runs the plan-then-execute agent pipeline and displays structured results.
"""

import streamlit as st
import time
from src.agents.framework import (
    run_agent_detailed, _get_available_categories, _detect_countries,
    _get_country_counts, _is_cross_border,
)

# --- Page Config ---
st.set_page_config(
    page_title="Healthcare Barrier Registry",
    page_icon="🏥",
    layout="wide",
)

# --- Header ---
st.title("Global Healthcare Barrier Registry")
st.markdown("*Map the barriers to cross-border healthcare — so you know what you're walking into.*")
st.divider()

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("Configuration")

    backend = st.radio(
        "LLM Backend",
        options=["claude", "hybrid", "ollama"],
        index=0,
        help="Claude: fastest + most accurate. Hybrid: local plan + cloud synthesis. Ollama: free but slower.",
    )

    st.divider()

    # Show database stats
    st.header("Database")
    cats = _get_available_categories()
    for country, country_cats in sorted(cats.items()):
        st.markdown(f"**{country}**: {len(country_cats)} categories")

    st.divider()
    st.caption("Built for AWE 2026 — June 15-18, Long Beach")

# --- Example Questions ---
EXAMPLES = [
    "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Canada?",
    "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Mexico?",
    "Compare telehealth rules across the United States, Canada, and Mexico",
    "What are the US federal rules for prescribing controlled substances via telehealth?",
    "What data privacy laws apply to telehealth in Canada?",
]

# --- Main Input ---
col1, col2 = st.columns([4, 1])
with col1:
    question = st.text_area(
        "Ask a healthcare policy question",
        placeholder="e.g., What barriers would a US-licensed doctor face providing telehealth to a patient in Canada?",
        height=80,
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("Search", type="primary", use_container_width=True)

# Example buttons
st.markdown("**Try an example:**")
example_cols = st.columns(len(EXAMPLES))
for i, ex in enumerate(EXAMPLES):
    with example_cols[i]:
        label = ex[:40] + "..." if len(ex) > 40 else ex
        if st.button(label, key=f"ex_{i}"):
            question = ex
            run_button = True

# --- Run Pipeline ---
if run_button and question.strip():
    with st.status("Running barrier analysis...", expanded=True) as status:
        progress_area = st.empty()
        start = time.time()

        def on_step(step, detail):
            icons = {
                "plan": "1/3 Planning",
                "plan_done": "1/3 Planning",
                "execute": "2/3 Searching",
                "execute_done": "2/3 Searching",
                "synthesize": "3/3 Synthesizing",
                "synthesize_done": "3/3 Complete",
            }
            label = icons.get(step, step)
            elapsed = time.time() - start
            progress_area.markdown(f"**{label}** ({elapsed:.0f}s) — {detail}")

        result = run_agent_detailed(question, verbose=False, backend=backend, on_step=on_step)

        elapsed = time.time() - start
        status.update(label=f"Analysis complete ({elapsed:.1f}s)", state="complete")

    # --- Display Results ---

    # Metadata bar
    meta_cols = st.columns(4)
    with meta_cols[0]:
        countries_str = ", ".join(result["countries"]) if result["countries"] else "None detected"
        st.metric("Countries", countries_str)
    with meta_cols[1]:
        st.metric("Records Found", result["record_count"])
    with meta_cols[2]:
        st.metric("Searches Run", result["search_count"])
    with meta_cols[3]:
        confidence = result["confidence"]
        level = confidence.get("level", "unknown")
        st.metric("Confidence", level.upper())

    # Cross-border badge
    if result["is_cross_border"]:
        st.success(f"Cross-border analysis: {' vs '.join(result['countries'])}")

    st.divider()

    # Search plan
    with st.expander(f"Search Plan ({len(result['plan'])} searches)", expanded=False):
        for i, search in enumerate(result["plan"]):
            kw = f" (keyword: {search.get('keyword', '')})" if search.get("keyword") else ""
            st.markdown(f"{i+1}. `{search['country']}/{search['category']}`{kw}")

    # Records by search
    exec_results = result.get("execution_results", {})
    with st.expander(f"Records Retrieved ({result['record_count']} unique)", expanded=False):
        for key, records in exec_results.get("results_by_search", {}).items():
            st.markdown(f"**{key}**: {len(records)} records")

    # Confidence details
    if confidence.get("caveats"):
        with st.expander("Confidence Details", expanded=False):
            st.markdown(f"**Level:** {confidence.get('level', 'unknown')}")
            st.markdown(f"**Records:** {confidence.get('count', 0)}")
            st.markdown(f"**Can answer:** {confidence.get('can_answer', False)}")
            st.markdown("**Caveats:**")
            for caveat in confidence.get("caveats", []):
                st.markdown(f"- {caveat}")

    st.divider()

    # Main answer
    st.markdown("## Analysis")
    st.markdown(result["answer"])

elif run_button:
    st.warning("Please enter a question.")
