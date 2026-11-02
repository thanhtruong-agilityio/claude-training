#!/usr/bin/env bash
# An intent PR was merged: create one ticket per docs/intents/<slug>.md that has none yet, and comment the links on the PR.
# Environment: PR (PR number), GH_TOKEN. Run from a checkout of the merge commit. GitHub issues only.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
cfg() { bash "$here/ticket-config.sh" "$@"; }

if [ "$(cfg tracker github)" != "github" ]; then
  echo "::notice::tracker is not github; create the ticket with /cl-core:intent publish"
  exit 0
fi

# Creating the ticket always runs. The Backlog label is applied unless the project opted out with ticket_updates: no-update.
label=""
[ "$(cfg ticket_updates unset)" != "no-update" ] && label=$(cfg intent "Backlog" "  ")
[ -n "$label" ] && gh label create "$label" --color BFD4F2 >/dev/null 2>&1 || true

links=""
while IFS= read -r path; do
  [[ "$path" =~ ^docs/intents/[^/]+\.md$ ]] || continue
  [ -f "$path" ] || continue
  title=$(sed -n 's/^# Intent: *//p' "$path" | head -1)
  title="${title:-$(basename "$path" .md)}"

  existing=$(gh issue list --state all --search "\"Intent: $path\" in:body" --json number --jq 'length')
  if [ "$existing" != "0" ]; then
    echo "::notice::$path already has a ticket"
    continue
  fi

  # First line stays "Intent: <path>" (the duplicate check searches for it); the file content follows.
  body="Intent: $path"$'\n\n'"$(cat "$path")"
  args=(--title "$title" --body "$body")
  [ -n "$label" ] && args+=(--label "$label")
  if ! url=$(gh issue create "${args[@]}"); then
    # The status label may not exist yet; create the ticket without it rather than lose it.
    echo "::warning::could not apply label '$label'; creating the ticket without it"
    url=$(gh issue create --title "$title" --body "$body")
  fi
  links+="- $path: $url"$'\n'
done < <(gh pr view "$PR" --json files --jq '.files[].path')

[ -n "$links" ] && gh pr comment "$PR" --body "Tickets created:"$'\n'"$links"
exit 0
