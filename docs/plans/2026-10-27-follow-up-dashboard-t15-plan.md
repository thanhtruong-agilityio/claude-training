# Plan: ticket 15, due follow-ups list on the patient list page

Status: draft for approval (Day 13). Branch `feat/38-due-follow-ups-list`, issue #38. Source: `docs/tickets/15-clinic-app-due-follow-ups-list.md` plus the frontend code.
Run tests with `make test-frontend` from `clinic-app/`.

Working order: QA translates the matrix rows `T15-*` into failing vitest tests first (one commit, red, test names carry the matrix id). Dev then makes them green. Two commits at least: `test:` then `feat:`.

Ticket 14 (the endpoint) is built in parallel in another worktree, so this ticket is developed against a mocked API (`vi.mock("../api")`), using the contract written in ticket 14. It is merged after ticket 14.

## Files that change

| File | Change |
|---|---|
| `clinic-app/frontend/src/types.ts` | add `DueFollowUp` (`patient_id`, `full_name`, `phone: string \| null`, `follow_up_date`, `days_overdue`) and `DueFollowUps` (`total`, `items`) next to `FollowUp` |
| `clinic-app/frontend/src/api.ts` | add `getDueFollowUps(asOf?: string)` calling `GET /api/reports/follow-ups` (`?as_of=` only when given) |
| `clinic-app/frontend/src/components/FollowUps.tsx` | rework in place: heading from `total`, table of rows, name link calling `onOpen(patient_id)`; renders nothing when `total` is 0 |
| `clinic-app/frontend/src/__tests__/FollowUps.test.tsx` | rewrite for the new behavior (written first) |
| `clinic-app/frontend/src/__tests__/PatientListPage.test.tsx` | mock `getDueFollowUps` instead of `listFollowUps` in `beforeEach` |

Untouched: `PatientListPage.tsx` (it already renders `<FollowUps onOpen={onOpen} />`), `listFollowUps` in `api.ts` (removal is out of scope), the backend, `styles.css` (reuse `.table-wrap`).

## Order of work (test first, one step per behavior)

Each step: failing test, see it fail, minimal code, green. Queries by text or label, fake names only.

1. Skeleton: API returns 3 items, heading "3 patients to call" and 3 rows (AC1, T15-01). Adds the type, the API function and the table.
2. Singular heading "1 patient to call" (AC2).
3. Row content: name, phone, "2026-10-20", "7 days overdue" (AC3).
4. Overdue labels via one small helper: 0 gives "Today", 1 gives "1 day overdue", 2 gives "2 days overdue", 30 gives "30 days overdue" (AC4, AC5a, AC5b, AC13).
5. Null phone gives an empty cell and no "null" text (AC6).
6. Click the name calls `onOpen` with that row's `patient_id`; clicking phone or date does not (AC7, AC7b).
7. Order is the response order, no sorting in the page (AC8).
8. Heading uses `total` (AC10) and is absent when `total` is 0 (AC14).
9. "Follow-ups today" text no longer appears (AC9); search box and add-patient form still present when rendering `PatientListPage` (AC11).
10. Long name (80 characters) renders in its row (AC12, see risk below).
11. Final: `make test-frontend` fully green, plus a type check (`strict`, no `any`).

## Risks

- **No loading or error handling here.** If the request fails, the promise rejection is unhandled and the block stays empty until ticket 16 lands. Accepted: ticket 16 is the owner. Do not merge 15 to production use without 16 if the endpoint can fail.
- **AC12 cannot be proved in jsdom.** There is no layout, so a vitest test can only check the name is rendered. Plan: put the name in a cell with `overflow-wrap: anywhere` (or reuse an existing class if one fits) inside `.table-wrap`, and check once by hand in the browser with an 80-character name. Record that check in the PR text.
- **Dependency on ticket 14.** The contract (`total`, `items`, five fields) is copied from ticket 14. If ticket 14 changes the shape, `types.ts` and the mocks change with it. Rebase on `main` after ticket 14 merges and run the app once against the real endpoint (`make up`) before opening the PR.
- **Two worktrees and Docker.** `make test-frontend` uses `docker compose run --rm --no-deps`, so it does not publish ports. Only one worktree runs `make up` at a time (ports 8000 and 5173).
- **Mock of the old API.** `PatientListPage.test.tsx` still mocks `listFollowUps`; with the component switched it must mock `getDueFollowUps`, otherwise the automock returns `undefined` and the component crashes on `total`.

## Proof

| AC | Test (in `FollowUps.test.tsx` unless noted) |
|---|---|
| AC1, AC2 | steps 1, 2 |
| AC3 | step 3 |
| AC4, AC5a, AC5b, AC13 | step 4 |
| AC6 | step 5 |
| AC7, AC7b | step 6 |
| AC8 | step 7 |
| AC9 | step 9 |
| AC10, AC14 | step 8 |
| AC11 | step 9, in `PatientListPage.test.tsx` |
| AC12 | step 10 plus the manual browser check |

## Ticket questions (zero-question test)

None needed to start. Defaults used: date shown as `YYYY-MM-DD` (ticket OQ1 working default); table layout with columns Name, Phone, Follow-up date, Overdue.
