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

# Creating the ticket always runs; the status label is a status write, so it follows ticket_updates.
label=""
[ "$(cfg ticket_updates unset)" = "update" ] && label=$(cfg intent "Backlog" "  ")

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

  args=(--title "$title" --body "Intent: $path")
  [ -n "$label" ] && args+=(--label "$label")
  if ! url=$(gh issue create "${args[@]}"); then
    # The status label may not exist yet; create the ticket without it rather than lose it.
    echo "::warning::could not apply label '$label'; creating the ticket without it"
    url=$(gh issue create --title "$title" --body "Intent: $path")
  fi
  links+="- $path: $url"$'\n'
done < <(gh pr view "$PR" --json files --jq '.files[].path')

[ -n "$links" ] && gh pr comment "$PR" --body "Tickets created:"$'\n'"$links"
exit 0
