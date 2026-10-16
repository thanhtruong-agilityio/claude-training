# Coding style

Follow the style already in the file you touch.

## Backend (`backend/app/`)
- Type-hint every function. Routes declare `response_model` and a `status_code` when not 200.
- Look-up helpers (`_get_patient`, `_get_visit`) raise `HTTPException` (404 missing, 409 archived); don't repeat that inline.
- Time comes from `clock.py` (`now()`, `today()`), never `datetime.now()` or `date.today()`.
- Deletes are soft (`deleted_at`); filter deleted rows in queries.
- Keep SQL/queries in `queries.py`, routing in `routers/`, schemas in `models.py`.

## Frontend (`frontend/src/`)
- TypeScript is `strict`: no `any`, no `@ts-ignore` to silence an error.
- Pages in `pages/`, reusable pieces in `components/`; API calls only through `api.ts`, shapes in `types.ts`.
- Keep `types.ts` in step with the backend models.
