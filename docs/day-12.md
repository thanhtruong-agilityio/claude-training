# Day 12 Capstone kickoff & planning

- **Date:** 2026-10-27
- **Trainee:** thanh.truong
- **Branch:** `training/day-12`

**Status:** Planning day done for the clinic-app mini-product (follow-up dashboard): intent, spec, ticket pack, test matrix, plan for the first ticket. No code yet.

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Capstone kickoff & planning (everyone)

- [x] Lead ("client"): vague brief + answers to open questions, in the artifacts, not in chat
- [x] BA: intake, open questions, spec, ticket pack
- [x] QA: test matrix from the acceptance criteria
- [x] Dev: questions only through the ticket (zero-question test on ticket 14)
- [ ] Day 13 build (one ticket = one PR = one worktree), not started
- [ ] Push branch and open PR for the Day 12 notes, pending

All four roles played by me, each step in a fresh context where possible.

Artifacts (feature: follow-up dashboard for the doctor):

| Artifact | Where |
|---|---|
| Intent | [docs/intents/2026-10-27-follow-up-dashboard.md](intents/2026-10-27-follow-up-dashboard.md) |
| Spec + 14 client answers | [docs/specs/2026-10-27-follow-up-dashboard-spec.md](specs/2026-10-27-follow-up-dashboard-spec.md) |
| Tickets 14, 15, 16 | [14](tickets/14-clinic-app-due-follow-ups-endpoint.md) · [15](tickets/15-clinic-app-due-follow-ups-list.md) · [16](tickets/16-clinic-app-due-follow-ups-states.md) |
| GitHub issues | #37 (BE), #38 (FE list), #39 (FE states) |
| Test matrix (63 rows) | [docs/specs/2026-10-27-follow-up-dashboard-test-matrix.md](specs/2026-10-27-follow-up-dashboard-test-matrix.md) |
| Plan for ticket 14 | [docs/plans/2026-10-27-follow-up-dashboard-t14-plan.md](plans/2026-10-27-follow-up-dashboard-t14-plan.md) |

---

## 3. Key takeaways

**Capstone kickoff: the flow**
- Day 12 = planning only. It is Day 02 (ticket analysis) + Day 05 (ticket pack) + Day 06 (test matrix) at real scale
- Same chain as the AI-native SDLC playbook: `intent.md` → `spec.md` → tickets → test matrix → `plan.md`; each step is a commit, each commit has a human gate
- The ticket pack is the direct input of Day 13. If a dev needs a meeting to understand it, the zero-question test failed

| Role | Output | Gate |
|---|---|---|
| Lead ("client") | `intent.md` from a deliberately vague brief; answers to open questions | Product owner accepts the intent |
| BA | Spec with flagged concerns, ticket pack | Every concern answered by the client |
| QA | Test matrix, at least one row per AC | No AC without a row |
| Dev | `plan.md` for ticket 14; questions as ticket comments | A stranger could build from the plan |

**What the BA step found (read the code before asking)**
- Brief: "who needs to come back, like a dashboard, ASAP". `GET /visits/follow-ups` already existed but matches one exact date, so a missed follow-up vanishes the next day
- 6 gaps (overdue, upcoming, "done" rule, duplicates per visit, thin rows, no real dashboard) → 14 questions for the client
- Client answers went into the spec and tickets: today + overdue, cut off at 30 days, one row per patient, most overdue first, no "contacted" button
- Left 2 answers undecided on purpose → written as `[ASSUMPTION]`, not guessed silently
- Split into 3 small tickets (BE endpoint, FE list, FE states), one PR each

**What the QA step found (tickets only, no code)**
- 63 rows, every AC covered, plus timezone, archived, empty, deleted-then-restored, 30/31-day boundary
- 9 ambiguities in the tickets. Most useful: name ordering with Vietnamese accents ("Ánh" sorts after "Bình" with a plain comparison)
- Resolved by the client: plain text comparison, ties by `patient_id`; ticket 14 AC9 and issue #37 updated

**What the Dev step found (zero-question test)**
- Fresh agent read only ticket 14 + code, wrote a 14-step test-first plan, every AC mapped to a test
- It reported no questions, but it silently kept the default name collation that QA had flagged. Verdict: pass with one question that should have been asked
- Lesson: ticket quality is only measured by someone who did not write it

| Metric | Result |
|---|---|
| Questions from the dev | 0 (1 should have been asked) |
| Ambiguities found by QA | 9 |
| Spec changes after the plan | 1 (AC9 ordering), then tickets rewritten to the user-story format |

**Lessons**
- Client answers live in the ticket/spec, never in chat
- Feature docs stay free of training references (no "Day 15"); the brief's deadline became "within two weeks, list first, total last"
- Check the numbering before adding tickets: `ls docs/tickets` was cut by `head`, so the first pack collided with tickets 09-13 and was renumbered to 14-16
- A token that can create issues cannot necessarily edit them: needed Issues read and write
- Local `.git/info/exclude` only tracks some `docs/` folders; added `!/docs/intents/`
