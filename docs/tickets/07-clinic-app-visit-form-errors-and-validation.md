# 07 - Clinic app: show API errors and validate the visit form

## Context
The visit form and the pages call the API without handling failures, and the form sends unchecked numbers.

## Actual
- A 409 (archived patient) or 422 throws inside the page; nothing is shown and the form stays open.
- Non-numeric text in Fee, Paid, Days, Weight or Temperature becomes `NaN`, is sent as `null`, and ends in an unexplained 422.
- A prescription row with a dosage but no drug name is dropped silently.

## Expected
- API errors show a short message near the action (save, delete, add patient, load).
- Invalid numbers are rejected in the form with a clear message before sending.
- A row with any field filled but no drug name shows an error instead of vanishing. Fully blank rows are still dropped.

## Scope
- FE only: `PatientRecordPage`, `PatientListPage`, `FollowUps`, `RevenuePage`, `VisitForm`, `api.ts`.

## Acceptance Criteria
- [ ] Failed save/delete/create shows a message and keeps the user's input
- [ ] Non-numeric fee/paid/days/weight/temperature blocks submit with a message
- [ ] Half-filled prescription row blocks submit with a message; blank row is still dropped
- [ ] Vitest tests for each case
