# Plan: ticket 14, due follow-ups report endpoint

Status: draft for approval (Day 13). Branch `feat/37-due-follow-ups-endpoint`, issue #37. Revised against the rewritten ticket (AC1 to AC16).

Working order: QA translates the matrix rows `T14-*` into failing pytest tests first (one commit, red, test names carry the matrix id). Dev then makes them green. Two commits at least: `test:` then `feat:`.

Source: `docs/tickets/14-clinic-app-due-follow-ups-endpoint.md` plus clinic-app code only.
Run tests with `make test-backend` from `clinic-app/`.

## Files that change

| File | Change |
|---|---|
| `clinic-app/backend/app/models.py` | add `DueFollowUpItem` (patient_id, full_name, phone|None, follow_up_date, days_overdue) and `DueFollowUpsRead` (total, items) next to `FollowUpRead` |
| `clinic-app/backend/app/routers/reports.py` | add `GET /reports/follow-ups` with `as_of: date | None = Query(None)`, `response_model=DueFollowUpsRead`; import new models |
| `clinic-app/backend/tests/test_reports.py` | new tests, written first |

Untouched: `GET /visits/follow-ups`, `main.py` (reports router already included), frontend.

## Order of work (test first, one step per behavior)

Each step: write the failing test, see it fail, minimal code, green. Tests use `client`, `patient`, `make_visit`; freeze time with `time-machine`; fake data only; `as_of` passed explicitly unless noted. Extra patients are created via `POST /patients`.

1. Skeleton: no data returns 200 `{"total": 0, "items": []}` (AC11). Adds route and models.
2. Follow-up today is listed, `days_overdue` 0, item shape correct (AC1).
3. Follow-up 7 days ago, `days_overdue` 7 (AC2).
4. Window: 30 days listed, 31 excluded (AC3).
5. Future follow-up excluded (AC4).
6. Soft-deleted visit with follow-up ignored (AC6).
7. Archived patient excluded (AC7).
8. Null phone is listed with `phone` null (AC10).
9. Newer-visit rule: a non-deleted visit with `visited_at` date >= follow_up_date drops the candidate (same day counts, per the ticket assumption). The carrying visit does not count against itself (exclude by visit id). A soft-deleted newer visit does not drop it (AC5).
10. One item per patient, latest `follow_up_date` wins (AC8). Candidates are filtered first (steps 4 to 9), then deduped.
11. Order: `days_overdue` desc, then `full_name` asc by the SQLite default comparison, then `patient_id` asc (AC9a to AC9c). Test names `"Ánh", "Bình", "an"` expect `Bình, an, Ánh`. Do the sort in SQL (`ORDER BY`) or in Python with plain string comparison, not locale-aware sorting.
12. Invalid `as_of` returns 422 for `banana`, `2026-02-30`, `27-10-2026` and the empty value (AC12). Only `YYYY-MM-DD` is accepted (BR7); check that `as_of=` is rejected and not treated as missing.
13. No `as_of`: freeze time at a clinic-time instant whose UTC date differs from the clinic date (e.g. 2026-10-26T18:00Z is 2026-10-27 01:00 in Asia/Ho_Chi_Minh), check `days_overdue` and listing are computed from `clock.today()` (AC13a); also an explicit `as_of` wins over the clock (AC13b). Use `clock.today()`, never `datetime.now()`.
14. Response shape: `total` equals the item count and each item has exactly the five fields (AC14). Visit with no `follow_up_date` is ignored (AC16).
15. Final: `make test-backend` fully green, including the old `/visits/follow-ups` tests unchanged (AC15).

Implementation sketch: select candidate Visit + Patient (follow_up_date set, `follow_up_date` between `as_of-30d` and `as_of`, `deleted_at` null, patient not archived). Drop a candidate if a different non-deleted visit of the same patient has `visited_at >= datetime.combine(follow_up_date, time.min)`, using a NOT EXISTS subquery. Dedupe in Python by patient (max follow_up_date). Sort in Python or SQL.

## Risks

- Route clash: `/reports/follow-ups` vs `/visits/follow-ups`. None, different prefixes (ticket says the same).
- Datetime vs date: `visited_at` is a naive datetime, `follow_up_date` a date. Compare by combining the date at 00:00 (`visited_at >= midnight of follow_up_date` equals "date on or after"). A wrong bound breaks the same-day case (step 9).
- Self-exclusion: a visit whose own `visited_at` date is >= its `follow_up_date` (follow-up set in the past) must not drop itself. Exclude by visit id.
- Filtering order: dedupe must run after the newer-visit drop, else the patient could vanish when a later candidate is dropped but an earlier one is valid.
- Timezone: only `clock.today()` as the default; test must prove it (step 13).
- Name sort uses SQLite default collation (binary, case-sensitive), the same as the existing endpoint. Not changed.
- Window bound `as_of - 30 days` crosses month and year ends; covered by the 30 and 31 day test.

## Proof

| AC | Test(s) in `test_reports.py` |
|---|---|
| AC1 | step 2, today listed, days_overdue 0 |
| AC2 | step 3, 7 days overdue |
| AC3a, AC3b | step 4, day 30 listed and day 31 not |
| AC4 | step 5, future not listed |
| AC5a to AC5e | step 9, newer visit drops (after, same day); soft-deleted newer visit does not; carrying visit does not drop itself; visit the day before does not drop |
| AC6 | step 6, deleted visit ignored |
| AC7 | step 7, archived hidden |
| AC8 | step 10, two due visits give one item with later date |
| AC9a to AC9c | step 11, most overdue first, same days by name (plain comparison), same name by `patient_id` |
| AC10 | step 8, phone null |
| AC11 | step 1, empty response and 200 |
| AC12 | step 12, 422 for `banana`, `2026-02-30`, `27-10-2026`, empty |
| AC13a, AC13b | step 13, time frozen across the UTC/clinic date boundary; explicit `as_of` wins |
| AC14 | step 2, item has exactly the five fields; `total` equals item count |
| AC15 | step 14, existing `/visits/follow-ups` tests stay green |
| AC16 | step 2 setup, visit without `follow_up_date` ignored |

## Ticket questions (zero-question test)

None. Checked and answered by the ticket plus code:
- Same-day visit: the ticket's [ASSUMPTION] states it counts as returned.
- Self-exclusion, window bounds, dedupe, order, null phone, 422 and clock source: all stated in Rules and ACs.
- Test tools (`time-machine`, fixtures): in `.claude/rules/testing.md` and `conftest.py`.
- Defaults chosen without needing an answer: `patient_id` as the final sort tie-break; pre-existing name collation kept.
