# Day 15 Review, Merge, Demo (Final Checkpoint)

- **Date:** 2026-10-29
- **Trainee:** thanh.truong
- **Branch:** `training/day-15`

**Status:** In progress. Course notes for "Building Effective Human Agent Teams" lessons 1, 2 and 4 are in; "Building with the Claude API" lessons Accessing the API, Getting an API key, Multi-turn conversations, System prompts, Temperature, Response streaming, Structured data, Prompt evaluation, A typical eval workflow, Generating test datasets, Running the eval, Model-based grading, Code-based grading, Prompt engineering, Being clear and direct, Being specific, Structure with XML tags and Tool use (intro, functions, schemas) and Handling message blocks noted; capstone items below are not ticked until done.

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

**Code-based grading**
- Code graders cover format (only the requested code type, no explanation) and valid syntax; the model grader keeps task following
- Validators on stripped text: `validate_json` (`json.loads`), `validate_python` (`ast.parse`), `validate_regex` (`re.compile`); 10 on success, 0 on error
- Each test case gets a `format` field (e.g. python) so the grader picks the validator; add it to the dataset generation prompt example
- Prompt: respond only with Python, JSON or a plain regex, no comments or explanation; optional assistant prefill with a code block opener
- Final score = average of model score and syntax score (weights adjustable). Baseline value matters less than whether prompt changes raise it

**Prompt engineering**
- Iterative loop: set a goal, write a simple prompt, evaluate, apply specific techniques, re-evaluate; repeat the last two until satisfied; each iteration should show measurable score gains
- Example: a one-day meal plan prompt for athletes (height, weight, goal, dietary restrictions)
- `PromptEvaluator`: `generate_dataset` (task description + input spec; 2-3 cases in development, more for final validation), `run_evaluation` (prompt function + dataset file, `extra_criteria`); `max_concurrent_tasks` start low (~3) to avoid rate limits
- Baseline prompt is deliberately naive; first scores are low (about 2.3/10 cited); report = numeric score + HTML with grader reasoning
- Change one thing at a time, evaluate, build on what works. Coming: clear and direct, specific, XML tags, examples

**Being clear and direct**
- The first line matters most: clear = plain language, say exactly what you want; direct = an instruction, not a question, starting with an action verb (write, create, generate)
- Guidelines: lead with the action, name the specific output, add key constraints (scope, audience, requirements), avoid vague or hedged wording
- Example: "what should an athlete eat" -> generate a one-day meal plan for an athlete meeting dietary restrictions; changing only the first line moved the score 2.32 -> 3.92

**Being specific**
- A vague request ("short story about someone who discovers a hidden talent") leaves length, cast and plot to Claude; specific guidelines narrow the range
- Two types: output quality guidelines (length, structure/format, required elements, tone/style) and process steps (how to work through it: brainstorm, select, outline, consider supporting elements)
- Use output guidelines in nearly every prompt; add process steps for complex work (troubleshooting, decisions, critical thinking, analysis, e.g. sales decline: several causes, not one); combine both for controlled output and thorough reasoning
- Meal-plan test: guidelines (calories, macros, meal timing, restrictions, portions in grams, budget) moved the score 3.92 -> 7.86

**Structure with XML tags**
- Big prompts can blur which text is instructions and which is data; tags (paired open/close labels) set boundaries so Claude sees what belongs together
- Helps: separate instructions from large data (sales records), keep content types apart (code vs docs in debugging), group related details (`<athlete_information>`)
- Names: no official schema needed; descriptive and specific (`<sales_records>` over `<data>`)
- Use for large context, mixed content, multiple variables (interpolation), clearer boundaries; benefit grows with prompt size, little difference in simple prompts
- No eval results in this lesson

**Introducing tool use**
- Claude only knows its training data; tools give a structured way to request fresh data (e.g. weather)
- Four steps: app sends question plus instructions for getting external data; Claude specifies exactly what it needs; your server fetches it (API or database); you send results back and Claude answers with both
- Benefits: real-time info, integrations with databases and APIs, latest data, predictable structured requests. Claude alone vs Claude plus your server (which does the retrieval). No code in this lesson

**Tool functions**
- A tool is a plain Python function Claude calls when it needs info or an action (preview: current date/time, add a duration, set reminders)
- Practices: descriptive names (function and parameters), validate inputs and raise errors for empty/invalid values, clear error messages (Claude can read them and retry with corrected parameters)
- Example `get_current_datetime(date_format="%Y-%m-%d %H:%M:%S")`: raises `ValueError` if the format is empty, returns `datetime.now().strftime(date_format)`
- The function is only part one: still need a JSON schema and integration into the chat system

**Tool schemas**
- JSON Schema = general-purpose validation spec, adopted for describing function parameters; Claude reads it as documentation
- Tool specification = `name` (clear, verb-noun), `description` (3-4 sentences: what it does, when to call, what data returns, each argument), `input_schema` (JSON Schema of the arguments)
- Generate with Claude: paste the function code, ask for a tool-calling schema, attach Anthropic's tool-use docs, review
- In code: schema dict next to the function with a suffix on the function name; defaulted args go in `properties` with `default` and are not required; validation errors still raised in the function body; optional `ToolParam` type wrapper for type checking

**Handling message blocks**
- With tools, a reply can hold several content blocks instead of one text block: a text block (Claude explains what it does) and a `tool_use` block (ID to track the call, function name, input as a dict)
- Enable tools by passing a list of tool schemas as `tools` in `messages.create`
- Append the assistant turn with role `assistant` and the full `response.content`, not just the text; Claude stores no history, you manage the list
- Five steps: send request with tools, receive multi-block reply, run the tool, send the result back with full history, receive the final answer
- Helpers that assume a single text block need updating. The page does not cover `stop_reason`

**Personal playbook**
- One page, three parts: favorite workflows, prompts, guardrails
- Built from the dojo plan and my Learning notes (tabs), not from memory

---

## 5. Sources

- Organizational checklist, Building Effective Human Agent Teams, Claude Academy: https://academy.claude.com/courses/building-effective-human-agent-teams/organizational-checklist
- Handling message blocks, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/handling-message-blocks
- Tool schemas, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/tool-schemas
- Tool functions, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/tool-functions
- Introducing tool use, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/introducing-tool-use
- Structure with XML tags, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/structure-with-xml-tags
- Being specific, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/being-specific
- Being clear and direct, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/being-clear-and-direct
- Prompt engineering, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/prompt-engineering
- Code-based grading, Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api/code-based-grading
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
