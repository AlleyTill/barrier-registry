# Barrier Registry MVP

## Problem
No interactive database of cross-border healthcare policy barriers exists. Healthcare entrepreneurs, new doctors, telehealth companies, and researchers have no way to check what regulatory obstacles they'll face before entering a new market. They discover barriers after investing time and money — often too late.

The WHO passed Resolution WHA71.7 on digital health in 2018. While this resolution addresses digital health broadly (not this specific tool), the gap it describes — fragmented, inconsistent cross-border health regulation — remains unsolved eight years later.

### Personal Evidence
The founder built a healthcare program in Morelia, Mexico (one city's survey: 212,000 door-to-door, 92,000 with unmet medical needs). The program was stolen and turned out to be incompatible with US regulations. There was no tool to warn about this beforehand. This is evidence from one location, not proof of the global case — but the pattern repeats wherever healthcare crosses borders.

## Who Benefits
- **Healthcare entrepreneurs** entering new markets (like the founder's experience in Mexico)
- **New doctors** exploring telehealth across borders or states
- **Telehealth companies** expanding internationally
- **Policy researchers** studying cross-border healthcare
- **Government health agencies** benchmarking their systems

## Priority Ranking (RICE Framework)

| Feature | Reach | Impact | Confidence | Effort | RICE Score | Priority |
|---------|-------|--------|------------|--------|------------|----------|
| US policy database + single agent query | High (any US healthcare worker) | High (no alternative exists) | High (data collected, sources verified) | Medium (Phase 0-1) | **Top** | Must Have |
| Cross-border comparison (US-CAN-MEX) | High (North American corridor) | High (founder's core use case) | Medium (agent reasoning untested on Ollama) | High (Phase 3) | **High** | Must Have |
| Gold standard benchmarks | Medium (researchers, policy makers) | Medium (useful but not urgent for users) | Low (benchmark selection is subjective/political) | Medium (Phase 4) | **Medium** | Should Have |
| Daily scanner for policy updates | Low (background process, invisible to users) | Medium (keeps data fresh) | Medium (government APIs may change) | Medium (Phase 2 adjacent) | **Low** | Could Have |
| Frontend web interface | High (accessibility) | Medium (CLI works for demo) | High (Streamlit is proven) | Low (Phase 5) | **Medium** | Should Have |
| Signup/membership system | High (AWE audience) | Low (doesn't affect core product) | High (Mailchimp/Buttondown is simple) | Low (Phase 5) | **Low** | Could Have |

### MoSCoW Summary
- **Must Have:** One working agent that answers US policy questions with citations. Cross-border comparison for 3 countries.
- **Should Have:** Gold standard benchmarks. Web frontend.
- **Could Have:** Daily scanner. Signup system. PDF export.
- **Won't Have (this version):** More than 3 countries. VR interface. Payment processing. Mobile app.

## Proposed Solution
An open registry of barriers to cross-border healthcare, powered by AI agents that:
1. Store and verify healthcare policy data, starting with key regulations per country (honest about coverage — not comprehensive yet)
2. Compare policies across borders to identify conflicts and gaps
3. Measure each country against gold standard benchmarks (best-performing country per category)
4. Say "I don't know" when data is insufficient — never guess
5. Cite specific database record IDs for every claim

### What It Is NOT
- NOT a solution platform (documents problems, invites others to contribute solutions)
- NOT legal advice (informational only, always cite sources)
- NOT a complete global database yet (starts with US, Canada, Mexico — honest about coverage gaps)
- NOT powered by general AI knowledge (agents ONLY reason from database records, never training data)

## Technical Approach
- **Agent framework:** Custom 140-line framework on Ollama first (understand the loop), then evaluate production frameworks
- **LLM strategy:** Ollama (llama3) for ALL tasks first. Only escalate to Claude if Ollama can't handle it. Test both, compare outputs for desirability, document where Claude is necessary.
- **Embeddings:** nomic-embed-text via Ollama (free) → Qdrant vector DB (already running)
- **Database:** SQLite (2,623 records already loaded: US/CAN/MEX policy + WHO indicators)
- **Frontend:** Streamlit (no JS needed)
- **Data sources:** CMS, CCHP, Health Canada, COFEPRIS, WHO GHO — government-backed only
- **Data authenticity:** Government sources are the most authoritative available, not infallible. All records have verification_status field. User-verified records are as trustworthy as machine-verified.

## Success Metrics
1. Agent answers questions accurately from database, citing specific record IDs
2. Agent says "I don't know" when data is insufficient (defined: no matching records, or all records older than 2 years)
3. Agent flags real policy conflicts between countries
4. Agent output matches or exceeds human baseline quality (see Human Quality Parameters below)
5. Tests pass on every commit
6. One working agent before adding a second
7. All tests written BEFORE the code (TDD)

## Human Quality Parameters
A "human quality" answer is the baseline the agent must match. Defined as:

### Grounding (Does every claim trace to data?)
- Every factual claim references a specific database record (by ID or policy_id_external)
- No claims from general knowledge or training data
- If a user-verified record lacks policy_id_external, verification_status: "user_verified" is sufficient citation
- "I found 3 relevant policies" is better than "Based on my knowledge..."

### Coverage (Does it find what's relevant?)
- Retrieves all records in the database matching the query topic
- Doesn't miss obvious matches (e.g., asking about US telehealth should find CCHP + CMS + federal records)
- Flags when coverage is thin: "Only 2 records found on this topic — coverage may be incomplete"

### Faithfulness (Is the summary accurate to the source?)
- Summary accurately represents what the source record says
- No exaggeration, minimization, or reinterpretation
- If the source is ambiguous, the agent says so instead of picking an interpretation

### Staleness Awareness
- Records older than 2 years get a warning: "This policy data is from [year] — verify it is still current"
- Records with verification_status: "failed" are excluded from answers
- Records with verification_status: "unverified" get a caveat

### Refusal Quality (How well does it say "I don't know"?)
- Returns "I don't know" when: zero matching records, query is about a country not in our database, query asks for legal advice
- "I don't know" always includes what it DID search and why it came up empty
- Never fabricates a plausible-sounding answer when the data isn't there

## What Happens If We Don't Build This
This gap persists until someone builds it. We're choosing to be that someone. Healthcare entrepreneurs, telehealth companies, and new doctors will continue discovering regulatory barriers after investing time and money — not before.
