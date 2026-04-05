# Implementation Tasks

## Phase 1: One Working Agent (Current)
- [ ] TASK-001: Build 140-line agent framework using Ollama (understand the loop)
- [ ] TASK-002: Wire SQLite database as an agent tool (search policies, search WHO data)
- [ ] TASK-003: Create character sheet for Agent #1 — US Policy Researcher
- [ ] TASK-004: Run Agent #1 manually — ask real questions, evaluate output
- [ ] TASK-005: Write tests (cites sources? says "I don't know"? returns real data?)
- [ ] TASK-006: Set up pre-commit hooks (tests must pass before commit)

## Phase 2: RAG + Embeddings
- [ ] TASK-007: Set up nomic-embed-text embeddings pipeline via Ollama
- [ ] TASK-008: Wire Qdrant as vector store for policy documents
- [ ] TASK-009: Chunk and embed existing policy data
- [ ] TASK-010: Add RAG tool to agent (semantic search instead of keyword only)
- [ ] TASK-011: Test RAG quality — does it retrieve relevant policies?

## Phase 3: Second Agent + Cross-Border
- [ ] TASK-012: Create character sheet for Agent #2 — Canada Policy Researcher
- [ ] TASK-013: Create character sheet for Agent #3 — Mexico Policy Researcher
- [ ] TASK-014: Build cross-border comparison tool (Agent A asks Agent B)
- [ ] TASK-015: Create Director/Orchestrator agent
- [ ] TASK-016: Test cross-border query: "What stops a US doctor from telehealth in Mexico?"

## Phase 4: Gold Standard Benchmarks
- [ ] TASK-017: Load Commonwealth Fund benchmark data into DB
- [ ] TASK-018: Build benchmark comparison tool
- [ ] TASK-019: Agent can answer "How far is Mexico from gold standard on X?"
- [ ] TASK-020: Test benchmark accuracy against source data

## Phase 5: Frontend + Deployment
- [ ] TASK-021: Build Streamlit interface (country selector, query input, results display)
- [ ] TASK-022: Add source citations to every output
- [ ] TASK-023: Add "I don't know" confidence indicators
- [ ] TASK-024: Deploy to Railway.app or Render.com
- [ ] TASK-025: Signup/email capture page

## Phase 6: AWE Preparation
- [ ] TASK-026: Elevator pitch written and practiced
- [ ] TASK-027: Live demo script (under 5 minutes)
- [ ] TASK-028: Business cards with QR code to platform
- [ ] TASK-029: Product name decided and domain registered
