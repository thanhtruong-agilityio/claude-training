# Day 06 Claude Code Desktop core

- **Date:** 2026-10-19
- **Trainee:** thanh.truong
- **Branch:** `training/day-06`
- **Track:** Developer

**Status:** Plan written, nothing run yet. Exercises use clinic-app tickets 08 and 10.

**Plan:** `docs/plans/2026-10-19-day-06-practice.md`

---

## 1. Setup check

- [x] Plan: Pro (Remote Control needs a subscription login, not an API key)
- [x] Setup PR merged (#22)
- [ ] Repo has at least one commit for worktrees
- [ ] Claude phone app / claude.ai/code reachable from phone

---

## 2. Exercises

- [ ] Two parallel worktree sessions (tickets 08, 10), watched in agent view
- [ ] Plan-mode change on ticket 08 steered with diff comments
- [ ] `/loop` on the ticket 10 PR, plus `loop.md` for the repo
- [ ] Remote Control: one steer from the phone
- [ ] One artifact (PR walkthrough)
- [ ] `ultrathink` vs `/effort` levels on the same problem
- [ ] One cloud session on a long task
- [ ] Both PRs merged

### Developer Checkpoint 2

- [ ] Two parallel sessions, both merged
- [ ] One plan-mode change steered through diff comments
- [ ] One artifact
- [ ] One Remote Control steer
- [ ] One `/loop` run

---

## 3. Key takeaways

| | `/effort <level>` | `ultrathink` |
|---|---|---|
| Scope | Whole session, until changed | That one turn only |
| How | Sets the effort level sent to the API | Adds an in-context instruction; effort level sent to the API stays the same |
| Levels (Sonnet 5.5) | `low` `medium` `high` `xhigh` `max` | n/a (keyword anywhere in the prompt) |
| Default (Sonnet 5.5) | `medium` | n/a |
| Reset | `/effort auto` clears the saved level | Just leave the word out |

- Other phrases ("think hard") are not keywords; only `ultrathink` is.
- Docs: https://code.claude.com/docs/en/model-config (the page does not say which levels each plan gets)

---

## 4. Effort experiment

Question: _"Why does Uvicorn log query strings in access logs, and what are the ways to prevent this at different layers?"_

| Level | Time | Answer detail | Plan note |
|---|---|---|---|
| `low` | 11.6 s | 2,245 chars. 5 layers (design, uvicorn logging, app middleware, proxy, log pipeline). 1 short filter snippet. No caveats. | Ran on Pro. |
| `medium` | 21.5 s | 2,438 chars. 4 layers, middleware folded under uvicorn. 1 short filter snippet. Warns against rewriting `scope["query_string"]`. | Default on Sonnet 5.5. Ran on Pro. |
| `high` | 40.8 s | 3,272 chars. Table with 6 layers incl. CDN/WAF (CloudFront `cs-uri-query`, WAF `RedactedFields`, ALB cannot redact), APM (Sentry `before_send`, OTel). Full runnable `LOGGING_CONFIG` + filter. Caveats: `fmt` alone is not enough; Gunicorn worker case flagged as unchecked. | Ran on Pro. Session raised from `medium` after start. |
| `medium` + `ultrathink` | 16.3 s | 3,466 chars. 4 layers. Longest "why" section (Common Log Format, server cannot know what is sensitive, OWASP). No code. Notes: answered from memory, `record.args` may differ per uvicorn version. | Keyword only; session stayed `medium`. |

Timing: from my clock when the question was sent (10:07:42 UTC) to each session's last activity. About ±2 s. All four ran at the same time.

Plan notes:
- Pro ran `low`, `medium`, `high` with no error.
- `xhigh` / `max`: docs list them for Sonnet 5.5 but do not say if Pro gets them. **Not tested.**
- 5-hour window went 31% → 35% over the whole experiment. That includes this session's own turns, so it is not per-run cost.

---

## 5. Observations

- `high` took ~3.5x as long as `low` and gave the most usable answer: runnable config, cloud tiers, an explicit "not verified" flag.
- `low` and `medium` were close in content; `medium` added one warning and merged two layers.
- `ultrathink` on `medium` changed the shape more than the speed: more reasoning in prose (why it is logged), no code. It finished before plain `medium` (16.3 s vs 21.5 s), so one run each is noise-level on time.
- Length is not quality: `ultrathink` was longest but had no code; `high` was shorter and more actionable.
- Caveats:
  - n = 1 per level; no repeats.
  - Each session got a throw-away first turn ("ready") so effort could be set before the question. `high` was raised after that turn.
  - Sessions ran in the repo checkout; no tool calls showed in the transcripts.
  - Answers not fact-checked: uvicorn is not installed locally.
