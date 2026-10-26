# Day 11 exercises

## Browser test of clinic-app with Claude in Chrome

- **Task:** Drive the running clinic-app from a Claude Code session with Claude in Chrome (`claude --chrome`), run scenarios from the design spec, record pass/fail with evidence.
- **Target:** http://localhost:5173 (FE) and http://localhost:8000 (BE) via `make up`, localhost only.
- **Spec:** `docs/specs/2026-10-15-clinic-app-design.md`

### Steps

1. Branch `training/day-11`, Docker running.
2. `make backup` first (`backups/` is gitignored), then `make up`.
3. Confirm the DB only holds fake data before letting Claude read any page.
4. Connect Claude in Chrome; Claude opens its own tab and drives the UI (click, type, screenshot, console, network).
5. Cross-check with `docker compose logs backend` and `make test`.
6. Record results; restore the DB from the backup when done.

### Results

| # | Screen | Scenario | Expected | Result |
|---|---|---|---|---|
| 1 | Patient list | Add patient with name only | Created, shown in list | Pass |
| 2 | Patient list | Add patient with whitespace-only name | Rejected | Pass in UI (list unchanged, red field). No request reached the BE, so the 422 is not verified |
| 3 | Visit form | `paid` > `fee` (200000 / 300000) | Error, form keeps data | Pass in UI ("Paid cannot exceed fee"). No request reached the BE, so the 422 is not verified |
| 4 | Visit form | Save visit with 1 drug, fee 200000, paid 100000 | `POST` 201, visit in history | Pass (dated 2026-10-26, Owed 100000) |
| 5 | Revenue | Today's range | 1 visit, collected 100000, owed 100000 | Pass |
| 6 | Logs | Backend log after the run | No request bodies or patient data | Pass (request lines only) |
| 7 | Tests | `make test` | All green | Pass (backend 35, frontend 14) |
| 8 | Patient list | Search by name, then by phone | Matching rows only | Pass ("zzzz" gives none) |
| 9 | Visit form | Extra blank drug row, then save | Blank row dropped | Pass (1 drug saved) |
| 10 | Patient list | Visit with follow-up today | Patient shown in "Follow-ups today" on top | Pass |
| 11 | Patient record | Allergies and history set | Highlighted box | Pass (red box). Values were set through the API, the UI has no field for them |
| 12 | Patient record | Delete a visit in the UI | Visit leaves the history | Pass (no confirm dialog) |
| 13 | API (fetch from the page) | Whitespace name, birth year 1800 / 2999, bad sex, paid > fee, negative fee, `days` 0, blank drug name | 422 each | Pass, all 422 |
| 14 | API | Visit for unknown patient | 404 | Pass |
| 15 | API | Soft delete, read, restore | 200, then 404, then 200 with both drugs | Pass; deleted visit left the revenue totals |
| 16 | API | Archive a patient, then new visit / restore visit | 409 each | Pass |
| 17 | API | Archived patient in the list | Hidden by default, back with `include_archived=true` | Pass |
| 18 | Timezone | `date` and `clock.now()` in the backend container | `+07` | Pass (not tested live near midnight) |
| 19 | Console | Reload the app, read console with a filter | No errors | Pass (only Vite and React DevTools info lines) |
| 20 | Console | Page script logs `console.error` after a 404 fetch, read with `pattern` and `onlyErrors` | Tagged error is found | Pass |

Findings:

- UI checks for the whitespace name and `paid` > `fee` never reach the BE; the 422s were confirmed with direct API calls (row 13).
- The spec API table says `GET /patients?q=`. The code uses `POST /patients/search` so the term stays out of access logs (ticket 10). The table is out of date; `GET /patients?q=` ignores `q`.
- No archive button and no allergy or history field in the UI; archive, allergies and restore only work through the API.

Not run: restore a visit through the UI (no restore button), negative `fee` and `days` 0 through the form (only through the API), timezone near midnight.

### Takeaways

| Point | Note |
|---|---|
| Browser test != API test | UI validation hid the backend. Check the 422s with an API call or a pytest case |
| Check the log for the request | Network/log lines prove whether a request was sent at all |
| Data safety first | Backup before testing, fake data only, check the DB before the AI reads a page |
| Delete buttons | A `confirm()` dialog would block the extension, so skip or warn first |
| Console vs network | The console tool only shows JS-side messages; a 404 opened as a page URL shows up in the network tool, not the console. Start tracking before the action, filter with `pattern` |
| Tool set | Claude in Chrome tools only showed up in the session after the connection was made; Playwright MCP is a separate tool |

## Archive / unarchive UI (ticket 09, PR #35) and code review

- **Task:** Close the "no archive button in the UI" gap from the browser test, then run `/code-review` on the PR and act on it.
- **Branch / PR:** `feat/09-archive-restore-ui`, https://github.com/thanhtruong-agilityio/claude-training/pull/35

### Browser check (Claude in Chrome, fake patient)

| # | Screen | Scenario | Expected | Result |
|---|---|---|---|---|
| 21 | Patient record | Click Archive | Confirm step, no request yet | Pass |
| 22 | Patient record | Confirm archive | `PATCH` 200, "Archived" label, Unarchive button | Pass |
| 23 | Patient list | Back to list | Patient hidden | Pass |
| 24 | Patient list | Tick "Show archived" | `GET ?include_archived=true`, patient back with label | Pass |
| 25 | Patient record | Unarchive | `PATCH` 200, Archive button again | Pass |
| 26 | Console | After the run, errors only | No errors | Pass |

Not run: archived patient hidden from Follow-ups (backend filter, backend tests cover it). Layout: the "Show archived" checkbox sits off its label (global label CSS).

### /code-review on PR #35 (7 findings)

| # | Finding | Decision |
|---|---|---|
| 1 | No error handling in `setArchived`, confirm sticks, double click sends two PATCHes | Partly fixed: confirm closes on click. No error message, same as `save`/`remove` |
| 2 | "New visit" shown for an archived patient (backend 409) | Fixed: button hidden |
| 3 | Stale list response can overwrite a newer one | Not changed: pre-existing, separate ticket |
| 4 | `load()` not awaited, PATCH response discarded | Not changed: no wrong result |
| 5 | `updatePatient` accepts only `{ is_archived }` | Not changed: widen with the Edit form |
| 6 | Confirm state survives an `id` change | Not applicable: `App.tsx` unmounts between patients |
| 7 | `useState` placement, no debounce | Not changed: style only |

Fixes in `fd55187`, each with a test that failed first. Result: backend 35, frontend 23, `tsc` clean. Review table also posted on the PR.

### Takeaways

| Point | Note |
|---|---|
| Verify each finding | 2 of 7 were real, 1 partly, 1 could not happen. Check the code before fixing |
| Two-click confirm | `window.confirm` blocks the Chrome extension, so confirm on the page instead |
| Test first for review fixes | Both fixes got a failing test before the change |
| Run tests in Docker | I ran `vitest` on the host once, against the clinic-app rule; use `make test` |
