# Day 06 Practice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use cl-core:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Meet Developer Checkpoint 2 (two parallel merged sessions, plan-mode diff steer, artifact, Remote Control steer, `/loop` run) by doing tickets 08 and 10 of `clinic-app`.

**Architecture:** Real ticket work carries every deliverable. Ticket 08 (Makefile backup) runs in plan-mode; ticket 10 (log redaction) carries `/loop`, `/rc` and the effort comparison. Two git worktrees run in parallel; a cloud session writes a separate docs file.

**Tech Stack:** Claude Code (worktrees, agent view, `/loop`, `/rc`, Artifacts, cloud sessions), git, GitHub `gh`, Docker Compose, FastAPI + pytest, SQLite.

**Spec:** `docs/specs/2026-10-19-day-06-practice-design.md`

**Architecture Diagrams:** none (declined).

## Global Constraints

- Plan tier: Pro (Remote Control needs a subscription login, not an API key).
- Never commit or push to `main`; ask before every push, merge, branch deletion.
- Branches: `chore/day-06-setup`, `training/day-06`, `fix/08-safe-backup`, `fix/10-no-patient-data-in-logs`. Conventional commits, lowercase subject.
- Synthetic data only in logs, artifact, screenshots. `*.db`, `backups/`, `.env`, `.claude/settings.local.json` stay untracked.
- Notes in English, terse tables/one-liners (`docs/day-05.md` structure).
- Legend: **[YOU]** = only you can do it (phone, screenshots, approvals). **[CLAUDE]** = done in session.

## How This Plan Was Created

1. **Spec provided:** `docs/specs/2026-10-19-day-06-practice-design.md`
2. **Implementation plan created:** this document
3. **Recommended execution:** `cl-core:executing-plans`, inline, because most steps need you at the keyboard or phone.

---

## File structure

| File | Task | Responsibility |
|---|---|---|
| `docs/plans/`, `docs/specs/`, `docs/definition-of-done.md`, `.github/` | 0 | untracked setup files, committed as one chore |
| `docs/day-06.md` | 0, 8 | day note and checkpoint checklist |
| `clinic-app/Makefile`, `clinic-app/README.md` | 2 | safe backup (ticket 08) |
| `clinic-app/backend/app/logging_filters.py`, `main.py`, `tests/test_logging.py` | 3 | redact query strings (ticket 10) |
| `loop.md` | 4 | repo loop prompts |
| `docs/day-06-effort-table.md` | 6 | cloud-session output, separate from `docs/day-06.md` |

---

### Task 0: Setup

**Files:** commit the untracked files; create `docs/day-06.md`.

**Acceptance Criteria:**
- [ ] Untracked files reviewed, no secret or real patient data
- [ ] `chore/day-06-setup` merged to `main` (or worktrees branch from it)
- [ ] `docs/day-06.md` exists on `training/day-06`

- [ ] **Step 1: Review untracked files [CLAUDE]**

Run: `git status --short && grep -rniE "secret|token|password|api[_-]?key" .github docs/definition-of-done.md docs/plans docs/specs/2026-10-15-clinic-app-design.md`
Expected: no hits that are real credentials; patient names in examples are fake.

- [ ] **Step 2: Commit on `chore/day-06-setup` [CLAUDE]** (already on this branch; the spec is committed)

```bash
git add .github docs/definition-of-done.md docs/plans docs/specs/2026-10-15-clinic-app-design.md
git commit -m "chore: add pr template, definition of done, clinic-app plan and spec"
```

- [ ] **Step 3: Push and open PR [YOU approve]**

Ask-first rule applies. After approval: `git push -u origin chore/day-06-setup`, then `/cl-core:pr`. Merge it, then `git switch main && git pull`.

- [ ] **Step 4: Create the day note [CLAUDE]**

Invoke the `day-note` skill for day 06 (branch `training/day-06`, `docs/day-06.md`). Leave all checkboxes unchecked.

---

### Task 1: Two worktrees + agent view

**Acceptance Criteria:**
- [ ] Two worktrees exist, one per ticket branch
- [ ] Both sessions visible in agent view; screenshot taken

- [ ] **Step 1: Create worktrees [CLAUDE]** (from updated `main`)

```bash
git worktree add ../wt-08 -b fix/08-safe-backup main
git worktree add ../wt-10 -b fix/10-no-patient-data-in-logs main
git worktree list
```
Expected: three entries.

- [ ] **Step 2: Start one Claude session in each [YOU]**

Open two terminals/windows: `cd ../wt-08 && claude`, `cd ../wt-10 && claude`. In each: `/cl-core:ticket 08` (resp. `10`).

- [ ] **Step 3: Open agent view, screenshot both running [YOU]**

- [ ] **Step 4: Port isolation [CLAUDE, in wt-10]**

Tests run with `--no-deps` in containers, so no port clash. If `make up` is needed in both, run it in only one. No `.db` is copied (untracked); for ticket 08 create a fake db (Task 2).

---

### Task 2: Ticket 08 in plan-mode (wt-08)

**Files:** Modify `clinic-app/Makefile` (`backup` target), `clinic-app/README.md` (restore steps).

**Acceptance Criteria:** the four criteria of `docs/tickets/08-clinic-app-safe-backup.md`, plus a diff-comment steer.

- [ ] **Step 1: Enter plan-mode [YOU]**

`Shift+Tab` until plan-mode, or `/plan`. Ask: "Plan ticket 08."

- [ ] **Step 2: Steer with diff comments [YOU]**

Comment on at least one line of the proposed plan/diff (e.g. "use the SQLite online backup, not cp"). Screenshot the comment and the revised plan.

- [ ] **Step 3: Implement (target after the steer) [CLAUDE]**

Expected shape of the target (CLI may be missing on host; fall back to the container):

```make
backup: ## consistent, verified copy to backups/clinic-<timestamp>.db
	@test -f backend/clinic.db || { echo "backend/clinic.db not found"; exit 1; }
	@mkdir -p backups
	@f=backups/clinic-$$(date +%Y%m%d-%H%M%S).db; \
	sqlite3 backend/clinic.db ".backup '$$f'" && \
	[ "$$(sqlite3 $$f 'PRAGMA integrity_check;')" = "ok" ] || { rm -f $$f; echo "backup failed integrity check"; exit 1; }; \
	echo "backup ok: $$f"
```

- [ ] **Step 4: Verify on fake data [CLAUDE]**

```bash
cd clinic-app && sqlite3 backend/clinic.db "create table t(x); insert into t values (1);" && make backup
```
Expected: `backup ok: backups/clinic-<ts>.db`. Then rename `backend/clinic.db` away and rerun: expected message `backend/clinic.db not found`, exit 1. Try the README restore steps once. Run `git status` to confirm `backups/` and `*.db` untracked.

- [ ] **Step 5: Commit [CLAUDE]**

```bash
git add clinic-app/Makefile clinic-app/README.md
git commit -m "fix(clinic-app): make backup a verified online snapshot"
```

- [ ] **Step 6: PR [YOU approve push]** `git push -u origin fix/08-safe-backup`, `/cl-core:pr`.

---

### Task 3: Ticket 10 (wt-10) - after Task 4 Step 1

**Files:** Create `clinic-app/backend/app/logging_filters.py`, `clinic-app/backend/tests/test_logging.py`; modify `clinic-app/backend/app/main.py`, `clinic-app/README.md`.

**Acceptance Criteria:** criteria of `docs/tickets/10-clinic-app-no-patient-data-in-logs.md`. Chosen approach: drop the query string from uvicorn's access log (one place, no API or UI change). The "frontend tests updated" criterion then reads: no frontend change, state so in the PR.

- [ ] **Step 1: Failing test**

```python
# clinic-app/backend/tests/test_logging.py
import logging
from app.logging_filters import RedactQueryFilter

def test_access_log_drops_query_string():
    record = logging.LogRecord("uvicorn.access", logging.INFO, "", 0,
        '%s - "%s %s HTTP/%s" %d', ("127.0.0.1:1", "GET", "/patients?q=Nguyen%20Test", "1.1", 200), None)
    assert RedactQueryFilter().filter(record) is True
    assert "Nguyen" not in record.getMessage()
    assert "/patients" in record.getMessage()
```

- [ ] **Step 2: Run, expect FAIL**

Run: `cd clinic-app && make test-backend`
Expected: FAIL, `ModuleNotFoundError: app.logging_filters`.

- [ ] **Step 3: Implement**

```python
# clinic-app/backend/app/logging_filters.py
import logging

class RedactQueryFilter(logging.Filter):
    """Uvicorn access records carry the full path; keep only the part before '?'."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple) and len(record.args) >= 3:
            args = list(record.args)
            args[2] = str(args[2]).split("?", 1)[0]
            record.args = tuple(args)
        return True
```

In `main.py` (read it first, add near the top, after imports):

```python
import logging
from app.logging_filters import RedactQueryFilter

logging.getLogger("uvicorn.access").addFilter(RedactQueryFilter())
```

- [ ] **Step 4: Run, expect PASS**

Run: `cd clinic-app && make test-backend`
Expected: all tests pass.

- [ ] **Step 5: Manual check [CLAUDE]**

```bash
cd clinic-app && make up   # other terminal
curl "http://localhost:8000/patients?q=FakeName"
docker compose logs backend | grep -c FakeName
```
Expected: `0`. Then add the README "Logs" paragraph (uvicorn access log: method, path, status; no query strings; no request bodies).

- [ ] **Step 6: Commit, PR [CLAUDE, YOU approve push]**

```bash
git add clinic-app/backend clinic-app/README.md
git commit -m "fix(clinic-app): keep query strings out of access logs"
```

---

### Task 4: Effort comparison, then `/loop`, `loop.md`, `/rc`

Order: Step 1 happens **before** Task 3 Step 3 (before the fix exists).

- [ ] **Step 1: Effort comparison [YOU run, CLAUDE records]**

In wt-10, before implementing: ask the same question ("how should uvicorn's access log stop recording `?q=`; list options and risks") with `ultrathink`, then with `/effort low`, `medium`, `high` (and any higher level your plan offers). Record in a table: level, time, answer quality, tier note. Note which options your Pro plan lacks.

- [ ] **Step 2: `/loop` on the PR [YOU]**

After the PR for ticket 10 exists: `/loop 15m check PR #<n>: CI status and new review comments`. Let it fire once, screenshot, then stop it.

- [ ] **Step 3: Second loop [YOU]**

No deploy exists, so: `/loop 5m check CI status of PR #<n> and stop when it is green`. Cap at 3 runs. Screenshot.

- [ ] **Step 4: Write `loop.md` [CLAUDE]**

Content: the two prompts above as reusable loops, interval, stop condition, and a note that loops end with the session and consume quota. Commit on `training/day-06`: `docs(loop): add loop prompts`.

- [ ] **Step 5: Remote Control steer [YOU]**

In wt-10 session: `/rc`. On the phone open claude.ai/code, find the session, send a steer such as "also add the README Logs paragraph". Confirm the session acts on it. Screenshot the phone.

---

### Task 5: Artifact

- [ ] **Step 1: Publish [CLAUDE]**

After PR 08 or 10 is open: ask for a PR walkthrough Artifact (what changed, why, how verified, fake-data evidence only). Share the link with a peer. [YOU] send it and screenshot.

---

### Task 6: Cloud session

- [ ] **Step 1: Push a branch [YOU approve]** `training/day-06` (or a dedicated `docs/day-06-effort-table` branch).

- [ ] **Step 2: Start the cloud session [YOU]**

Task: "Write `docs/day-06-effort-table.md`: a table comparing `/effort` levels and `ultrathink` (when to use, cost, speed, plan tier), from the official docs." Close the laptop.

- [ ] **Step 3: Check progress from claude.ai/code [YOU]**, screenshot. Review and merge its PR yourself (ask-first).

---

### Task 7: Merge

- [ ] **Step 1: Merge order [YOU approve each merge]**: ticket 08 PR, then rebase ticket 10 (`git fetch && git rebase origin/main` in wt-10), re-run `make test-backend`, merge.
- [ ] **Step 2: Cleanup after both merged [YOU approve]**: `git worktree remove ../wt-08 ../wt-10`, delete merged branches.

---

### Task 8: Close out

- [ ] **Step 1: Fill `docs/day-06.md` [CLAUDE]** with the day-05 structure: header, status, 1. Setup check, 2. Exercises (checkboxes true to what ran), 3. Key takeaways (effort table, tier notes, loop/rc lessons). Add the checkpoint checklist:

```markdown
- [ ] Two parallel sessions, both merged
- [ ] One plan-mode change steered through diff comments
- [ ] One artifact
- [ ] One Remote Control steer
- [ ] One /loop run
```
Only tick boxes with evidence.

- [ ] **Step 2: Advisor check [CLAUDE]** one line: "is the checkpoint met, anything unsupported?" before reporting done.

- [ ] **Step 3: Commit, PR [YOU approve push]**

```bash
git add docs/day-06.md loop.md
git commit -m "docs(notes): add notes for day 06 claude code desktop core"
```

---

## Self-review

- Spec coverage: setup (0), worktrees/agent view (1), plan-mode steer (2), ticket 10 (3), effort + loop + rc + loop.md (4), artifact (5), cloud (6), merge (7), notes/advisor (8). All spec steps covered.
- Placeholders: only `<n>` (PR number) and `<ts>`, filled at run time.
- Consistency: filter name `RedactQueryFilter` and file `logging_filters.py` identical in test and implementation.
