"""
TASK-005: Agent framework with Ollama (llama3) and Claude backends.
Simple think → act → observe loop with max_iterations guard.
Tools query the SQLite database only — no training data answers.
"""

import json
import os
import re
import httpx
from dotenv import load_dotenv
from src.database.models import get_session, HealthPolicy, WHOIndicator
from src.validation.thresholds import evaluate_answer_confidence

load_dotenv(override=True)

OLLAMA_URL = "http://localhost:11434/api/chat"
CLAUDE_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # cheapest for testing the loop
OLLAMA_MODEL = "llama3"
MAX_ITERATIONS_DEFAULT = 12


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
    """Evaluate whether retrieved records meet data sufficiency thresholds.
    Accepts list of record dicts OR list of record IDs (will look them up).
    """

    class FakeRecord:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)

    if not records:
        records = []

    # If passed record IDs (ints), look them up from the database
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


TOOLS = {
    "search_policies": search_policies,
    "search_who_indicators": search_who_indicators,
    "list_categories": list_categories,
    "check_confidence": check_confidence,
}

TOOL_DESCRIPTIONS = """Available tools (call ONE per turn using JSON):
1. search_policies(country?, category?, keyword?) — Search policy database. country=ISO alpha-3 (USA, CAN, MEX). All params optional. Use ONE or TWO filters at a time, not all three — narrow searches miss records.
2. search_who_indicators(country?, indicator?) — Search WHO health indicators.
3. list_categories(country?) — List all policy categories with counts. Call this FIRST to see what's in the database.
4. check_confidence(records) — Evaluate data sufficiency. Pass the records list from a previous search.

To call a tool, respond with ONLY this JSON (no other text):
{"tool": "tool_name", "args": {"param": "value"}}

When you have enough data, respond with FINAL ANSWER: followed by your answer."""


# --- SYSTEM PROMPT ---

SYSTEM_PROMPT = """You are the US Policy Researcher agent for the Global Healthcare Barrier Registry.

RULES:
- You can ONLY use data from the database via tools. NEVER answer from general knowledge.
- Cite every fact with [Record ID: N]. No citation = don't say it.
- Label inferences: "Inference (not directly stated in any record): ..."
- Flag non-English records: "[language: X — verify with original source]"
- Flag records 2+ years old with a staleness warning.
- If 0 records found after thorough searching: say "I don't know" + what you searched + why it's empty.
- If 1-2 records: answer with caveat "coverage may be incomplete."
- NEVER give legal advice. Say "consult a licensed attorney."
- List data gaps at the end: what the database does NOT have on this topic.
- State confidence: HIGH / MODERATE / LOW with reasoning.

SEARCH STRATEGY — THIS IS CRITICAL:
- FIRST call list_categories() to see what categories exist.
- For cross-border questions, you MUST search BOTH countries separately.
- Do MULTIPLE searches: one per relevant category per country.
- Use only ONE or TWO filters per search (country+category OR country+keyword). Three filters = too narrow.
- Do NOT give a FINAL ANSWER until you have searched at least 4 different category/country combinations.
- A cross-border question needs 6-8 searches minimum.

EXAMPLE SEARCH SEQUENCE for "US doctor telehealth to Mexico":
  1. list_categories()
  2. search_policies(country="USA", category="telehealth")
  3. search_policies(country="MEX", category="telehealth")
  4. search_policies(country="USA", category="medical_licensing")
  5. search_policies(country="MEX", category="medical_licensing")
  6. search_policies(country="USA", category="data_privacy")
  7. search_policies(country="MEX", category="data_privacy")
  8. search_policies(country="USA", category="drug_regulation")

OUTPUT FORMAT (you MUST follow this exactly):
  **1. [Topic]**
  [Fact from database] [Record ID: 374]
  *Inference (not directly stated in any record):* [Your reasoning]

  **2. [Next Topic]**
  ...

  ### What the database does NOT have (gaps):
  - [gap 1]
  - [gap 2]

  ### Confidence: MODERATE
  [Reasoning]

WORKFLOW:
1. list_categories() to see what's available
2. Multiple search_policies() calls — at least 4-8 searches across countries and categories
3. check_confidence() on your combined results
4. FINAL ANSWER with record IDs cited for EVERY fact, inferences labeled, gaps listed"""


# --- LLM BACKENDS ---

def _call_ollama(messages: list[dict]) -> str:
    """Call Ollama API and return the assistant's reply."""
    response = httpx.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
        timeout=300.0,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _call_claude(messages: list[dict]) -> str:
    """Call Claude API and return the assistant's reply."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key.startswith("paste"):
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to .env file.")

    # Claude API uses system param separately
    system_msg = ""
    chat_messages = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            chat_messages.append({"role": m["role"], "content": m["content"]})

    response = httpx.post(
        CLAUDE_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": CLAUDE_MODEL,
            "max_tokens": 4096,
            "system": system_msg,
            "messages": chat_messages,
        },
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


# --- AGENT LOOP ---

def run_agent(question: str, max_iterations: int = MAX_ITERATIONS_DEFAULT, verbose: bool = False, backend: str = "ollama") -> str:
    """Run the agent loop: think → act → observe, up to max_iterations.
    backend: 'ollama' or 'claude'
    """
    llm_call = _call_claude if backend == "claude" else _call_ollama

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + TOOL_DESCRIPTIONS},
        {"role": "user", "content": question},
    ]
    tool_calls_made = 0
    all_records = []  # Track all retrieved records for grading

    for i in range(max_iterations):
        if verbose:
            print(f"\n--- Iteration {i + 1}/{max_iterations} ({backend}) ---")

        reply = llm_call(messages)

        if verbose:
            print(f"Agent: {reply[:200]}...")

        # Check for final answer — but reject if too few searches done
        if "FINAL ANSWER:" in reply:
            if tool_calls_made < 4:
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"You have only done {tool_calls_made} searches. Cross-border questions need at least 4-8 searches across BOTH countries and multiple categories. Keep searching before giving your final answer. Search the other country and more categories."})
                continue
            return reply.split("FINAL ANSWER:", 1)[1].strip()

        # Try to parse tool call
        tool_call = _parse_tool_call(reply)
        if tool_call:
            tool_name, args = tool_call
            if tool_name in TOOLS:
                if verbose:
                    print(f"Calling: {tool_name}({args})")
                result = TOOLS[tool_name](**args)
                tool_calls_made += 1
                # Track policy records for grading
                if tool_name == "search_policies" and isinstance(result, list):
                    all_records.extend(result)
                result_str = json.dumps(result, default=str)
                # Cap observation size to avoid blowing context
                if len(result_str) > 4000:
                    result_str = result_str[:4000] + f"... (truncated, {len(result)} total results)"
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"Tool result ({tool_name}):\n{result_str}"})
            else:
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": f"Error: Unknown tool '{tool_name}'. Available: {list(TOOLS.keys())}"})
        else:
            # No tool call and no final answer — nudge the agent
            messages.append({"role": "assistant", "content": reply})
            if tool_calls_made >= 6:
                messages.append({"role": "user", "content": f"You have done {tool_calls_made} searches — that is enough. Please provide your FINAL ANSWER: now with record ID citations for every fact, inferences labeled, gaps listed, and confidence stated."})
            else:
                messages.append({"role": "user", "content": "Please either call a tool using JSON format or provide your FINAL ANSWER: with citations."})

    return f"Agent reached max iterations ({max_iterations}) without a final answer. Last response:\n{reply}"


def _parse_tool_call(text: str) -> tuple[str, dict] | None:
    """Extract a tool call JSON from the agent's response."""
    # Find JSON objects that contain "tool" — handle one level of nested braces for args
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
    args = sys.argv[1:]
    use_claude = "--claude" in args
    args = [a for a in args if a != "--claude"]
    q = " ".join(args) if args else "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Mexico?"
    b = "claude" if use_claude else "ollama"
    print(f"\nQuestion: {q}")
    print(f"Backend: {b}\n")
    answer = run_agent(q, verbose=True, backend=b)
    print(f"\n{'='*60}\nFINAL ANSWER:\n{'='*60}\n{answer}")
