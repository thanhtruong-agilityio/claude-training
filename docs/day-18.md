# Day 18 Model Context Protocol: Advanced Topics

- **Date:** 2026-11-04
- **Trainee:** thanh.truong
- **Branch:** `training/day-18`

**Status:** In progress. The StreamableHTTP transport, StreamableHTTP in depth and State and the StreamableHTTP transport noted; the course quiz is still open.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Model Context Protocol: Advanced Topics

- [x] The StreamableHTTP transport
- [x] StreamableHTTP in depth
- [x] State and the StreamableHTTP transport
- [ ] Sampling (only summarized in the course overview, see [day-17.md](day-17.md))
- [ ] Course quiz

Earlier lessons of this course (overview, log and progress notifications, roots, JSON message types, the STDIO transport) are in [day-17.md](day-17.md).

---

## 3. Key takeaways

**The StreamableHTTP transport**
- Lets MCP clients connect over HTTP to servers hosted elsewhere; unlike stdio (same machine only), it makes public MCP servers possible
- Pitfall: a setup that works locally over stdio can break when deployed over HTTP, usually because of configuration settings
- Two settings, both default `false`: `stateless_http` (connection state) and `json_response` (response format); deployment constraints may force them to `true`, which can break progress notifications, logging and server-initiated requests
- Core limitation: clients easily reach servers at a known URL, but servers cannot easily initiate requests back to clients (no known URL)
- Affected: server-initiated requests (Create Message = sampling, List Roots) and notifications (Progress, Logging, Initialized, Cancelled)
- The transport has a workaround for HTTP's limits; forcing stateless or JSON-response mode means working within those limits, trading functionality for remote hosting. If an app relies heavily on server-initiated requests or real-time notifications, reconsider the transport or use another communication pattern
- The page does not explain POST, GET SSE streams or session IDs (next lesson), and has no code

**StreamableHTTP in depth**
- Core problem: sampling, notifications and logging need the server to send requests to the client, but HTTP is built for clients calling servers
- Setup: client initializes, server returns a session ID, client confirms with an initialized notification; the session ID must be sent on all later requests
- Workaround: the client keeps a GET request open as a Server-Sent Events (SSE) stream so the server can send messages at any time
- Each tool call adds a second, short-lived SSE connection that closes after the result; progress notifications go over the primary connection, logging and the tool result over the tool-specific one
- `stateless_http` and `json_response` can disable this SSE mechanism and limit server-to-client features
- More complex than the other MCP transports; the dual-connection model helps with debugging

**State and the StreamableHTTP transport**
- Scaling: behind a load balancer the GET SSE stream and POST tool calls may hit different instances, so a POST needing sampling must coordinate with the instance holding the stream
- `stateless_http`: removes that coordination; no session IDs, no server-to-client requests (sampling, progress reports, resource subscriptions unavailable); clients can skip the initialization handshake
- `json_response`: disables streaming for POST responses; clients get only the final result as plain JSON
- Use stateless for horizontal scaling without server-to-client needs; use json_response when streaming is not needed or a system expects plain JSON
- If you develop with STDIO but deploy with HTTP, test under the production transport since stateful and stateless behavior can differ a lot

---

## 4. Sources

- The StreamableHTTP transport, Model Context Protocol: Advanced Topics, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/the-streamablehttp-transport
- StreamableHTTP in depth, Model Context Protocol: Advanced Topics, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/streamablehttp-in-depth
- State and the StreamableHTTP transport, Model Context Protocol: Advanced Topics, Claude Academy: https://academy.claude.com/courses/model-context-protocol-advanced-topics/state-and-the-streamablehttp-transport
