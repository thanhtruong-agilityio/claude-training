# 10 - Clinic app: keep patient data out of access logs

## Context
The spec says patient data must not be logged. Request bodies are not logged, but uvicorn's access log records the full URL, including `GET /patients?q=<name or phone>`.

## Actual
Searching for a patient writes their name or phone number to the container logs (`make logs`).

## Expected
Search terms and other patient data are not written to any log.

## Scope
- Move the search term out of the URL (for example `POST /patients/search` with a JSON body), or drop the query string from the access log.
- Keep `GET /patients` for the plain list.
- README: state which logs exist and what they contain.

## Notes
`/reports/revenue` and `/visits/follow-ups` only carry dates, which are fine.

## Acceptance Criteria
- [ ] A search for a fake name does not appear in `docker compose logs backend`
- [ ] Search by name and by phone still works in the UI
- [ ] Backend and frontend tests updated
