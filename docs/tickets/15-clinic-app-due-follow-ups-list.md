# 15 - [FE] Show due follow-ups list on patient list page

- Spec: [follow-up dashboard](../specs/2026-10-27-follow-up-dashboard-spec.md)
- Issue: https://github.com/thanhtruong-agilityio/claude-training/issues/38
- Blocked by: 14

## Context
The doctor wants to see who needs to come back without searching. The patient list is the home page, so the list goes there. It reads the endpoint from ticket 14 and replaces the current "Follow-ups today" block.

## Client answers that apply
- A simple list plus one total at the top, for example "5 patients to call". No calendar or chart (Q4).
- Fields: name, phone, follow-up date, days overdue. No diagnosis (Q5).
- Clicking a name opens the patient record, nothing more (Q9).
- Patients without a phone show an empty phone cell (Q12).
- No "contacted/done" button in this version (Q8).
- If time is short, the list comes first and the total comes last (Q13).

## Scope
In:
- Replace the `FollowUps` block on `PatientListPage` with the new list.
- Heading shows the total: `N patients to call` (`1 patient to call` when N is 1).
- One row per item with name (link), phone, follow-up date and days overdue. Show `Today` instead of `0 days overdue`.
- Order is the order the endpoint returns.
- Add `getDueFollowUps(asOf?)` to `api.ts` and the matching types to `types.ts`.

Out:
- Empty, loading and error states (ticket 16).
- Actions on a row (mark contacted, new visit), filters, upcoming follow-ups, export.
- Removing the old `listFollowUps` API function or the old endpoint.

## Acceptance Criteria
- [ ] AC1 Given the endpoint returns 3 items, when the patient list page opens, then the heading reads "3 patients to call" and 3 rows are shown.
- [ ] AC2 Given 1 item, then the heading reads "1 patient to call".
- [ ] AC3 Given an item with `days_overdue` 7, then the row shows the name, phone, follow-up date and "7 days overdue".
- [ ] AC4 Given an item with `days_overdue` 0, then the row shows "Today".
- [ ] AC5 Given an item with `days_overdue` 1, then the row shows "1 day overdue".
- [ ] AC6 Given an item with `phone` null, then the row is shown with an empty phone cell and no "null" text.
- [ ] AC7 Given a row, when the doctor clicks the name, then the patient record for that `patient_id` opens.
- [ ] AC8 Given the items, then the rows appear in the same order as the response.
- [ ] AC9 The old "Follow-ups today" heading no longer appears on the page.

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
