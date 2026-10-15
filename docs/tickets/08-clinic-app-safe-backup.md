# 08 - Clinic app: make `make backup` safe for a running database

## Context
All clinic records live in one SQLite file. `make backup` copies it with plain `cp` while the app may be writing.

## Actual
A copy taken during a write can be inconsistent or corrupt, and nothing checks the backup is readable.

## Expected
The backup is a consistent snapshot and is verified.

## Scope
- `clinic-app/Makefile`: use SQLite's online backup (`sqlite3 backend/clinic.db ".backup ..."`, or Python's `sqlite3` backup API inside the backend container if the CLI is missing on the host).
- Run `PRAGMA integrity_check` on the new file and fail the target if it is not `ok`.
- README: document restore steps.

## Acceptance Criteria
- [ ] `make backup` creates `backups/clinic-<timestamp>.db` while the app is running
- [ ] The target fails with a clear message if `backend/clinic.db` does not exist or the integrity check fails
- [ ] Restore steps are in the README and were tried once on fake data
- [ ] `backups/` and `*.db` stay untracked
