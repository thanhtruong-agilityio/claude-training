# Day 09 Hooks and Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use cl-core:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship format-on-edit and notify-on-finish hooks as PRs, climb the automation ladder, and evaluate `@claude review` on the first hook PR.

**Architecture:** Hooks live in `.claude/settings.json` (notify, repo-wide) and `clinic-app/.claude/settings.json` (format, clinic-app only) and call small scripts under the matching `hooks/` folder. Hooks run on the host (not in docker), so formatters are called through `uv run --project` and the local `node_modules/.bin`. The `@claude` GitHub Action goes in first so the hook PR can be reviewed by it.

**Tech Stack:** Claude Code hooks (PostToolUse, Stop), bash + jq, ruff, prettier, GitHub Actions (`anthropics/claude-code-action`), `gh` CLI.

**Spec:** `docs/specs/2026-10-21-day-09-hooks-and-automation-design.md`

**Architecture Diagrams:** none.

## Global Constraints

- One ticket per branch, named `<type>/<ticket>-<slug>`, ticket id lowercase.
- Commits: Conventional Commits, lowercase subject.
- Never commit or push to `main`, `master`, `develop`, `release/*`.
- Ask the user before every push, merge, branch deletion, deploy.
- Hooks and workflows must not read `.env`, `*.db`, `backups/`.
- `.claude/settings.local.json` stays out of git.
- PR body follows `.github/pull_request_template.md` (Ticket, What, Why, How tested, Risk).
- Order: Task 1 (tickets) -> Task 2 (PR 0) -> Task 3 (PR 1) -> Task 4 (exercise) -> Task 5 (PR 2) -> Tasks 6-8 -> Task 9 (day note).

## How This Plan Was Created

1. **Spec provided:** `docs/specs/2026-10-21-day-09-hooks-and-automation-design.md`
2. **Implementation plan created:** This document
3. **Recommended execution:** `cl-core:executing-plans`

---

## File Structure

| File | Responsibility |
|---|---|
| `docs/tickets/11-claude-github-action.md` | Ticket for PR 0 |
| `docs/tickets/12-format-on-edit-hook.md` | Ticket for PR 1 |
| `docs/tickets/13-notify-on-finish-hook.md` | Ticket for PR 2 |
| `.github/workflows/claude.yml` | `@claude` responder (PR 0) |
| `clinic-app/.claude/hooks/format-on-edit.sh` | Reads hook JSON, formats one file (PR 1) |
| `.claude/hooks/notify-on-finish.sh` | Desktop notification (PR 2) |
| `.claude/settings.json` | Registers the hooks (PR 1, PR 2) |
| `clinic-app/backend/pyproject.toml` | Add `ruff` to dev group (PR 1) |
| `clinic-app/frontend/package.json`, `.prettierrc` | Add `prettier` (PR 1) |
| `docs/day-09.md` | Day note |

---

### Task 1: Write the three tickets

Branch: `docs/day-09-tickets`, from `main`. Include the spec and this plan in the same commit (they are untracked on `main` now).

**Files:**
- Create: `docs/tickets/11-claude-github-action.md`, `docs/tickets/12-format-on-edit-hook.md`, `docs/tickets/13-notify-on-finish-hook.md`
- Already written, to be committed: `docs/specs/2026-10-21-day-09-hooks-and-automation-design.md`, `docs/plans/2026-10-21-day-09-hooks-and-automation.md`

**Interfaces:**
- Produces: ticket ids `11`, `12`, `13` used in branch names and PR bodies.

**Acceptance Criteria:**
- [ ] Each ticket uses the same sections as `docs/tickets/10-clinic-app-no-patient-data-in-logs.md` (Context, Scope, Acceptance Criteria)
- [ ] Nothing committed on `main`

- [ ] **Step 1: Create the branch**

Run: `git switch -c docs/day-09-tickets`
Expected: `Switched to a new branch 'docs/day-09-tickets'`

- [ ] **Step 2: Write ticket 11**

```markdown
# 11 - Add the @claude GitHub Action

## Context
Day 09 exercise needs `@claude review` to answer on a PR. The repo has no workflows.

## Scope
- Add `.github/workflows/claude.yml` using `anthropics/claude-code-action`.
- Trigger on comments, review comments, reviews and issues that mention `@claude`.

## Acceptance Criteria
- [ ] Commenting `@claude review` on a PR starts the workflow
- [ ] The API key comes from the `ANTHROPIC_API_KEY` repo secret, never from a file
```

- [ ] **Step 3: Write ticket 12**

```markdown
# 12 - Format files automatically after Claude edits them

## Context
Claude edits files in clinic-app without a formatter, so style drifts between edits.

## Scope
- PostToolUse hook on Edit and Write that formats the edited file.
- Backend `*.py` with ruff, frontend `src/**/*.{ts,tsx}` with prettier.
- Add both tools as dev dependencies. Format existing code once, in its own commit.

## Acceptance Criteria
- [ ] Editing a `.py` file and a `.tsx` file leaves them formatted
- [ ] Other file types are left alone
- [ ] A formatter failure never blocks the edit
- [ ] `make test` passes
```

- [ ] **Step 4: Write ticket 13**

```markdown
# 13 - Notify when Claude finishes

## Context
Long turns need a signal when Claude stops and waits for input.

## Scope
- Stop hook that shows a desktop notification (macOS).

## Acceptance Criteria
- [ ] A notification appears when a turn ends
- [ ] The hook exits 0 even if the notifier is missing
```

- [ ] **Step 5: Commit**

```bash
git add docs/tickets/11-claude-github-action.md docs/tickets/12-format-on-edit-hook.md docs/tickets/13-notify-on-finish-hook.md docs/specs/2026-10-21-day-09-hooks-and-automation-design.md docs/plans/2026-10-21-day-09-hooks-and-automation.md
git commit -m "docs(tickets): add day 09 spec, plan and tickets 11-13"
```

Ask the user before pushing or opening a PR for this branch.

---

### Task 2: PR 0 - the @claude workflow

Branch: `ci/11-claude-github-action`, from `main`.

**Files:**
- Create: `.github/workflows/claude.yml`

**Interfaces:**
- Consumes: repo secret `ANTHROPIC_API_KEY` (set by the user, see Step 1).
- Produces: a workflow that answers `@claude` comments; Task 4 depends on it being merged.

**Acceptance Criteria:**
- [ ] Workflow file passes `gh workflow list` after merge
- [ ] No key appears in any committed file

- [ ] **Step 1: User sets the secret (agent must not handle the key)**

Ask the user to run, in their own terminal, and paste the key at the prompt:

```bash
gh secret set ANTHROPIC_API_KEY
```

Also confirm the Claude GitHub app is installed on the repo (`/install-github-app` in Claude Code does both). Do not paste the key into the chat.

- [ ] **Step 2: Create the branch**

Run: `git switch main && git switch -c ci/11-claude-github-action`

- [ ] **Step 3: Write the workflow**

```yaml
name: Claude

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  pull_request_review:
    types: [submitted]
  issues:
    types: [opened, assigned]

jobs:
  claude:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

Before committing, check the current major version and input names in the action's README (`gh api repos/anthropics/claude-code-action/readme --jq .content | base64 -d | head -80`); fix `@v1` or inputs if they differ.

- [ ] **Step 4: Validate the YAML parses**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/claude.yml')); print('ok')"`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/claude.yml
git commit -m "ci(claude): add @claude github action workflow"
```

- [ ] **Step 6: Ask the user, then push and open the PR**

After approval: `git push -u origin ci/11-claude-github-action`, then open the PR with the template (Ticket: 11, How tested: YAML parse; real test is Task 4). Ask the user before merging. The workflow only answers once it exists on `main`.

---

### Task 3: PR 1 - format-on-edit hook

Branch: `feat/12-format-on-edit-hook`, from `main` (after PR 0 is merged).

**Files:**
- Modify: `clinic-app/backend/pyproject.toml` (dev group)
- Modify: `clinic-app/frontend/package.json`, `package-lock.json`
- Create: `clinic-app/frontend/.prettierrc`
- Create: `clinic-app/.claude/hooks/format-on-edit.sh`
- Create: `clinic-app/.claude/settings.json` (registers the hook; scoped to clinic-app, so it applies when Claude is launched from `clinic-app/`)

**Interfaces:**
- Consumes: Claude Code PostToolUse stdin JSON with `.tool_input.file_path`.
- Produces: `clinic-app/.claude/hooks/format-on-edit.sh`, executable, always exits 0.

**Acceptance Criteria:**
- [ ] `.py` under `clinic-app/backend/` and `.ts/.tsx` under `clinic-app/frontend/src/` are formatted by the script
- [ ] Any other path is untouched; missing file or missing tool exits 0
- [ ] `make test` passes
- [ ] Baseline formatting is its own commit

- [ ] **Step 1: Create the branch**

Run: `git switch main && git pull --ff-only && git switch -c feat/12-format-on-edit-hook`

- [ ] **Step 2: Add the tools**

```bash
uv add --project clinic-app/backend --dev ruff
cd clinic-app/frontend && npm install --save-dev prettier && cd ../..
```

Create `clinic-app/frontend/.prettierrc` (matches existing double quotes and semicolons; the code uses lines up to 100 characters):

```json
{ "printWidth": 100 }
```

- [ ] **Step 3: Check how big the baseline diff is**

Run: `uv run --project clinic-app/backend ruff format --diff clinic-app/backend/app clinic-app/backend/tests | head -60` and `clinic-app/frontend/node_modules/.bin/prettier --check clinic-app/frontend/src`
Expected: list of files that would change. If the diff is large, tell the user and ask whether to keep the baseline in this PR or move it to a separate PR.

- [ ] **Step 4: Baseline commit**

```bash
uv run --project clinic-app/backend ruff format clinic-app/backend/app clinic-app/backend/tests
clinic-app/frontend/node_modules/.bin/prettier --write clinic-app/frontend/src
git add clinic-app
git commit -m "style(clinic-app): format existing code with ruff and prettier"
```

Do not stage `clinic.db` or `node_modules` (they are ignored).

- [ ] **Step 5: Write the failing check for the script**

The script does not exist yet. Prepare two scratch files and run the (missing) script:

```bash
printf 'x   =   1\n' > clinic-app/backend/app/_scratch.py
printf 'const   a  =  1\n' > clinic-app/frontend/src/_scratch.ts
echo '{"tool_input":{"file_path":"'"$PWD"'/clinic-app/backend/app/_scratch.py"}}' | clinic-app/.claude/hooks/format-on-edit.sh
```

Expected: `No such file or directory`

- [ ] **Step 6: Write the script**

`clinic-app/.claude/hooks/format-on-edit.sh`:

```bash
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
```

Run: `chmod +x clinic-app/.claude/hooks/format-on-edit.sh`

- [ ] **Step 7: Run the check and make it pass**

```bash
echo '{"tool_input":{"file_path":"'"$PWD"'/clinic-app/backend/app/_scratch.py"}}' | clinic-app/.claude/hooks/format-on-edit.sh
echo '{"tool_input":{"file_path":"'"$PWD"'/clinic-app/frontend/src/_scratch.ts"}}' | clinic-app/.claude/hooks/format-on-edit.sh
echo '{"tool_input":{"file_path":"'"$PWD"'/README.md"}}' | clinic-app/.claude/hooks/format-on-edit.sh; echo "exit=$?"
cat clinic-app/backend/app/_scratch.py clinic-app/frontend/src/_scratch.ts
```

Expected: `x = 1` and `const a = 1;`, then `exit=0` for the README call. Then remove the scratch files: `rm clinic-app/backend/app/_scratch.py clinic-app/frontend/src/_scratch.ts`.

- [ ] **Step 8: Register the hook**

Create `clinic-app/.claude/settings.json`:

```json
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Edit|Write",
      "hooks": [
        { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/format-on-edit.sh" }
      ]
    }
  ]
}
```

Validate: `jq . clinic-app/.claude/settings.json > /dev/null && echo ok`

- [ ] **Step 9: Test it live**

Restart the session so settings reload, ask Claude to add a badly spaced line to a scratch `.py` file under `clinic-app/backend/app/`, and confirm it comes back formatted. Delete the scratch file afterwards.

- [ ] **Step 10: Run the project tests**

Run: `make test`
Expected: backend and frontend tests pass.

- [ ] **Step 11: Commit**

```bash
git add clinic-app/.claude/hooks/format-on-edit.sh clinic-app/.claude/settings.json clinic-app/backend/pyproject.toml clinic-app/backend/uv.lock clinic-app/frontend/package.json clinic-app/frontend/package-lock.json clinic-app/frontend/.prettierrc
git commit -m "feat(hooks): format files on edit with ruff and prettier"
```

- [ ] **Step 12: Ask the user, then push and open the PR**

Ticket: 12. How tested: Step 7 outputs, Step 9, `make test`. Risk: first edit of an unformatted file creates diff noise; roll back by removing the `hooks` key.

---

### Task 4: Exercise - evaluate `@claude review`

**Files:**
- Modify: `docs/day-09.md` (evaluation table, written in Task 9)

**Acceptance Criteria:**
- [ ] `@claude review` ran on PR 1
- [ ] Every comment has a verdict: correct / wrong / ignore, with one-line reason

- [ ] **Step 1: Trigger the review**

Run: `gh pr comment <pr-1-number> --body "@claude review"` (ask the user first, it posts to GitHub).

- [ ] **Step 2: Wait for the workflow**

Run: `gh run list --workflow claude.yml --limit 3`
Expected: a run for the comment, ending `completed`. If it fails, read `gh run view <id> --log-failed` and fix the cause (usually the secret or the app install) before retrying; stop if the same error happens twice.

- [ ] **Step 3: Collect and judge the comments**

Run: `gh pr view <pr-1-number> --comments` and `gh api repos/{owner}/{repo}/pulls/<pr-1-number>/comments`
For each comment verify against the code (cl-core:receiving-code-review) and record: comment, verdict, reason. Apply the valid fixes as new commits on the PR branch.

---

### Task 5: PR 2 - notify-on-finish hook

Branch: `feat/13-notify-on-finish-hook`, from `main`.

**Files:**
- Create: `.claude/hooks/notify-on-finish.sh`
- Modify: `.claude/settings.json`

**Interfaces:**
- Produces: `.claude/hooks/notify-on-finish.sh`, executable, always exits 0.

**Acceptance Criteria:**
- [ ] Running the script shows a notification
- [ ] Missing `osascript` does not fail the hook

- [ ] **Step 1: Create the branch**

Run: `git switch main && git pull --ff-only && git switch -c feat/13-notify-on-finish-hook`

- [ ] **Step 2: Write the script**

`.claude/hooks/notify-on-finish.sh`:

```bash
#!/usr/bin/env bash
# Stop hook: desktop notification when Claude finishes a turn.
osascript -e 'display notification "Claude finished, waiting for you" with title "Claude Code"' 2>/dev/null || true
exit 0
```

Run: `chmod +x .claude/hooks/notify-on-finish.sh && .claude/hooks/notify-on-finish.sh; echo "exit=$?"`
Expected: a macOS notification and `exit=0`.

- [ ] **Step 3: Register the hook**

Add to the `hooks` object in `.claude/settings.json` next to `PostToolUse`:

```json
"Stop": [
  {
    "hooks": [
      { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/notify-on-finish.sh" }
    ]
  }
]
```

Validate: `jq . .claude/settings.json > /dev/null && echo ok`

- [ ] **Step 4: Test it live**

Restart the session, send any short prompt, confirm the notification appears when the turn ends.

- [ ] **Step 5: Commit, then ask before push and PR**

```bash
git add .claude/hooks/notify-on-finish.sh .claude/settings.json
git commit -m "feat(hooks): notify when claude finishes a turn"
```

Ticket: 13. Risk: notification noise; roll back by removing the `Stop` key.

---

### Task 6: `/goal` on a bounded task

**Acceptance Criteria:**
- [ ] Goal condition is checkable by a command
- [ ] Result recorded for the day note

- [ ] **Step 1: Pick the task and run it**

Run in Claude Code: `/goal` with the condition: "all `.py` files in clinic-app/backend/app and tests pass `ruff format --check` and `make test-backend` exits 0". If PR 1 already formatted the baseline, use instead: "README of clinic-app lists every make target in the Makefile". Keep it on a throwaway branch `chore/day-09-goal`; do not open a PR for it.

- [ ] **Step 2: Record**

Write down: the condition, how many turns it took, whether it stopped on its own. Delete the throwaway branch only after asking the user.

---

### Task 7: Desktop scheduled task (morning briefing)

**Acceptance Criteria:**
- [ ] Task exists with a schedule and has run at least once

- [ ] **Step 1: Create the task**

In Claude Code Desktop, create a scheduled task, weekdays 08:30, working folder this repo. Prompt: reuse the PR/CI check wording from `docs/` or `.claude` loop prompts added in PR #25 (find it with `git show cc53482 --stat`), plus "list open PRs, their CI state, and unreviewed `@claude` comments". Read-only: the prompt must not push or merge.

- [ ] **Step 2: Run it once now ("Run now") and record the output**

Expected: a short briefing. Note anything it got wrong.

---

### Task 8: Routines (note only)

**Acceptance Criteria:**
- [ ] Section for the day note, no routine created

- [ ] **Step 1: Read the Routines overview** and write 3-5 terse lines: where it runs (cloud, not your machine), trigger types, how it differs from the Desktop scheduled task, and the risk for this repo (`clinic.db` / patient data must never be reachable from a cloud run; the repo ignores `*.db` but a routine clones from GitHub, so check that nothing sensitive is committed first).

---

### Task 9: Day note

Branch: `training/day-09`, from `main`. Use the `day-note` skill to create the branch and `docs/day-09.md` skeleton.

**Files:**
- Create: `docs/day-09.md`

**Acceptance Criteria:**
- [ ] Same structure as `docs/day-08.md`: header (date 2026-10-21, trainee, branch), status line, `1. Setup check`, `2. Courses` with checkboxes, `3. Key takeaways`
- [ ] Checkboxes reflect real state; pending items stay unchecked
- [ ] Contains: hook PR links, automation ladder results (Tasks 6-8), the `@claude review` evaluation table from Task 4
- [ ] Terse tables and one-liners, no prose

- [ ] **Step 1: Generate the skeleton** with the `day-note` skill.
- [ ] **Step 2: Fill sections 2 and 3** from the records of Tasks 2-8. Use `/day-recap` for the takeaways draft, then trim to the repo's terse style.
- [ ] **Step 3: Commit**

```bash
git add docs/day-09.md
git commit -m "docs(notes): add notes for day 09 hooks and automation"
```

Ask the user before pushing.

---

## Self-Review

- **Spec coverage:** PR 0 -> Task 2; PR 1 -> Task 3; PR 2 -> Task 5; `/goal` -> Task 6; scheduled task -> Task 7; Routines note -> Task 8; exercise -> Task 4; day note -> Task 9; tickets -> Task 1.
- **Placeholders:** `<pr-1-number>` and `<id>` are values known only at run time; everything else is concrete.
- **Consistency:** script names `format-on-edit.sh` and `notify-on-finish.sh` and ticket ids 11-13 are used the same way in every task and in the File Structure table.
