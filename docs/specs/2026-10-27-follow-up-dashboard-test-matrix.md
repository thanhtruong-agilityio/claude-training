# Test matrix: follow-up dashboard

- Source: tickets 14, 15, 16 (acceptance criteria, business rules, exceptions).
- Author: ThanhTruong (playing QA)
- Date: 2026-10-27
- Test data: fake patients only. "Today" is 2026-10-27, passed as `as_of` unless the row says otherwise.
- Types: H = happy path, E = edge, X = error.

## Ticket 14 - [BE] due follow-ups report endpoint

| ID | AC | Scenario | Input | Expected | Type |
|---|---|---|---|---|---|
| T14-01 | AC1 | Follow-up due today | Patient A, visit on 2026-10-20 with `follow_up_date` 2026-10-27 | A listed, `days_overdue` 0, `total` 1 | H |
| T14-02 | AC2 | Follow-up 7 days overdue | Patient A, `follow_up_date` 2026-10-20 | A listed, `days_overdue` 7 | H |
| T14-03 | AC3a | Boundary: exactly 30 days overdue | `follow_up_date` 2026-09-27 | Listed, `days_overdue` 30 | E |
| T14-04 | AC3b | Boundary: 31 days overdue | `follow_up_date` 2026-09-26 | Not listed | E |
| T14-05 | AC4 | Follow-up tomorrow | `follow_up_date` 2026-10-28 | Not listed | H |
| T14-06 | AC5a | Patient came back after the follow-up date | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-22 | Not listed | H |
| T14-07 | AC5c | Patient came back on the follow-up date itself | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-20 | Not listed (OQ1 working default) | E |
| T14-08 | AC5e | Visit the day before the follow-up date | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-19 | Listed | E |
| T14-09 | AC5b | Newer visit is soft-deleted | As T14-06, then visit 2 deleted | Listed | E |
| T14-10 | AC5b | Newer visit is restored after delete | As T14-09, then restore visit 2 | Not listed | E |
| T14-11 | AC5d | The visit carrying the date does not count against itself | One visit on 2026-10-20 with `follow_up_date` 2026-10-20 | Listed | E |
| T14-12 | AC6 | Soft-deleted visit with a follow-up date | Only visit deleted, `follow_up_date` 2026-10-20 | Not listed | H |
| T14-13 | AC7 | Archived patient | Patient archived, `follow_up_date` 2026-10-20 | Not listed | H |
| T14-14 | AC7 | Patient unarchived again | As T14-13, then unarchive | Listed | E |
| T14-15 | AC8 | Two due visits, one patient | Visit 1 (visited 2026-10-01, follow-up 2026-10-20), visit 2 (visited 2026-10-05, follow-up 2026-10-25) | One item, `follow_up_date` 2026-10-25, `days_overdue` 2 | H |
| T14-16 | AC14 | Two patients, one due visit each | A and B due | `total` 2, two items | H |
| T14-17 | AC9a | Order by days overdue | A overdue 3, B overdue 10, C due today | Order B, A, C | H |
| T14-18 | AC9b | Tie on days overdue, plain names | "Binh" and "An", both overdue 5 | Order An, Binh | H |
| T14-19 | AC9b | Tie with accents and case | "Ánh", "Bình", "an", overdue 5 | Order "Bình", "an", "Ánh" | E |
| T14-20 | AC9c | Same name, same overdue days | Two patients "An", ids 1 and 2, overdue 5 | id 1 then id 2 | E |
| T14-21 | AC10 | Patient without phone | Patient with no phone, due | Listed, `phone` null, not empty string | H |
| T14-22 | AC11 | No due patients, empty database | Empty database | 200, `{"total": 0, "items": []}` | H |
| T14-23 | AC11 | Patients exist but none due | Patients, none due | 200, `total` 0, empty `items` | H |
| T14-24 | AC12 | Invalid date | `as_of=banana` | 422 | X |
| T14-25 | AC12 | Impossible date | `as_of=2026-02-30` | 422 | X |
| T14-26 | AC12 | Wrong format | `as_of=27-10-2026` | 422 | X |
| T14-27 | AC12 | Empty value | `as_of=` | 422 | X |
| T14-28 | AC13a | Default uses clinic time, UTC date differs | No `as_of`; clock 2026-10-28 01:00 clinic time (2026-10-27 18:00 UTC); follow-up 2026-10-27 | Today is 2026-10-28; `days_overdue` 1 | E |
| T14-29 | AC13a | Default near midnight, same date in both zones | No `as_of`; clock 2026-10-27 23:30 clinic time (16:30 UTC); follow-up 2026-10-27 | Today is 2026-10-27; `days_overdue` 0 | E |
| T14-30 | AC13b | Explicit `as_of` overrides the clock | `as_of=2026-10-20` while clock says 2026-10-27 | Uses 2026-10-20 | H |
| T14-31 | AC15 | Old endpoint unchanged | `GET /visits/follow-ups?date=2026-10-27` | Same behavior as before this change | E |
| T14-32 | AC14 | Response shape | Any non-empty result | Item has exactly `patient_id`, `full_name`, `phone`, `follow_up_date`, `days_overdue`; `total` equals item count | H |
| T14-33 | AC16 | Visit without follow-up date | Visit with `follow_up_date` null | Ignored | H |
| T14-34 | AC12 | Compact date, added after review | `as_of=20261027` (the parser accepts it, the format rule must not) | 422 | X |
| T14-35 | AC12 | ISO week date, added after review | `as_of=2026-W44-2` (same) | 422 | X |

## Ticket 15 - [FE] due follow-ups list on patient list page

| ID | AC | Scenario | Input | Expected | Type |
|---|---|---|---|---|---|
| T15-01 | AC1 | Heading and rows, 3 items | API returns 3 items | Heading "3 patients to call", 3 rows | H |
| T15-02 | AC2 | Singular heading | API returns 1 item | Heading "1 patient to call" | H |
| T15-03 | AC3 | Row content | Item: name, phone, date 2026-10-20, `days_overdue` 7 | Row shows name, phone, "2026-10-20", "7 days overdue" | H |
| T15-04 | AC4 | Due today | `days_overdue` 0 | Row shows "Today", not "0 days overdue" | H |
| T15-05 | AC5a | One day overdue | `days_overdue` 1 | "1 day overdue" | E |
| T15-06 | AC5b | Two days overdue | `days_overdue` 2 | "2 days overdue" | E |
| T15-07 | AC6 | No phone | `phone` null | Empty phone cell; "null" and "undefined" never appear | H |
| T15-08 | AC7 | Open record | Click the name of the second row | Record page for that row's `patient_id` opens | H |
| T15-09 | AC7b | Phone and date are not links | Click the phone, then the date | Nothing opens | E |
| T15-10 | AC8 | Order kept | API returns B, A, C | Rows show B, A, C; no re-sorting | H |
| T15-11 | AC9 | Old block removed | Open the page with items | Text "Follow-ups today" absent | H |
| T15-12 | AC10 | Heading uses `total` | `total` 5 | Heading "5 patients to call" | E |
| T15-13 | AC11 | Rest of the page intact | Page opens with items | Search box and "add patient" form present | H |
| T15-14 | AC12 | Long name | 80-character name | Name wraps in its row; no horizontal scroll | E |
| T15-15 | AC13 | 30-day-old item | `days_overdue` 30 | "30 days overdue" | E |
| T15-16 | AC14 | Total 0 | `total` 0, `items` [] | No "patients to call" heading | E |

## Ticket 16 - [FE] empty, loading, error states

| ID | AC | Scenario | Input | Expected | Type |
|---|---|---|---|---|---|
| T16-01 | AC1a | Loading | Request pending | "Loading follow-ups..."; no heading, no rows | H |
| T16-02 | AC1b | Loading ends on success | Request resolves with items | Loading text gone, list shows | H |
| T16-03 | AC2a | Empty | `{"total": 0, "items": []}` | "No patients to call"; section still visible | H |
| T16-04 | AC2b | Empty has no rows or heading | Same as T16-03 | No rows, no "patients to call" heading | E |
| T16-05 | AC3a | Server error | API returns 500 | "Could not load follow-ups" and "Try again" | X |
| T16-06 | AC3b | Client error | API returns 422 | Same message and button | X |
| T16-06b | AC3b | Client error through the real `api.ts`, added after review | `fetch` answers 422 with a body containing a patient name | Same message and button; the name is not on the page | X |
| T16-07 | AC3c | Network failure | Request rejects | Same message and button | X |
| T16-08 | AC4a | Retry succeeds with items | Click "Try again"; API returns 2 items | List with 2 rows, error text gone | H |
| T16-09 | AC4b | Retry succeeds, empty | Click "Try again"; API returns `total` 0 | "No patients to call" | H |
| T16-10 | AC4c | Retry in progress | Click "Try again" and keep the request pending; click again | "Loading follow-ups..." shown; only one request sent | E |
| T16-11 | AC4d | Retry fails again | Click "Try again"; API fails again | Error message and "Try again" shown again | X |
| T16-12 | AC5 | Page works in error state | In error state, type in search box, open add-patient form | Both work | H |
| T16-13 | AC6 | No data in error text | API 500 with a body containing a patient name | Only "Could not load follow-ups"; the name is not on the page | X |
| T16-14 | AC7 | No data in logs | Same as T16-13 | Nothing from the response body in the console or logs | X |

## Rows added after review

Three rows were added after the `@claude` reviews of PRs #42 and #45, each closing a gap the review found: T14-34, T14-35 (the format check in BR7 was never reached by the old invalid values) and T16-06b (422 was only tested with a mocked `api`). The matrix went from 63 rows to 66: ticket 14 has 35, ticket 15 has 16, ticket 16 has 15.

Existing tests strengthened, no new row: T14-15 now fails if the earlier follow-up wins; T15-10 now fails if rows are sorted by days or date; T15-08 now checks the name is a link; T16-14 now asserts no console call at all.

## Coverage check

- Every acceptance criterion has at least one row (checked by script): ticket 14 AC1 to AC16 (with sub-ids), ticket 15 AC1 to AC14, ticket 16 AC1a to AC7.
- Risk areas covered: timezone (T14-28, T14-29), archived patients (T14-13, T14-14), empty results (T14-22, T14-23, T16-03), deleted data (T14-06, T14-09 to T14-12), boundary values (T14-03, T14-04, T15-15).

## Ambiguities found while writing the first version, and how they were resolved

| Q | Ticket | Problem | Resolution |
|---|---|---|---|
| Q1 | 14 | Same-day visit: "after" vs "on or after" | Kept as open question OQ1 (client); working default in AC5c |
| Q2 | 14 | "Two due visits" example did not say when both stay due | AC8 now has dates |
| Q3 | 14 | Name ordering with accents and case | Plain text comparison; BR5, AC9b, AC9c |
| Q4 | 14 | Empty or non-ISO `as_of` | BR7, AC12 |
| Q5 | 15 | Date format not specified | BR3 (`YYYY-MM-DD`); asked as OQ1 |
| Q6 | 15 | Heading source | BR2, AC10 |
| Q7 | 15, 16 | Heading when total is 0 | No heading: AC14 (15), AC2b (16) |
| Q8 | 16 | 4xx, 5xx and network failure | All the same: BR1, AC3a to AC3c |
| Q9 | 16 | Retry pending or failing | BR2, BR3, AC4c, AC4d |
