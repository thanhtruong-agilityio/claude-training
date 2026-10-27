# 16 - [FE] Add empty, loading, error states to due follow-ups list

- Spec: [follow-up dashboard](../specs/2026-10-27-follow-up-dashboard-spec.md)
- Issue: https://github.com/thanhtruong-agilityio/claude-training/issues/39
- Blocked by: 15

## Story
As the doctor, I want the follow-up list to tell me when it is loading, empty or broken, so that I never mistake a missing list for "nobody to call".

## Context
The list from ticket 15 only covers the happy path. The old block hides itself when empty, which a doctor can read as "the screen is broken". This ticket makes every state explicit.

## Client answers that apply
- The client did not specify these states. The behavior and wording below are BA decisions, kept minimal.
- If time is short, this ticket is the first one to drop (Q13).

## Business rules
- BR1 Every failed request is treated the same: any HTTP error status or a network failure.
- BR2 While a request is pending (first load or retry), the loading text is shown and "Try again" is disabled or absent.
- BR3 A failed retry returns to the error state.
- BR4 Messages are fixed text: "Loading follow-ups...", "No patients to call", "Could not load follow-ups", "Try again".

## Exceptions
- The error message never contains patient data or any part of the response body.
- The rest of the page (search, add patient) keeps working in every state.

## Scope
In:
- Loading, empty and error states of the list from ticket 15, and the "Try again" button.

Out:
- Retry with backoff, offline mode, toasts, logging of response bodies.
- Any change to the backend.

## Acceptance Criteria
- [x] AC1a Given the request is pending, when the page opens, then "Loading follow-ups..." is shown, with no heading and no rows.
- [x] AC1b Given the request is pending, when it succeeds with items, then the loading text disappears and the list shows.
- [x] AC2a Given the response has `total` 0, when the page opens, then "No patients to call" is shown and the section stays visible.
- [x] AC2b Given the response has `total` 0, when the page opens, then no rows and no "patients to call" heading are shown.
- [x] AC3a Given the endpoint answers 500, when the page opens, then "Could not load follow-ups" and a "Try again" button are shown.
- [x] AC3b Given the endpoint answers 422, when the page opens, then "Could not load follow-ups" and a "Try again" button are shown.
- [x] AC3c Given the request fails with a network error, when the page opens, then "Could not load follow-ups" and a "Try again" button are shown.
- [x] AC4a Given the error state, when the doctor clicks "Try again" and the request succeeds with items, then the list shows and the error text is gone.
- [x] AC4b Given the error state, when the doctor clicks "Try again" and the response has `total` 0, then "No patients to call" is shown.
- [x] AC4c Given the error state, when the doctor clicks "Try again", then "Loading follow-ups..." is shown while the request is pending and a second click cannot send a second request.
- [x] AC4d Given the error state, when the doctor clicks "Try again" and the request fails again, then the error message and "Try again" are shown again.
- [x] AC5 Given the error state, when the doctor types in the search box or opens the "add patient" form, then both work.
- [x] AC6 Given the endpoint answers 500 with a body containing a patient name, when the page opens, then the message is only "Could not load follow-ups" and the name is not on the page.
- [x] AC7 Given the same 500 response as AC6, when the page opens, then nothing from the response body is written to the console or logs.

## Open questions
| # | Question | Owner | Working default until answered |
|---|---|---|---|
| OQ1 | Is the wording of the four messages acceptable? | Client | The text in BR4 |

## Technical Notes
- Files: the component from ticket 15 and its test file in `frontend/src/__tests__/`. No `any`. Fake data only.
- Do not log request or response bodies (they can contain patient data).

## Dependencies
- Blocked by: 15.
- Blocks: none.

## Estimate
S
