"""
Barrier Registry — Streamlit Frontend

Provides a web interface for querying cross-border healthcare policy barriers.
Runs the plan-then-execute agent pipeline and displays structured results.
"""

import streamlit as st
import json
import time
from src.agents.framework import (
    run_agent_detailed, _get_available_categories, _detect_countries,
    _get_country_counts, _is_cross_border,
)
from src.beliefs.manager import get_active_beliefs, get_belief_count

# --- Page Config ---
st.set_page_config(
    page_title="Barrier Registry",
    page_icon="🏥",
    layout="wide",
)

# --- Header ---
st.title("Barrier Registry")
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

    # Belief stats
    st.header("Beliefs")
    try:
        counts = get_belief_count()
        active = counts.get("active", 0)
        stale = counts.get("stale", 0)
        superseded = counts.get("superseded", 0)
        st.markdown(f"**Active:** {active}")
        st.markdown(f"**Stale:** {stale}")
        st.markdown(f"**Superseded:** {superseded}")
    except Exception:
        st.markdown("*No beliefs yet*")

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

    # --- Belief Network Panel ---
    st.divider()
    st.markdown("## Belief Network")
    st.caption("SALT-inspired persistent inferences — the system learns from every query")

    new_beliefs = result.get("beliefs", [])
    prior_beliefs = result.get("execution_results", {}).get("prior_beliefs", [])

    if new_beliefs:
        st.markdown(f"### New Beliefs ({len(new_beliefs)} extracted)")
        for b in new_beliefs:
            classification = b.get("classification", "")
            confidence = b.get("confidence_score", 0)
            source_ids = b.get("source_record_ids", "[]")
            if isinstance(source_ids, str):
                source_ids = json.loads(source_ids)

            col_tag, col_text = st.columns([1, 4])
            with col_tag:
                badge_colors = {
                    "PROHIBITION": "red",
                    "CONFLICT": "orange",
                    "REGULATORY_GAP": "blue",
                    "ASYMMETRY": "violet",
                }
                color = badge_colors.get(classification, "gray")
                st.markdown(f":{color}[**{classification}**]")
                st.progress(confidence, text=f"{confidence:.0%}")
            with col_text:
                st.markdown(f"**{b['statement_text']}**")
                st.caption(f"Category: {b.get('category', 'N/A')} | Sources: {source_ids}")

    if prior_beliefs:
        with st.expander(f"Prior Beliefs ({len(prior_beliefs)} active)", expanded=False):
            for b in prior_beliefs:
                conf = b.get("confidence_score", 0)
                st.markdown(
                    f"- [{b.get('classification', '')}] {b['statement_text']} "
                    f"*(confidence: {conf:.0%}, sources: {b.get('source_record_ids', [])})*"
                )

    if not new_beliefs and not prior_beliefs:
        st.info("No beliefs yet. Run a cross-border query to start building the belief network.")

    # --- Belief Graph Visualization ---
    if result["is_cross_border"] and new_beliefs:
        st.markdown("### Agent Network")
        countries = result["countries"]
        if len(countries) >= 2:
            # Build Graphviz DOT with belief edges
            edges = []
            for b in new_beliefs:
                label = b.get("classification", "barrier")
                short_text = b["statement_text"][:50]
                edges.append(f'  "{countries[0]}" -> "{countries[1]}" [label="{label}\\n{short_text}..."]')

            dot = f"""digraph beliefs {{
  rankdir=LR
  node [shape=box, style=filled, fillcolor=lightblue, fontsize=14]
  edge [fontsize=9, color=gray40]
  "{countries[0]}" [fillcolor=lightyellow]
  "{countries[1]}" [fillcolor=lightyellow]
{chr(10).join(edges)}
}}"""
            st.graphviz_chart(dot)

elif run_button:
    st.warning("Please enter a question.")
