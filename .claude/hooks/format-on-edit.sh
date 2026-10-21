#!/usr/bin/env bash
# PostToolUse hook: format the file Claude just edited. Never blocks the edit.
f=$(jq -r '.tool_input.file_path // empty')
[ -n "$f" ] && [ -f "$f" ] || exit 0
root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

case "$f" in
  "$root"/clinic-app/backend/*.py)
    uv run --project "$root/clinic-app/backend" ruff format "$f" >&2 || true
    ;;
  "$root"/clinic-app/frontend/src/*.ts | "$root"/clinic-app/frontend/src/*.tsx)
    "$root/clinic-app/frontend/node_modules/.bin/prettier" --write "$f" >&2 || true
    ;;
esac
exit 0
