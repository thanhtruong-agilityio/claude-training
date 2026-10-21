# Day 09: Hooks and automation (requirements)

Course task, not the `docs/tickets/09-*` ticket (edit and archive patient).

## Goal

Ship hooks as PRs, climb the automation ladder, then evaluate `@claude review` on the first hook PR.

## Scope

| # | Item | Scope | Done when |
|---|------|-------|-----------|
| 0 | PR 0: GitHub Actions `@claude` | `.github/workflows/claude.yml` + API key secret | Workflow runs on a PR; merged before PR 1 is reviewed |
| 1 | PR 1: format-on-edit | PostToolUse hook on Edit/Write. `ruff format` for `clinic-app/backend/**/*.py` (via `uv run`), `prettier` for `clinic-app/frontend/src/**/*.{ts,tsx}`. Add both dev-dependencies and minimal config | Editing a `.py` and a `.tsx` file auto-formats it; `make test` green; PR follows template |
| 2 | PR 2: notify-on-finish | Stop hook, desktop notification (macOS `osascript`) | Notification fires when a turn ends; PR follows template |
| 3 | `/goal` | One small bounded task (e.g. format backend, tests green) | Goal condition and result recorded |
| 4 | Desktop scheduled task | Morning briefing, reuse `/loop` prompts from PR #25 | Scheduled and run at least once |
| 5 | Routines (cloud) | Note only: compare with scheduled task; risk of `clinic.db` / patient data in cloud runs | Section in day note |
| 6 | Exercise | `@claude review` on PR 1; judge each comment (correct / wrong / ignore) | Evaluation table in day note |
| 7 | Note | `docs/day-09.md` in the day-note structure, terse style | Checkboxes match real state |

## Order

PR 0 -> PR 1 -> exercise (6), then PR 2, `/goal`, scheduled task, Routines note, day note.

## Constraints

- One ticket per branch, `<type>/<ticket>-<slug>`; three short tickets go in `docs/tickets/` so branches carry an id: 11 = claude workflow (PR 0), 12 = format-on-edit (PR 1), 13 = notify-on-finish (PR 2).
- Never commit or push to `main`; ask before every push, merge, branch deletion, deploy.
- Hooks and workflows must not read `.env`, `*.db`, `backups/`.
- `.claude/settings.local.json` stays out of git.

## Open points

- Confirm PR 0 (Actions) precedes PR 1.
- Prettier/ruff versions and config are decided in the plan.
