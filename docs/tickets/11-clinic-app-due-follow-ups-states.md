# 11 - [FE] Add empty, loading, error states to due follow-ups list

- Spec: [follow-up dashboard](../specs/2026-10-27-follow-up-dashboard-spec.md)
- Blocked by: 10

## Context
The list from ticket 10 only covers the happy path. The current block hides itself when empty, which a doctor can read as "the screen is broken". This ticket makes every state explicit.

## Client answers that apply
- The client did not specify these states. The wording below is a BA decision, kept minimal.
- If time is short, this ticket is the first one to drop (Q13).

## Scope
In:
- Loading: while the request is pending, show "Loading follow-ups..." and no total.
- Empty: when `total` is 0, show "No patients to call" and no rows.
- Error: when the request fails, show "Could not load follow-ups" and a "Try again" button that repeats the request. The rest of the page (search, add patient) keeps working.

Out:
- Retry with backoff, offline mode, toasts, logging of response bodies.
- Any change to the backend.

## Acceptance Criteria
- [ ] AC1 Given the request is pending, then "Loading follow-ups..." is shown, with no total and no rows.
- [ ] AC2 Given the response has `total` 0, then "No patients to call" is shown and the section is not hidden.
- [ ] AC3 Given the request fails, then "Could not load follow-ups" and a "Try again" button are shown.
- [ ] AC4 Given the error state, when the doctor clicks "Try again" and the request succeeds, then the list or the empty message is shown.
- [ ] AC5 Given the error state, then the patient search and "add patient" form still work.
- [ ] AC6 The error message does not include patient data or the raw response body.

## Technical Notes
- Files: the component from ticket 10 and its test file in `frontend/src/__tests__/`. No `any`. Fake data only.
- Do not log request or response bodies (they can contain patient data).

## Dependencies
- Blocked by: 10.
- Blocks: none.

## Assumptions
- [ASSUMPTION] The wording of the three messages is acceptable to the client.

## Estimate
S
