# Day 01 Mental model + Claude basics

- **Date:** 2026-10-12
- **Trainee:** thanh.truong
- **Branch:** `training/day-01`

**Status:** AI Fluency + AI capabilities and limitations done (lessons + quizzes). Claude 101 lessons 1–12 done; lesson 13 + quiz pending.

**4Ds:** https://claude.ai/artifact/YanKZK7FtZwivZzKSQWeqR

**Claude 101:** https://claude.ai/code/artifact/60f1d227-730f-4aaa-a729-061d61cf1e70

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

- [x] What is Claude? 
- [x] Your first conversation with Claude 
- [x] Getting better results getting-better-results
- [x] How you'll work with Claude on your desktop 
- [x] Introduction to projects introduction-to-projects
- [x] Creating with artifacts creating-with-artifacts
- [x] Working with skills working-with-skills
- [x] Connecting your tools connecting-your-tools
- [x] Enterprise search enterprise-search
- [x] Research for deep dives 
- [x] Claude in action: use-cases by role 
- [x] Other ways to work with Claude
- [x] course quiz + badge: https://academy.claude.com/verify/5bf1aec64de285c15a3de1fbfa8388c5

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


---

**1. What it is and where it runs**

| Concept | Meaning | Why it matters |
|---|---|---|
| Constitutional AI | Principle-based alignment; avoids harmful output, keeps behavior transparent | Safety ≠ correctness; still verify |
| Steerable | Tone, role, behavior set by prompt | = "define role/tone" technique |
| Thinking | Step-by-step reasoning before answering | Multi-step problems; adds latency |
| Context window | 200K+ tokens (~500 pages), up to 1M on paid plans/supported models | Still lost-in-the-middle risk |
| Surfaces | claude.ai · Code · Slack (Tag) · Design · M365 · Chrome · Cowork | Match tool to where the work lives |

**2. Prompting + iterating**
- Prompt = **stage** (role, goal, background) + **task** (action) + **rules** (style, tone, examples) = Description in 4D
- Uploads (PDF, DOCX, CSV, TXT, PNG, JPEG) are a context shortcut
- Model: **Sonnet** default · Opus for hardest multi-step · extended thinking only when needed · changing model = new chat
- Persistent: Settings > Account > Instructions for Claude · Settings > Memory (on by default Free/Pro/Max, off by default Team/Enterprise until Owner allows)
- Pencil icon = edit + resubmit a message

| Symptom | Cause | Fix |
|---|---|---|
| Too generic | Missing context | Add audience, role, constraints |
| Too long/short | Claude guesses length | State length |
| Wrong format | Content understood, layout not | Show example / describe structure |
| Confident but wrong | Plausible errors on specifics | Verify, ask sources/confidence, enable web search |
| Wrong tone | Tone undescribed | Describe it or paste a sample |


**3. Persistent context: Projects vs Skills vs Connectors **

| | Holds | Applies | Example |
|---|---|---|---|
| **Project** | Knowledge (files) + instructions + own chats | Every chat in the project | Brand guidelines hub |
| **Skill** | A process (steps, order, method) | When invoked (Claude auto-selects) | Excel/Word/PPT/PDF creation, QBR workflow |
| **Connector (MCP)** | Live access to external tools | Per request, scoped to my permissions | Drive, Slack, Jira, Asana |
| **Enterprise search** | Pre-built project over org tools | "Ask {Org}" in sidebar | Policy, onboarding, status |
