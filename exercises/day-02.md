# Day 02 exercises

## Ticket analysis (workshop)

- **Task:** For each ticket, write a three-sentence analysis (what it asks, what is ambiguous, first step). Use Claude to find gaps and draft clarifying questions, cross-reference the codebase, then compare with the ticket's outcome.
- **Source:** https://github.com/thanhtruong-agilityio/claude-training/issues (#9, local ticket 10 = #14, #11, #12, and #13)

### Tickets

| # | Title | Reported by |
|---|---|---|
| [#9](https://github.com/thanhtruong-agilityio/claude-training/issues/9) | [clinic-app] Bug: visits booked on the wrong day (container runs UTC) | not stated |
| [#14](https://github.com/thanhtruong-agilityio/claude-training/issues/14) | [clinic-app] Keep patient data out of access logs (local file `docs/tickets/10-clinic-app-no-patient-data-in-logs.md`) | not stated |
| [#11](https://github.com/thanhtruong-agilityio/claude-training/issues/11) | [clinic-app] Show API errors and validate the visit form | not stated |
| [#12](https://github.com/thanhtruong-agilityio/claude-training/issues/12) | [clinic-app] Make make backup safe for a running database (local file `docs/tickets/08-clinic-app-safe-backup.md`) | not stated |
| [#13](https://github.com/thanhtruong-agilityio/claude-training/issues/13) | [clinic-app] Edit and archive a patient in the UI (local file `docs/tickets/09-clinic-app-edit-and-archive-patient.md`) | not stated |

Note: local ticket numbers in `docs/tickets/` and GitHub issue numbers are offset (local 05 = #9, local 08 = #12, local 09 = #13, local 10 = #14). Check the title before posting anything to an issue.

### Claude Code analysis (`/analyze-ticket`, with code cross-reference)

#### Analysis of issue #9: "Bug: visits booked on the wrong day (container runs UTC)"

Source: the analysis comment on https://github.com/thanhtruong-agilityio/claude-training/issues/9 (written before the fix; code references are to the pre-fix lines).

**Summary**

This ticket asks that every "now" and "today" value in `clinic-app` use clinic local time (`Asia/Ho_Chi_Minh`), because the backend container runs in UTC. A visit created between 00:00 and 07:00 local time is stored with the previous day's date, which skews daily revenue, today's follow-ups and the birth-year check.

It is ambiguous on whether setting the container `TZ` is the whole fix or a stopgap, how to freeze the clock in the test, and what the frontend should do when the browser is not in the clinic's timezone.

My first step is a failing test that runs with `TZ=UTC` and a clock frozen at 18:00 UTC (01:00 local), and checks that a new visit gets the local date.

**Core**

| Field | Content |
|---|---|
| What | Visits created at 00:00-07:00 clinic time get the previous day's `visited_at`. Daily revenue, today's follow-ups and "birth year cannot be in the future" are off in the same window. |
| For whom | The clinic (one doctor, Vietnam, UTC+7) and the revenue reports they read. |
| Done when | 1. A test fails before the fix: at 01:00 local, a new visit is booked on the local date.<br>2. Follow-ups "today" and the revenue default range use the local date.<br>3. `docker compose exec backend date` reports `Asia/Ho_Chi_Minh`.<br>4. README mentions the timezone setting. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Present | Local docker compose, backend container in UTC. |
| Steps to reproduce | Present | Run with `TZ=UTC`, freeze the clock at 18:00 UTC. |
| Expected vs actual | Present | Both stated. |
| Attachments (logs) | Missing | None. |
| Priority / deadline | Missing | None. |
| Related tickets | Partial | Ticket 06 (PUT resets the visit date) touches the same area. |

**Codebase** (under `clinic-app/`, pre-fix)

| Location | Relevance |
|---|---|
| `backend/app/models.py:30`, `:69` | `date.today().year` in the birth-year check. |
| `backend/app/models.py:38` | `created_at` uses `datetime.now`. |
| `backend/app/models.py:111` | `visited_at` default uses `datetime.now`. |
| `backend/app/routers/reports.py:17` | `date.today()` for the report day. |
| `backend/app/routers/visits.py:75` | `deleted_at = datetime.now()`. Not in the ticket, same problem. |
| `frontend/src/pages/RevenuePage.tsx:5` | "Today" from the browser's local time. |
| `backend/Dockerfile`, `docker-compose.yml` | No `TZ`, no `tzdata` (to check on `python:3.12-slim`). |

**Assumptions**

- Container `TZ=Asia/Ho_Chi_Minh` (plus `tzdata` if needed) satisfies the criteria; the clinic runs in one timezone.
- The test can freeze the clock and set `TZ=UTC`.
- Existing stored data is out of scope.
- `deleted_at` and `created_at` get the same fix as `visited_at`.

**Gaps (most blocking first)**

1. Container `TZ` or an explicit timezone in code? The ticket scopes only the container.
2. The frontend "today" comes from the browser, so it can disagree with the backend.
3. `deleted_at` and `created_at` are not mentioned.
4. Treatment of already-stored visits is not mentioned.

**Questions**

| # | Question | Ask |
|---|---|---|
| 1 | Rely on container `TZ` (as scoped), or use an explicit `ZoneInfo("Asia/Ho_Chi_Minh")` helper in the code? | Dev lead |
| 2 | Should `RevenuePage` use the clinic timezone explicitly, or is the browser's local time acceptable? | PO |
| 3 | Include `deleted_at` and `created_at` in the fix? | PO |
| 4 | Do existing visits need a data migration? | PO |
| 5 | Is adding a clock-freezing dev dependency acceptable? | Dev lead |

**What happened next (from the ticket comments)**

- Reproduction: `freezegun` could not reproduce it, because `models.py` holds `datetime.now` from import time, so a test passed for the wrong reason. `time-machine` made 2 tests fail for the right reason.
- A container-only `TZ` fix would not turn those tests green, so Q1 was answered with an explicit `ZoneInfo("Asia/Ho_Chi_Minh")` helper (`backend/app/clock.py`). Fixed in commit `179718d` (PR #16).
- QA verified it with 24 test cases: 23 PASS, TC-24 BLOCKED (no pre-fix visit in the test database). Suggested status: Verified.

---

#### Analysis of ticket 10 (GitHub #14): "Keep patient data out of access logs"

Source: `docs/tickets/10-clinic-app-no-patient-data-in-logs.md`, re-run on the GitHub issue (identical text). Also posted as a comment on https://github.com/thanhtruong-agilityio/claude-training/issues/14.

**Summary**

This ticket asks that a patient search term (name or phone) never reach any log. Today it is sent as `GET /patients?q=...`, so uvicorn's access log writes it out.

It is ambiguous on the fix (a `POST /patients/search` with a JSON body, or dropping the query string from the access log) and on what "any log" covers.

My first step is to reproduce the leak: run the stack, search for a fake name, and check `docker compose logs backend`.

**Core**

| Field | Content |
|---|---|
| What | Searching for a patient writes their name or phone to the container logs (`make logs`). |
| For whom | The clinic (patient privacy). The spec says patient data must not be logged. |
| Done when | 1. A search for a fake name does not appear in `docker compose logs backend`.<br>2. Search by name and by phone still works in the UI.<br>3. Backend and frontend tests updated. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Partial | Docker compose is implied. No version or commit. |
| Steps to reproduce | Partial | Search in the UI, then read `make logs`. No exact steps. |
| Expected vs actual | Present | Both stated. |
| Attachments (logs) | Missing | No sample log line. |
| Priority / deadline | Missing | None. |
| Related tickets | Missing | None linked. |

**Codebase** (under `clinic-app/`)

| Location | Relevance |
|---|---|
| `backend/app/routers/patients.py:29-37` | The `q` query param on `GET /patients` does the search. |
| `frontend/src/api.ts:18-19` | `listPatients` puts `q` in the URL. |
| `backend/Dockerfile:7` | uvicorn runs with default access logging and no custom logging config. |
| `Makefile:9-10` | `make logs` is `docker compose logs -f`. |
| `backend/tests/test_patients.py:28-35` | Existing search tests (name, phone). |
| `frontend/src/__tests__/PatientListPage.test.tsx:34` | Existing search test. |
| `README.md:21`, `docs/specs/2026-10-15-clinic-app-design.md:79` | The existing rule: do not log request bodies that contain patient data. |

**Assumptions**

- "Any log" means the backend container's output, including the uvicorn access log. Browser history and dev-tools network logs are out of scope.
- Both options in the ticket scope are acceptable, and the dev chooses.
- No reverse proxy or other service logs the URL.
- `/patients/{id}` carries only an id, which is not sensitive.

**Gaps (most blocking first)**

1. Which fix: move the term to a request body, or filter the access log.
2. Whether `GET /patients?q=` is removed or kept once the search moves.
3. Whether the README log inventory covers only the backend or also the frontend.
4. Only the first acceptance criterion can be checked by a command.
5. Other routes with patient data in the URL (e.g. visits filtered by patient) are not checked; the ticket only clears `/reports/revenue` and `/visits/follow-ups`.
6. Whether the fix must hold outside the `--reload` dev setup (`backend/Dockerfile:7`).

**Questions**

| # | Question | Ask |
|---|---|---|
| 1 | Do you prefer `POST /patients/search` with a JSON body or suppressing the query string in the access log? (I'd recommend the POST: it fixes the cause, while log filtering depends on config staying in place.) | PO / dev lead |
| 2 | Should `GET /patients?q=` be removed once the search moves, keeping `GET /patients` only for the plain list? | PO / dev lead |
| 3 | Should the README log inventory cover only the backend container, or also the frontend (vite proxy)? | PO |
| 4 | Fix search only, or also check other routes for patient data in URLs? | PO |
| 5 | Is the `--reload` dev setup the only deployment, or must the fix hold in production too? | Dev lead |

Status: questions not answered yet. I made no changes to the app.


---

#### Analysis of issue #11: "Show API errors and validate the visit form"

Source: https://github.com/thanhtruong-agilityio/claude-training/issues/11 (label: enhancement; the "Actual" section reads like a bug).

**Summary**

This ticket asks that the clinic-app frontend shows API errors near the action, rejects non-numeric Fee, Paid, Days, Weight and Temperature before sending, and flags a half-filled prescription row instead of dropping it silently.

It is ambiguous on the message wording and placement, whether a 422 should show the server's field-level detail, what counts as an invalid number (negative, zero, decimals), and where load errors appear on `FollowUps` and `RevenuePage`.

My first step is to get those answers, then size it. It is probably medium (six files plus a shared error pattern), so it goes through design before code.

**Core**

| Field | Content |
|---|---|
| What | A 409 (archived patient) or 422 throws inside the page and nothing is shown. `NaN` is sent as `null` and ends in an unexplained 422. A prescription row with a dosage but no drug name vanishes. |
| For whom | The clinic staff entering visits. |
| Done when | 1. Failed save/delete/create shows a message and keeps the input.<br>2. Non-numeric fee/paid/days/weight/temperature blocks submit with a message.<br>3. Half-filled prescription row blocks submit; a blank row is still dropped.<br>4. Vitest tests for each case. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Present | FE only, clinic-app. |
| Steps / expected vs actual | Present | Both stated. |
| Attachments (logs) | Missing | No screenshots or 409/422 response bodies. |
| Priority / deadline | Missing | None. |
| Related tickets | Missing | None linked. |

**Codebase** (under `clinic-app/frontend/src/`)

| Location | Relevance |
|---|---|
| `api.ts:10` | Throws `Error("Request failed: <status>")`; the response body (detail) is dropped. |
| `components/VisitForm.tsx:19`, `:48-49`, `:71` | `Number(...)` with no check, so `NaN` goes through. |
| `components/VisitForm.tsx:67` | Rows filtered by `drug_name.trim()` only: the silent drop. |
| `pages/*.tsx`, `components/FollowUps.tsx` | No `try`/`catch`: every failure is unhandled. |
| `__tests__/` | Tests exist for PatientListPage, RevenuePage, FollowUps, VisitForm. None for PatientRecordPage. |
| Backend | Not checked (status codes and error body shape unknown). |

**Assumptions**

- Errors are shown inline as text near the action; no toast library.
- `api.ts` exposes a readable message (response `detail` or a fallback).
- Fee/Paid/Weight/Temperature are non-negative decimals; Days is a positive integer.
- "Any field filled" means drug, dosage, days or note; Days defaults to "1", so an untouched row must still count as blank.
- Vitest and Testing Library are already set up.

**Gaps (most blocking first)**

1. Whether the 422 shows field-level detail or one generic text.
2. Numeric rules (0, negatives, ranges, decimals for Days).
3. Placement of load errors on the list, follow-up and revenue pages.
4. Bug or enhancement (decides whether to reproduce first).

**Questions**

| # | Question | Ask |
|---|---|---|
| 1 | Show the backend's field-level 422 detail, or one generic text? What does the error body look like? | Dev lead |
| 2 | May Fee and Paid be 0? Are negatives rejected? Ranges for Days, Weight, Temperature; decimals for Days? | PO |
| 3 | Load errors on `PatientListPage`, `FollowUps`, `RevenuePage`: inline in place of the list, or a banner? | PO |
| 4 | Highlight each invalid field, or one message above the submit button? | PO |
| 5 | Bug or enhancement? | PO |

Status: questions not answered yet. I made no changes to the app.

---

#### Analysis of issue #12: "Make make backup safe for a running database"

Source: https://github.com/thanhtruong-agilityio/claude-training/issues/12 (label: enhancement). Also posted as a comment on the issue.

**Summary**

This ticket asks that `make backup` takes a consistent snapshot of the SQLite database with SQLite's online backup, verifies the copy with `PRAGMA integrity_check`, and that the README documents restore steps.

It is ambiguous on whether the Python fallback must be built or a clear "sqlite3 not found" error is enough, what to do with a backup that fails the check, and what "tried once on fake data" counts as evidence.

My first step is to rewrite the `backup` target in `clinic-app/Makefile` and test it against a throwaway copy of the database with fake data.

**Core**

| Field | Content |
|---|---|
| What | `make backup` copies `backend/clinic.db` with plain `cp` while the app may be writing. The copy can be torn, and nothing checks it is readable. |
| For whom | The clinic (one doctor): all patient records live in this one file. |
| Done when | 1. `make backup` creates `backups/clinic-<timestamp>.db` while the app runs.<br>2. The target fails with a clear message if the db is missing or the integrity check fails.<br>3. Restore steps are in the README and were tried once on fake data.<br>4. `backups/` and `*.db` stay untracked. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Partial | Host vs container not stated; host has `/usr/bin/sqlite3`. |
| Steps / expected vs actual | Present | Context, Actual and Expected are stated. |
| Reproduction | Missing | No example of a torn copy. |
| Attachments (logs) | Missing | None. |
| Priority / deadline | Missing | None. |
| Related tickets | Missing | None linked. |

**Codebase** (under `clinic-app/`)

| Location | Relevance |
|---|---|
| `Makefile` (`backup` target) | `mkdir -p backups` then `cp backend/clinic.db backups/clinic-$$(date +%Y%m%d-%H%M%S).db`. No existence check, no verification. |
| `README.md:14-19` | Backup section describes the `cp`; no restore steps. |
| `backend/app/db.py` | `sqlite:///clinic.db`, no WAL pragma, so default rollback-journal mode. |
| `docker-compose.yml` | `./backend` is bind-mounted to `/app`, so the host path is the live file. |
| `.gitignore` | `*.db` is already ignored; `backups/` has no rule of its own. |

**Assumptions**

- It runs on the host and uses the host `sqlite3`; Python's backup API only if the CLI is missing.
- The filename keeps the `clinic-YYYYMMDD-HHMMSS.db` pattern.
- A backup that fails the check is deleted so it is not mistaken for a good one.
- Restore is manual: stop the app, copy the file over `backend/clinic.db`, start the app.
- `*.db` already keeps `backups/` contents untracked.

**Questions (most blocking first)**

| # | Question | Ask |
|---|---|---|
| 1 | Implement the Python fallback, or is a clear "sqlite3 not found" error enough? | PO / dev lead |
| 2 | On a failed integrity check, delete the bad file or keep it for inspection? | PO |
| 3 | Should the restore steps require stopping the app first? | Dev lead |
| 4 | Add an explicit `backups/` entry to `.gitignore`, or is `*.db` enough? | Dev lead |
| 5 | Is a restore on a copy of the db with fake data enough for "tried once"? Record the output in the PR? | PO |

Status: questions not answered yet. No changes made to the app.

---

#### Analysis of issue #13: "Edit and archive a patient in the UI"

Source: https://github.com/thanhtruong-agilityio/claude-training/issues/13 (label: enhancement; local file `docs/tickets/09-clinic-app-edit-and-archive-patient.md`). Also posted as a comment on the issue.

**Summary**

This ticket asks for an Edit form (all administrative fields) and an Archive/Unarchive button on the patient record page, a "Show archived" toggle on the list page, and a backend change so `sex: ""` is accepted and stored as `null`.

It is ambiguous on what "empty" means for the other optional fields, whether the form is inline or a modal, and how an archived patient's page should behave (the backend answers 409 for new visits).

My first step is the backend: a failing test for `sex: ""`, then the fix, before any frontend work.

**Core**

| Field | Content |
|---|---|
| What | A typo in a name or an old patient can only be fixed through `PATCH /patients/{id}`. The UI has no edit or archive screen. |
| For whom | The clinic staff (one doctor). |
| Done when | 1. Edit saves trimmed values; blank name rejected with a message.<br>2. Archive hides the patient from the list and follow-ups; unarchive brings them back.<br>3. "Show archived" toggle on the list page.<br>4. `sex: ""` accepted and stored as `null`; invalid values still 422.<br>5. Tests for BE and FE. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Present | clinic-app, FE + BE. |
| Steps / expected vs actual | Present | Context, scope and criteria stated. |
| UI design / mockup | Missing | None. |
| Message wording | Missing | Only "rejected with a message". |
| Priority / deadline | Missing | None. |
| Related tickets | Partial | #11 (API errors in the visit form) touches the same error pattern. |

**Codebase** (under `clinic-app/`)

| Location | Relevance |
|---|---|
| `backend/app/routers/patients.py:30-35` | `include_archived` already exists. |
| `backend/app/models.py:9`, `:44`, `:50` | `Sex = Literal["male","female","other"]`, so `""` returns 422. |
| `backend/app/models.py:61` | Validator for blank `full_name` on update (trimming not checked). |
| `backend/app/routers/reports.py:25`, `visits.py:20` | Follow-ups hide archived patients; visits for an archived patient return 409. |
| `backend/tests/test_patients.py:42-53` | Archive and unarchive already tested. |
| `frontend/src/pages/PatientRecordPage.tsx:42` | Display only: no edit or archive UI. |
| `frontend/src/api.ts` | No patient update function and no `include_archived` found (grep only; confirm). |
| `frontend/src/__tests__/` | Only `PatientListPage.test.tsx` covers patients; none for the record page. |

**Assumptions**

- "Empty" `sex` means `""` only; the blank option in the form sends `""` or `null`.
- Trimming applies to all text fields; a blank optional field is stored as `null`.
- Archive needs no confirmation dialog.
- The edit form sits on the record page, not a separate route.
- Vitest and Testing Library are the frontend test stack.

**Questions (most blocking first)**

| # | Question | Ask |
|---|---|---|
| 1 | Should a blank optional field (phone, address, allergies, history) be saved as `null` or as an empty string, like `sex`? | PO |
| 2 | Does an explicit `sex: null` in PATCH also clear the value, or only `""`? | Dev lead |
| 3 | Should Archive ask for confirmation, given that an archived patient cannot get new visits (409)? | PO |
| 4 | Is the edit form inline on the record page or a modal? | PO |
| 5 | Should an archived patient's record page stay viewable and editable, so "Show archived" lets the user open it and unarchive? | PO |

Status: questions not answered yet. No changes made to the app.

---

## Reporter role-play (`/reporter-roleplay`)

- **Task:** Write the questions you would ask the reporter, then role-play reporter/dev in pairs.
- **Skill:** `.claude/skills/reporter-roleplay/SKILL.md`. I am the dev, Claude is the reporter. Each answer is tagged `[ticket]`, `[reporter]`, `[unknown]` or `[decision]`.
- **Run on:** issue #9 (questions taken from the analysis comment, because the ticket has no Open questions section). Persona: non-technical clinic-side person, since "Reported by" is not stated. The ticket was already fixed (commit `179718d`), so this was practice.

### Role-play on #9

| # | Question (dev) | Reporter's answer | Tag |
|---|---|---|---|
| 1 | Container `TZ` or explicit `ZoneInfo` helper? | Code question, can't judge. I only care that a visit at 1am shows today's date. | `[unknown]` (dev lead) |
| 2 | Should `RevenuePage` use the clinic timezone, or is the browser's time acceptable? | Scope says the frontend "today" and backend must agree. Not sure anyone uses it outside the clinic. | `[ticket]` `[decision]` (PO) |
| 3 | Include `deleted_at` and `created_at`? | Yes, Expected says "all now and today values". | `[ticket]` |
| 4 | Do existing visits need a data migration? | Not in the ticket. Old 00:00-07:00 visits are on the wrong day, and changing them changes past revenue. | `[decision]` (PO / clinic owner) |
| 5 | Is a clock-freezing dev dependency acceptable? | Don't know what that is. Ask the dev lead. | `[unknown]` (dev lead) |

### Debrief

| Gap | Status |
|---|---|
| Q1 `TZ` vs `ZoneInfo` | open |
| Q2 `RevenuePage` and browser timezone | open |
| Q3 `deleted_at` / `created_at` | closed |
| Q4 Old visits | open |
| Q5 Test clock library | open |

**What I learned about my questions**
- Q3 was already answered by the ticket. Re-read the ticket before asking.
- Q1 and Q5 are technical, so they go to the dev lead, not the reporter.
- Q2 and Q4 need the PO. Rewrite them as business questions: "Do staff ever open Revenue from outside the clinic?" and "Should we correct the dates of old visits, knowing it changes past daily revenue?"
- `[reporter]` answers are plausible, not real. Confirm them with the actual reporter.

**Updated first step:** send Q2 and Q4 to the PO, and Q1 and Q5 to the dev lead.

### Role-play on #11

- **Run on:** issue #11 (questions taken from the analysis comment). Persona: non-technical product-side person, since "Reported by" is not stated.

| # | Question (dev) | Reporter's answer | Tag |
|---|---|---|---|
| 1 | Show the backend's field-level 422 detail, or one generic text? What does the error body look like? | Two questions in one, and the second is technical. Don't know the body shape. I only want staff to understand what went wrong. | `[unknown]` `[decision]` (API owner, PO + dev lead) |
| 2 | May Fee and Paid be 0? Negatives? Ranges for Days, Weight, Temperature; decimals for Days? | Fee 0 plausible (free follow-up), negative fee odd, decimal Days odd. Rest not thought about. | `[reporter]` `[decision]` `[unknown]` (PO, clinician for medical ranges) |
| 3 | Load errors on `PatientListPage`, `FollowUps`, `RevenuePage`: inline or banner? | Ticket says "a short message near the action". Inline is fine, just no blank page. | `[ticket]` `[reporter]` `[decision]` (PO) |
| 4 | Highlight each invalid field, or one message above submit? | Ticket only says "clear message". I want to see which field is wrong. | `[ticket]` `[reporter]` `[decision]` (PO / design) |
| 5 | Bug or enhancement? | Label says `enhancement`, but for staff a silent failed save feels like a bug. | `[ticket]` `[reporter]` `[decision]` (PO / dev lead) |

### Debrief (#11)

| Gap | Status | Answer or owner |
|---|---|---|
| 422 detail vs generic text | open | PO + dev lead; check a real response |
| Error body shape | open | API owner / logs (backend not checked) |
| Fee/Paid = 0, negatives | partly closed | Reporter guess: 0 ok, negatives odd. PO confirms |
| Days decimals | partly closed | Reporter guess: integer only. PO confirms |
| Paid > Fee, ranges for Days/Weight/Temp | open | PO (clinician for medical ranges) |
| Load error placement | partly closed | Near the action; inline vs banner, retry: PO |
| Field highlight vs one message | open | PO / design |
| Bug or enhancement | open | PO / dev lead |

**What I learned about my questions**
- Q3 and Q5 were single and specific, and Q3 pointed to a ticket line.
- Q1 bundled a PO question and a technical one: split it (error body to the dev lead, wording to the PO).
- Q2 bundled five questions: ask one field at a time with an example value.
- Q4: offer two concrete options to choose between.
- `[reporter]` answers are plausible, not real. Confirm them with the actual reporter.

**Updated first step:** run the API with an archived patient and an invalid payload and capture the real 409/422 bodies. Then send the PO one short message with the four open decisions (422 text, numeric rules, load-error layout, field highlighting). Size the ticket after that.

### Role-play on #12

- **Run on:** issue #12 (questions taken from the analysis comment, because the ticket has no Open questions section). Persona: non-technical clinic-side person, since "Reported by" is not stated.

| # | Question (dev) | Reporter's answer | Tag |
|---|---|---|---|
| 1 | Implement the Python fallback, or is a clear "sqlite3 not found" error enough? | Technical, can't judge. The ticket allows either. I only want a backup that works when I run it. | `[ticket]` `[unknown]` (dev lead) |
| 2 | On a failed integrity check, delete the bad file or keep it for inspection? | Ticket only says the target must fail with a clear message. I don't want a bad file sitting next to good ones where I might restore it by mistake. Whether to keep it for the dev is not my call. | `[ticket]` `[reporter]` `[decision]` (PO / dev lead) |
| 3 | Should the restore steps require stopping the app first? | Don't know what is safe. I need steps I can follow without breaking anything. | `[unknown]` (dev lead) |
| 4 | Add an explicit `backups/` entry to `.gitignore`, or is `*.db` enough? | The ticket only says both stay untracked. Git is not my area. | `[ticket]` `[unknown]` (dev lead; check with `git status` after a backup) |
| 5 | Is a restore on a copy of the db with fake data enough for "tried once"? Record the output in the PR? | Fine by me, I never want real patient data used for a test. How it is recorded is for the team. | `[ticket]` `[reporter]` `[decision]` (PO) |

### Debrief (#12)

| Gap | Status | Answer or owner |
|---|---|---|
| Python fallback vs "sqlite3 not found" error | open | Dev lead; ticket allows both |
| Failed backup: delete or keep | partly closed | Reporter wish: must not be mistaken for a good backup. Keep-for-inspection: PO / dev lead |
| Stop the app before restore | open | Dev lead |
| `backups/` rule in `.gitignore` | open | Dev lead; verify with `git status` |
| Evidence for "tried once" | partly closed | Reporter guess: fake data only. PO confirms the format (PR output) |

**What I learned about my questions**
- Q1, Q3 and Q4 are technical, so they go to the dev lead, not the reporter. Q4 can be answered by running `git status` after a backup, no question needed.
- Q2 mixed a reporter concern (don't restore a bad file by mistake) with a design choice: ask "should a failed backup stay on disk?" and offer two options.
- Q5 was short and specific; it got a usable answer.
- Q3 needs an observable form for the reporter: "Can the clinic restore while patients are being entered?"
- `[reporter]` answers are plausible, not real. Confirm them with the actual reporter.

**Updated first step:** ask the dev lead Q1 and Q3 in one short message, and check Q4 with `git status` after a test backup. Then rewrite the `backup` target and test it on a throwaway copy of the db with fake data. Q2 and Q5 go to the PO, whose answers don't block the first step.

### Role-play on #13

- **Run on:** issue #13 (questions taken from the analysis comment, because the ticket has no Open questions section). Persona: non-technical clinic-side person, since "Reported by" is not stated.

| # | Question (dev) | Reporter's answer | Tag |
|---|---|---|---|
| 1 | Blank optional field (phone, address, allergies, history): `null` or empty string, like `sex`? | Don't know the storage. Ticket only says `sex` becomes `null`. I want a blank phone to look blank. | `[unknown]` `[decision]` (dev lead, PO) |
| 2 | Does an explicit `sex: null` in PATCH also clear the value, or only `""`? | API question, can't answer. I only want to clear sex from the form. | `[unknown]` (dev lead) |
| 3 | Should Archive ask for confirmation? | A misclick is annoying, but Unarchive exists, so I'd skip the dialog. | `[reporter]` `[decision]` (PO) |
| 4 | Edit form inline or modal? | Ticket says "on the patient record page, an Edit form". No mockup, either is fine. | `[ticket]` `[decision]` (PO / design) |
| 5 | Archived patient's record page viewable and editable? | Viewable, yes: the ticket has a "Show archived" toggle and an Unarchive button. Editable while archived is not stated. | `[ticket]` `[decision]` (PO) |

### Debrief (#13)

| Gap | Status | Answer or owner |
|---|---|---|
| Blank optional fields: `null` vs `""` | open | Dev lead + PO; reporter wants them to look blank |
| `sex: null` in PATCH | open | Dev lead (API behavior) |
| Archive confirmation | partly closed | Reporter guess: no dialog (Unarchive undoes it). PO confirms |
| Inline form vs modal | open | PO / design |
| Archived record page viewable | closed | Yes, implied by the toggle and Unarchive button |
| Archived record page editable | open | PO |

**What I learned about my questions**
- Q4 and Q5 were single and specific, and both pointed at ticket lines.
- Q1 mixed storage (technical) with display (business): split it, and ask the PO "should a cleared phone show as blank?".
- Q2 is technical, so it never belonged with the reporter. Check `models.py` and ask the dev lead.
- Q3: offer two options ("confirm dialog or Unarchive only") to get a faster decision.
- Q5 bundled "viewable" and "editable": ask them separately.
- `[reporter]` answers are plausible, not real. Confirm them with the actual reporter.

**Updated first step:** the backend test for `sex: ""` is unaffected by the open gaps, so write that failing test today. Send the PO one message: archive confirmation, inline vs modal, and whether an archived record is editable. Send the dev lead the `null` vs `""` question for blank fields.

### Role-play on #14

- **Run on:** issue #14 (questions taken from the analysis comment, because the ticket has no Open questions section). Persona: non-technical clinic-side person, since "Reported by" is not stated.

| # | Question (dev) | Reporter's answer | Tag |
|---|---|---|---|
| 1 | `POST /patients/search` with a JSON body, or suppress the query string in the access log? | Technical, can't judge. The ticket allows either. I only want a patient's name or phone never to show up when I run `make logs`. | `[ticket]` `[unknown]` (dev lead) |
| 2 | Should `GET /patients?q=` be removed once the search moves, keeping `GET /patients` only for the plain list? | Ticket only says to keep `GET /patients` for the plain list. I don't care about the URL, but if the old way still works, someone may use it and the name leaks again. | `[ticket]` `[reporter]` `[decision]` (PO / dev lead) |
| 3 | Should the README log inventory cover only the backend container, or also the frontend (vite proxy)? | Ticket says "state which logs exist and what they contain" and Expected says "any log". I don't know which logs exist; I only see `make logs`. | `[ticket]` `[unknown]` (dev lead) |
| 4 | Fix search only, or also check other routes for patient data in URLs? | Ticket says "search terms and other patient data", and clears only `/reports/revenue` and `/visits/follow-ups`. If any other screen puts a name or phone in the address, it is the same problem. I can't list the routes. | `[ticket]` `[unknown]` (dev lead; check by grep and a test run) |
| 5 | Is the `--reload` dev setup the only deployment, or must the fix hold in production too? | Not in the ticket. I only know what I see with `make logs`. Whether there is another setup, I can't say. | `[unknown]` `[decision]` (dev lead / PO) |

### Debrief (#14)

| Gap | Status | Answer or owner |
|---|---|---|
| POST body vs access-log filter | open | Dev lead; ticket allows both |
| Remove `GET /patients?q=` | partly closed | Ticket keeps the plain list. Reporter wish: no way left to leak a name. PO / dev lead confirm |
| README log inventory scope | partly closed | Ticket: "which logs exist". Which logs exist: dev lead (check compose and vite output) |
| Other routes with patient data in URLs | partly closed | Ticket: no patient data anywhere. Route list: dev lead (grep `api.ts` and routers) |
| Must the fix hold outside `--reload` dev | open | Dev lead / PO |

**What I learned about my questions**
- Q1 bundled a choice and my own recommendation. Split it: the technical choice goes to the dev lead, and the reporter only confirms the outcome ("name never appears in `make logs`").
- Q2 and Q4 got a usable reporter wish because they pointed to a ticket line. Q4 can be mostly answered by grep, no question needed.
- Q3 and Q5 are technical or environment questions, so they go to the dev lead, not the reporter. Q5 for the reporter: "Does the clinic run this anywhere other than the docker compose setup?"
- `[reporter]` answers are plausible, not real. Confirm them with the actual reporter.

**Updated first step:** reproduce the leak today (run the stack, search a fake name, check `docker compose logs backend`) and grep the frontend and routers for other patient data in URLs. Then send the dev lead Q1, Q3 and Q5 in one short message, and Q2 to the PO.
