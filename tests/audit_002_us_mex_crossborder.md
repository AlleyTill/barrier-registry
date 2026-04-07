# Audit #002: US-Mexico Cross-Border Agent Output
## Date: 2026-04-07
## Question: "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Mexico?"
## Mode: --claude (Haiku plan, Opus synthesis)

---

## Pipeline Stats
- Searches planned: 13 keyword + 2 semantic
- Records retrieved: 67 unique
- Records cited in output: 48 unique IDs
- Backend: Claude (Haiku plan, Opus synthesis with extended thinking)

---

## Verification Results

### Record Existence: 48/48 PASS
Every cited Record ID exists in the database. Zero hallucinated IDs.

### Country Attribution: 48/48 PASS
Every record is USA or MEX as expected. Zero misattributions.

### Language Flags: MINOR INACCURACY
- Agent claimed "~30 records are from non-English (Spanish) sources"
- Actual Spanish records cited: 22
- Agent overestimated by 8. All 22 actual Spanish records ARE Spanish in the DB.
- No Spanish records were missed (not flagged when they should have been).
- **Severity: Low** — overcounting is safer than undercounting for translation warnings.

### Gap Claims: 9/9 VALID (after deep verification)
All gaps the agent listed are confirmed absent from the database:
1. Mexican immigration/temporary practice permits for foreign physicians — VALID
2. USMCA/T-MEC professional services mutual recognition — VALID
3. Mexican state-level telehealth regulations — VALID (state health laws exist but contain no telehealth-specific rules)
4. COFEPRIS enforcement actions against foreign telehealth providers — VALID
5. US state rules on treating patients outside the US (international) — VALID
6. Cross-border telehealth pilot programs or special zones — VALID
7. Professional liability insurance for cross-border telehealth — VALID
8. Informed consent requirements specific to cross-border telehealth — VALID
9. Language requirements for medical practice/documentation in Mexico — VALID

Initial keyword search produced false positives on 7 of 9 gaps, but deep inspection confirmed none of those records actually contain the specific information claimed as gaps.

### Barrier Classifications: 8 barriers identified
| # | Classification | Description |
|---|---------------|-------------|
| 1 | PROHIBITION | No Mexican license pathway for US doctors (Cédula required) |
| 2 | REGULATORY GAP | No dedicated telehealth law in Mexico; US rules domestic-only |
| 3 | CONFLICT | Dual privacy regimes (HIPAA vs LFPDPPP) |
| 4 | PROHIBITION | US prescriptions not valid in Mexican pharmacies |
| 5 | REGULATORY GAP | No liability framework for cross-border telehealth |
| 6 | ASYMMETRY | No reimbursement pathway in either country |
| 7 | REGULATORY GAP | Bilateral health cooperation doesn't cover clinical telehealth |
| 8 | ASYMMETRY | Different drug regulatory systems (FDA vs COFEPRIS) |

All classifications are reasonable and supported by cited records.

---

## Failures Found

### 1. Spanish record count overestimate (MINOR)
Agent said "~30 records are from non-English (Spanish) sources" but only 22 of the 48 cited records are Spanish. Overcounting by 8. Low severity — conservative direction (warns more, not less).

### 2. Uncited records that should have been cited

**Notable misses (8 records):**

| ID | Category | Title | Why it matters |
|----|----------|-------|---------------|
| 350 | healthcare_access | Ley General de Salud (General Health Law) | Mexico's PRIMARY healthcare law. Agent referenced it indirectly (Title XII, Title VIII Bis) but never cited the core law record itself. |
| 351 | healthcare_access | Ley General de Salud — Texto Vigente Consolidado | Consolidated text with all amendments through 2025. |
| 368 | healthcare_access | Mexico Medical Tourism and Cross-Border Healthcare Regulations | DIRECTLY relevant — covers COFEPRIS standards for cross-border healthcare, JCI accreditation. |
| 438 | clinical_standards | NOM-004-SSA3-2012 — Clinical Records | Documentation standards for medical encounters. Relevant to telehealth documentation requirements. |
| 450 | patient_rights | Carta de los Derechos Generales de los Pacientes | Patient rights charter — relevant to consent and patient protections. |
| 472 | digital_health | CENETEC Dirección de Telesalud | Mexico's national telehealth program. Agent cited ID:474 (CENETEC guide) but not the program overview. |
| 485 | medical_tourism | JCI-Accredited Hospitals and Medical Tourism Standards | Cross-border healthcare infrastructure in border cities. Supporting context. |
| 468 | international_health | WHO-Mexico Country Cooperation 2024-2025 | International health cooperation context. |

**Root cause:** Same pattern as Audit #001 — agent cites direct regulatory records but misses foundational laws (Ley General de Salud core record) and supporting context (medical tourism, patient rights charter, national telehealth program overview).

### 3. Reasonable omissions

**USA (4 records):** IDs 372, 387, 390, 391 — proposed legislation, audio-only coverage, store-and-forward, RPM summaries. Modality-specific US records are noise for a cross-border question. Same pattern as Audit #001. NOT failures.

**MEX (19 records):** State health laws (462-466), specific NOMs (blood disposal, emergency equipment), disability inclusion law, palliative care, bioethics, biosimilars, OECD pricing analysis, WHO/PAHO cooperation. These are peripheral to the core cross-border telehealth question. Reasonable omissions.

---

## Scorecard

| Metric | Score |
|--------|-------|
| Citation accuracy | 48/48 (100%) |
| Country attribution | 48/48 (100%) |
| Language flags | 22/22 flagged correctly, but count overclaimed (~30 vs actual 22) |
| Gap validity | 9/9 (100%) |
| Recall (core records cited) | 48/56 relevant (86%) |
| Hallucinations | 0 |
| False gaps | 0 |

**Overall: PASS with 8 supporting-context misses and minor Spanish count overestimate**

---

## Comparison with Audit #001 (US-Canada)

| Metric | Audit #001 (US-CAN) | Audit #002 (US-MEX) |
|--------|--------------------|--------------------|
| Records cited | 58 | 48 |
| Citation accuracy | 100% | 100% |
| Country attribution | 100% | 100% |
| Gap validity | 6/6 (100%) | 9/9 (100%) |
| Recall | 91% | 86% |
| Hallucinations | 0 | 0 |
| Notable misses | 6 supporting context | 8 supporting context + foundational law |

**Pattern confirmed across both audits:**
1. Zero hallucinations — the "ONLY use records provided" instruction works
2. Core regulatory citations are accurate and well-attributed
3. Supporting context records (trade agreements, foundational laws, workforce data, patient rights) get dropped
4. Language flag counts can be overclaimed (conservative — safe direction)
5. Gap claims are consistently valid after deep verification

## Lessons
1. The "cite supporting context" prompt fix (added after Audit #001) didn't fully solve the problem for Mexico — agent still missed foundational Ley General de Salud and patient rights records
2. Consider adding: "Always cite the foundational/primary legislation for each country in the query, not just the specific regulatory provisions" to the synthesis prompt
3. Mexico's richer dataset (79 records, 24 categories) means more potential misses than Canada's smaller set — the agent triages by relevance, which is correct, but drops too many supporting records
