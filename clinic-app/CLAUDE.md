# CLAUDE.md (clinic-app)

Local web app for a doctor's home clinic: patients, visits, prescriptions, fees, revenue. Design: `../docs/specs/2026-10-15-clinic-app-design.md`. Repo-wide rules are in `../CLAUDE.md`.

## Run and test (all via Docker, run from `clinic-app/`)

- `make up` — BE http://localhost:8000, FE http://localhost:5173
- `make test` — backend (pytest) + frontend (vitest); `make test-backend` / `make test-frontend` for one side
- `make backup` — copy `backend/clinic.db` to `backups/`
- Don't run `pytest` or `npm test` directly on the host.

## Layout

- `backend/app/`: `main.py`, `models.py`, `queries.py`, `clock.py`, `db.py`, `routers/` (patients, visits, reports). FastAPI + SQLModel + SQLite. Tests in `backend/tests/` (in-memory DB via `conftest.py`).
- `frontend/src/`: `pages/`, `components/`, `api.ts`, `types.ts`, `__tests__/`. React + Vite + TypeScript.

## Conventions

- "Now"/"today" come from `clock.py` (`Asia/Ho_Chi_Minh`), never `datetime.now()` directly.
- Revenue is booked on the visit date. Deleting a visit is a soft delete.
- Every behavior change ships with a test. AI output is a proposal until `make test` has passed.

## Never do

- Never commit `*.db` or `backups/`.
- Never use real patient data in tests, logs, or any AI tool.
- Never log request bodies that contain patient data.
- Never publish ports beyond 127.0.0.1 (there is no login).

## Skills (`.claude/skills/`)

`run-tests` · `data-safety` · `add-endpoint`

## Review agents (`.claude/agents/`, read-only)

`backend-reviewer` · `frontend-reviewer` · `data-safety-reviewer`
