# Plan: ticket 16, loading, empty and error states for the due follow-ups list

Status: draft for approval (Day 13). Branch `feat/39-due-follow-ups-states`, issue #39. Source: `docs/tickets/16-clinic-app-due-follow-ups-states.md` plus the frontend code on `main` after #43.
Run tests with `make test-frontend` from `clinic-app/`.

Working order: QA translates the matrix rows `T16-*` into failing vitest tests first (one commit, red, test names carry the matrix id). Dev then makes them green. Two commits at least: `test:` then `feat:`.

## Files that change

| File | Change |
|---|---|
| `clinic-app/frontend/src/components/FollowUps.tsx` | replace the single `data` state with a status (`loading`, `ready`, `error`) plus the data; one `load()` used on mount and by "Try again"; render the three states |
| `clinic-app/frontend/src/__tests__/FollowUps.test.tsx` | new tests for the states (written first); adjust T15-16 (see risks) |
| `clinic-app/frontend/src/__tests__/FollowUpsErrors.test.tsx` | new file: AC6 and AC7 with the real `api.ts` and a stubbed `fetch` (the other file mocks `api`) |
| `clinic-app/frontend/src/__tests__/PatientListPage.test.tsx` | AC5: error state while search and add-patient still work |

Untouched: `api.ts` (its `request()` already throws an `Error` that only carries the status), the backend, `PatientListPage.tsx`, `styles.css` unless a state needs a class.

## Behavior (from the ticket)

- `loading`: text "Loading follow-ups...", no heading, no rows, no button.
- `ready`, total 0: text "No patients to call", section visible, no heading, no rows.
- `ready`, total above 0: unchanged from #43.
- `error`: text "Could not load follow-ups" and a "Try again" button. Nothing from the error is shown or logged.
- "Try again": back to `loading`, same request, then `ready` or `error` again. A second click while pending cannot send a second request.

## Order of work (test first, one step per behavior)

Each step: failing test, see it fail, minimal code, green. Queries by text and role. Fake data only.

1. Loading: pending promise, "Loading follow-ups..." shown, no heading, no rows (AC1a, T16-01).
2. Loading ends on success with items (AC1b, T16-02).
3. Empty: total 0 shows "No patients to call", section stays (AC2a, T16-03) and no rows or heading (AC2b, T16-04).
4. Error, 500: reject with an `Error` whose message carries the status, message and "Try again" button shown (AC3a, T16-05).
5. Error, 422 and network failure: same output (AC3b, AC3c, T16-06, T16-07).
6. Retry succeeds with items (AC4a, T16-08) and with total 0 (AC4b, T16-09).
7. Retry in progress: after the click the loading text is shown and the button is gone; `getDueFollowUps` has been called exactly twice even after a second click attempt (AC4c, T16-10). Implementation: set `loading` synchronously, plus an in-flight ref guard.
8. Retry fails again: error message and button again (AC4d, T16-11).
9. Page test: with the request rejected, the search box and the add-patient form still work (AC5, T16-12), in `PatientListPage.test.tsx`.
10. Error text safety, in `FollowUpsErrors.test.tsx` with the real `api.ts`: stub `fetch` to answer 500 with a body containing a fake patient name. The page shows only "Could not load follow-ups", the name is not in the document (AC6, T16-13), and `console.log/error/warn` were not called with the body (AC7, T16-14).
11. Final: `make test-frontend` fully green, `tsc --noEmit` clean, strict TypeScript, no `any`.

## Risks

- **T15-16 breaks.** It asserts that `/to call/` is absent when total is 0, and "No patients to call" matches. Change it to look for the heading pattern (`/^\d+ patients? to call$/`), which keeps its meaning (no heading). This changes a test from #43 on purpose; say so in the PR.
- **`catch` must not log.** `.catch(() => setStatus("error"))` ignores the error object. No `console.*` in the component. The AC7 test spies on the console to keep it that way.
- **React batching and the double click.** A second click could arrive before the re-render removes the button. The in-flight ref guard covers it; the test in step 7 proves it.
- **Unmounted component.** A response arriving after unmount would set state on an unmounted component. React 18 no longer warns about it, so it is left out (YAGNI).
- **Other tests that render `PatientListPage`** now show "No patients to call" when the mocked total is 0. Check that none of them looks for a text that this one also matches.
- **Wording is a BA default** (ticket OQ1, unanswered by the client). Texts live in one place so a change is one line.
- **Browser check:** the real states can only be seen in a browser (stop the backend for the error state). Plan: one check with Chrome if it is connected again, otherwise say in the PR that it was not done.

## Proof

| AC | Test |
|---|---|
| AC1a, AC1b | steps 1, 2 |
| AC2a, AC2b | step 3 |
| AC3a, AC3b, AC3c | steps 4, 5 |
| AC4a, AC4b | step 6 |
| AC4c | step 7 |
| AC4d | step 8 |
| AC5 | step 9, in `PatientListPage.test.tsx` |
| AC6, AC7 | step 10, in `FollowUpsErrors.test.tsx` |

## Ticket questions (zero-question test)

None needed to start. Defaults used: the four message texts exactly as in the ticket (BR4); the error branch treats every rejection the same (BR1).
