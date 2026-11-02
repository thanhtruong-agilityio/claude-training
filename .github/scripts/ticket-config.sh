#!/usr/bin/env bash
# Read one value from docs/ticket-config.yml. Prints the default when the file or the key is missing.
# Usage: bash .github/scripts/ticket-config.sh <key> [<default>] [<indent>]
#   key      a top-level key (ticket_updates, tracker) or, with indent "  ", a key under statuses (in-dev)
set -euo pipefail

key="$1"
default="${2:-}"
indent="${3:-}"
config="${TICKET_CONFIG:-docs/ticket-config.yml}"

value=""
if [ -f "$config" ]; then
  value=$(sed -n "s/^${indent}${key}: *\([^#]*\).*/\1/p" "$config" | head -1 | sed 's/[[:space:]]*$//; s/^"\(.*\)"$/\1/')
fi
printf '%s\n' "${value:-$default}"
