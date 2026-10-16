---
paths:
  - "**/backend/tests/**"
  - "**/frontend/src/__tests__/**"
---

# Testing

- Every behavior change ships with a test that fails without it. Fix a bug by writing the failing test first.
- Run with `make test` (or `make test-backend` / `make test-frontend`) from `clinic-app/`. Never run `pytest` or `npm test` on the host. AI output is a proposal until the run is green.

## Backend (pytest)
- Use the `client` and `patient` fixtures and the `make_visit` helper from `conftest.py`; the DB is in-memory.
- Freeze time with `time-machine`; never depend on the real clock.
- Check status codes and validation (422), not just the happy path.

## Frontend (vitest + Testing Library)
- Query by label or text, as a user would; don't test implementation details.
- Fixtures use made-up names, never real patients.
