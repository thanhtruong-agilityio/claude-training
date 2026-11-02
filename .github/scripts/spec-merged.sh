#!/usr/bin/env bash
# A spec PR was merged: move its ticket from In Progress to Spec Review, or warn when it is in another status.
# Environment: BRANCH (head branch of the PR), PR (PR number), GH_TOKEN. GitHub issues only.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
cfg() { bash "$here/ticket-config.sh" "$@"; }

[ "$(cfg tracker github)" = "github" ] || { echo "::notice::tracker is not github; set the status by hand"; exit 0; }
[ "$(cfg ticket_updates unset)" = "update" ] || { echo "::notice::ticket_updates is not 'update'; nothing written"; exit 0; }

key=$(bash "$here/spec-key.sh" "$BRANCH") || { echo "::notice::not a spec branch"; exit 0; }
[[ "$key" =~ ^[0-9]+$ ]] || { echo "::notice::KEY '$key' is not a GitHub issue number; set the status by hand"; exit 0; }

in_dev=$(cfg in-dev "In Progress" "  ")
review=$(cfg spec-review "Spec Review" "  ")
labels=$(gh issue view "$key" --json labels --jq '.labels[].name')

if grep -qxF "$in_dev" <<<"$labels"; then
  args=(--remove-label "$in_dev" --add-label "$review")
  grep -qxF "claimed" <<<"$labels" && args+=(--remove-label claimed)
  gh issue edit "$key" "${args[@]}"
  gh issue comment "$key" --body "Spec PR #$PR merged. Status set to $review."
else
  gh issue edit "$key" --add-label needs-human
  gh issue comment "$key" --body "Spec PR #$PR merged but the ticket is not $in_dev, so its status was not changed. A person needs to check it."
fi
