# Day 19 Building with the Claude API

- **Date:** 2026-11-05
- **Trainee:** thanh.truong
- **Branch:** `training/day-19`

**Status:** In progress. 63 lessons of the course noted (request basics through workflows vs agents); only the course quiz and any lessons not listed below are still open.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training
- [ ] Note details arrtifact: https://claude.ai/artifact/Wju7QKicS3VHTFdAjqVwDf

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
- [x] Implementing multiple turns
- [x] Using multiple tools
- [x] Fine-grained tool calling
- [x] The text edit tool
- [x] The web search tool
- [x] Introducing retrieval augmented generation
- [x] Text chunking strategies
- [x] Text embeddings
- [x] The full RAG flow
- [x] Implementing the RAG flow
- [x] BM25 lexical search
- [x] A multi-index RAG pipeline
- [x] Extended thinking
- [x] Image support
- [x] PDF support
- [x] Citations
- [x] Prompt caching
- [x] Rules of prompt caching
- [x] Prompt caching in action
- [x] Code execution and the Files API
- [x] Introducing MCP
- [x] MCP clients
- [x] Defining tools with MCP
- [x] The server inspector
- [x] Implementing a client
- [x] Defining resources
- [x] Accessing resources
- [x] Defining prompts
- [x] Prompts in the client
- [x] Anthropic apps
- [x] Enhancements with MCP servers
- [x] Agents and workflows
- [x] Parallelization workflows
- [x] Chaining workflows
- [x] Routing workflows
- [x] Agents and tools
- [x] Environment inspection
- [x] Workflows vs agents
- [ ] Course quiz and any remaining lessons (the course has 67 lessons in total)

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

**More tool use**
- Loop condition: keep going while `stop_reason == "tool_use"`; `run_tools` returns a `tool_result` per `tool_use` block, errors with `is_error: True`; a `run_tool` router by name keeps the loop unchanged
- Adding a tool = function + schema in the `tools` list + case in `run_tool`; use a date-math tool because Claude is unreliable at date addition
- Fine-grained tool calling (`fine_grained=True`): `InputJsonEvent` has `partial_json` and `snapshot`; no server-side validation, so wrap parsing in `try`/`except json.JSONDecodeError`
- Text edit tool: send a schema stub per model (e.g. `text_editor_20250124`, name `str_replace_editor`) and implement view, replace, create, insert and undo handlers yourself
- Web search tool: type `web_search_20250305`, name `web_search`, enable it in org settings, set `max_uses` and `allowed_domains`; response has `ServerToolUseBlock`, `WebSearchToolResultBlock` and citations

**RAG**
- Prompt stuffing hits length limits and costs more; RAG chunks the document, searches the chunks and adds only matches ("trades simplicity for scalability")
- Chunking: size-based (`chunk_by_char`, overlap), structure-based (`chunk_by_section`), sentence-based, semantic-based; no single best strategy
- Embeddings: lists of floats for meaning; Anthropic has none, use VoyageAI (`voyage-3-large`, `VOYAGE_API_KEY`)
- Flow: chunk, embed, store in a vector database (`VectorIndex.add_vector`); at query time embed the question with the same model and `search`; cosine distance = 1 - cosine similarity (lower is closer); store the original text with each vector
- BM25 (`BM25Index`) catches exact terms (e.g. an incident ID) that semantic search misses; combine in a `Retriever` with reciprocal rank fusion, sum of 1/(k + rank), k=60 default

**Advanced model features**
- Extended thinking: `thinking={"type": "enabled", "budget_tokens": N}`, N at least 1024 and below `max_tokens`; no prefill; do not edit signed thinking blocks; pass redacted blocks back
- Images: `image` block with base64 source, up to 100 images, 5MB each, tokens about width x height / 750; PDFs: `document` block with `application/pdf`
- Citations: `"citations": {"enabled": True}` on a `document` block; fields `cited_text`, `document_index`, `document_title`, page numbers (plain text gives character positions)
- Prompt caching: `cache_control: {"type": "ephemeral"}`, longhand text blocks, 5 minute default (1 hour costs more), at least 1024 tokens, up to 4 breakpoints, order tools then system then messages; check `cache_creation_input_tokens` and `cache_read_input_tokens`; cache the last tool and system prompt blocks
- Files API + code execution: upload for a file ID, `container_upload` block, `code_execution_20250522`, isolated Docker with no network, outputs via `code_execution_output` file IDs

**MCP**
- Your server is an MCP client that connects to MCP servers exposing tools, prompts and resources; it removes hand-written tool definitions (check that a server is official)
- Client messages: `ListToolsRequest` / `ListToolsResult`, `CallToolRequest` / `CallToolResult`; transport agnostic (stdio, HTTP, WebSockets)
- Server (Python SDK): `FastMCP`, `@mcp.tool` with `Field` descriptions, `ValueError` for unknown IDs; test with `mcp dev` (MCP Inspector)
- `MCPClient` wrapper with `list_tools()` and `call_tool()`; resources via `@mcp.resource` (direct vs templated URIs, `mime_type`) and `read_resource` (check `mimeType`); prompts via `@mcp.prompt()`, `list_prompts()`, `get_prompt()`
- Claude Code has a built-in MCP client: `claude mcp add <name> <command>`; Claude Code and Computer Use are example agents

**Workflows and agents**
- Workflows = predefined call series for known steps (accurate, testable); agents = goal plus tools, Claude plans (flexible, less predictable); prefer workflows
- Patterns: parallelization (independent sub-tasks then aggregate), chaining (sequential focused steps, more latency), routing (categorize, then one specialized pipeline), evaluator-optimizer (producer, grader, feedback loop)
- Agents work best with abstract, combinable tools (`bash`, `read`, `write`, `edit`, `glob`, `grep`) and environment inspection (screenshots, read before write)

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
- Implementing multiple turns: https://academy.claude.com/courses/building-with-the-claude-api/implementing-multiple-turns
- Using multiple tools: https://academy.claude.com/courses/building-with-the-claude-api/using-multiple-tools
- Fine-grained tool calling: https://academy.claude.com/courses/building-with-the-claude-api/fine-grained-tool-calling
- The text edit tool: https://academy.claude.com/courses/building-with-the-claude-api/the-text-edit-tool
- The web search tool: https://academy.claude.com/courses/building-with-the-claude-api/the-web-search-tool
- Introducing retrieval augmented generation: https://academy.claude.com/courses/building-with-the-claude-api/introducing-retrieval-augmented-generation
- Text chunking strategies: https://academy.claude.com/courses/building-with-the-claude-api/text-chunking-strategies
- Text embeddings: https://academy.claude.com/courses/building-with-the-claude-api/text-embeddings
- The full RAG flow: https://academy.claude.com/courses/building-with-the-claude-api/the-full-rag-flow
- Implementing the RAG flow: https://academy.claude.com/courses/building-with-the-claude-api/implementing-the-rag-flow
- BM25 lexical search: https://academy.claude.com/courses/building-with-the-claude-api/bm25-lexical-search
- A multi-index RAG pipeline: https://academy.claude.com/courses/building-with-the-claude-api/a-multi-index-rag-pipeline
- Extended thinking: https://academy.claude.com/courses/building-with-the-claude-api/extended-thinking
- Image support: https://academy.claude.com/courses/building-with-the-claude-api/image-support
- PDF support: https://academy.claude.com/courses/building-with-the-claude-api/pdf-support
- Citations: https://academy.claude.com/courses/building-with-the-claude-api/citations
- Prompt caching: https://academy.claude.com/courses/building-with-the-claude-api/prompt-caching
- Rules of prompt caching: https://academy.claude.com/courses/building-with-the-claude-api/rules-of-prompt-caching
- Prompt caching in action: https://academy.claude.com/courses/building-with-the-claude-api/prompt-caching-in-action
- Code execution and the Files API: https://academy.claude.com/courses/building-with-the-claude-api/code-execution-and-the-files-api
- Introducing MCP: https://academy.claude.com/courses/building-with-the-claude-api/introducing-mcp
- MCP clients: https://academy.claude.com/courses/building-with-the-claude-api/mcp-clients
- Defining tools with MCP: https://academy.claude.com/courses/building-with-the-claude-api/defining-tools-with-mcp
- The server inspector: https://academy.claude.com/courses/building-with-the-claude-api/the-server-inspector
- Implementing a client: https://academy.claude.com/courses/building-with-the-claude-api/implementing-a-client
- Defining resources: https://academy.claude.com/courses/building-with-the-claude-api/defining-resources
- Accessing resources: https://academy.claude.com/courses/building-with-the-claude-api/accessing-resources
- Defining prompts: https://academy.claude.com/courses/building-with-the-claude-api/defining-prompts
- Prompts in the client: https://academy.claude.com/courses/building-with-the-claude-api/prompts-in-the-client
- Anthropic apps: https://academy.claude.com/courses/building-with-the-claude-api/anthropic-apps
- Enhancements with MCP servers: https://academy.claude.com/courses/building-with-the-claude-api/enhancements-with-mcp-servers
- Agents and workflows: https://academy.claude.com/courses/building-with-the-claude-api/agents-and-workflows
- Parallelization workflows: https://academy.claude.com/courses/building-with-the-claude-api/parallelization-workflows
- Chaining workflows: https://academy.claude.com/courses/building-with-the-claude-api/chaining-workflows
- Routing workflows: https://academy.claude.com/courses/building-with-the-claude-api/routing-workflows
- Agents and tools: https://academy.claude.com/courses/building-with-the-claude-api/agents-and-tools
- Environment inspection: https://academy.claude.com/courses/building-with-the-claude-api/environment-inspection
- Workflows vs agents: https://academy.claude.com/courses/building-with-the-claude-api/workflows-vs-agents
