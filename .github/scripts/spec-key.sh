#!/usr/bin/env bash
# Print the ticket KEY of a spec branch: spec/<KEY>, spec/<KEY>-answers or spec/<KEY>-r<N>.
# Exit 1 when the branch is not a spec branch or the KEY has unexpected characters.
# Usage: bash .github/scripts/spec-key.sh <branch>
set -euo pipefail

branch="${1:-}"
case "$branch" in spec/*) ;; *) exit 1 ;; esac

key="${branch#spec/}"
key="${key%-answers}"
key="${key%-r[0-9]*}"
[[ "$key" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]] || exit 1
printf '%s\n' "$key"
