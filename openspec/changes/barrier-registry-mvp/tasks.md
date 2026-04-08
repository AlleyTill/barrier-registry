# Implementation Tasks

## Phase 0: Foundation Before Code
- [x] TASK-000: Set up pre-commit hooks (tests must pass before any commit)
- [x] TASK-001: Manually answer a cross-border policy question from the database — this is the barrier registry benchmark the agent must match
- [x] TASK-002: Define "insufficient data" thresholds (no records = "I don't know", records older than 2 years = staleness warning)
- [x] TASK-003: Write tests FIRST (TDD) — agent cites record IDs? says "I don't know" when it should? returns only DB data?

## Phase 1: One Working Agent
- [x] TASK-004: Design character sheet for Agent #1 — US Policy Researcher (Role, Goals, Tools, Constraints, NEVER/ALWAYS, dialogue examples, version number)
- [x] TASK-005: Framework rewritten from ReAct → plan-then-execute (3-step pipeline: Plan → Execute → Synthesize). Supports 3 modes: --claude (fastest), --hybrid (default, Qwen3 plans + Opus synthesizes), --local (free but slow)
- [x] TASK-006: SQLite tools wired — search_policies, search_who_indicators, list_categories, check_confidence
- [x] TASK-007: Agent tested manually — 3-mode comparison (cloud/hybrid/local), 8 failures documented in tests/framework_failure_log.md
- [x] TASK-008: Claude backend produces quality output; hybrid mode (Qwen3 8B plans, Opus 4.6 synthesizes) is the default
- [x] TASK-008b: NCD flooding fix — 329 CMS NCDs now filtered by medical specialty taxonomy (two-pass: detect question specialties → return only matching NCDs). 55 tests passing.
- [ ] TASK-009: Write formal US-Canada human baseline, grade agent output against it

## Phase 2: RAG + Embeddings
- [x] TASK-010: Embedding pipeline built — Ollama nomic-embed-text (768 dims), batch embedding via src/data_ingestion/embeddings.py
- [x] TASK-011: Qdrant wired in local file mode (no server needed), stored at data/qdrant_store
- [x] TASK-012: All 496 records embedded and persisted. No chunking needed (avg 174 char summaries).
- [x] TASK-013: search_policies_semantic() added to agent framework. Execute step now runs keyword searches + one semantic search per country to catch what keywords miss.
- [x] TASK-014: 62 tests passing. Key test: semantic finds records keyword misses (e.g., "narcotics" → controlled substances). Telehealth cross-border, privacy, drug regulation all tested.

## Phase 3: Second Agent + Cross-Border
- [ ] TASK-015: Create character sheet for Agent #2 — Canada Policy Researcher
- [ ] TASK-016: Create character sheet for Agent #3 — Mexico Policy Researcher
- [ ] TASK-017: Build cross-border comparison tool (Agent A asks Agent B)
- [ ] TASK-018: Create Director/Orchestrator agent
- [ ] TASK-019: Test cross-border query: "What stops a US doctor from telehealth in Mexico?"

## Phase 4: Barrier Registry Benchmarks
- [ ] TASK-020: Load Commonwealth Fund benchmark data into DB
- [ ] TASK-021: Build benchmark comparison tool
- [ ] TASK-022: Agent can answer "How far is Mexico from barrier registry benchmark on X?"
- [ ] TASK-023: Test benchmark accuracy against source data

## Phase 5: Frontend + Deployment
- [ ] TASK-024: Build Streamlit interface (country selector, query input, results display)
- [ ] TASK-025: Add source citations to every output
- [ ] TASK-026: Add "I don't know" confidence indicators
- [ ] TASK-027: Deploy to Railway.app or Render.com
- [ ] TASK-028: Signup/email capture page
- [ ] TASK-028b: Add Terms of Service — "informational only, not legal advice" disclaimer on every output

## Phase 6: AWE Preparation
- [ ] TASK-029: Elevator pitch written and practiced
- [ ] TASK-030: Live demo script (under 5 minutes)
- [ ] TASK-031: Business cards with QR code to platform
- [ ] TASK-032: Product name decided and domain registered
