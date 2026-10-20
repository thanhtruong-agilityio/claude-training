# mcp-docs

Course example (Introduction to Model Context Protocol, lessons 1-9): a document MCP server, an MCP client, and a CLI chat that talks to Claude or OpenAI through it. Notes: `docs/day-08.md`.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. `cd exercises/mcp-docs && uv sync`
3. `cp .env.example .env` and fill in one provider (never commit `.env`):
   - Claude (default): `ANTHROPIC_API_KEY`; optional `CLAUDE_MODEL` (default `claude-sonnet-5-5`).
   - OpenAI: `LLM_PROVIDER=openai`, `OPENAI_API_KEY` and `OPENAI_MODEL` (no default: set the model you can use).

## Run

- Chat: `uv run main.py`
  - `@plan.md` adds a document to your question (resource read).
  - `/format plan.md` runs the server's `format` prompt.
  - Ctrl-D quits.
- Server only, in the browser Inspector: `uv run mcp dev mcp_server.py` → http://127.0.0.1:6274

## Test

`uv run pytest -q` (no API key needed; the LLM is stubbed).

## Layout

| File | Role |
|---|---|
| `mcp_server.py` | docs dict, 2 tools, 2 resources, 1 prompt |
| `mcp_client.py` | stdio client wrapper |
| `llm.py` | provider-neutral `Reply` / `ToolCall` types |
| `claude.py` | Anthropic adapter |
| `openai_llm.py` | OpenAI adapter |
| `providers.py` | `make_llm(env)`: picks the adapter from `LLM_PROVIDER` |
| `chat.py` | tool loop, `@mention`, `/command` |
| `cli.py` | prompt_toolkit UI + autocomplete |
| `main.py` | entry point |
