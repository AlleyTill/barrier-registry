# Framework Failure Log

Documented failures found during stress testing. Purpose: examine patterns, prevent regressions, inform future framework design.

---

## Failure 001: False Gap — Agent claimed data didn't exist when it did
- **Date:** 2026-04-06
- **Framework:** ReAct v1 (old loop, Haiku 4.5)
- **Question:** "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Canada?"
- **Failure:** Agent stated "the database does NOT contain comparable Canadian federal or provincial data privacy requirements" — but 7 CAN/data_privacy records exist (PIPEDA [406], PHIPA [407], Alberta HIA [408], BC E-Health [409], Quebec [410, 411], OPC summary [435]).
- **Root cause:** Agent searched `data_privacy` for USA but never searched `data_privacy` for CAN. Treated zero results from a search it never ran as "data doesn't exist."
- **Fix applied:** Plan-then-execute architecture with required category injection ensures data_privacy is always searched for every country in the question.

## Failure 002: Wrong category name — search returned zero because category doesn't exist
- **Date:** 2026-04-06
- **Framework:** ReAct v1
- **Question:** Same as Failure 001
- **Failure:** Agent searched `cross_border_health` for CAN. Actual category is `cross_border`. Got zero results, concluded no cross-border data exists. Missed 4 records including USMCA [429].
- **Root cause:** Agent guessed category names instead of using actual names from the database. `cross_border_health` is the MEX category; CAN uses `cross_border`.
- **Fix applied:** Plan-then-execute pre-fetches real category names and validates them. Planner can only use categories that actually exist. Required category injection covers variants (`cross_border`, `cross_border_health`, `international_health`).

## Failure 003: Wrong country citations — Mexico records cited in US-Canada answer
- **Date:** 2026-04-06
- **Framework:** ReAct v1
- **Question:** Same as Failure 001
- **Failure:** Agent cited Record IDs 458, 459, 481 (US-Mexico Border Health Commission, Healthy Border 2020, CDC US-Mexico Binational Health Program) in an answer about US-Canada barriers. All three are country=MEX.
- **Root cause:** A broad keyword search pulled in Mexico records, and the agent didn't verify country attribution before citing them.
- **Fix applied:** Plan-then-execute searches by explicit country+category pairs. Synthesis prompt receives only records from searched countries.

## Failure 004: Premature final answer rejection wasted iterations
- **Date:** 2026-04-06
- **Framework:** ReAct v2 (patched loop)
- **Question:** "What are the US federal rules for prescribing controlled substances via telehealth?"
- **Failure:** Agent produced a good answer at iteration 3 with 2 searches. The framework's hard-coded minimum of 4 searches bounced it back. Agent then searched Mexico for a US-only question, wasting iterations until it hit max 12 without a final answer.
- **Root cause:** Minimum search count (4) was designed for cross-border questions but applied to all questions. No distinction between single-country and cross-border scope.
- **Fix applied:** Added `is_cross_border` detection. Single-country questions need 2 minimum, cross-border need 4. Ultimately replaced by plan-then-execute which eliminates this problem entirely.

## Failure 005: Search cap cut off agent before covering all categories
- **Date:** 2026-04-06
- **Framework:** ReAct v2 (patched loop)
- **Question:** "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Canada?"
- **Failure:** 8-search cap told the agent to wrap up before it could search CAN/drug_regulation, CAN/healthcare_access, CAN/insurance, CAN/cross_border. Missed 19 relevant records.
- **Root cause:** The cap was a band-aid to stop runaway iterations. But cross-border questions with 10+ relevant categories per country need more than 8 searches.
- **Fix applied:** Plan-then-execute has no cap — it runs every search in the validated plan. Required category injection guarantees critical categories are always included.

## Failure 006: Never searched CAN drug_regulation — missed controlled substance laws
- **Date:** 2026-04-06
- **Framework:** ReAct v2 AND first plan-then-execute run (planner omitted it)
- **Question:** Same as Failure 005
- **Failure:** Neither framework version searched CAN/drug_regulation. Missed Controlled Drugs and Substances Act [424], Telehealth Prescribing FAQ [425], Proposed Amendments [426]. Agent then listed "controlled substance prescribing rules across the US-Canada border" as a gap — but the data was there.
- **Root cause (ReAct):** Agent ran out of iterations. **Root cause (Plan-then-execute):** Planner (Haiku) judged drug_regulation wasn't relevant enough for a telehealth question. Wrong — prescribing is core to telehealth practice.
- **Fix applied:** REQUIRED_CATEGORIES list forces drug_regulation (and equivalents) to be searched for every country in the question, regardless of planner judgment. Framework injects it post-validation.

## Failure 007: Audio-only gap claim was false
- **Date:** 2026-04-06
- **Framework:** ReAct v2
- **Question:** "What are the US federal rules for prescribing controlled substances via telehealth?"
- **Failure:** Agent listed "Requirements for audio-only vs. video telehealth" as a data gap. Record 387 ("Audio-Only Telehealth Coverage — National Summary") exists and covers this.
- **Root cause:** Agent didn't search broadly enough within the USA/telehealth category to surface Record 387, or didn't recognize it as relevant when forming gap claims.
- **Fix applied:** Plan-then-execute retrieves ALL records in each category (no keyword narrowing), so Record 387 would be in the synthesis context. Agent can't claim a gap for data it was shown.

## Failure 008: Grader (Claude Code) praised failures without verifying
- **Date:** 2026-04-06
- **Framework:** N/A — this was a process failure, not a framework failure
- **Failure:** Claude Code graded the first US-Canada ReAct output as PASS on all 5 criteria without checking the database. The agent missed 7 CAN data_privacy records, 4 cross_border records, cited Mexico records — and the grader said "PASS" because the output "looked right."
- **Root cause:** Pattern matching on output format (structured, citations present, confidence stated) substituted for actual verification.
- **Fix applied:** Feedback memory saved: every grading must verify cited Record IDs against DB, query for categories the agent should have searched, and confirm gap claims by searching for what the agent says is missing.

---

## Patterns Observed

1. **ReAct agents trust their own search results too much.** Zero results from a search they ran = "data doesn't exist." Zero results from a search they never ran = also "data doesn't exist." The agent can't distinguish between these two cases.

2. **Category name guessing is fragile.** Different countries use different names for equivalent concepts (`cross_border` vs `cross_border_health` vs `international_health`). LLMs guess wrong.

3. **Caps and nudges are band-aids.** Every threshold we added (min searches, max searches, nudge timing) created a new failure mode. The agent either stopped too early or wasted iterations.

4. **Separating planning from execution eliminates most failures.** When the framework controls what gets searched (deterministic code) and the LLM only controls analysis (its strength), coverage failures drop to near zero.

5. **Required category injection catches planner blind spots.** Even good planners make judgment calls about relevance. For healthcare policy, some categories are always relevant regardless of the specific question. Hard-coding these as required is safer than trusting LLM judgment.
