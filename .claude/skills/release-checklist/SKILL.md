---
name: release-checklist
description: Use when a branch is ready to ship - before pushing, opening a PR or merging - runs the team's release checklist step by step and reports what passed, failed or was skipped
---

# Release checklist

Run these steps in order. Report each as `pass`, `fail` or `skipped (reason)`. Stop at the first `fail` and say what to fix.

## Steps

1. **Branch**: `git branch --show-current`. Must be `training/day-NN` or `<type>/<ticket>-<slug>`. Never `main`, `master`, `develop` or `release/*`.
2. **Clean tree**: `git status`. Only files that belong to this change are staged. Flag any untracked file that is not part of it; don't add it.
3. **No secrets**: staged files contain no `*.db`, `.env`, tokens or `.claude/settings.local.json`. No client secrets or customer data in notes or commit text.
4. **Tests**: only if `clinic-app/` changed, run `make test` from `clinic-app/` and quote the real result. Docs-only change: `skipped (docs only)`.
5. **Commits**: `git log main..HEAD`. Each subject is Conventional Commits, lowercase (e.g. `docs(notes): add notes for day NN <topic>`). Check with `cl-core:commit`; skip that check for `training/` branch names, which `cl-core:branch` rejects.
6. **PR text**: follow `.github/pull_request_template.md` and `docs/definition-of-done.md`. If either file does not exist, say `skipped (file missing)`; don't invent its content.
7. **Ask before shipping**: show the result table, then ask before every push, merge, branch deletion and deploy.

## Output

| # | Step | Result |
|---|------|--------|

Then one line: ready to ship, or what blocks it.

## Rules

- Never push, merge or open the PR as part of this checklist; step 7 is a question, not an action.
- A result is only `pass` after you ran the command and read its output.
- Don't run build or test commands for parts of the repo that did not change.
