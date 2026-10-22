# Day 09 Automation ladder

- **Date:** 2026-10-22
- **Trainee:** thanh.truong
- **Branch:** `sync/day-09`

**Status:** Automation ladder in progress — routine vs desktop task vs `/loop` noted; `/goal`, morning-briefing task, routine and `@claude` PR review exercise pending.

---

## 1. Setup check

- [ ] `ANTHROPIC_API_KEY` repo secret set (needed by `.github/workflows/claude.yml`)

---

## 2. Exercises

### Automation ladder

- [ ] `/goal` on a bounded task
- [ ] Desktop scheduled task (morning briefing)
- [ ] Routines overview (cloud)
- [ ] GitHub Actions `@claude` on the training repo

### Exercise: `@claude review`

- [ ] Open the next PR, then comment `@claude review` (opening the PR alone does not trigger the workflow)
- [ ] Evaluate Claude's comments: which are correct, which are noise, which I would apply

---

## 3. Key takeaways

**Automation ladder: which mechanism runs unattended**

| | Routine (cloud) | Desktop scheduled task | `/loop` (in-session) |
|---|---|---|---|
| Runs on | Anthropic cloud infra | My machine | Current session |
| Machine must be on? | No | Yes: app open and machine awake | Yes: session must stay alive |
| Trigger | Schedule, API, GitHub webhook | Schedule only | Interval only |
| Access | GitHub repo(s) and connectors | Local files and tools | Session context |
| Durability | Persistent | Persistent | Expires after 7 days |

**Routine**
- Saved config (prompt, one or more repos, connectors) run on cloud infra; schedule + API + GitHub webhook triggers → closer to a background agent than cron
- Fully autonomous, no approval prompts → scope connectors and repo access tightly
- Default: Claude may only push to branches prefixed `claude/`
- Each run = a cloud session; repo is cloned fresh, so only committed files exist (no `.env`, no uncommitted edits)
- Still research preview: daily run cap and supported plans may have changed → check the official docs

**Desktop scheduled task**
- Runs only while the desktop app is open and the machine is awake; in return it reaches the local filesystem and tools
- Steps: create task (name, prompt, frequency, folder, permission mode) → **Run now** to pre-approve tool permissions → scheduled run opens a new session → read the output
- Prompt must stand alone: nobody is there to answer questions or approve prompts

**`/loop`**
- Repeats a prompt on an interval inside the current session; expires after 7 days
- Fires between turns only, never while Claude is answering
- Fits short-lived polling I am watching, e.g. waiting for CI to finish

**Which one to pick**

| Need | Use |
|---|---|
| Reliability, runs with machine off, or event-triggered (nightly issue triage, weekly dependency audit, review on PR) | Routine |
| Local files or local tools | Desktop scheduled task |
| Temporary repeat during the current session | `/loop` |

**GitHub Actions `@claude`**
- `.github/workflows/claude.yml` fires only when a comment, review or issue contains `@claude`
- Runs on a GitHub runner with `ANTHROPIC_API_KEY` (API billing); config lives in git, so the whole team sees it

| | Routine with GitHub trigger | `claude.yml` `@claude` |
|---|---|---|
| Configured in | claude.ai UI | Repo (git) |
| Runs on | Anthropic cloud | GitHub runner |
| Billed to | Plan usage | API key |
