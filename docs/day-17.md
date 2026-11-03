# Day 17 Model Context Protocol: Advanced Topics

- **Date:** 2026-11-03
- **Trainee:** thanh.truong
- **Branch:** `training/day-17`

**Status:** In progress. Course overview, "Log and progress notifications" and "Roots" noted; JSON message types and The STDIO transport also noted; Sampling and StreamableHTTP are only covered by the overview so far.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Model Context Protocol: Advanced Topics

- [x] Course overview
- [x] Log and progress notifications
- [x] Roots
- [ ] Sampling (only summarized in the overview)
- [x] JSON message types
- [x] The STDIO transport
- [ ] StreamableHTTP transport (only summarized in the overview)
- [ ] Course quiz

---

## 3. Key takeaways

**Course overview**
- Beyond basic MCP: sampling, log/progress notifications, roots, JSON message types, and the STDIO and StreamableHTTP transports (stateful vs stateless)
- Sampling: a server asks the client to run a prompt through the LLM, moving API key, cost and integration work to the client; the client handles it with a `sampling_callback` passed at session init
- JSON message types: request-result pairs vs one-way notifications (report an event, expect no reply)
- STDIO transport: local; initialization handshake = initialize request, initialize result with capabilities, `initialized` notification, required before any other request
- StreamableHTTP: `stateless_http=True` drops session IDs and server-to-client requests so instances scale without coordination, but disables sampling, progress and subscriptions; `json_response=True` only turns off streaming of POST responses (client gets the final JSON, no intermediate logs or progress)

**Log and progress notifications**
- A server keeps users informed during long tool calls; the client decides how to show it, and may ignore it (optional UX)
- Log notification = text status message, sent with `context.info()`; progress notification = current value vs total, sent with `context.report_progress()`
- The server gives each tool function a `Context` object automatically
- Client side: `logging_callback` passed when the `ClientSession` is created; `progress_callback` passed to each `call_tool` call

**Roots**
- Problem: the user gives only a filename, Claude has to find it
- Roots = approved local directories a server may access; `list_roots` shows them, `read_dir` browses one to find the file, then the full path is used
- Requests outside the roots fail, but the MCP SDK does not enforce this: write your own check (`is_path_allowed()`) and run it before any file operation
- Roots can be supplied through tools or prompts (two ways)

**JSON message types**
- Clients and servers exchange JSON messages, each type with a purpose (call a tool, list resources, report an event); typical flow: client sends a tool-call request, server runs it, server replies with a result
- Two categories: request-result pairs (sender expects a response: Call Tool, List Prompts, Read Resource, Initialize) and notifications (one-way, no reply: Progress, Logging Message, Tool List Changed, Resource Updated)
- Clients send requests and notifications; servers send requests to clients and broadcast notifications; MCP is bidirectional, but some transports (e.g. streamable HTTP) restrict direction, which affects transport choice
- The authoritative list of types is in the MCP specification repo (separate from the SDKs; types are written in TypeScript only to describe structures); the lesson does not cover fields or errors

**The STDIO transport**
- Transport = channel carrying JSON messages (HTTP, WebSockets, ...). STDIO = most common in development: client starts the server as a subprocess; client writes to the server's stdin, server writes to stdout; either side can send at any time; same machine only
- Test without a client: `uv run server.py`, then type JSON messages and read replies
- Handshake: (1) client sends initialize request (2) server replies with initialize result describing capabilities (3) client sends initialized notification (no reply); other requests only after this
- Four scenarios any transport must handle: client request, server response, server request, client response (stdio maps them to stdin/stdout); other transports may not let the server initiate requests, and production over different machines needs other transports

---

## 4. Sources

- Model Context Protocol: Advanced Topics, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics
- The STDIO transport, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/the-stdio-transport
- JSON message types, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/json-message-types
- Log and progress notifications, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/log-and-progress-notifications
- Roots, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/roots
