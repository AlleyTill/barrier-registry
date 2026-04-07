# Audit #001: US-Canada Cross-Border Agent Output
## Date: 2026-04-07
## Question: "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Canada?"
## Mode: --claude (Haiku plan, Opus synthesis)

---

## Pipeline Stats
- Searches planned: 11 keyword + 2 semantic
- Records retrieved: 77 unique
- Records cited in output: 58 unique IDs
- Backend: Claude (Haiku plan, Opus synthesis with extended thinking)

---

## Verification Results

### Record Existence: 58/58 PASS
Every cited Record ID exists in the database. Zero hallucinated IDs.

### Country Attribution: 58/58 PASS
Every record was attributed to the correct country (USA or CAN). Zero misattributions.

### Language Flags: 3/3 PASS
French-language records 400, 410, 411 correctly flagged. No French records missed.

### Gap Claims: 6/6 VALID
All gaps the agent listed are confirmed absent from the database:
1. US malpractice insurer policies on foreign jurisdiction claims — not in DB
2. Canadian immigration/work permit for foreign virtual care physicians — not in DB
3. Provincial fee schedules for out-of-country physician billing — not in DB
4. Temporary telemedicine registration for foreign-licensed physicians — not in DB
5. Enforcement actions or case law for unauthorized cross-border telehealth — not in DB
6. HIPAA adequacy determination or CAN-US data sharing MOUs — not in DB

Initial keyword search produced false positives (matching "Canadian" or "physician" broadly) but deep inspection confirmed none of those records contain the specific information claimed as gaps.

### Barrier Classifications: 10 barriers identified
| # | Classification | Description |
|---|---------------|-------------|
| 1 | PROHIBITION | Provincial licensure required |
| 2 | REGULATORY GAP | No CAN-US licensing compact |
| 3 | CONFLICT | No CMPA liability protection for foreign MDs |
| 4 | CONFLICT | Dual privacy compliance (HIPAA + PIPEDA) |
| 5 | PROHIBITION | Cannot prescribe controlled substances without CDSA auth |
| 6 | ASYMMETRY | No provincial health plan reimbursement for foreign providers |
| 7 | CONFLICT | Standard of care = patient's Canadian province |
| 8 | PROHIBITION | Prescriptions not fillable at Canadian pharmacies |
| 9 | ASYMMETRY | MCC credentialing required, no fast-track |
| 10 | PROHIBITION | BC and Quebec require local clinic affiliation |

All classifications are reasonable and supported by cited records.

---

## Failures Found

### 1. Uncited records that should have been cited (6 records)

| ID | Category | Title | Why it matters |
|----|----------|-------|---------------|
| 429 | cross_border | USMCA Healthcare and Pharmaceutical Provisions | Directly relevant trade agreement for US-CAN cross-border healthcare. Agent discussed barriers but missed the actual bilateral agreement. |
| 508 | clinical_standards | Canadian Task Force on Preventive Health Care Guidelines | Relevant to standard-of-care differences. Agent discussed standard of care (Barrier #7) but didn't cite the source of Canadian clinical guidelines. |
| 510 | clinical_standards | CanMEDS Physician Competency Framework | Relevant to credential recognition (CanMEDS vs ACGME). Agent mentioned credentialing but not why the frameworks differ. |
| 511 | health_workforce | CIHI Health Workforce Data and Trends | 6.5M Canadians lack a family doctor — drives demand for cross-border telehealth. Missing context. |
| 433 | healthcare_access | Bill S-5 Connected Care for Canadians Act (2026) | Federal interoperability legislation relevant to digital health barriers. |
| 423 | telehealth | CMPA Virtual Care Medico-Legal Guidance | Overlaps with ID:497 but more specific to virtual care. Minor miss. |

**Root cause:** The synthesis prompt tells the LLM to cite facts but doesn't explicitly tell it to cite supporting/contextual records. The agent nails direct regulatory citations but drops supplementary context.

**Fix:** Add to SYNTHESIZE_PROMPT: "When contextual records provide background that strengthens a barrier finding (workforce data, trade agreements, competency frameworks), cite them as supporting evidence."

### 2. Reasonable omissions (14 US state-level records) — NOT failures

IDs 372, 377-386, 387, 390, 391 are individual US state telehealth parity laws and modality summaries. For a cross-border question, the agent correctly focused on federal-level US rules (IMLC, HIPAA, Ryan Haight, DEA extensions). Individual state laws are noise in this context.

---

## Scorecard

| Metric | Score |
|--------|-------|
| Citation accuracy | 58/58 (100%) |
| Country attribution | 58/58 (100%) |
| Language flags | 3/3 (100%) |
| Gap validity | 6/6 (100%) |
| Recall (relevant records cited) | 58/64 relevant (91%) |
| Hallucinations | 0 |
| False gaps | 0 |

**Overall: PASS with 6 minor citation gaps (supporting context, not core findings)**

---

## Lessons for Future Audits
1. Gap verification keyword search must be narrow — broad keywords produce false positives
2. Check for records the agent SHOULD have cited, not just records it DID cite
3. Distinguish between core regulatory citations (must-have) and supporting context (nice-to-have)
4. State-level records are noise for cross-border questions — not a failure to omit them
5. The synthesis prompt needs a nudge to cite contextual/supporting records, not just direct regulatory matches
