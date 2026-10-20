# Clinic app design

Date: 2026-10-15 · Status: draft for review

## Goal

A web app for a doctor running a private clinic at home. The doctor records patients, each visit, the prescription and the fee collected.

## Scope

- One user (the doctor). No login roles, no multi-user.
- Runs locally. FastAPI + React + SQLite, same stack and layout as `todo-app/`. New project in `clinic-app/`; `todo-app/` is untouched.
- In: patient records, visits, prescription items, visit fee, daily/monthly revenue summary.
- Out (not MVP): appointment booking, printing/PDF prescriptions, lab image upload, SMS reminders, drug catalog, stock, multi-user.

## Data model

**patients**: `id`, `full_name` (required), `birth_year`, `sex`, `phone`, `address`, `allergies`, `medical_history`, `is_archived` (default false), `created_at`.

**visits**: `id`, `patient_id` (FK), `visited_at`, `symptoms`, `diagnosis`, `notes`, `weight_kg`, `temperature_c`, `blood_pressure`, `fee`, `paid_amount`, `follow_up_date` (nullable), `deleted_at` (nullable; set = soft-deleted, cleared on restore).

**prescription_items**: `id`, `visit_id` (FK), `drug_name`, `dosage` (free text), `days`, `note`.

Rules:
- Money is an integer (VND). `fee` defaults to 0 and must be >= 0.
- Payment status is derived from `paid_amount` vs `fee`, not stored.
- Revenue is booked on the visit date (`visited_at`). A debt paid later is recorded by editing `paid_amount`, so past days' totals change. This is accepted for the MVP; separate payment records are out of scope.
- Text fields are trimmed; empty or whitespace-only `full_name` and `drug_name` are rejected. Blank prescription rows sent by the UI are dropped before saving.
- `days` > 0. `sex` is one of `male`, `female`, `other`, or empty. `birth_year` is between 1900 and the current year.
- Dates: `visited_at` is stored as local clinic time. `from`/`to` in reports are dates, both inclusive.
- Visits are soft-deleted (`deleted_at`). Prescription items are never deleted with it, so a restore brings the full visit back. No cascade delete.
- Patients are never hard-deleted; they are archived with `is_archived`, and unarchived with `PATCH /patients/{id}`. Archived patients are hidden from search and follow-ups by default.
- Lists, "last visit date" and revenue reports exclude soft-deleted visits.

## Screens

1. **Patient list** (home): search by name or phone, "add patient" form (only name required), today's follow-ups on top; each row shows name, birth year, phone, last visit date.
2. **Patient record**: administrative info, allergies and medical history highlighted, visit history newest first, "new visit" button.
3. **Visit form**: one page with symptoms/diagnosis/notes, vitals, prescription rows (add/remove), fee/paid/follow-up date. Saved in one request.
4. **Revenue summary**: pick a day or month; shows visit count, total collected, total owed.

## API

| Method | Path | Purpose |
|---|---|---|
| GET, POST | `/patients?q=`, `/patients` | search, create |
| GET, PATCH | `/patients/{id}` | record with visit history, edit, archive |
| POST | `/patients/{id}/visits` | create visit with prescription items in one request |
| GET, PUT | `/visits/{id}` | read, update (replaces all prescription items) |
| DELETE | `/visits/{id}` | soft delete |
| POST | `/visits/{id}/restore` | restore |
| GET | `/visits/follow-ups?date=` | patients due for follow-up |
| GET | `/reports/revenue?from=&to=` | visit count, collected, owed |

## Errors

- Required field empty/whitespace → 422.
- `paid_amount` negative or greater than `fee` → 422.
- Unknown patient/visit, or soft-deleted visit (except restore) → 404.
- New visit, edit or restore of a visit for an archived patient → 409.
- Restore of a visit that is not deleted → 409.
- Route order: `GET /visits/follow-ups` is declared before `/visits/{id}`, with a test, otherwise "follow-ups" is parsed as an id.
- Visit and its prescription items are saved in one transaction: all or nothing.

## Testing

Test-first, like `todo-app/backend/tests/test_todos.py`.
- Backend: pytest with in-memory SQLite, one test file per router. Focus: trim/empty rejection, all-or-nothing save, soft delete hidden from lists and reports, restore, revenue ignores deleted visits.
- Frontend: vitest for the visit form (add/remove prescription rows) and the search box.
- Test data is fake only.

## Data safety

- `*.db` is already in `.gitignore`; the clinic database must never be committed.
- No real patient data in any AI tool or in tests.
- Bind uvicorn to 127.0.0.1 only, publish no docker port to the LAN, strict CORS. There is no login, so anyone on the home network could otherwise read the records.
- Backup: a `make backup` target copies the database to a dated file. One SQLite file is the only copy of all records.
- Keep the `.db` file outside synced folders (iCloud, Dropbox) and rely on disk encryption (FileVault).
- Do not log request bodies that contain patient data.

## Layout

```
clinic-app/
  backend/app/{db.py, models.py, main.py, routers/{patients,visits,reports}.py}
  backend/tests/
  frontend/src/{api.ts, types.ts, components/, pages/}
  docker-compose.yml, Makefile, README.md
```
