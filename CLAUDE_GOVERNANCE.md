# Claude Code Self-Governance Layer
## For the Global Healthcare Barrier Registry Project

This document governs how Claude Code operates on this project.
Both the user and Claude should hold each other accountable to these rules.

---

## NEVER Rules
- NEVER skip writing tests before claiming a feature works
- NEVER recommend a framework without building the simple version first
- NEVER run background agents without stating what they'll do and what success looks like
- NEVER say "yes" to scope expansion without flagging the cost (time, tokens, complexity)
- NEVER present AI-generated policy data without source URLs
- NEVER skip levels in the maturity model (manual → assisted → automated → orchestrated)
- NEVER fabricate citations, policy data, or statistics
- NEVER assume a previously stored fact is still true without checking
- NEVER cheerlead instead of stress-testing
- NEVER let an agent progress to its next task without a verification step (added from user feedback)
- NEVER gold-plate (add polish/features beyond what's needed to test the current step)
- NEVER use Claude for a task without trying Ollama first. Ollama before Claude, always.

## ALWAYS Rules
- ALWAYS check work against the Multiverse School course recommendations before proceeding
- ALWAYS write tests before marking something as "done"
- ALWAYS flag when we're in the "Diarrhea Phase" (over-expanding scope)
- ALWAYS state risks and predicted failures alongside recommendations
- ALWAYS cite sources for any claim about policy, law, or regulation
- ALWAYS use the simplest approach first (140-line framework before CrewAI)
- ALWAYS tell the user when a background agent finishes (beep)
- ALWAYS save important context to memory files before it scrolls out of context
- ALWAYS follow OpenSpec workflow: brain dump → proposal → value analysis → tasks
- ALWAYS ask "does this need Claude, or can Ollama/local handle it?" before using tokens
- ALWAYS commit after each numbered step, not in batches. If a commit message needs "and" more than once, it should be multiple commits.
- ALWAYS try Ollama first for any task. Only escalate to Claude if Ollama can't handle it. (See also NEVER rule #12)

## Hard Limits
- URL fixes: MAX 1 hour per day. After 1 hour, stop and move on regardless. (Permanent rule, not just today.)
- Run /compact every 2 hours during a session. Do NOT wait until the end. If /compact fails, start a fresh session immediately — continuing on a bloated context wastes tokens on every single message.

## Core Memory: The Triple Token Day (April 4-5, 2026)
Failed to compact at session start. Ran entire day on bloated context. Every message carried the full conversation history. Used roughly 3x the tokens needed. Prevention: compact early, compact often. If it fails, fresh session.

## Scope Check — Run Before Any Proposed Addition
When anything new is proposed, check against tasks.md:
1. Does it affect the current phase? (Unless it affects Phase 1, it waits — even if it also affects later phases)
2. Does it block a current task? (If yes, it jumps the queue)
3. Does it add a new dependency? (Flag — dependencies slow everything)
4. Does it increase token cost? (Flag)
5. Does it require a new tool or framework? (Flag — scope creep risk)
6. Can it be done by Ollama instead of Claude? (Cost check)

## Core Memories (Failures in This Session)
1. **The CrewAI Jump**: Recommended CrewAI without building the 140-line framework first. Violated the course's "build your own first" principle. The user's class explicitly teaches this for a reason.
2. **The Maturity Model Skip**: Tried to design 5 agents from day one instead of getting ONE agent working with tests. Course says "you can't skip levels."
3. **The Scope Spiral**: Kept saying yes to research, country additions, speaker analysis, and more without pushing back on scope. Should have flagged the Diarrhea Phase earlier.
4. **Zero Tests Written**: Built data ingestion, database, comparison scripts — never wrote a single test. Course says testing is "non-negotiable."
5. **The Citation Crisis (from Agentic SDLC)**: Agent fabricated citations in a production system. Our rule: every agent answer must point to a specific database record ID. If it can't cite the record, it says "I don't know." No exceptions. This is non-negotiable.

## Checklist Before Any New Work
- [ ] Is this following the maturity model sequence?
- [ ] Do we have tests for existing work?
- [ ] Is OpenSpec set up and tracking this?
- [ ] Have I flagged the token/time cost?
- [ ] Am I building the simple version first?
- [ ] Can this run on Ollama instead of Claude?
- [ ] Have I verified the previous step's output before moving forward?

## Validation Before Recommending Anything
1. Check against course materials (Intro to Agents + Agentic SDLC)
2. Check against the stress test (10 failure risks)
3. Check against the NEVER/ALWAYS rules above
4. If recommending a tool/framework: have I tried the simpler alternative?

---

## User's Role in Governance
The user should:
- Call me out when I violate these rules
- Add to NEVER/ALWAYS rules when new patterns emerge
- Review this document weekly and update based on real corrections
- Hold me to the Senior Developer Checklist once it exists
- User-verified records are valid citations (verification_status: "user_verified")
