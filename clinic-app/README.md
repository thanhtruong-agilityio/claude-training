# Clinic app

Local web app for a doctor running a small private clinic at home: patients, visits, prescriptions, fees, revenue summary. Design: `docs/specs/2026-10-15-clinic-app-design.md`.

## Run

- `make up`, then open http://localhost:5173 (API on http://localhost:8000).
- `make test` runs backend (pytest) and frontend (vitest) tests in containers.

## Timezone

The clinic runs on `Asia/Ho_Chi_Minh`. The backend computes "now" and "today" in that zone (`backend/app/clock.py`), and `docker-compose.yml` sets `TZ=Asia/Ho_Chi_Minh` on the backend container. Check with `docker compose exec backend date`. Visits saved before this change keep their stored date.

## Backup

All records live in one SQLite file: `backend/clinic.db`.

- `make backup` takes a consistent snapshot (SQLite online backup, safe while the app is running) into `backups/clinic-<timestamp>.db`, then runs `PRAGMA integrity_check` on it. It fails with a message if `backend/clinic.db` is missing or the check is not `ok`, and removes the bad file. Needs `sqlite3` on the host. Run it regularly and copy the result to a second disk.
- Keep this folder out of synced folders (iCloud, Dropbox) and turn on disk encryption (FileVault).

### Restore

1. `make down` (the app must not be writing).
2. Check the backup: `sqlite3 backups/clinic-<timestamp>.db "PRAGMA integrity_check;"` must print `ok`.
3. Keep the current file just in case: `mv backend/clinic.db backend/clinic.db.old` (delete it once you are happy).
4. `cp backups/clinic-<timestamp>.db backend/clinic.db`
5. `make up` and check the data in the app.

## Data safety

- There is no login. The app only listens on 127.0.0.1; never publish its ports to the network.
- `*.db` is gitignored. Never commit the database, and never use real patient data in tests or in any AI tool.
- Request bodies containing patient data must not be logged.

## Logs

Read them with `make logs` (`docker compose logs -f`).

| Log | Contains | Patient data |
|---|---|---|
| backend (uvicorn access) | client, method, path, status, e.g. `POST /patients/search 200` | none: search terms go in a POST body, never the URL; request bodies are not logged |
| backend (uvicorn startup/reload) | server start, reload and shutdown messages | none |
| frontend (Vite dev server) | startup lines only; proxied `/api` requests are not logged | none |

Search is `POST /patients/search` with a JSON body. `GET /patients` is the plain list and ignores a `q` query parameter, so never put a name or phone number in a URL: the access log would record it. `/reports/revenue` and `/visits/follow-ups` only carry dates.

## Notes

- Revenue is booked on the visit date. Recording a later payment edits the visit's `paid_amount`, so earlier days' totals change.
- Deleting a visit hides it (soft delete); it can be restored via the API (`POST /visits/{id}/restore`).
