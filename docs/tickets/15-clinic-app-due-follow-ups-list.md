# 15 - [FE] Show due follow-ups list on patient list page

- Spec: [follow-up dashboard](../specs/2026-10-27-follow-up-dashboard-spec.md)
- Issue: https://github.com/thanhtruong-agilityio/claude-training/issues/38
- Blocked by: 14
- Blocks: 16

## Story
As the doctor, I want to see on the home page who needs to come back and how many, so that I can call them without searching.

## Context
The patient list is the home page, so the list goes there. It reads the endpoint from ticket 14 and replaces the current "Follow-ups today" block.

## Client answers that apply
- A simple list plus one total at the top, for example "5 patients to call". No calendar or chart (Q4).
- Fields: name, phone, follow-up date, days overdue. No diagnosis (Q5).
- Clicking a name opens the patient record, nothing more (Q9).
- Patients without a phone show an empty phone cell (Q12).
- No "contacted/done" button in this version (Q8).
- If time is short, the list comes first and the total comes last (Q13).

## Business rules
- BR1 Rows appear in the order the endpoint returns. The page does not sort.
- BR2 The heading shows the `total` field of the response.
- BR3 The follow-up date is shown as `YYYY-MM-DD`.
- BR4 `days_overdue` 0 is shown as `Today`; 1 as `1 day overdue`; n > 1 as `n days overdue`.
- BR5 The heading is `1 patient to call` when the total is 1, otherwise `N patients to call`.

## Exceptions
- Total 0: the heading is not shown (the empty message belongs to ticket 16).
- Phone null: empty cell, never the text "null".

## Scope
In:
- Replace the `FollowUps` block on `PatientListPage` with the new list.
- One row per item: name (link), phone, follow-up date, days overdue.
- Add `getDueFollowUps(asOf?)` to `api.ts` and the matching types to `types.ts`.

Out:
- Loading, empty and error states (ticket 16).
- Actions on a row (mark contacted, new visit), filters, upcoming follow-ups, export.
- Removing the old `listFollowUps` API function or the old endpoint.

## Acceptance Criteria
- [ ] AC1 Given the endpoint returns 3 items, when the patient list page opens, then the heading reads "3 patients to call" and 3 rows are shown.
- [ ] AC2 Given the endpoint returns 1 item, when the page opens, then the heading reads "1 patient to call".
- [ ] AC3 Given an item with name, phone, `follow_up_date` 2026-10-20 and `days_overdue` 7, when the page opens, then the row shows the name, the phone, "2026-10-20" and "7 days overdue".
- [ ] AC4 Given an item with `days_overdue` 0, when the page opens, then the row shows "Today" and not "0 days overdue".
- [ ] AC5a Given an item with `days_overdue` 1, when the page opens, then the row shows "1 day overdue".
- [ ] AC5b Given an item with `days_overdue` 2, when the page opens, then the row shows "2 days overdue".
- [ ] AC6 Given an item with `phone` null, when the page opens, then the row has an empty phone cell and the text "null" does not appear.
- [ ] AC7 Given the list is shown, when the doctor clicks the name in a row, then the patient record for that row's `patient_id` opens.
- [ ] AC7b Given the list is shown, when the doctor clicks the phone or the date in a row, then nothing opens.
- [ ] AC8 Given the endpoint returns patients B, A, C in that order, when the page opens, then the rows show B, A, C.
- [ ] AC9 Given the list is shown, when the page opens, then the text "Follow-ups today" does not appear.
- [ ] AC10 Given the response has `total` 5, when the page opens, then the heading reads "5 patients to call".
- [ ] AC11 Given the list is shown, when the page opens, then the patient search box and the "add patient" form are still present.
- [ ] AC12 Given an item whose name has 80 characters, when the page opens, then the name wraps inside its row and the page does not scroll horizontally.
- [ ] AC13 Given an item with `days_overdue` 30, when the page opens, then the row shows "30 days overdue".
- [ ] AC14 Given the response has `total` 0, when the page opens, then no "patients to call" heading is shown.

## Open questions
| # | Question | Owner | Working default until answered |
|---|---|---|---|
| OQ1 | Which date format does the doctor want to read in the list? | Client | `YYYY-MM-DD` (BR3) |

## Technical Notes
- Files: `frontend/src/pages/PatientListPage.tsx`, `frontend/src/components/FollowUps.tsx` (rework or replace), `frontend/src/api.ts`, `frontend/src/types.ts`.
- Reuse the existing `onOpen(patientId)` pattern from `FollowUps`.
- Update `frontend/src/__tests__/FollowUps.test.tsx` and `PatientListPage.test.tsx` to the new behavior. Tests first, fake data only. Run with `make test-frontend`.
- TypeScript strict: no `any`. Keep `types.ts` in step with the backend models from ticket 14.

## Dependencies
- Blocked by: 14.
- Blocks: 16.

## Estimate
M
