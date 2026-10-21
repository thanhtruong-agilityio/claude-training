# Day 06 practice - design

Source: https://dojo.agilityio.dev/schedule/day-06.html (Developer track, Claude Code Desktop core). Plan: Pro.

## Goal

Meet Developer Checkpoint 2 by folding every deliverable into real work on two clinic-app tickets.

| Checkpoint item | Where it happens |
|---|---|
| Two parallel sessions, both merged | Tickets 08 and 10, one git worktree each |
| One plan-mode change steered via diff comments | Ticket 08 |
| One artifact | PR walkthrough of 08 or 10 |
| One Remote Control steer | Ticket 10, from the phone |
| One `/loop` run | PR of ticket 10 |

Also required by the exercise: `loop.md`, `ultrathink` vs `/effort` comparison with plan-tier notes, one cloud session, a screenshot of each deliverable.

## Tickets

- `docs/tickets/08-clinic-app-safe-backup.md` - branch `fix/08-safe-backup`.
- `docs/tickets/10-clinic-app-no-patient-data-in-logs.md` - branch `fix/10-no-patient-data-in-logs`.
- Merge order: 08 first, then rebase 10 if config files overlap.

## Steps

0. **Setup.** Review untracked `.github/`, `docs/definition-of-done.md`, `docs/plans/`, `docs/specs/` for secrets or real patient data. Commit them on `chore/day-06-setup` (separate chore). Worktrees branch from it, or from `main` once it is merged. Create `training/day-06` + `docs/day-06.md` with the `day-note` skill.
1. **Parallel sessions.** One worktree per ticket. Each needs its own venv, `node_modules`, SQLite file and ports. Watch both in agent view.
2. **Plan-mode (08).** Plan first, steer the plan with diff comments.
3. **Ticket 10.** Open PR, `/loop 15m` on it. No real deploy exists, so `/loop 5m check the deploy` becomes a CI-status check with a run cap (Pro quota). Write `loop.md`. `/rc`, then one steer from the phone via claude.ai/code.
4. **Effort comparison.** Run `ultrathink` and several `/effort` levels on the ticket 10 logging problem before fixing it (or on a reverted copy). Verify which features the Pro plan allows and record gaps.
5. **Artifact.** PR walkthrough of 08 or 10, shared with a peer.
6. **Cloud session.** Long docs task in a separate file/branch (`docs/day-06-effort-table.md`), so it does not race with `docs/day-06.md`. Needs a pushed branch. Close the laptop, check progress from claude.ai/code.
7. **Close.** Merge both PRs, fill `docs/day-06.md` (day-note structure + checkpoint checklist), consult the advisor before reporting done.

## Rules

- Synthetic data only in logs, artifact, screenshots. Capture screenshots as each step finishes.
- Ask before every push, merge, branch deletion.
- Never commit to `main`; conventional commits, lowercase subject.
- Claude does: worktrees, code, PRs, `loop.md`, notes. User does: phone steer, agent view, screenshots to the channel.
