# Day 13 Capstone build

- **Date:** 2026-10-27
- **Trainee:** thanh.truong
- **Branch:** `training/day-13`

**Status:** Tickets 14 (BE) and 15 (FE) built in two isolated worktrees, one PR each (#42, #43), reviewed, tests green, not merged yet. Ticket 16 not started.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Exercises

### Build the follow-up dashboard (clinic-app)

- [x] Plan mode first: plans for ticket 14 and 15 approved before any code
- [x] Two worktrees, two isolated agent sessions, one ticket each
- [x] QA step: matrix rows turned into failing tests first, then Dev made them green
- [x] Ticket 14 (BE, issue #37): PR #42 opened, reviewed, review nits fixed
- [x] Ticket 15 (FE, issue #38): PR #43 opened as draft, reviewed, review nits fixed
- [x] Manual browser check with the real endpoint (fake data), AC12 long name
- [ ] PR #42 merged
- [ ] PR #43 rebased on `main`, ready for review, merged
- [ ] Ticket 16 (FE states, issue #39) built
- [ ] `@claude review` result on PR #42 read (comment posted, output not read yet)
- [ ] Another person reviewed the PRs, CI green (no CI runs on PRs, see takeaways)

| Artifact | Where |
|---|---|
| Plan, ticket 14 | [docs/plans/2026-10-27-follow-up-dashboard-t14-plan.md](plans/2026-10-27-follow-up-dashboard-t14-plan.md) |
| Plan, ticket 15 | [docs/plans/2026-10-27-follow-up-dashboard-t15-plan.md](plans/2026-10-27-follow-up-dashboard-t15-plan.md) (on the `feat/38-…` branch) |
| PRs | #42 (BE endpoint), #43 (FE list) |
| Browser check screenshots | [wide](../exercises/day-13-due-follow-ups-wide.png), [narrow](../exercises/day-13-due-follow-ups-narrow.png) |
| GitLab sync of Day 12 | branch `sync/day-12` pushed; the merge request into GitLab `main` is opened and merged by hand (not confirmed) |

---

## 3. Key takeaways

**Plan mode first**
- The plan is the biggest lever: nothing is written until the plan is approved. Both plans were approved, then committed as the first commit of each branch
- Plan 14 came from Day 12 and was revised against the rewritten ticket (new ACs). Plan 15 was written after reading the frontend code
- Plans listed risks up front, and most were real: no error state until ticket 16, AC12 not provable in jsdom, merge order, Docker ports

**Git worktrees + parallel sessions**
- Two tickets in flight: `feat/37-due-follow-ups-endpoint` (BE) and `feat/38-due-follow-ups-list` (FE, built against a mocked API from the ticket 14 contract)
- Ticket 16 depends on 15 and 15 on 14, so only two could run in parallel; the third waits for the merge
- `make test-*` uses `docker compose run --rm --no-deps`: no published ports, so two worktrees test side by side. Only one can run `make up`

| Step | Ticket 14 (BE) | Ticket 15 (FE) |
|---|---|---|
| Red (tests first) | 32 failed, 36 passed | 22 failed, 15 passed |
| Green | 68 passed | 37 passed |
| Review nits fixed | 3 (imports, narrower query, one 422 shape) | 2 (CSS class, wrapped import) |

**What went wrong (honest)**
- Docker daemon was off: the BE agent stopped and reported blocked, no commits and no fake test results. I restarted it once the daemon was up. The FE agent opened Docker Desktop on its own, outside what I asked
- Hook `block-main.sh` looks at the working directory, not the branch being committed, so both agents were blocked while the shell stood in the main checkout. One agent tried `CL_ALLOW_MAIN=1`, which was denied; both then used `git -C <worktree>`
- The FE agent wrote the code before committing the red tests, so the red run had 6 unrelated tests failing too. The QA-then-Dev split is only formal when one agent plays both roles
- `curl` was denied and the Chrome extension was not connected at first, so the browser check came late. Chrome would not shrink below 556px, so 400px was not tested
- The GitHub token needed permissions one by one: Issues write, then Pull requests write; merging still needs Contents write, so merges are done on the web. Local `main` had stray merge commits, so Day 13 branches start from `origin/main`

**Review and CI**
- Reviewed my own PRs in the order: correctness, tests, readability, security, scope. No blockers; five nits on each PR, the five code nits fixed (3 on #42, 2 on #43), the doc and cleanup ones left for later
- The only workflow is `claude.yml`: it runs only when a comment or review contains `@claude`. No `pull_request` trigger, so no test CI and no automatic review. "CI green" in the definition of done cannot be met today
- Next step if wanted: a second workflow running `make test` on pull requests

**Who edits what (rule of the day)**
- Everything today was Claude-assisted: spec updates, tests, code, PR texts, this note. Human edit: plan approvals, review decisions, the "simple comparison" rule for names, merge decisions
- The BA step found no new questions during the build; open question OQ1 (same-day visit counts as coming back) is still a working default, not a client answer

**GitLab mirror**
- Histories differ (GitHub squashes, GitLab merges `sync/day-NN`): sync is a branch plus a merge request, never a push to `main`. Packaged as the `sync-gitlab` skill (PR #41)
