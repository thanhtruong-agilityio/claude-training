# Day 01 Mental model + Claude basics

- **Date:** 2026-10-12
- **Trainee:** thanh.truong
- **Branch:** `training/day-01`

**Status:** AI Fluency + AI capabilities and limitations done (lessons + quizzes). Claude 101 still pending.

---

## 1. Setup check

- [x] Signed in to claude.ai
- [x] Claude Desktop installed (Chat / Cowork / Code)
- [x] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### 2.1 AI Fluency: Framework and foundations

- [x] Introduction to AI Fluency
- [x] Why do we need AI Fluency?
- [x] The 4D Framework
- [x] Generative AI fundamentals
- [x] Capabilities & limitations
- [x] A closer look at Delegation
- [x] Project planning and Delegation
- [x] A closer look at Description
- [x] Effective prompting techniques
- [x] A closer look at Discernment
- [x] The Description–Discernment loop
- [x] A closer look at Diligence
- [x] Quiz + badge: https://academy.claude.com/verify/a5abc0e1f35c14fce0a79b55343657d8

### 2.2 AI capabilities and limitations (separate course)

- [x] Intro to AI Capabilities and limitations
- [x] What We Mean by AI
- [x] How AI Gets Its Character
- [x] Next Token Prediction
- [x] Knowledge
- [x] Working Memory
- [x] Steerability
- [x] When Properties Collide
- [x] Course quiz + badge: https://academy.claude.com/verify/08b8e2abb51286c0463bcaf514e8cff4

### 2.3 Claude 101

- [ ] Lessons 1–4 — *pending*

---

## 3. Key takeaways

**AI Fluency = effective, efficient, ethical, safe.** Framework over prompt tricks — tools change, competencies don't.

**3 engagement modes**
- **Automation** — AI executes a defined task
- **Augmentation** — AI as thinking partner
- **Agency** — AI runs independently; I define knowledge + behavior, not steps

**4D**

| D | One-liner | Sub-parts |
|---|---|---|
| Delegation | Decide what I do vs. AI does | Problem Awareness · Platform Awareness · Task Delegation |
| Description | Tell AI what, how, and how to behave | Product · Process · Performance |
| Discernment | Check output, reasoning, behavior | Product · Process · Performance |
| Diligence | Own it responsibly | Creation · Transparency · Deployment |

**How LLMs work (why verification beats trust)**
- Next-token prediction: pre-training → fine-tuning → inference
- Generates, doesn't retrieve → plausible ≠ correct
- Limits: knowledge cutoff, hallucination, context window, non-determinism, multi-step reasoning, no access to my data
- Mitigations: search/docs in context, run the code, keep sessions focused, RAG/tools/MCP, extended thinking

**Delegation heuristics**
- Experts in their field first, AI delegators second
- Work types: tedious-but-clear → automate · uncertain → augment · knowledge gap → AI researches, I verify · high-stakes → human
- Judgment signals: can't write acceptance criteria yet, context not in repo, hard to reverse, I own the outcome
- Test: *if AI is wrong in a plausible way, will I catch it before it matters?* Yes → delegate. No → mine.
- Skipping the sort = decisions get made by default

**Prompting (6 techniques)**
1. Give context (what + why + background)
2. Show examples
3. Specify constraints
4. Break into steps
5. Ask AI to think first
6. Define role / tone

Iterate with diagnosis, not retries. Secret weapon: ask AI to improve the prompt.

**Loop:** Describe → Discern → Refine (repeat) → Integrate (my expertise + final call).

---

**AI capabilities and limitations — machine side of the 4D**

4D = what *I* do. This course = the machine properties I'm responding to. Each property is a continuum: same mechanism → capability *and* limitation. Calibrated trust = locate the task, don't trust/distrust wholesale.

**Training fingerprints**
- Pre-training → document completer; fine-tuning → assistant
- Side effects: **sycophancy**, **verbosity**, **over-caution**, **confidence ≠ correctness**
- Counter: invite disagreement, ask for short answers, never read tone as reliability

**4 properties**

| Property | Works well | Breaks on | Fix |
|---|---|---|---|
| **Next token prediction** | Common patterns: summarize, reformat, explain | Specifics: names, dates, stats, citations, URLs | Verify specifics, use sources |
| **Knowledge** | Frequent, stable, pre-cutoff topics | Post-cutoff, niche, local, contested; stale defaults | Web search, RAG/MCP, supply docs |
| **Working memory** | Context fits, single focused session | Long docs/chats, lost-in-the-middle, new chat = blank slate | Front-load key info, chunk, standing context (project/CLAUDE.md) |
| **Steerability** | Short, concrete, verifiable instructions | Long reasoning (drift), letter-over-spirit, math | Checkpoints, state the goal, code execution, structured output |

**Common failures = two properties colliding**

| Symptom | Fix |
|---|---|
| Fake citation / wrong specific | Verify or use a tool with sources |
| Drifts in long chat | Re-supply context or start fresh |
| Followed instruction, missed intent | Restate the goal, not the instruction louder |
| Agrees instantly when I push back | Ask it to re-check on the merits |
| Confident wrong math | Offload to code |

