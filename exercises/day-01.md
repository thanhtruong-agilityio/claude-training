# Day 01 exercises

## 1. Bug summary

- **Task:** Summarize a trip-planner-api bug: `Agent config not found for a registered agent after the cache was loaded`

| Ver | Prompt | What was wrong / good |
|---|---|---|
| v1 | Summarize this bug:<br><br>Agent config not found for a registered agent after the cache was loaded. | Summary matched the given line. Gave 3 generic likely causes. Wrongly guessed the message came from the Claude Code / agent harness (`.claude/agents/`), not the service. Ended by asking where I saw it, what I was doing, and for a stack trace |
| v2 | this is a bug in trip-planner-api, a FastAPI service that runs<br>LangGraph agents (create_trip / edit_trip graphs). Agent configs are<br>loaded from the database and cached in memory.<br><br>Summarize it in exactly 5 bullets:<br>1. Symptom (what the user or system sees)<br>2. Likely cause<br>3. Impact (who or what is affected)<br>4. How to reproduce<br>5. Suggested next step<br><br>Bug details:<br>Agent config not found for a registered agent after the cache was loaded. | Exactly 5 bullets in the requested order. Concrete symptom, repro and next step with file:line. Called the cause a hypothesis, "not reproduced", "haven't run this yet". Cited files and lines are real and correct |
| v3 | Context: trip-planner-api, a FastAPI service running LangGraph agents.<br>Agent configs are loaded from the database and cached in memory.<br><br>Before answering:<br>- State your assumptions.<br>- Ask me for anything missing instead of guessing.<br><br>Then summarize the bug in 5 bullets: symptom, likely cause, impact,<br>how to reproduce, suggested next step.<br><br>Rules:<br>- Label each bullet [FACT] if it comes directly from the details below,<br>or [GUESS] if you inferred it.<br>- Do not name any file, function or line number unless it appears in the<br>details below.<br><br>Bug details:<br>Agent config not found for a registered agent after the cache was loaded. | Listed assumptions and 6 missing-info questions first. Every bullet labeled [FACT]/[GUESS] (only the symptom is FACT). Named no files. Less specific than v2. Asked about registration order although the prompt already said "after the cache was loaded" |

### Where AI surprised me

**Good**
- v3 asked for what was missing instead of guessing, and labeled every bullet [FACT] or [GUESS]
- v2 labeled its cause as a hypothesis and said it had not run the repro; its file:line citations were real

**Bad**
- v1 guessed the message came from the Claude Code / agent harness, not the service -> property: working memory (session context bleeding in) -> fix: state the service and bug context in the prompt (v2)
- v1 listed generic causes with no evidence -> property: next-token (plausible, not grounded) -> fix: ask for [FACT]/[GUESS] labels (v3)

---

## 2. Explain a concept

- **Task:** Explain cache invalidation (TTL, write-through, event-based) using the case "item registered after the cache was loaded"

| Ver | Prompt | What was wrong / good |
|---|---|---|
| v1 | Explain cache invalidation. | Correct and thorough: 6 strategies, why it is hard (races, thundering herd, layers). Generic: did not touch my case (agent registered after cache load). Used "trip" examples that were not in the prompt. Row "write-around / explicit delete" mixes two ideas |
| v2 | Context: trip-planner-api, a FastAPI service that runs LangGraph agents.<br>Agent configs are loaded from the database and cached in memory.<br><br>Explain cache invalidation to a backend developer, in exactly 5 sections:<br>1. What it is (2 sentences)<br>2. Why it matters for this case: an agent is registered after the cache<br>   was loaded, and its config is not found<br>3. Three strategies: TTL, write-through, event-based invalidation<br>   (one line each)<br>4. Trade-offs per strategy (table: strategy \| pros \| cons)<br>5. Which one you would pick here, and why<br><br>Keep each section short and concrete. | Exactly 5 sections as asked. Section 2 solved my case and noted per-task caches. Added details not in the prompt: Redis and load-at-startup were right, ECS Fargate was wrong. Recommended "reload on miss", which the code already does |
| v3 | Context: trip-planner-api, a FastAPI service that runs LangGraph agents.<br>Agent configs are loaded from the database and cached in memory.<br><br>Before answering:<br>- State your assumptions.<br>- Ask me for anything missing instead of guessing.<br><br>Then explain cache invalidation to a backend developer, in exactly 5 sections:<br>1. What it is<br>2. Why it matters for this case: an agent is registered after the cache<br>   was loaded, and its config is not found<br>3. Three strategies: TTL, write-through, event-based invalidation<br>4. Trade-offs per strategy (table: strategy \| pros \| cons)<br>5. Which one you would pick here, and why<br><br>Rules:<br>- Label each section [GENERAL] if it is standard, widely accepted knowledge,<br>  or [GUESS] if it depends on how my service actually works.<br>- Do not name any file, function, library or version unless it appears<br>  in the details above.<br>- At the end, list what you are unsure about. | Listed 5 assumptions and 5 questions first. Labeled sections [GENERAL]/[GUESS]. Named no infrastructure. Added risks v2 missed (negative results cached, updates and deletes need invalidation). Answered with assumptions instead of waiting. Also recommended "reload on miss", which already exists |

### Where AI surprised me

**Good**
- v2 gave the right Redis and load-at-startup details without them being in the prompt
- v3 named no infrastructure, labeled sections [GENERAL]/[GUESS], and listed what it did not know

**Bad**
- v2 stated the service runs on ECS Fargate, which is wrong, and it was not in the prompt -> property: next-token (plausible specific, not grounded) -> fix: v3 rule "do not name any file, function, library or version unless it appears in the details"
- v2 and v3 both recommended "reload on cache miss" as the fix, but the code already does that -> property: knowledge (no access to my code under the v3 rule; v2 did not check) -> fix: give it the relevant code, or ask it to check the repo before recommending

---

## 3. Drafting task

- **Task:** Draft a ticket update (status comment) about the bug and the plan to handle it

| Ver | Prompt | What was wrong / good |
|---|---|---|
| v1 | Write a ticket update about this bug:<br><br>Agent config not found for a registered agent after the cache was loaded. | Explored the repo on its own and wrote a full status: fix commit, root cause, fix, remaining risks, test file. Every fact I checked was correct. Honest about limits (not confirmed on main, tests not re-run, not posted). Broke my "only use facts I give" criterion, but the extra facts were right |
| v2 | I'm a backend developer on trip-planner-api, a FastAPI service that runs<br>LangGraph agents. Write a status comment for the bug ticket [TICKET-ID].<br><br>Facts:<br>- Bug: Agent config not found for a registered agent after the cache<br>  was loaded.<br>- Who or what is affected: model calls for an agent that was added to<br>  AGENT_REGISTRY after the config cache was populated<br>- What I have done so far: fixed in commit 6691af0, which is on main; added a<br>  regression test in tests/core/test_agent_config_resolver.py<br>- Current finding: resolve_all() used to return the cached blob even if it<br>  lacked a registered agent; it now returns the cache only when its keys<br>  cover AGENT_REGISTRY_KEYS, otherwise it reloads from the DB<br>- Next step: confirm the fix is in the deployed build, then close the ticket<br>- Owner and target date: not decided yet<br>- Blockers: none<br><br>Format: use exactly these headings, one or two lines each:<br>Status, Findings, Impact, Next steps, Blockers.<br>Tone: neutral and factual, written for someone who has not followed the bug. | Exactly 5 headings, only my facts, no invented owner or date. Two small silent inferences ("deployment not yet confirmed", error message taken from the bug title) |
| v3 | I'm a backend developer on trip-planner-api, a FastAPI service that runs<br>LangGraph agents. Write a status comment for the bug ticket [TICKET-ID].<br><br>Before writing:<br>- State your assumptions.<br>- Ask me for anything missing instead of guessing.<br><br>Facts:<br>- Bug: Agent config not found for a registered agent after the cache<br>  was loaded.<br>- Who or what is affected: model calls for an agent that was added to<br>  AGENT_REGISTRY after the config cache was populated<br>- What I have done so far: fixed in commit 6691af0, which is on main; added a<br>  regression test in tests/core/test_agent_config_resolver.py<br>- Current finding: resolve_all() used to return the cached blob even if it<br>  lacked a registered agent; it now returns the cache only when its keys<br>  cover AGENT_REGISTRY_KEYS, otherwise it reloads from the DB<br>- Next step: confirm the fix is in the deployed build, then close the ticket<br>- Owner and target date: not decided yet<br>- Blockers: none<br><br>Format: use exactly these headings, one or two lines each:<br>Status, Findings, Impact, Next steps, Blockers.<br>Tone: neutral and factual, written for someone who has not followed the bug.<br><br>Rules:<br>- Use only the facts above. Do not add causes, dates, owners, or promises<br>  that I did not give you.<br>- Mark each Findings line [CONFIRMED] if it comes from my facts, or<br>  [HYPOTHESIS] if you inferred it.<br>- If a fact is missing, write "[TBD]" in that heading instead of filling it in.<br>- After the draft, list every statement you inferred. | Same content as v2 plus assumptions, [CONFIRMED]/[TBD], and a list of 3 inferred statements that exposed v2's two silent ones. Turned "not decided yet" into [TBD]. Asked questions but wrote the draft anyway |

### Where AI surprised me

**Good**
- v1 found the fix, root cause and test on its own, and every fact I checked was correct; it said what it had not confirmed
- v2 invented no owner or date even without a rule against it
- v3's "inferred" list exposed two small inferences that v2 made silently

**Bad**
- v2 slipped in two inferences (deployment not confirmed, error message taken from the bug title) without saying so -> property: next-token (plausible gap-filling) -> fix: v3 rule "list every statement you inferred"
