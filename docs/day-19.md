# Day 19 Building with the Claude API

- **Date:** 2026-11-05
- **Trainee:** thanh.truong
- **Branch:** `training/day-19`

**Status:** In progress. Lessons 1 to 25 of the course noted (request basics through multi-turn tool use); the remaining lessons and the course quiz are still open.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Building with the Claude API

- [x] Accessing the API
- [x] Making a request
- [x] Multi-turn conversations
- [x] System prompts
- [x] Temperature
- [x] Response streaming
- [x] Structured data
- [x] Prompt evaluation
- [x] A typical eval workflow
- [x] Generating test datasets
- [x] Running the eval
- [x] Model-based grading
- [x] Code-based grading
- [x] Prompt engineering
- [x] Being clear and direct
- [x] Being specific
- [x] Structure with XML tags
- [x] Providing examples
- [x] Introducing tool use
- [x] Project overview
- [x] Tool functions
- [x] Tool schemas
- [x] Handling message blocks
- [x] Sending tool results
- [x] Multi-turn conversations with tools
- [ ] Remaining lessons and course quiz (the course has 67 lessons in total)

Request flow and getting an API key are in [day-15.md](day-15.md).

---

## 3. Key takeaways

**Making requests**
- Flow: client, your server, Anthropic API, model, back; the API key stays on the server
- `client.messages.create()` takes `model`, `max_tokens` (a ceiling, not a target; output is cut off if reached) and `messages` (dicts with `role` and `content`); text is read from `message.content[0].text`
- Keep the key in `.env` (`ANTHROPIC_API_KEY`) and add `.env` to `.gitignore`

**Controlling output**
- Claude is stateless: store every message and resend the full list each request (roles `user` and `assistant`)
- System prompt goes in the `system` parameter as a plain string; omit the key when empty because `None` is rejected
- Temperature 0 to 1: low (0.0-0.3) for facts, code, extraction; medium (0.4-0.7) for summaries; high (0.8-1.0) for brainstorming and creative work
- Streaming: small events in one request; `text_stream` yields only text, `get_final_message()` returns the assembled message
- Structured data: prefill the assistant turn with the opening code fence and use the closing fence as the stop sequence, then strip and parse

**Prompt evaluation**
- Prompt engineering writes prompts; prompt evaluation measures them with an eval pipeline instead of testing once or twice
- Loop: draft a prompt, build a dataset, run it, grade (1 to 10), compare average scores, revise
- Dataset generation with a light model (Haiku) using prefill and a stop sequence, saved to `dataset.json`
- `run_prompt`, `run_test_case`, `run_eval` run the dataset; graders: code (format, syntax via `validate_json`, `validate_python`, `validate_regex`), model (strengths, weaknesses, reasoning, score), human (flexible but slow)
- Final score can average the model grade and the syntax score

**Prompt engineering techniques**
- Iterate: goal, simple baseline prompt, evaluate, apply one technique, re-evaluate (`PromptEvaluator`, start with low `max_concurrent_tasks`)
- Be clear and direct: open with an action-verb instruction (example score 2.32 to 3.92)
- Be specific: output guidelines (what the result looks like) plus process steps (how to reason) (3.92 to 7.86)
- XML tags separate instructions from data; descriptive names beat generic ones
- Examples: one-shot or multi-shot pairs wrapped in `<sample_input>` and `<ideal_output>`, chosen from top eval scores, with an explanation of why each output is ideal; best for corner cases and complex formats

**Tool use**
- Claude only knows its training data; tools let it request outside data that your server fetches
- Project: a reminder system with three tools (get current date time, add duration to date time, set a reminder)
- A tool is a plain Python function with a descriptive name, input validation and clear errors Claude can read and retry on
- Tool spec = `name`, `description` (when to use, what it returns, each argument), `input_schema` (JSON Schema)
- Pass the specs in `tools`; the reply can hold several blocks (`text` and `tool_use` with `id`, name, `input`); append the whole `response.content` to the history
- Send results back in a user message: `tool_result` with `tool_use_id` matching the request, `content` as a string, `is_error`; run the function with `**input`; the follow-up request must include the full history and `tools`
- Multiple tool calls in one reply each need their own matching ID
- Multi-turn loop: call chat, append the reply, break if no tool is requested, otherwise run tools and append results, repeat; helpers `add_user_message` (string, blocks or Message), `chat` (adds `tools` and `system` only when given, returns the full message) and `text_from_message`

---

## 4. Sources

- Building with the Claude API, Claude Academy: https://academy.claude.com/courses/building-with-the-claude-api
- Accessing the API: https://academy.claude.com/courses/building-with-the-claude-api/accessing-the-api
- Making a request: https://academy.claude.com/courses/building-with-the-claude-api/making-a-request
- Multi-turn conversations: https://academy.claude.com/courses/building-with-the-claude-api/multi-turn-conversations
- System prompts: https://academy.claude.com/courses/building-with-the-claude-api/system-prompts
- Temperature: https://academy.claude.com/courses/building-with-the-claude-api/temperature
- Response streaming: https://academy.claude.com/courses/building-with-the-claude-api/response-streaming
- Structured data: https://academy.claude.com/courses/building-with-the-claude-api/structured-data
- Prompt evaluation: https://academy.claude.com/courses/building-with-the-claude-api/prompt-evaluation
- A typical eval workflow: https://academy.claude.com/courses/building-with-the-claude-api/a-typical-eval-workflow
- Generating test datasets: https://academy.claude.com/courses/building-with-the-claude-api/generating-test-datasets
- Running the eval: https://academy.claude.com/courses/building-with-the-claude-api/running-the-eval
- Model-based grading: https://academy.claude.com/courses/building-with-the-claude-api/model-based-grading
- Code-based grading: https://academy.claude.com/courses/building-with-the-claude-api/code-based-grading
- Prompt engineering: https://academy.claude.com/courses/building-with-the-claude-api/prompt-engineering
- Being clear and direct: https://academy.claude.com/courses/building-with-the-claude-api/being-clear-and-direct
- Being specific: https://academy.claude.com/courses/building-with-the-claude-api/being-specific
- Structure with XML tags: https://academy.claude.com/courses/building-with-the-claude-api/structure-with-xml-tags
- Providing examples: https://academy.claude.com/courses/building-with-the-claude-api/providing-examples
- Introducing tool use: https://academy.claude.com/courses/building-with-the-claude-api/introducing-tool-use
- Project overview: https://academy.claude.com/courses/building-with-the-claude-api/project-overview
- Tool functions: https://academy.claude.com/courses/building-with-the-claude-api/tool-functions
- Tool schemas: https://academy.claude.com/courses/building-with-the-claude-api/tool-schemas
- Handling message blocks: https://academy.claude.com/courses/building-with-the-claude-api/handling-message-blocks
- Sending tool results: https://academy.claude.com/courses/building-with-the-claude-api/sending-tool-results
- Multi-turn conversations with tools: https://academy.claude.com/courses/building-with-the-claude-api/multi-turn-conversations-with-tools
