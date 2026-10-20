# Day 08 Model Context Protocol

- **Date:** 2026-10-20
- **Trainee:** thanh.truong
- **Branch:** `training/day-08`

**Status:** Introduction to Model Context Protocol in progress — lessons 1-9 noted; lesson 10, course quiz and MCP and connectors exercise pending.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Introduction to Model Context Protocol

- [x] Introducing MCP
- [x] MCP clients
- [x] Defining tools with MCP
- [x] The server inspector
- [x] Implementing a client
- [x] Defining resources
- [x] Accessing resources
- [x] Defining prompts
- [x] Prompts in the client
- [ ] Lesson 10
- [ ] Course quiz

### Exercise: MCP and connectors

Course: Introduction to Model Context Protocol.

- [ ] Add the GitHub connector
- [ ] Add the Playwright MCP server
- [ ] Use one MCP tool end-to-end in a session (e.g. query PRs, comment on one)

---

## 3. Key takeaways

**Introduction to MCP: introducing MCP**
- MCP = communication layer giving Claude context + tools without writing extensive custom integration code ("shifts the burden of tool definitions and execution" off your server)
- Architecture: **MCP client** (your app) → **MCP servers** (tools, prompts, resources) → outside service
- Problem: GitHub chat app needs tool schemas + functions for repos, PRs, issues, projects → heavy build and maintenance. Fix: connect to a GitHub MCP server that defines/executes the tools (e.g. `get_repos()`)
- Anyone can author servers; providers publish official ones (e.g. AWS)

| | Direct API calls | MCP |
|---|---|---|
| Tool definitions | You write | Provided by server |
| Execution logic | You implement | Handled by server |
| Maintenance | Yours | Server author's |

- MCP ≠ tool use: MCP supplies predefined tools, tool use is how Claude calls them (complementary)

**Introduction to MCP: MCP clients**
- Client = bridge between your server and MCP servers: access to a server's tools, handles message exchange and protocol details
- **Transport agnostic**: stdio (most common, same machine) · HTTP · WebSockets · other network protocols
- Core messages: `ListToolsRequest`/`Result` (discover tools) · `CallToolRequest`/`Result` (run one tool with args)
- Flow for "What repositories do I have?": user query → your server asks client for tools → client asks MCP server → query + tools to Claude → Claude picks a tool → client runs it via MCP server (calls GitHub) → results back via server to Claude → Claude writes answer → user
- Each component has one job; client hides server-communication complexity

**Introduction to MCP: defining tools with MCP**
- Official **Python MCP SDK** defines tools with decorators → no hand-written JSON schemas
- Example: document server with 2 tools (read, edit); docs in an in-memory dict `{doc_id: text}`
- Server: `FastMCP("DocumentMCP", log_level="ERROR")`
- `@mcp.tool(...)` registers a function and sets name/description; type hints + `Field(description=...)` generate the schema Claude reads
- `read_doc_contents(doc_id)` → returns text, `ValueError` if missing · `edit_document(doc_id, old_str, new_str)` → find-and-replace (exact match incl. whitespace), checks doc exists
- Benefits: automatic validation, clear param descriptions, native Python exceptions, automatic registration

| | Hand-written JSON schema | SDK decorator |
|---|---|---|
| Definition | Manual JSON | Python function + decorator |
| Param info | In schema | Type hints + `Field` |
| Validation | Build separately | From type hints |
| Registration | Manual | Automatic |

**Introduction to MCP: the server inspector**
- MCP Inspector = browser-based tool in the Python MCP SDK: test/debug a server in real time, no full client app needed (UI is under active development)
- Start: activate env → `mcp dev mcp_server.py` → open `http://127.0.0.1:6274`
- **Connect** (Disconnected → Connected) · tabs: Resources / Tools / Prompts · **List Tools** → pick tool → fill inputs (e.g. `doc_id`) → **Run Tool** → check status + returned data
- Test sequences (edit then read): server state persists between calls
- Use throughout development: quick iteration, edge cases and errors, state checks, real-time debugging

**Introduction to MCP: implementing a client**
- Client lets app code use the server. Real projects usually build a client **or** a server, not both (course builds both to show the fit)
- Two parts: custom **MCP client wrapper class** (`mcp_client.py`, handles connection cleanup automatically) + SDK **client session** (the actual connection)
- `list_tools()`: session `list_tools()` → returns `result.tools` · `call_tool(name, input)`: forwards Claude-supplied name + input dict to the server, returns result. Both `async`/`await`
- Used in the CLI at 2 points: get tools to send to Claude · execute tools when Claude requests them
- Test: run the client file directly → prints tool definitions (descriptions + input schemas). End-to-end: ask about `report.pdf` → tools → Claude picks → app executes → Claude answers

**Introduction to MCP: defining resources**
- Resources expose **data, not actions** (like HTTP GET handlers). Example: `@document_name` mentions → list docs (autocomplete) + fetch contents; mentioned content injected into the prompt, so Claude needs no tool
- Flow: client sends `ReadResourceRequest` (URI) → server runs matching function → `ReadResourceResult`
- `@mcp.resource("docs://documents", mime_type="application/json")` = direct · `@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")` = templated (`{doc_id}` passed as kwarg)
- Return str / JSON / binary; `mime_type` hints format; SDK serializes automatically. Unknown ID → `ValueError`
- Test: `uv run mcp dev mcp_server.py` → Inspector **Resources** (direct) / **Resource Templates**

| | Direct | Templated |
|---|---|---|
| URI | Static | Has parameters |
| Use | List all | Fetch one |
| Inspector | Resources | Resource Templates |

**Introduction to MCP: accessing resources**
- Resources go straight into the prompt → no tool call, more efficient context
- Flow: user types `@` ref → client recognizes a resource request → `ReadResourceRequest` → `ReadResourceResult` with content
- Client `read_resource(uri)` (async): awaits session read-resource (URI via pydantic `AnyUrl`), takes `result.contents[0]` (one resource at a time), checks `isinstance(..., types.TextResourceContents)`
- MIME branch: `application/json` → `json.loads`; anything else → raw `text`
- CLI test: `@` shows autocomplete, pick with arrows + space, content joins the prompt, model answers immediately

| | Resource access | Tool call |
|---|---|---|
| Data arrives | In the prompt as context | Model requests during conversation |
| Round trips | None extra | Separate call + response |
| Initiated by | User (`@`) | Model |
| Best for | Docs/data the user wants the model to see | Actions/queries the model must trigger |

**Introduction to MCP: defining prompts**
- MCP prompts = reusable, tested templates a server offers instead of user-written instructions. Server authors do the prompt engineering → users get expert results without the skill
- Example `/format doc_id`: user types `/`, picks `format`, gives doc ID → Claude uses the server prompt to read and reformat to clean markdown
- Defined with `@mcp.prompt(name=..., description=...)`; typed params with `Field(description=...)`; f-string interpolation; returns list of `base.UserMessage` (can mix user/assistant messages); can tell Claude to use a tool (e.g. `edit_document`)
- Test in MCP Inspector: shows arguments + the exact messages sent to Claude
- Best when domain-specific (document server: format/summarize/analyze; data server: report/visualization)

| | User-written | Server MCP prompt |
|---|---|---|
| Quality | Varies | Consistent, tested |
| Edge cases | Often unhandled | Handled by design |
| User effort | Write and refine | Pick command + args |
| Updates | Each user | Once on server, all clients benefit |

**Introduction to MCP: prompts in the client**
- Prompt support completes the MCP client: list the server's prompts + retrieve one with variables filled in
- `list_prompts()` → session list → `result.prompts` · `get_prompt(name, args)` → session get → `result.messages` (e.g. `format_document` + `{"doc_id": "plan.md"}` interpolated)
- CLI test: `/` lists prompts as commands → pick `format` → choose a doc → full prompt sent to Claude, which uses its tools to fetch/process
- Prompt = reusable set of user + assistant messages: high quality, well tested, relevant to the server's purpose
- Server workflow: write + evaluate → define with `@mcp.prompt` → clients request any time → client args become kwargs → function returns formatted messages
- Parameterized prompts = consistent instructions + customization; suit complex workflows

| | `list_prompts` | `get_prompt` |
|---|---|---|
| Input | None | Name + args dict |
| Output | `result.prompts` | `result.messages` |
| Purpose | Discover | Fill in and retrieve |

Source: Introducing MCP · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/introducing-mcp
Source: MCP clients · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/mcp-clients
Source: Defining tools with MCP · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/defining-tools-with-mcp
Source: The server inspector · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/the-server-inspector
Source: Implementing a client · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/implementing-a-client
Source: Defining resources · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/defining-resources
Source: Accessing resources · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/accessing-resources
Source: Defining prompts · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/defining-prompts
Source: Prompts in the client · Introduction to Model Context Protocol — https://academy.claude.com/courses/introduction-to-model-context-protocol/prompts-in-the-client
