# Implementation Tasks

## Phase 0: Foundation Before Code
- [ ] TASK-000: Set up pre-commit hooks (tests must pass before any commit)
- [ ] TASK-001: Manually answer a cross-border policy question from the database — this is the gold standard the agent must match
- [ ] TASK-002: Define "insufficient data" thresholds (no records = "I don't know", records older than 2 years = staleness warning)
- [ ] TASK-003: Write tests FIRST (TDD) — agent cites record IDs? says "I don't know" when it should? returns only DB data?

## Phase 1: One Working Agent
- [ ] TASK-004: Design character sheet for Agent #1 — US Policy Researcher (Role, Goals, Tools, Constraints, NEVER/ALWAYS, dialogue examples, version number)
- [ ] TASK-005: Build 140-line agent framework using Ollama (llama3). Must include max_iterations parameter.
- [ ] TASK-006: Wire SQLite database as an agent tool (search policies, search WHO data)
- [ ] TASK-007: Run Agent #1 manually — ask real questions, compare output to TASK-001 human baseline
- [ ] TASK-008: Run same questions through Claude and compare outputs (desirability comparison — for future reference, not deployment)
- [ ] TASK-009: Fix failures, iterate until agent matches human baseline quality with citations

## Phase 2: RAG + Embeddings
- [ ] TASK-010: Set up nomic-embed-text embeddings pipeline via Ollama
- [ ] TASK-011: Wire Qdrant as vector store for policy documents
- [ ] TASK-012: Chunk and embed existing policy data
- [ ] TASK-013: Add RAG tool to agent (semantic search instead of keyword only)
- [ ] TASK-014: Test RAG quality — does it retrieve relevant policies?

## Phase 3: Second Agent + Cross-Border
- [ ] TASK-015: Create character sheet for Agent #2 — Canada Policy Researcher
- [ ] TASK-016: Create character sheet for Agent #3 — Mexico Policy Researcher
- [ ] TASK-017: Build cross-border comparison tool (Agent A asks Agent B)
- [ ] TASK-018: Create Director/Orchestrator agent
- [ ] TASK-019: Test cross-border query: "What stops a US doctor from telehealth in Mexico?"

## Phase 4: Gold Standard Benchmarks
- [ ] TASK-020: Load Commonwealth Fund benchmark data into DB
- [ ] TASK-021: Build benchmark comparison tool
- [ ] TASK-022: Agent can answer "How far is Mexico from gold standard on X?"
- [ ] TASK-023: Test benchmark accuracy against source data

## Phase 5: Frontend + Deployment
- [ ] TASK-024: Build Streamlit interface (country selector, query input, results display)
- [ ] TASK-025: Add source citations to every output
- [ ] TASK-026: Add "I don't know" confidence indicators
- [ ] TASK-027: Deploy to Railway.app or Render.com
- [ ] TASK-028: Signup/email capture page

## Phase 6: AWE Preparation
- [ ] TASK-029: Elevator pitch written and practiced
- [ ] TASK-030: Live demo script (under 5 minutes)
- [ ] TASK-031: Business cards with QR code to platform
- [ ] TASK-032: Product name decided and domain registered
