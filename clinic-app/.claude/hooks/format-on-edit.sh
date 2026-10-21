#!/usr/bin/env bash
# PostToolUse hook: format the file Claude just edited. Never blocks the edit.
f=$(jq -r '.tool_input.file_path // empty')
[ -n "$f" ] && [ -f "$f" ] || exit 0
app="$(cd "$(dirname "$0")/../.." && pwd)"

case "$f" in
  "$app"/backend/*.py)
    uv run --project "$app/backend" ruff format "$f" >&2 || true
    ;;
  "$app"/frontend/src/*.ts | "$app"/frontend/src/*.tsx)
    "$app/frontend/node_modules/.bin/prettier" --write "$f" >&2 || true
    ;;
esac
exit 0
