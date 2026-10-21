#!/usr/bin/env bash
# Stop hook: desktop notification when Claude finishes a turn.
osascript -e 'display notification "Claude finished, waiting for you" with title "Claude Code"' 2>/dev/null || true
exit 0
