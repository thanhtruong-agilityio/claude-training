# Clinic app

Local web app for a doctor running a small private clinic at home: patients, visits, prescriptions, fees, revenue summary. Design: `docs/specs/2026-10-15-clinic-app-design.md`.

## Run

- `make up`, then open http://localhost:5173 (API on http://localhost:8000).
- `make test` runs backend (pytest) and frontend (vitest) tests in containers.

## Timezone

The clinic runs on `Asia/Ho_Chi_Minh`. The backend computes "now" and "today" in that zone (`backend/app/clock.py`), and `docker-compose.yml` sets `TZ=Asia/Ho_Chi_Minh` on the backend container. Check with `docker compose exec backend date`. Visits saved before this change keep their stored date.

## Backup

All records live in one SQLite file: `backend/clinic.db`.

- `make backup` copies it to `backups/clinic-<timestamp>.db`. Run it regularly and copy the result to a second disk.
- Keep this folder out of synced folders (iCloud, Dropbox) and turn on disk encryption (FileVault).

## Data safety

- There is no login. The app only listens on 127.0.0.1; never publish its ports to the network.
- `*.db` is gitignored. Never commit the database, and never use real patient data in tests or in any AI tool.
- Request bodies containing patient data must not be logged.

## Notes

- Revenue is booked on the visit date. Recording a later payment edits the visit's `paid_amount`, so earlier days' totals change.
- Deleting a visit hides it (soft delete); it can be restored via the API (`POST /visits/{id}/restore`).
