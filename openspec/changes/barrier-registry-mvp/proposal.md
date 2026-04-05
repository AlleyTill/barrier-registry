# Barrier Registry MVP

## Problem
No interactive database of cross-border healthcare policy barriers exists. Healthcare entrepreneurs, new doctors, telehealth companies, and researchers have no way to check what regulatory obstacles they'll face before entering a new market. They discover barriers after investing time and money — often too late.

The WHO called for this in Resolution WHA71.7 (2018). Eight years later, it still doesn't exist.

### Personal Evidence
The founder built a healthcare program in Morelia, Mexico (212,000 surveyed door-to-door, 92,000 with unmet medical needs). The program was stolen and turned out to be incompatible with US regulations. There was no tool to warn about this beforehand.

## Who Benefits
- **Healthcare entrepreneurs** entering new markets (like the founder's experience in Mexico)
- **New doctors** exploring telehealth across borders or states
- **Telehealth companies** expanding internationally
- **Policy researchers** studying cross-border healthcare
- **Government health agencies** benchmarking their systems

## Proposed Solution
An open registry of barriers to cross-border healthcare, powered by AI agents that:
1. Store verified healthcare policy data per country (government sources only)
2. Compare policies across borders to identify conflicts and gaps
3. Measure each country against gold standard benchmarks (best-performing country per category)
4. Say "I don't know" when data is insufficient — never guess

### What It Is NOT
- NOT a solution platform (documents problems, invites others to contribute solutions)
- NOT legal advice (informational only, always cite sources)
- NOT a complete global database yet (starts with US, Canada, Mexico — honest about coverage gaps)

## Technical Approach
- **Agent framework:** Custom 140-line framework first (understand the loop), then evaluate CrewAI/Claude SDK
- **LLM strategy:** Ollama (llama3, gemma3) for routine tasks (free), Claude for complex reasoning
- **Embeddings:** nomic-embed-text via Ollama (free) → Qdrant vector DB (already running)
- **Database:** SQLite (2,623 records already loaded: US/CAN/MEX policy + WHO indicators)
- **Frontend:** Streamlit (no JS needed)
- **Data sources:** CMS, CCHP, Health Canada, COFEPRIS, WHO GHO — government-backed only

## Success Metrics
- Agent answers questions accurately from database, citing sources
- Agent says "I don't know" when data is insufficient
- Agent flags real policy conflicts between countries
- Tests pass on every commit
- One working agent before adding a second

## What Happens If We Don't Build This
People like the founder keep walking into walls they couldn't see. Healthcare programs fail not because the medicine is bad, but because nobody mapped the regulatory landscape. The WHO keeps writing papers about the problem. Nobody builds the tool.
