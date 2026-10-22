# Day 10 Review & quality

- **Date:** 2026-10-23
- **Trainee:** thanh.truong
- **Branch:** `training/day-10`

**Status:** Seeded-bug review experiment, round 1 done with two manual reviews; `/ultrareview` itself not run yet.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Exercises

### Exercise: review a seeded-buggy branch

- [x] Seed 4 bugs + 1 decoy in `clinic-app/backend` on a throwaway branch, open a draft PR (#32, "do not merge")
- [x] Run `make test-backend` to see what the tests already catch
- [x] Review PR #32 and score the findings against the answer key (2 manual reviews)
- [ ] Run `/ultrareview` on PR #32 (not available in the sessions used so far)
- [ ] Round 2: subtler bugs, neutral PR description
- [ ] Close PR #32 and delete `test/seeded-bugs-clinic` (needs an explicit yes)

---

## 3. Key takeaways

**Seeded-buggy branch: what it means**
- Plant known bugs on a throwaway branch, run the reviewer, compare with the answer key → measures what it finds and what it reports by mistake
- Keep the answer key out of the repo and out of the PR text; use a fresh session for the review so the reviewer has no hints

| Metric | Meaning |
|---|---|
| Recall | Bugs found / bugs seeded |
| False positives | Findings that are not seeded bugs (decoy included) |
| Right cause | Names the right line and the right reason, not just "something is off" |

**Round 1: seeded bugs**

| # | File | Change | Type |
|---|---|---|---|
| 1 | `reports.py` | `revenue`: `visited_at < end` → `<= end` | boundary |
| 2 | `reports.py` | `follow_ups`: dropped the `deleted_at is None` filter | missing filter |
| 3 | `reports.py` | `revenue`: `owed` = sum of fee, ignores `paid_amount` | wrong calculation |
| 4 | `visits.py` | `create_visit`: dropped `_require_active` (archived patient should be 409) | missing validation |
| Decoy | `queries.py` | redundant `list(items)`, correct | noise |

**Round 1: results**
- `make test-backend`: 3 failed, 32 passed → the 3 failing tests cover all 4 bugs (the revenue test catches #1 and #3 together). Failing tests ≠ number of bugs
- Two manual reviews of PR #32 (plain Claude passes, not `/ultrareview`)

| | Review 1 | Review 2 |
|---|---|---|
| Recall | 4/4 | 4/4 |
| Right cause | 4/4 | 4/4 |
| False positives | 0 (decoy filed as nit) | 0 (decoy filed as nit) |
| Wrong inference | Guessed one bug had no test (#3) | Same: "3 failed but 4 bugs → one is uncaught" |

- Both reviews made the same mistake: matched "3 failing tests" to "3 bugs" without checking
- Review 2 added that #3 double-counts payments (`collected + owed`)

**Limits: what this does not show**
- Not `/ultrareview`: both reviews were manual passes, so the tool itself is unmeasured
- Both reviewers saw the PR body ("do not merge", "3 failed") → they knew bugs were planted
- Diff was 4 small edits; "dropped one line" bugs are the easiest kind
- Fair reading: Claude catches obvious bugs on a small, hinted diff and handles a decoy well; subtle bugs and big diffs untested
