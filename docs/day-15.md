# Day 15 Review, Merge, Demo (Final Checkpoint)

- **Date:** 2026-10-29
- **Trainee:** thanh.truong
- **Branch:** `training/day-15`

**Status:** In progress. Course notes for "Building Effective Human Agent Teams" lessons 1, 2 and 4 are in; "Building with the Claude API" lessons Accessing the API, Getting an API key, Multi-turn conversations, System prompts, Temperature, Response streaming, Structured data, Prompt evaluation, A typical eval workflow, Generating test datasets, Running the eval and Model-based grading noted; capstone items below are not ticked until done.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Building Effective Human Agent Teams

- [x] Why multiplayer AI matters
- [x] How multiplayer agents differ
- [ ] What a strong team looks like (not noted yet)
- [x] Organizational checklist
- [x] Practical ways to start
- [x] Course quiz

---

## 3. Exercises

### Morning: review and merge

- [ ] Cross-review: Dev reviews QA's test code, QA reviews a Dev PR, BA checks merged behavior against the acceptance criteria
- [ ] Gaps found become same-day tickets
- [ ] Merge the work, tag a release, run the deploy
- [ ] Remote Control (`/rc`) or Dispatch demo: approve and steer a Claude session from the phone

### Afternoon: demo, retro, playbook

- [ ] Pair demo (10 min, no slides): ticket, plan, PR, review, tests, artifact, shipping
- [ ] Retro: items to standardize (`CLAUDE.md` rules, skills, hooks, review checklist), each as a repo issue with a named owner
- [x] Personal playbook "How I work with Claude" (workflows, prompts, guardrails) drafted as a doc artifact: https://claude.ai/artifact/GGQoCnHQDMmZrCcvZf1jfC
- [ ] Playbook shared (artifact link or repo wiki)

### Final checkpoint "Company-ready"

- [ ] Capstone shipped end-to-end
- [ ] Track skill bar shown (BA/QA)
- [ ] Day 3, 6 and 11 checklists all complete

---

## 4. Key takeaways

**How multiplayer agents differ**
- Single-player agent = an extension of you; multiplayer agent acts as itself
- Own identity: its own credentials, the team decides its access
- Shared memory grows from everyone; shared context keeps it current

**Organizational checklist (readiness before multiplayer AI)**
- Five questions: (1) information open and searchable, not in private docs and DMs (2) ownership written down, agents included (3) every teammate, agents included, has the tools (4) key agent work checked by a rubric, a test or a second agent before a person reviews (5) a written north star
- Four principles: clear roles, written north star, gradual release, appropriate information access ("gradual release" is named but not developed on the page)
- Why each matters: siloed info leaves agents out of date; unclear ownership duplicates work; agents without tools guess or make mistakes; checks before human review shorten finalizing; no shared goal means nobody can anticipate the next need
- Reflection: which question would my team disagree about most; what do we keep private by habit that could be shared on purpose

**Accessing the API (Building with the Claude API)**
- Five-step flow: request to server, request to Anthropic API, model processing, response to server, response to client
- Never call the API from client code: the secret API key would be exposed; the client calls your server, the server holds the key and calls Anthropic (SDKs: Python, TypeScript, JavaScript, Go, Ruby, or plain HTTP)
- Required fields: API key, model, messages, max tokens
- Inside Claude: tokenization (text to tokens) -> embedding (token to numbers) -> contextualization (meaning from surrounding words) -> generation (probabilities for the next token, with controlled randomness; repeat per token)
- Generation stops on max tokens, a natural end-of-sequence token, or a stop sequence
- Response has message, usage (input and output tokens) and stop reason; use it to design secure architecture, set token limits, handle stop reasons, debug

**Getting an API key**
- Console (platform.claude.com) -> Get API Keys -> Create Key -> pick workspace (Default) and a name -> copy from the popup
- The full key is shown once; if lost, delete it and create a new one
- Key name is only a label; the key value authenticates requests, so keep it secret

**Multi-turn conversations**
- Claude is stateless: no history between requests, so a vague follow-up ("write another sentence") loses context
- Fix: keep the message list in your app and resend it in full each time
- Loop: send user message -> append reply as `assistant` -> append next `user` message -> resend all
- Roles must be right: `user` = your input, `assistant` = Claude's output
- Three helpers: add user message, add assistant message, chat (calls API with model, max tokens, full list; returns text of first content block)

**System prompts**
- A system prompt sets Claude's role, tone and approach, so answers are tailored (example: math tutor gives hints and worked examples, not instant answers)
- Passed as a plain string in the `system` parameter of the create call; also keeps Claude on task
- Helper: chat function takes an optional `system`; build params (model, `max_tokens`, `messages`) and add `system` only when given, because the API rejects `system=None`
- System prompt = how Claude responds; user message = what is asked

**Temperature**
- Generation: tokenize -> predict next-token probabilities -> sample one; repeat
- Temperature is 0 to 1 and reshapes those probabilities: near 0 = almost always the most probable token (deterministic), near 1 = spread across more options (varied, creative)
- Low 0.0-0.3: facts, coding, extraction, moderation. Medium 0.4-0.7: summaries, education, problem-solving, constrained creative. High 0.8-1.0: brainstorming, open creative, marketing copy, jokes
- Code: `temperature` param added to the `chat` helper (lesson default 1.0) next to model, `max_tokens`, `messages`; the page does not state the API's own default
- It changes likelihood, not a guarantee: 0.0 gave consistent runs, 1.0 more variety

**Response streaming**
- Standard replies can take 10-30 s; streaming sends the reply in pieces as it is generated, so text appears gradually (one request, many events)
- Events: MessageStart, ContentBlockStart, ContentBlockDelta (carries the text), ContentBlockStop, MessageDelta, MessageStop
- Raw: `stream=True` on `messages.create`, iterate and parse events yourself. Simple: `messages.stream(...)` as a context manager, iterate `stream.text_stream`. Then `stream.get_final_message()` for storage (e.g. a database)
- Use for user-facing chat; improves perceived latency, content unchanged

**Structured data**
- Default: Claude wraps JSON/code in markdown fences and adds explanation, which breaks copy-paste use (example: an app generating AWS EventBridge rules)
- Fix = assistant prefill (an assistant message that opens the json fence, so Claude continues with content only) + stop sequence (the closing fence, so no trailing commentary)
- Strip whitespace before parsing (e.g. standard JSON parser)
- Same method for Python, lists, CSV: find the wrapper Claude naturally uses and use it as both prefill and stop sequence

**Prompt evaluation**
- Writing a prompt is step one; reliable apps also need prompt engineering (write: multishot examples, XML tags) and prompt evaluation (measure: automated tests against expected answers, compare versions, review errors)
- After drafting: (1) test once and ship = risky (2) test a few times, patch a corner case = better, users still find failures (3) score with an evaluation pipeline, iterate on objective metrics = more effort, much more confidence
- Why: find weaknesses before users, compare versions with data, broader input coverage; cost is upfront time and infrastructure
- No code in this lesson; later lessons cover the eval workflow

**A typical eval workflow**
- Five-step loop: (1) draft a prompt template = baseline (2) build an eval dataset of production-like questions (example: 3 questions; real: hundreds or thousands, hand-written or Claude-generated) (3) run: fill the template per question, send, collect replies (4) grade: a grader scores each question + answer, typically 1-10, average to one number per version (example baseline about 7.66) (5) revise and repeat, compare averages (example: "answer in detail" raised it to 8.7)
- Benefit: numeric comparison between versions, scores replace guesswork

**Generating test datasets**
- Case: a prompt that helps users write AWS-related Python, JSON or regex; it should return only the code/config/regex, no commentary
- Dataset = JSON objects with a `task` field; hand-written or Claude-generated. Generate with a faster model (Haiku is a sensible choice for test data)
- Generation prompt asks for an array of tasks (Python, JSON or regex each), gives an example format, tasks solvable with a single function, object or regex; lesson asks for three
- Prefill the opening json fence + closing fence as stop sequence, parse with `json.loads`, save with `json.dump` (indented) to `dataset.json`
- Helpers: `add_user_message`, `add_assistant_message`, `chat` (optional system, temperature, stop sequences)

**Running the eval**
- Pipeline core = three functions: `run_prompt(test_case)` (task into a simple prompt, user message, `chat`, returns output), `run_test_case(test_case)` (calls run_prompt, hardcoded score 10 as placeholder, returns dict with `output`, `test_case`, `score`), `run_eval(dataset)` (loops all cases, collects list)
- Run: load `dataset.json`, pass to `run_eval`; Haiku takes about 30 s for the full dataset; result = JSON array, one object per case
- Prompt has no formatting instructions so outputs are verbose (refined later); next lesson replaces the fake score with model-based grading

**Model-based grading**
- A grader turns an output into a score, usually 1-10, higher = better. Three types: code (length, required/banned words, JSON/Python/regex syntax, readability), model (another model call judges quality, instruction following, completeness, helpfulness, safety), human (most flexible, slow and tedious: comprehensiveness, depth, conciseness, relevance)
- Define criteria first; for code generation: format (code only), valid syntax, addresses the task. Code graders for format and syntax, model graders for task-following
- Model grader prompt: expert reviewer, returns JSON with 1-3 strengths, 1-3 weaknesses, short reasoning, 1-10 score; prefill json fence + closing fence stop sequence
- Ask for strengths, weaknesses and reasoning with the score, otherwise scores cluster around 6
- Test runner records output, test case, score, reasoning; a separate function averages scores into one metric per prompt version. Model graders can be somewhat inconsistent but give a stable enough baseline

**Personal playbook**
- One page, three parts: favorite workflows, prompts, guardrails
- Built from the dojo plan and my Learning notes (tabs), not from memory

---

## 5. Sources

- Organizational checklist, Building Effective Human Agent Teams, Claude Academy: https://academy.claude.com/courses/building-effective-human-agent-teams/organizational-checklist
- Model-based grading, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/model-based-grading
- Running the eval, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/running-the-eval
- Generating test datasets, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/generating-test-datasets
- A typical eval workflow, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/a-typical-eval-workflow
- Prompt evaluation, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/prompt-evaluation
- Structured data, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/structured-data
- Response streaming, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/response-streaming
- Temperature, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/temperature
- System prompts, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/system-prompts
- Multi-turn conversations, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/multi-turn-conversations
- Getting an API key, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/getting-an-api-key
- Accessing the API, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/accessing-the-api
- Day 15: Review, Merge, Demo, dojo: https://dojo.agilityio.dev/schedule/day-15.html
