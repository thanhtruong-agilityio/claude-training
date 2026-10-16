# Coding style

Follow the style already in the file you touch.

## Backend (`backend/app/`)
- Type-hint function parameters; add return types on new helpers. Routes declare `response_model` (and `status_code` when not 200) where they return a body.
- Missing records raise `HTTPException(404, ...)`; archived patients raise 409 on writes. Reuse the helpers in the router you're editing (`_get_visit`, `_get_patient` in `routers/visits.py`) instead of repeating the check.
- Time comes from `clock.py` (`now()`, `today()`), never `datetime.now()` or `date.today()`.
- Deletes are soft (`deleted_at`); filter deleted rows in queries.
- Schemas in `models.py`, routing in `routers/`. `queries.py` holds shared read helpers (e.g. `load_visit_read`); most simple queries live in the router.

## Frontend (`frontend/src/`)
- TypeScript is `strict`: no `any`, no `@ts-ignore` to silence an error.
- Pages in `pages/`, reusable pieces in `components/`; API calls only through `api.ts`, shapes in `types.ts`.
- Keep `types.ts` in step with the backend models.
