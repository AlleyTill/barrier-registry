# Barrier Registry

*Map the barriers to cross-border healthcare — so you know what you're walking into.*

A research prototype that uses an AI agent pipeline to identify, classify, and surface policy barriers between healthcare jurisdictions (initially US ↔ Mexico ↔ Canada).

## What it does

Given a query like *"What barriers exist for a US-licensed physician seeking to consult on a Mexican patient's care?"*, the system:

1. Plans a multi-step retrieval strategy across the seeded policy corpus (CMS NCDs and related sources)
2. Runs semantic search via Qdrant over indexed policy documents
3. Synthesizes a structured answer citing the specific rules, jurisdictions, and conflict points
4. Maintains a SALT-style belief layer so insights from earlier queries can inform later ones

The Streamlit frontend exposes the pipeline with three backend modes (Claude, hybrid, local Ollama), category filters, country-aware result counts, and live belief stats.

## Tech stack

- **Agent framework:** CrewAI + custom plan-then-execute pipeline (`src/agents/framework.py`)
- **Frontend:** Streamlit (`src/frontend/app.py`)
- **API layer:** FastAPI + Uvicorn
- **Vector store:** Qdrant
- **LLM backends:** Anthropic Claude (cloud), Ollama (local), or hybrid plan/synthesis split
- **Data:** Seeded CMS NCD corpus + structured taxonomy (see `seed_*.py`, `data/`)
- **Belief layer:** SALT-inspired persistence for lateral reasoning across queries

## Status

**Archived after Phase 6 (April 2026).** Six development phases were completed — full retrieval pipeline, cross-border query support, US/Canada/Mexico coverage, the SALT belief layer, and the Streamlit interface. The project was archived because the top-down state-by-state policy-scraping approach turned out to be legally infeasible at scale for a solo builder.

The work pivoted into a successor project — **Community Registry** — which inverts the model: instead of scraping policy from above, it lets verified healthcare professionals and developers contribute the barriers they actually encounter. Targeted public launch at AWE 2026.

## Run it locally

```bash
git clone https://github.com/AlleyTill/barrier-registry.git
cd barrier-registry
python -m venv venv
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Set your Anthropic key (Claude backend) — see .env example below
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Seed the database
python seed_all_cms.py

# Launch
streamlit run src/frontend/app.py
```

Opens at `http://localhost:8501`.

## Repository layout

- `src/agents/` — agent framework, plan-then-execute pipeline
- `src/beliefs/` — SALT belief extraction and management
- `src/data_ingestion/` — embeddings + Qdrant indexing
- `src/frontend/` — Streamlit UI
- `data/` — seeded policy corpus
- `tests/` — 135 tests covering the agent pipeline, belief layer, and synthesis correctness
- `openspec/` — proposal, tasks, and governance documents from the spec-driven build process
- `CHECKPOINTS.md` — checkpoint log from the build

## Author

Built solo by [Alley Till](https://github.com/AlleyTill) over Phases 1–6, with Claude Code as a pair programmer. Part of an ongoing learn-to-code journey through the Multiverse School.
