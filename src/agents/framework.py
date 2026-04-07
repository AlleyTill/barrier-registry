"""
Agent framework: Plan-Then-Execute architecture.
Step 1 (Plan): LLM generates a structured search plan from the question + real categories.
Step 2 (Execute): Framework runs every search deterministically. No LLM involved.
Step 3 (Synthesize): LLM analyzes all results and writes the cited answer.

Backends: Claude (cloud), Ollama (local).
Tools query the SQLite database only — no training data answers.
"""

import json
import os
import re
import httpx
from dotenv import load_dotenv
from src.database.models import get_session, HealthPolicy, WHOIndicator
from src.validation.thresholds import evaluate_answer_confidence
try:
    from src.data_ingestion.embeddings import search_semantic
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False
    search_semantic = None

load_dotenv(override=True)

OLLAMA_URL = "http://localhost:11434/api/chat"
CLAUDE_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL_PLAN = "claude-haiku-4-5-20251001"  # planning is simple, haiku is fine
CLAUDE_MODEL_SYNTHESIZE = "claude-opus-4-6"  # synthesis needs the best reasoning
OLLAMA_MODEL = "qwen3:8b"


# --- TOOLS ---

def search_policies(country: str = "", category: str = "", keyword: str = "") -> list[dict]:
    """Search health_policies table. Filter by country (ISO alpha-3), category, or keyword in title/summary."""
    session = get_session()
    query = session.query(HealthPolicy).filter(HealthPolicy.verification_status != "failed")
    if country:
        query = query.filter(HealthPolicy.country == country.upper())
    if category:
        query = query.filter(HealthPolicy.category.ilike(f"%{category}%"))
    if keyword:
        query = query.filter(
            (HealthPolicy.title.ilike(f"%{keyword}%")) | (HealthPolicy.summary.ilike(f"%{keyword}%"))
        )
    results = query.all()
    session.close()
    return [
        {
            "record_id": r.id, "country": r.country, "source": r.source,
            "title": r.title, "summary": (r.summary or "")[:500],
            "original_language": r.original_language, "last_updated": r.last_updated,
            "verification_status": r.verification_status, "source_url": r.source_url,
        }
        for r in results
    ]


def search_who_indicators(country: str = "", indicator: str = "") -> list[dict]:
    """Search WHO indicators by country or indicator name."""
    session = get_session()
    query = session.query(WHOIndicator)
    if country:
        query = query.filter(WHOIndicator.country == country.upper())
    if indicator:
        query = query.filter(WHOIndicator.indicator_name.ilike(f"%{indicator}%"))
    results = query.limit(50).all()
    session.close()
    return [
        {"id": r.id, "country": r.country, "indicator": r.indicator_name, "year": r.year, "value": r.value}
        for r in results
    ]


def list_categories(country: str = "") -> list[dict]:
    """List all policy categories in the database, with record counts. Optionally filter by country."""
    session = get_session()
    query = session.query(HealthPolicy.category).filter(HealthPolicy.verification_status != "failed")
    if country:
        query = query.filter(HealthPolicy.country == country.upper())
    cats = query.all()
    session.close()
    counts = {}
    for (cat,) in cats:
        counts[cat] = counts.get(cat, 0) + 1
    return [{"category": k, "count": v} for k, v in sorted(counts.items())]


def check_confidence(records: list = None) -> dict:
    """Evaluate whether retrieved records meet data sufficiency thresholds."""

    class FakeRecord:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)

    if not records:
        records = []

    if records and isinstance(records[0], (int, float)):
        session = get_session()
        db_records = session.query(HealthPolicy).filter(HealthPolicy.id.in_([int(r) for r in records])).all()
        session.close()
        fake = [FakeRecord({
            "record_id": r.id, "country": r.country, "title": r.title,
            "original_language": r.original_language, "last_updated": r.last_updated,
            "verification_status": r.verification_status,
        }) for r in db_records]
    else:
        fake = [FakeRecord(r) for r in records]

    result = evaluate_answer_confidence(fake)
    return {"level": result.level, "count": result.record_count, "caveats": result.caveats, "can_answer": result.can_answer}


def search_policies_semantic(query: str, country: str = "", category: str = "", limit: int = 20) -> list[dict]:
    """Semantic search over policy embeddings. Finds records by meaning, not just keywords.
    Use when keyword search might miss relevant records (e.g., 'prescribing rules' finds 'controlled substances')."""
    if not HAS_SEMANTIC:
        return []
    return search_semantic(query=query, country=country, category=category, limit=limit)


TOOLS = {
    "search_policies": search_policies,
    "search_policies_semantic": search_policies_semantic,
    "search_who_indicators": search_who_indicators,
    "list_categories": list_categories,
    "check_confidence": check_confidence,
}


# --- SPECIALTY-BASED RELEVANCE FILTERING ---

# When a single category search returns more than this many records,
# use two-pass specialty filtering instead of dumping everything.
MAX_RECORDS_PER_CATEGORY = 50

# Medical specialty taxonomy — maps keyword patterns to specialty groups.
# Used to tag large result sets (like NCDs) and filter by relevance.
SPECIALTY_MAP = {
    "cardiovascular": [
        "heart", "cardiac", "cardio", "pacemaker", "defibrillator", "aortic",
        "valve", "artery", "arterial", "vascular", "aneurysm", "angina",
        "atrial", "ventricular", "coronary", "ecg", "ekg", "electrocardiograph",
        "hypertension", "blood pressure", "thrombosis", "embolism", "stent",
        "bypass", "ablation", "counterpulsation", "revascularization",
        "transcatheter", "mitral", "tricuspid", "icd", "tavr", "laac",
        "his bundle", "carotid body", "endocardial electrical stimulation",
        "carotid function", "ventriculectomy",
    ],
    "oncology": [
        "cancer", "tumor", "oncolog", "chemotherapy", "carcinoma", "neoplast",
        "malignant", "metastasis", "metastatic", "biopsy", "radiation",
        "lymphoma", "melanoma", "sarcoma", "leukemia", "mastectomy",
        "lumpectomy", "mammogram", "prostate screen", "colorectal screen",
        "pap smear", "cervical", "car t-cell", "car-t", "chimeric antigen",
        "photodynamic", "actinic keratosis", "stem cell transplant",
    ],
    "respiratory": [
        "lung", "pulmonary", "respiratory", "bronch", "cpap", "sleep apnea",
        "oxygen", "ventilat", "tracheostomy", "copd", "pneumo", "airway",
        "thoracic", "spirometry", "nebuliz",
    ],
    "neurology": [
        "brain", "neural", "neuro", "seizure", "epilepsy", "parkinson",
        "tremor", "alzheimer", "dementia", "eeg", "deep brain stimulation",
        "vagus nerve", "multiple sclerosis", "stroke", "cranial",
        "intracranial", "stereotax", "cerebral", "l-dopa", "levodopa",
        "cochlear", "speech-language", "dysphagia", "melodic intonation",
        "electroconvulsive", "bell's palsy", "facial nerve paralysis",
        "evoked response", "nerve tract",
    ],
    "musculoskeletal": [
        "bone", "joint", "spine", "spinal", "lumbar", "orthoped", "fracture",
        "arthroscop", "osteo", "disc", "vertebr", "scoliosis", "musculoskel",
        "tendon", "ligament", "osteogenic", "prosthetic shoe",
        "meniscus", "manipulation",
    ],
    "renal_urological": [
        "renal", "kidney", "dialysis", "urinar", "bladder", "urol",
        "nephro", "esrd", "transplant", "incontinence", "prostat",
        "pelvic floor", "catheter", "capd", "ultrafiltration",
        "hemoperfusion", "hemofiltration", "uroflowmet",
    ],
    "endocrine_metabolic": [
        "diabet", "insulin", "glucose", "thyroid", "obesity", "bariatric",
        "nutrition", "metabolic", "hemoglobin a1c", "glycated",
        "enteral", "parenteral",
    ],
    "gastrointestinal": [
        "gastric", "intestin", "esophag", "colon", "liver", "hepat",
        "pancrea", "abdomin", "fecal", "cholecyst", "gallbladder",
        "hernia", "gastrophotograph", "endoscopy",
    ],
    "ophthalmology": [
        "eye", "ocular", "ophthalm", "retina", "cataract", "intraocular",
        "lens", "corneal", "vitrectomy", "keratoplasty", "visual",
        "scleral shell", "perimetry", "endothelial cell",
    ],
    "hematology": [
        "blood", "hematolog", "transfusion", "platelet", "coagul",
        "anemia", "erythropoie", "hemophilia", "immunoglobulin",
        "iron therapy", "heparin",
    ],
    "infectious_disease": [
        "hiv", "aids", "hepatitis", "infection", "virus", "viral",
        "immunodeficiency", "prep ", "antibiotic", "sti ", "sexually transmitted",
    ],
    "pain_rehabilitation": [
        "pain", "tens", "nerve stimulat", "rehabilitation", "electric stimul",
        "biofeedback", "acupuncture", "diathermy",
    ],
    "diagnostic_imaging": [
        "mri", "magnetic resonance", "pet scan", "pet ", "fdg", "ct scan",
        "computed tomography", "ultrasound", "x-ray", "imaging", "radiolog",
        "tomography", "spect", "angiography", "thermography",
        "transillumination", "diaphanography",
    ],
    "behavioral_health": [
        "alcohol", "substance", "drug abuse", "tobacco", "smoking",
        "depression", "mental health", "psychiatric", "psycholog",
        "counseling", "behavioral", "narcotic addiction", "withdrawal treatment",
    ],
    "wound_skin": [
        "wound", "skin", "dermal", "ulcer", "decubitus", "burn",
        "psoriasis", "hyperbaric oxygen",
    ],
    "general_preventive": [
        "screening", "preventive", "wellness", "routine", "immunization",
        "vaccine", "prophylaxis",
    ],
    "laboratory_diagnostics": [
        "sequencing", "ngs", "lipid testing", "prothrombin time",
        "gamma glutamyl", "histocompatibility", "plethysmograph",
        "conduction threshold", "lymphocyte mitogen", "sweat test",
        "cytotoxic food", "pharmacogenomic", "laboratory test",
        "diagnostic breath", "food allergy", "hair analysis",
        "hemorheograph", "obsolete or unreliable", "challenge ingestion",
        "microvolt t-wave",
    ],
    "dme_assistive": [
        "durable medical equipment", "speech generating", "mobility assistive",
        "air-fluidized", "seat elevation", "wheelchair", "pneumatic compress",
        "infusion pump", "hospital bed", "seat lift", "ibot",
        "white cane", "continence aid", "gravlee",
    ],
    "surgical_procedures": [
        "angioplasty", "abortion", "wrong body part", "wrong patient",
        "wrong surgical", "laser procedure", "sterilization", "embolization",
        "gender dysphoria", "gender reassignment", "ultrasonic surgery",
        "plastic surgery", "moon face", "cavernous nerve", "vabra aspirator",
    ],
    "immunology": [
        "immune globulin", "photopheresis", "apheresis", "cellular immunotherapy",
        "cellular therapy", "antigen", "sublingual admin",
        "histamine therapy", "dmso", "dimethyl sulfoxide",
    ],
    "therapies_rehab": [
        "verteporfin", "photosensitive drug", "transcendental meditation",
        "pritikin", "infrared therapy", "chelation", "thermogenic",
        "impotence",
    ],
    "administrative": [
        "consultation", "physician's office", "patient education",
        "pronouncement of death", "home health nurse",
        "podiatrist", "skilled nursing facility",
    ],
}


def _tag_specialties(record: dict) -> set[str]:
    """Tag a record with matching medical specialties based on title and summary."""
    text = f"{record.get('title', '')} {record.get('summary', '')}".lower()
    tags = set()
    for specialty, keywords in SPECIALTY_MAP.items():
        if any(kw in text for kw in keywords):
            tags.add(specialty)
    return tags


def _detect_question_specialties(question: str) -> set[str]:
    """Detect which medical specialties a question is about."""
    q = question.lower()
    matches = set()
    for specialty, keywords in SPECIALTY_MAP.items():
        if any(kw in q for kw in keywords):
            matches.add(specialty)
    return matches


def _filter_by_specialty(records: list[dict], question: str) -> list[dict]:
    """Two-pass specialty filter for large result sets.
    Pass 1: Detect which specialties the question is about.
    Pass 2: Return only records matching those specialties.
    Fallback: if no specialty matches, return records with direct keyword overlap."""
    question_specialties = _detect_question_specialties(question)

    if question_specialties:
        # Pass 2: keep records whose specialties overlap with the question's
        filtered = [r for r in records if _tag_specialties(r) & question_specialties]
        if filtered:
            return filtered

    # No specialty matched — return empty. Every record should be tagged to at least
    # one specialty. If zero match, the question isn't about any NCD-relevant topic.
    return []


# --- LLM BACKENDS ---

def _call_ollama(messages: list[dict], model: str = None, timeout: float = 600.0) -> str:
    """Call Ollama API and return the assistant's reply."""
    response = httpx.post(
        OLLAMA_URL,
        json={"model": model or OLLAMA_MODEL, "messages": messages, "stream": False},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _call_claude(messages: list[dict], model: str = None, thinking: bool = False) -> str:
    """Call Claude API and return the assistant's reply.
    If thinking=True, enables extended thinking and returns both thinking and text.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("paste"):
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to .env file.")

    system_msg = ""
    chat_messages = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            chat_messages.append({"role": m["role"], "content": m["content"]})

    request_body = {
        "model": model or CLAUDE_MODEL_SYNTHESIZE,
        "max_tokens": 16384,
        "system": system_msg,
        "messages": chat_messages,
    }

    if thinking:
        request_body["thinking"] = {
            "type": "enabled",
            "budget_tokens": 10000,
        }

    response = httpx.post(
        CLAUDE_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=request_body,
        timeout=300.0,
    )
    response.raise_for_status()
    content_blocks = response.json()["content"]

    thinking_text = ""
    answer_text = ""
    for block in content_blocks:
        if block["type"] == "thinking":
            thinking_text = block["thinking"]
        elif block["type"] == "text":
            answer_text = block["text"]

    if thinking and thinking_text:
        return thinking_text, answer_text
    return answer_text


# --- STEP 1: PLAN ---

def _get_available_categories() -> dict[str, list[str]]:
    """Get real categories per country from the database."""
    session = get_session()
    results = session.query(HealthPolicy.country, HealthPolicy.category).filter(
        HealthPolicy.verification_status != "failed"
    ).distinct().all()
    session.close()

    by_country = {}
    for country, category in results:
        by_country.setdefault(country, []).append(category)
    for country in by_country:
        by_country[country] = sorted(set(by_country[country]))
    return by_country


PLAN_PROMPT = """You are a search planner for a healthcare policy database.

Given a user's question and the ACTUAL categories available in the database, generate a search plan.

AVAILABLE CATEGORIES BY COUNTRY:
{categories}

YOUR JOB: Return a JSON array of searches to execute. Each search is an object with:
- "country": ISO alpha-3 code (USA, CAN, MEX, GBR)
- "category": EXACT category name from the list above
- "keyword": optional keyword to narrow results (use sparingly)

RULES:
- ONLY use category names that exist in the list above. Do NOT invent categories.
- For cross-border questions, search ALL relevant categories in BOTH countries.
- Include every category that COULD be relevant. More searches is better than missing data.
- For a cross-border question between 2 countries with 6 categories each, expect 10-16 searches.
- For a single-country question, expect 3-8 searches.
- Include keyword searches only when the question mentions specific terms (drug names, act names, etc.)

Return ONLY the JSON array, no other text. Example:
[
  {{"country": "USA", "category": "telehealth"}},
  {{"country": "CAN", "category": "telehealth"}},
  {{"country": "USA", "category": "medical_licensing"}}
]"""


def _generate_plan(question: str, backend: str = "claude", verbose: bool = False) -> list[dict]:
    """Step 1: Generate a search plan from the question + real categories."""
    categories = _get_available_categories()
    cat_str = "\n".join(
        f"  {country}: {', '.join(cats)}"
        for country, cats in sorted(categories.items())
    )

    messages = [
        {"role": "system", "content": PLAN_PROMPT.format(categories=cat_str)},
        {"role": "user", "content": question},
    ]

    if backend == "claude":
        reply = _call_claude(messages, model=CLAUDE_MODEL_PLAN)
    else:
        reply = _call_ollama(messages)

    if verbose:
        print(f"[PLAN] Raw planner output:\n{reply}\n")

    # Parse JSON array from reply
    # Strip markdown code fences if present
    cleaned = re.sub(r'```json\s*', '', reply)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = cleaned.strip()

    try:
        plan = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find a JSON array in the response
        match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if match:
            plan = json.loads(match.group())
        else:
            raise ValueError(f"Planner did not return valid JSON: {reply}")

    # Validate plan and inject required categories
    valid_plan = _validate_plan(plan, categories, verbose, question=question)
    return valid_plan


def _detect_countries(question: str, available_countries: list[str]) -> list[str]:
    """Detect which countries are referenced in the question."""
    q = question.lower()
    # Pad with spaces so word-boundary keywords match at start/end of string
    q_padded = f" {q} "
    # Replace common punctuation with spaces so "US," "US." "US?" all match "us "
    for ch in ",.?!;:()[]{}\"'":
        q_padded = q_padded.replace(ch, " ")
    # Normalize multiple spaces
    while "  " in q_padded:
        q_padded = q_padded.replace("  ", " ")

    # Map common names/keywords to ISO codes
    country_keywords = {
        "USA": ["us ", "u.s.", "usa", "united states", "american", "federal"],
        "CAN": ["canad", "ontario", "quebec", "british columbia", "alberta",
                "saskatchewan", "manitoba", "nova scotia", "new brunswick",
                "newfoundland", "prince edward"],
        "MEX": ["mexic", "mexico"],
        "GBR": ["uk ", "u.k.", "gbr", "united kingdom", "britain", "england", "nhs"],
    }
    found = []
    for code, keywords in country_keywords.items():
        if code in available_countries and any(kw in q_padded for kw in keywords):
            found.append(code)
    return found


# Categories that MUST be searched for every country in the question.
# Missing any of these in a healthcare policy query could cause real-world harm.
# Each entry maps a required concept to all known category names for it across countries.
REQUIRED_CATEGORIES = [
    # Drug/substance regulation — different names across countries
    ["drug_regulation"],
    # Medical licensing — who can legally practice
    ["medical_licensing"],
    # Data privacy — patient information protection
    ["data_privacy"],
    # Telehealth — core topic for virtual care queries
    ["telehealth"],
    # Cross-border — any category covering cross-border movement
    ["cross_border", "cross_border_health", "international_health"],
    # Healthcare access — foundational laws (Canada Health Act, etc.)
    ["healthcare_access"],
    # Insurance/coverage — who pays
    ["insurance"],
    # Medical liability — malpractice, jurisdictional liability
    ["medical_liability"],
]


def _validate_plan(plan: list[dict], categories: dict[str, list[str]],
                    verbose: bool = False, question: str = "") -> list[dict]:
    """Validate the search plan, then inject required categories the planner missed."""
    valid = []
    seen = set()

    for search in plan:
        country = search.get("country", "").upper()
        category = search.get("category", "")
        keyword = search.get("keyword", "")

        if country not in categories:
            if verbose:
                print(f"[PLAN] Skipping invalid country: {country}")
            continue

        if category not in categories[country]:
            if verbose:
                print(f"[PLAN] Skipping invalid category: {country}/{category}")
            continue

        # Deduplicate
        key = (country, category, keyword)
        if key in seen:
            continue
        seen.add(key)

        valid.append({"country": country, "category": category, "keyword": keyword})

    # Inject required categories for each country in the question
    countries_in_question = _detect_countries(question, list(categories.keys()))
    if not countries_in_question:
        # Fallback: use all countries the planner referenced
        countries_in_question = list(set(s["country"] for s in valid))

    for country in countries_in_question:
        if country not in categories:
            continue
        for required_group in REQUIRED_CATEGORIES:
            # Check if any variant from this group is already in the plan
            already_covered = any(
                (country, variant, "") in seen or
                any(s["country"] == country and s["category"] == variant for s in valid)
                for variant in required_group
            )
            if already_covered:
                continue
            # Find which variant exists in this country's categories
            for variant in required_group:
                if variant in categories[country]:
                    key = (country, variant, "")
                    if key not in seen:
                        seen.add(key)
                        valid.append({"country": country, "category": variant, "keyword": ""})
                        if verbose:
                            print(f"[PLAN] Injected required category: {country}/{variant}")
                    break

    if verbose:
        print(f"[PLAN] Validated plan: {len(valid)} searches")
        for s in valid:
            kw = f" (keyword: {s['keyword']})" if s.get('keyword') else ""
            print(f"  -> {s['country']}/{s['category']}{kw}")
        print()

    return valid


# --- STEP 2: EXECUTE ---

def _execute_plan(plan: list[dict], verbose: bool = False, question: str = "") -> dict:
    """Step 2: Run every search in the plan. No LLM involved.
    Large result sets are filtered by relevance to the question."""
    all_results = {}
    all_records = []

    for i, search in enumerate(plan):
        country = search["country"]
        category = search["category"]
        keyword = search.get("keyword", "")

        if verbose:
            kw = f", keyword='{keyword}'" if keyword else ""
            print(f"[EXECUTE] Search {i+1}/{len(plan)}: {country}/{category}{kw}")

        results = search_policies(country=country, category=category, keyword=keyword)

        # Filter large result sets by medical specialty to avoid context flooding
        if len(results) > MAX_RECORDS_PER_CATEGORY and question:
            filtered = _filter_by_specialty(results, question)
            if verbose:
                specialties = _detect_question_specialties(question)
                print(f"  -> {len(results)} records found, filtered to {len(filtered)} by specialty {sorted(specialties) if specialties else '(keyword fallback)'}")
            results = filtered
        elif verbose:
            print(f"  -> {len(results)} records found")

        key = f"{country}/{category}"
        if keyword:
            key += f" (keyword: {keyword})"
        all_results[key] = results
        all_records.extend(results)

    # Semantic search: supplement keyword results with embedding-based matches
    # Run one semantic search per country to catch what keywords missed
    keyword_ids = {r["record_id"] for r in all_records}
    countries_searched = sorted(set(s["country"] for s in plan))

    for country in countries_searched:
        if verbose:
            print(f"[EXECUTE] Semantic search: {country} (question-based)")
        try:
            sem_results = search_policies_semantic(
                query=question or "healthcare policy",
                country=country,
                limit=15,
            )
            # Only keep results NOT already found by keyword search
            new_results = [r for r in sem_results if r["record_id"] not in keyword_ids]
            if new_results:
                key = f"{country}/semantic"
                all_results[key] = new_results
                all_records.extend(new_results)
                for r in new_results:
                    keyword_ids.add(r["record_id"])
                if verbose:
                    print(f"  -> {len(new_results)} NEW records found (not in keyword results)")
            elif verbose:
                print(f"  -> 0 new records (all already found by keyword search)")
        except Exception as e:
            if verbose:
                print(f"  -> Semantic search failed: {e} (continuing with keyword results only)")

    # Deduplicate records by record_id
    seen_ids = set()
    unique_records = []
    for r in all_records:
        if r["record_id"] not in seen_ids:
            seen_ids.add(r["record_id"])
            unique_records.append(r)

    if verbose:
        print(f"\n[EXECUTE] Total: {len(unique_records)} unique records from {len(plan)} keyword + {len(countries_searched)} semantic searches\n")

    # Run confidence check
    confidence = check_confidence(unique_records)

    return {
        "results_by_search": all_results,
        "all_records": unique_records,
        "confidence": confidence,
        "search_count": len(plan),
    }


# --- STEP 3: SYNTHESIZE ---

COUNTRY_CONTEXT = {
    "USA": (
        "US Policy Context: Federal system. CMS/Medicare is federal, but medical licensing "
        "is state-by-state (50 states + DC + territories). HIPAA is the federal health privacy "
        "framework. DEA regulates controlled substances (schedules I-V). Interstate Medical "
        "Licensure Compact (IMLC) covers 42+ states for expedited cross-state licensing. "
        "Telehealth reimbursement rules are set by CMS for Medicare, but states regulate "
        "practice standards. FSMB oversees state medical boards."
    ),
    "CAN": (
        "Canada Policy Context: Federal-provincial system under the Canada Health Act. "
        "Medical licensing is provincial — each province has its own College of Physicians "
        "and Surgeons (CPSO in Ontario, CPSBC in BC, etc.). Privacy is split: PIPEDA (federal "
        "private-sector) plus provincial health privacy laws (PHIPA in ON, HIA in AB, etc.). "
        "Controlled substances regulated under CDSA (federal). Drug coverage is NOT part of "
        "the Canada Health Act — provincial formularies vary widely. CMPA provides medico-legal "
        "protection (not insurance) for physicians. No national telehealth license — each "
        "province requires separate registration."
    ),
    "MEX": (
        "Mexico Policy Context: Federal system with state-level health laws under the Ley "
        "General de Salud. Medical licensing requires Cédula Profesional from SEP. COFEPRIS "
        "regulates drugs, devices, and health products. No dedicated telehealth law — "
        "telemedicine recognized under NOM-257-SSA1-2014. LFPDPPP governs personal data "
        "privacy. Public health insurance through IMSS (formal workers), ISSSTE (government "
        "workers), and IMSS-Bienestar (uninsured). Medical liability under civil and "
        "administrative law (CONAMED handles arbitration)."
    ),
    "GBR": (
        "UK Policy Context: National Health Service (NHS) provides universal coverage funded "
        "by taxation. General Medical Council (GMC) handles medical licensing nationally. "
        "Care Quality Commission (CQC) regulates health providers including telehealth. "
        "Data protection under UK GDPR + Data Protection Act 2018. MHRA regulates medicines "
        "and medical devices. Post-Brexit, UK-EU healthcare agreements are bilateral."
    ),
}


CROSS_BORDER_PROMPT = """
CROSS-BORDER ANALYSIS INSTRUCTIONS (multiple countries detected in records):

Countries in this query: {countries}
Records per country: {country_counts}

{country_contexts}

You MUST structure your answer as a CROSS-BORDER COMPARISON:

For each policy area relevant to the question (e.g., licensing, telehealth rules, privacy,
prescribing/controlled substances, liability, insurance/coverage):

1. **[Policy Area]**
{country_bullets}
   - **Barrier:** [What specific conflict, gap, or mismatch exists between these systems]
   - **Classification:** [One of: PROHIBITION — explicitly banned in one jurisdiction |
     REGULATORY GAP — one country has no rule on this topic |
     CONFLICT — countries have rules that contradict each other |
     ASYMMETRY — one country regulates this area, another doesn't]

If no records exist for one country on a policy area, state: "No records in database for
[Country] on [topic]" — do NOT infer policy from silence. Absence of a record does NOT mean
absence of a rule.

After the comparison sections, include:

### Barrier Summary
| # | Barrier | Classification | Countries |
|---|---------|---------------|-----------|
| 1 | [Short description] | PROHIBITION / REGULATORY GAP / CONFLICT / ASYMMETRY | [which countries] |

### Data Asymmetry Notice
{asymmetry_notice}
"""


SYNTHESIZE_PROMPT = """You are the Policy Researcher agent for the Global Healthcare Barrier Registry.

You have been given ALL relevant records from the database for a user's question. Your job is to synthesize a comprehensive, cited answer.

RULES:
- You can ONLY use the records provided below. NEVER answer from general knowledge.
- Cite every fact with [Record ID: N]. No citation = don't say it.
- Label inferences: "Inference (not directly stated in any record): ..."
- Flag non-English records: "[language: X — verify with original source]"
- Flag records 2+ years old with a staleness warning. ONLY list Record IDs in staleness
  or language warnings if you actually cited them in your answer — never reference uncited records.
- If 0 records are relevant: say "I don't know" + why.
- If 1-2 records: answer with caveat "coverage may be incomplete."
- NEVER give legal advice. Say "consult a licensed attorney."
- ALWAYS cite the foundational/primary legislation for each country (e.g., Canada Health Act,
  Ley General de Salud, HIPAA) — not just specific provisions or subsections. If a record
  contains a country's core healthcare law, cite it even if you also cite more specific records.
- Cite supporting context records: trade agreements (USMCA/T-MEC), bilateral cooperation,
  workforce data, competency frameworks, patient rights, medical tourism regulations, and
  national program overviews. These strengthen findings even if not the primary regulatory source.
- When counting non-English records or stale records in your confidence section, count ONLY
  records you actually cited — do not estimate. Use the language metadata provided in each record.
- List data gaps at the end: what the records do NOT cover on this topic.
  IMPORTANT: A gap is something the DATABASE DOES NOT HAVE. Do NOT list something as a gap if a record below covers it.
- State confidence: HIGH / MODERATE / LOW with reasoning.

OUTPUT FORMAT:
  **1. [Topic]**
  [Fact from records] [Record ID: N]
  *Inference (not directly stated in any record):* [Your reasoning]

  **2. [Next Topic]**
  ...

  ### What the database does NOT have (gaps):
  - [gap 1]
  - [gap 2]

  ### Confidence: MODERATE
  [Reasoning]

SEARCHES PERFORMED:
{searches_performed}

CONFIDENCE CHECK:
{confidence}

DATABASE RECORDS:
{records}"""


def _is_cross_border(execution_results: dict) -> bool:
    """Return True if execution results contain records from 2+ countries."""
    countries = set(r["country"] for r in execution_results.get("all_records", []))
    return len(countries) >= 2


def _get_country_counts(records: list[dict]) -> dict[str, int]:
    """Count records per country."""
    counts = {}
    for r in records:
        c = r["country"]
        counts[c] = counts.get(c, 0) + 1
    return counts


def _build_cross_border_section(execution_results: dict) -> str:
    """Build the cross-border prompt section from execution results."""
    records = execution_results.get("all_records", [])
    country_counts = _get_country_counts(records)
    countries = sorted(country_counts.keys())

    # Build country context block
    contexts = []
    for c in countries:
        if c in COUNTRY_CONTEXT:
            contexts.append(COUNTRY_CONTEXT[c])
    country_contexts = "\n\n".join(contexts)

    # Build asymmetry notice
    max_count = max(country_counts.values())
    min_count = min(country_counts.values())
    if max_count > min_count * 3:
        sparse = [c for c, n in country_counts.items() if n == min_count]
        dense = [c for c, n in country_counts.items() if n == max_count]
        asymmetry_notice = (
            f"WARNING: Significant data asymmetry detected. "
            f"{', '.join(dense)} has {max_count} records vs {', '.join(sparse)} "
            f"with {min_count} records. Coverage for {', '.join(sparse)} may be "
            f"incomplete — barriers may exist that are not captured in this database."
        )
    else:
        asymmetry_notice = "Record counts are roughly balanced across countries."

    counts_str = ", ".join(f"{c}: {n}" for c, n in sorted(country_counts.items()))

    # Build per-country bullet template for the comparison format
    country_bullets = "\n".join(
        f"   - **{c}:** [State the rule with citation] [Record ID: N]"
        for c in countries
    )

    return CROSS_BORDER_PROMPT.format(
        countries=", ".join(countries),
        country_counts=counts_str,
        country_contexts=country_contexts,
        country_bullets=country_bullets,
        asymmetry_notice=asymmetry_notice,
    )


def _synthesize(question: str, execution_results: dict, backend: str = "claude", verbose: bool = False) -> str:
    """Step 3: LLM synthesizes the answer from all retrieved records."""
    # Format searches performed
    searches_str = "\n".join(
        f"  - {key}: {len(results)} records"
        for key, results in execution_results["results_by_search"].items()
    )

    # Format records
    records_str = json.dumps(execution_results["all_records"], default=str, indent=2)

    # Format confidence
    confidence_str = json.dumps(execution_results["confidence"], default=str, indent=2)

    system = SYNTHESIZE_PROMPT.format(
        searches_performed=searches_str,
        confidence=confidence_str,
        records=records_str,
    )

    # Pre-compute record stats so the LLM doesn't have to count
    all_records = execution_results.get("all_records", [])
    non_english = [r for r in all_records if r.get("original_language", "en") != "en"]
    if non_english:
        lang_counts = {}
        for r in non_english:
            lang = r.get("original_language", "unknown")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        lang_summary = ", ".join(f"{n} in {l}" for l, n in sorted(lang_counts.items()))
        system += f"\n\nRECORD LANGUAGE STATS (pre-computed from full result set):\n"
        system += f"Non-English records available: {len(non_english)} ({lang_summary}).\n"
        system += f"Non-English Record IDs: {[r['record_id'] for r in non_english]}\n"
        system += f"IMPORTANT: In your confidence section, only count non-English records from this list that you ACTUALLY CITED in your answer.\n"

    # Append cross-border instructions when records span multiple countries
    if _is_cross_border(execution_results):
        cross_border_section = _build_cross_border_section(execution_results)
        system += cross_border_section
        if verbose:
            countries = sorted(set(r["country"] for r in all_records))
            print(f"[SYNTHESIZE] Cross-border mode: {', '.join(countries)}")

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]

    if verbose:
        print("[SYNTHESIZE] Sending to LLM for analysis...")

    if backend == "claude":
        result = _call_claude(messages, model=CLAUDE_MODEL_SYNTHESIZE, thinking=True)
        if isinstance(result, tuple):
            thinking_text, reply = result
            if verbose and thinking_text:
                print(f"\n--- THINKING ---\n{thinking_text}\n--- END THINKING ---\n")
        else:
            reply = result
    else:
        reply = _call_ollama(messages)

    return reply


# --- MAIN ENTRY POINT ---

def run_agent(question: str, verbose: bool = False, backend: str = "claude") -> str:
    """Run the plan-then-execute agent pipeline.
    backend: 'claude', 'ollama', or 'hybrid' (Ollama plans, Claude synthesizes)
    """
    plan_backend = backend
    synth_backend = backend

    if backend == "hybrid":
        plan_backend = "ollama"
        synth_backend = "claude"

    if verbose:
        print(f"{'='*60}")
        print(f"PLAN-THEN-EXECUTE PIPELINE")
        if backend == "hybrid":
            print(f"Plan: Ollama ({OLLAMA_MODEL}) | Synthesis: Claude ({CLAUDE_MODEL_SYNTHESIZE})")
        else:
            print(f"Backend: {backend}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")

    # Step 1: Plan
    if verbose:
        print("--- STEP 1: PLANNING ---")
    plan = _generate_plan(question, backend=plan_backend, verbose=verbose)

    if not plan:
        return "Planning failed: no valid searches generated. Check that the question references countries in the database."

    # Step 2: Execute
    if verbose:
        print("--- STEP 2: EXECUTING SEARCHES ---")
    results = _execute_plan(plan, verbose=verbose, question=question)

    # Step 3: Synthesize
    if verbose:
        print("--- STEP 3: SYNTHESIZING ANSWER ---")
    answer = _synthesize(question, results, backend=synth_backend, verbose=verbose)

    return answer


def run_agent_detailed(question: str, verbose: bool = False, backend: str = "claude",
                       on_step=None) -> dict:
    """Run the plan-then-execute pipeline and return structured results for UI consumption.
    Returns dict with: question, backend, plan, execution_results, answer, countries, confidence.
    on_step: optional callback(step_name, detail) for progress reporting.
    """
    plan_backend = backend
    synth_backend = backend
    if backend == "hybrid":
        plan_backend = "ollama"
        synth_backend = "claude"

    def _report(step, detail=""):
        if on_step:
            on_step(step, detail)

    # Step 1: Plan
    _report("plan", "Generating search plan...")
    plan = _generate_plan(question, backend=plan_backend, verbose=verbose)
    if not plan:
        return {
            "question": question, "backend": backend, "plan": [],
            "execution_results": {}, "answer": "Planning failed: no valid searches generated.",
            "countries": [], "confidence": {"level": "no_data", "can_answer": False},
        }
    _report("plan_done", f"{len(plan)} searches planned")

    # Step 2: Execute
    _report("execute", f"Searching {len(plan)} categories + semantic...")
    results = _execute_plan(plan, verbose=verbose, question=question)
    record_count = len(results.get("all_records", []))
    _report("execute_done", f"{record_count} records found")

    # Step 3: Synthesize
    _report("synthesize", "Analyzing records and identifying barriers...")
    answer = _synthesize(question, results, backend=synth_backend, verbose=verbose)
    _report("synthesize_done", "Analysis complete")

    countries = sorted(set(r["country"] for r in results.get("all_records", [])))

    return {
        "question": question,
        "backend": backend,
        "plan": plan,
        "execution_results": results,
        "answer": answer,
        "countries": countries,
        "confidence": results.get("confidence", {}),
        "record_count": record_count,
        "search_count": results.get("search_count", 0),
        "is_cross_border": len(countries) >= 2,
    }


# --- LEGACY REACT LOOP (kept for comparison testing) ---

def run_agent_react(question: str, max_iterations: int = 12, verbose: bool = False, backend: str = "ollama") -> str:
    """Legacy ReAct loop. Kept for A/B comparison with plan-then-execute."""
    llm_call = _call_claude if backend == "claude" else _call_ollama

    react_system = """You are the US Policy Researcher agent for the Global Healthcare Barrier Registry.

RULES:
- You can ONLY use data from the database via tools. NEVER answer from general knowledge.
- Cite every fact with [Record ID: N]. No citation = don't say it.
- Label inferences: "Inference (not directly stated in any record): ..."
- Flag non-English records: "[language: X — verify with original source]"
- Flag records 2+ years old with a staleness warning.
- If 0 records found: say "I don't know" + what you searched.
- NEVER give legal advice. Say "consult a licensed attorney."
- List data gaps at the end.
- State confidence: HIGH / MODERATE / LOW with reasoning.

Available tools (call ONE per turn using JSON):
1. search_policies(country?, category?, keyword?) — Search policy database.
2. search_who_indicators(country?, indicator?) — Search WHO health indicators.
3. list_categories(country?) — List policy categories with counts.
4. check_confidence(records) — Evaluate data sufficiency.

To call a tool: {"tool": "tool_name", "args": {"param": "value"}}
When done: FINAL ANSWER: followed by your answer."""

    messages = [
        {"role": "system", "content": react_system},
        {"role": "user", "content": question},
    ]
    tool_calls_made = 0

    for i in range(max_iterations):
        if verbose:
            print(f"\n--- Iteration {i + 1}/{max_iterations} ({backend}) ---")

        reply = llm_call(messages)
        if verbose:
            print(f"Agent: {reply[:200]}...")

        if "FINAL ANSWER:" in reply:
            return reply.split("FINAL ANSWER:", 1)[1].strip()

        tool_call = _parse_tool_call(reply)
        if tool_call:
            tool_name, args = tool_call
            if tool_name in TOOLS:
                if verbose:
                    print(f"Calling: {tool_name}({args})")
                result = TOOLS[tool_name](**args)
                tool_calls_made += 1
                result_str = json.dumps(result, default=str)
                if len(result_str) > 4000:
                    result_str = result_str[:4000] + f"... (truncated, {len(result)} total results)"
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"Tool result ({tool_name}):\n{result_str}"})
            else:
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"Error: Unknown tool '{tool_name}'. Available: {list(TOOLS.keys())}"})
        else:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "Please call a tool or provide your FINAL ANSWER: with citations."})

    return f"Agent reached max iterations ({max_iterations}) without a final answer."


def _parse_tool_call(text: str) -> tuple[str, dict] | None:
    """Extract a tool call JSON from the agent's response."""
    matches = re.findall(r'\{[^{}]*"tool"[^{}]*(?:\{[^{}]*\}[^{}]*)?\}', text)
    for match in matches:
        try:
            parsed = json.loads(match)
            if "tool" in parsed:
                return parsed["tool"], parsed.get("args", {})
        except json.JSONDecodeError:
            continue
    return None


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    use_claude = "--claude" in args
    use_hybrid = "--hybrid" in args
    use_local = "--local" in args
    use_react = "--react" in args
    args = [a for a in args if a not in ("--claude", "--hybrid", "--local", "--react")]

    q = " ".join(args) if args else "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Canada?"

    if use_claude:
        b = "claude"
    elif use_local:
        b = "ollama"
    else:
        # Hybrid is the default — best quality (local plan + cloud synthesis)
        b = "hybrid"

    mode_label = "react (legacy)" if use_react else "plan-then-execute"
    if b == "hybrid":
        mode_label += f" | Plan: {OLLAMA_MODEL} | Synthesis: {CLAUDE_MODEL_SYNTHESIZE}"

    print(f"\nQuestion: {q}")
    print(f"Mode: {mode_label}\n")

    if use_react:
        answer = run_agent_react(q, verbose=True, backend=b)
    else:
        answer = run_agent(q, verbose=True, backend=b)

    print(f"\n{'='*60}\nFINAL ANSWER:\n{'='*60}\n{answer}")
