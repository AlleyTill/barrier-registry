"""
TASK-005: 140-line agent framework using Ollama (llama3).
Simple think → act → observe loop with max_iterations guard.
Tools query the SQLite database only — no training data answers.
"""

import json
import re
import httpx
from src.database.models import get_session, HealthPolicy, WHOIndicator
from src.validation.thresholds import evaluate_answer_confidence

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"
MAX_ITERATIONS_DEFAULT = 5


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


def check_confidence(records: list[dict]) -> dict:
    """Evaluate whether retrieved records meet data sufficiency thresholds."""

    class FakeRecord:
        def __init__(self, d):
            for k, v in d.items():
                setattr(self, k, v)

    fake = [FakeRecord(r) for r in records]
    result = evaluate_answer_confidence(fake)
    return {"level": result.level, "count": result.record_count, "caveats": result.caveats, "can_answer": result.can_answer}


TOOLS = {
    "search_policies": search_policies,
    "search_who_indicators": search_who_indicators,
    "check_confidence": check_confidence,
}

TOOL_DESCRIPTIONS = """Available tools (call ONE per turn using JSON):
1. search_policies(country?, category?, keyword?) — Search policy database. country=ISO alpha-3 (USA, CAN, MEX).
2. search_who_indicators(country?, indicator?) — Search WHO health indicators.
3. check_confidence(records) — Evaluate data sufficiency. Pass the records list from a previous search.

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
- If 0 records found: say "I don't know" + what you searched + why it's empty.
- If 1-2 records: answer with caveat "coverage may be incomplete."
- NEVER give legal advice. Say "consult a licensed attorney."
- List data gaps at the end: what the database does NOT have on this topic.
- State confidence: HIGH / MODERATE / LOW with reasoning.

WORKFLOW: Search the database (multiple searches if needed), check confidence, then give your final answer."""


# --- AGENT LOOP ---

def run_agent(question: str, max_iterations: int = MAX_ITERATIONS_DEFAULT, verbose: bool = False) -> str:
    """Run the agent loop: think → act → observe, up to max_iterations."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + TOOL_DESCRIPTIONS},
        {"role": "user", "content": question},
    ]

    for i in range(max_iterations):
        if verbose:
            print(f"\n--- Iteration {i + 1}/{max_iterations} ---")

        response = httpx.post(
            OLLAMA_URL,
            json={"model": MODEL, "messages": messages, "stream": False},
            timeout=120.0,
        )
        response.raise_for_status()
        reply = response.json()["message"]["content"]

        if verbose:
            print(f"Agent: {reply[:200]}...")

        # Check for final answer
        if "FINAL ANSWER:" in reply:
            return reply.split("FINAL ANSWER:", 1)[1].strip()

        # Try to parse tool call
        tool_call = _parse_tool_call(reply)
        if tool_call:
            tool_name, args = tool_call
            if tool_name in TOOLS:
                if verbose:
                    print(f"Calling: {tool_name}({args})")
                result = TOOLS[tool_name](**args)
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
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What barriers would a US-licensed doctor face trying to provide telehealth services to a patient in Mexico?"
    print(f"\nQuestion: {q}\n")
    answer = run_agent(q, verbose=True)
    print(f"\n{'='*60}\nFINAL ANSWER:\n{'='*60}\n{answer}")
