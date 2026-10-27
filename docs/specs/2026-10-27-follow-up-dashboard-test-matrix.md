# Test matrix: follow-up dashboard

- Source: tickets 14, 15, 16 only (acceptance criteria and scope). No code or spec was used to write the expected results.
- Author: ThanhTruong (playing QA)
- Date: 2026-10-27
- Test data: fake patients only. "Today" below is a fixed date, 2026-10-27, passed as `as_of` unless the row says otherwise.
- Types: H = happy path, E = edge, X = error.

## Ticket 14 - [BE] due follow-ups report endpoint

| ID | AC | Scenario | Input | Expected | Type |
|---|---|---|---|---|---|
| T14-01 | AC1 | Follow-up due today | Patient A, visit on 2026-10-20 with `follow_up_date` 2026-10-27 | A listed, `days_overdue` 0, `total` 1 | H |
| T14-02 | AC2 | Follow-up 7 days overdue | Patient A, `follow_up_date` 2026-10-20 | A listed, `days_overdue` 7 | H |
| T14-03 | AC3 | Boundary: exactly 30 days overdue | `follow_up_date` 2026-09-27 | Listed, `days_overdue` 30 | E |
| T14-04 | AC3 | Boundary: 31 days overdue | `follow_up_date` 2026-09-26 | Not listed | E |
| T14-05 | AC4 | Follow-up tomorrow | `follow_up_date` 2026-10-28 | Not listed | H |
| T14-06 | AC5 | Patient came back after the follow-up date | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-22 | Not listed | H |
| T14-07 | AC5 | Patient came back on the follow-up date itself | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-20 | Not listed (see Q1) | E |
| T14-08 | AC5 | Visit the day before the follow-up date | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-19 | Listed (visit 2 is not on or after the date) | E |
| T14-09 | AC5 | Newer visit is soft-deleted | Visit 1 follow-up 2026-10-20; visit 2 on 2026-10-22, then deleted | Listed | E |
| T14-10 | AC5 | Newer visit is restored after delete | As T14-09, then restore visit 2 | Not listed | E |
| T14-11 | AC5 | The visit carrying the date does not count against itself | One visit on 2026-10-20 with `follow_up_date` 2026-10-20 | Listed | E |
| T14-12 | AC6 | Soft-deleted visit with a follow-up date | Only visit deleted, `follow_up_date` 2026-10-20 | Not listed | H |
| T14-13 | AC7 | Archived patient | Patient archived, `follow_up_date` 2026-10-20 | Not listed | H |
| T14-14 | AC7 | Patient unarchived again | As T14-13, then unarchive | Listed | E |
| T14-15 | AC8 | Two due visits, one patient | Visit 1 follow-up 2026-10-10, visit 2 follow-up 2026-10-20, visit 2 visited 2026-10-05 | One item, `follow_up_date` 2026-10-20 (see Q2) | H |
| T14-16 | AC8 | Two patients, one due visit each | A and B due | Two items | H |
| T14-17 | AC9 | Order by days overdue | A overdue 3, B overdue 10, C due today | Order B, A, C | H |
| T14-18 | AC9 | Tie on days overdue | "Binh" and "An", both overdue 5 | Order An, Binh | H |
| T14-19 | AC9 | Tie with accents and case | "Ánh", "Bình", "an" overdue 5 | Plain text comparison: "Bình", "an", "Ánh" (uppercase ASCII before lowercase before accented letters) | E |
| T14-33 | AC9 | Same name, same overdue days | Two patients named "An", ids 1 and 2, overdue 5 | Order by `patient_id`: 1 then 2 | E |
| T14-20 | AC10 | Patient without phone | Patient with no phone, due | Listed, `phone` null, not empty string | H |
| T14-21 | AC11 | No due patients | Empty database | 200, `{"total": 0, "items": []}` | H |
| T14-22 | AC11 | Only non-due data | Patients exist but none due | 200, `total` 0, empty `items` | H |
| T14-23 | AC12 | Invalid date | `as_of=banana` | 422 | X |
| T14-24 | AC12 | Impossible date | `as_of=2026-02-30` | 422 | X |
| T14-25 | AC12 | Wrong format | `as_of=27-10-2026` | 422 (see Q4) | X |
| T14-26 | AC12 | Empty value | `as_of=` | 422 or default to today (see Q4) | X |
| T14-27 | AC13 | Default uses clinic time | No `as_of`; clock set to 2026-10-27 23:30 clinic time (2026-10-27 16:30 UTC) | "Today" is 2026-10-27; follow-up 2026-10-27 has `days_overdue` 0 | E |
| T14-28 | AC13 | Default near midnight, UTC date differs | Clock 2026-10-28 01:00 clinic time (2026-10-27 18:00 UTC) | "Today" is 2026-10-28; follow-up 2026-10-27 has `days_overdue` 1 | E |
| T14-29 | AC13 | Explicit `as_of` overrides the clock | `as_of=2026-10-20` while clock says 2026-10-27 | Uses 2026-10-20 | H |
| T14-30 | Scope | Old endpoint unchanged | `GET /visits/follow-ups?date=2026-10-27` | Same behavior as before this change | E |
| T14-31 | Scope | Response shape | Any non-empty result | Item has exactly `patient_id`, `full_name`, `phone`, `follow_up_date`, `days_overdue`; `total` equals item count | H |
| T14-32 | Scope | Visit without follow-up date | Visit with `follow_up_date` null | Ignored | H |

## Ticket 15 - [FE] due follow-ups list on patient list page

| ID | AC | Scenario | Input | Expected | Type |
|---|---|---|---|---|---|
| T15-01 | AC1 | Heading and rows, 3 items | API returns 3 items | Heading "3 patients to call", 3 rows | H |
| T15-02 | AC2 | Singular heading | API returns 1 item | Heading "1 patient to call" | H |
| T15-03 | AC3 | Row content | Item: name, phone, date 2026-10-20, `days_overdue` 7 | Row shows name, phone, the date, "7 days overdue" (see Q5) | H |
| T15-04 | AC4 | Due today | `days_overdue` 0 | Row shows "Today", not "0 days overdue" | H |
| T15-05 | AC5 | One day overdue | `days_overdue` 1 | "1 day overdue" (singular) | E |
| T15-06 | AC5 | Two days overdue | `days_overdue` 2 | "2 days overdue" | E |
| T15-07 | AC6 | No phone | `phone` null | Empty phone cell; text "null" or "undefined" never appears | H |
| T15-08 | AC7 | Open record | Click the name of the second row | Record page for that row's `patient_id` opens | H |
| T15-09 | AC7 | Name is the only link | Click the phone or date | Nothing opens (the ticket says the name) | E |
| T15-10 | AC8 | Order kept | API returns B, A, C | Rows show B, A, C; no re-sorting | H |
| T15-11 | AC9 | Old block removed | Open the page with items | Text "Follow-ups today" absent | H |
| T15-12 | Scope | Heading matches `total`, not rows | `total` 5 | Heading uses `total` (see Q6) | E |
| T15-13 | Scope | Long name | 80-character name | Row stays readable, no overflow of the page | E |
| T15-14 | Scope | Rest of the page intact | Page opens | Search box and "add patient" form still present | H |
| T15-15 | Scope | 30-day-old item | `days_overdue` 30 | "30 days overdue" | E |

## Ticket 16 - [FE] empty, loading, error states

| ID | AC | Scenario | Input | Expected | Type |
|---|---|---|---|---|---|
| T16-01 | AC1 | Loading | Request pending | "Loading follow-ups..."; no total, no rows | H |
| T16-02 | AC1 | Loading ends on success | Request resolves with items | Loading text disappears, list shows | H |
| T16-03 | AC2 | Empty | `{"total": 0, "items": []}` | "No patients to call"; section still visible; no rows | H |
| T16-04 | AC2 | Empty heading | Same as T16-03 | No "0 patients to call" heading, or defined by ticket (see Q7) | E |
| T16-05 | AC3 | Server error | API returns 500 | "Could not load follow-ups" and a "Try again" button | X |
| T16-06 | AC3 | Network failure | Request rejects | Same message and button (see Q8) | X |
| T16-07 | AC3 | Client error | API returns 422 | Same message and button (see Q8) | X |
| T16-08 | AC4 | Retry succeeds with items | Click "Try again"; API now returns 2 items | List with 2 rows, error text gone | H |
| T16-09 | AC4 | Retry succeeds, empty | Click "Try again"; API returns `total` 0 | "No patients to call" | H |
| T16-10 | AC4 | Retry fails again | Click "Try again"; API fails again | Error stays visible (see Q9) | X |
| T16-11 | AC4 | Button pressed repeatedly | Click "Try again" 3 times fast | Not specified (see Q9) | E |
| T16-12 | AC5 | Page works in error state | In error state, type in search box, open add-patient form | Both work | H |
| T16-13 | AC6 | No data in error text | API 500 with a body containing a patient name | Message is only "Could not load follow-ups"; the body is not shown | X |
| T16-14 | AC6 | No data in logs | Same as T16-13 | Nothing from the response body is logged | X |

## Coverage check

- Every acceptance criterion has at least one row: ticket 14 AC1 to AC13, ticket 15 AC1 to AC9, ticket 16 AC1 to AC6.
- Risk areas covered: timezone (T14-27, T14-28), archived patients (T14-13, T14-14), empty results (T14-21, T14-22, T16-03), deleted data (T14-06, T14-09 to T14-12), boundary values (T14-03, T14-04, T15-15).

## Ambiguities found in the tickets

These are questions for the BA. The expected results above that depend on them are marked "see Q".

| Q | Ticket / AC | Problem | Why it matters |
|---|---|---|---|
| Q1 | 14 / AC5 | The client said "after the follow-up date" but the ticket says "on or after". A patient who comes back exactly on the date is dropped. The ticket marks this as an assumption, but the client has not confirmed. | T14-07 passes or fails depending on the answer. |
| Q2 | 14 / AC8 | "Two due visits" is not defined when the earlier visit's follow-up is already satisfied by the later visit. | T14-15: visit 2 happened after visit 1's date, so visit 1 is satisfied; the example only works because of that. Say it explicitly. |
| Q3 | 14 / AC9 | "Name ascending" did not say how to compare accents and upper or lower case. **Resolved:** plain text comparison, no folding; ties by `patient_id`. Ticket 14 AC9 now says so. | T14-19, T14-33. |
| Q4 | 14 / AC12 | "Not a valid date" does not cover the empty value (`as_of=`) or non-ISO formats. | T14-25 and T14-26 have no single expected result. |
| Q5 | 15 / AC3 | The format of the follow-up date is not specified (2026-10-20, 20/10/2026, ...). | The test cannot assert the text. |
| Q6 | 15 / Scope | The heading uses `total`, but nothing says what happens if `total` and the number of items differ. | Low risk; confirm the heading reads `total`. |
| Q7 | 15 AC2 and 16 AC2 | Ticket 15 builds the heading from the total; ticket 16 shows "No patients to call". Nothing says whether the heading is also shown when the total is 0. | T16-04 could show both "0 patients to call" and "No patients to call". |
| Q8 | 16 / AC3 | "The request fails" does not say whether a 4xx response, a 5xx response and a network failure behave the same. | T16-05 to T16-07. |
| Q9 | 16 / AC4 | Not defined: what the page shows while a retry is running, what happens when the retry fails, and whether the button is disabled during a request. | T16-10, T16-11. |
