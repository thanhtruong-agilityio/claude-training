# Walk-in waiting queue (check-in, queue number, call display) design

Date: 2026-11-02 · Status: draft for review
Ticket: 58 · Intent: docs/intents/walk-in-waiting-queue.md (ThanhTruong, role TBD)

## Goal
Reception and the doctor have no shared, current view of who has arrived and who is next; patients are tracked on paper. Reception checks a patient in and gives a queue number, a display shows who is being called, and the doctor sees the waiting queue.

## Scope
- In: check-in, queue number, waiting list for the doctor, call-next, a call display page. Extends `clinic-app/` (FastAPI + SQLModel + SQLite, React).
- Out (not now): links to appointments (online booking is a separate intent), SMS or voice calls, wait-time statistics, per-doctor queues, queue history reports.

## Requirements
- R1. Reception can check in an existing, non-archived patient; the patient then appears in the waiting list.
- R2. Each check-in gets a queue number, shown to reception in the check-in response. (Assumption: numbers start at 1 and reset each clinic day.)
- R3. Queue numbers are unique within a clinic day, including when two check-ins arrive at the same time.
- R4. A patient who is already waiting or called cannot be checked in again (409). (Assumption: the intent is silent; a duplicate would break R2.)
- R5. An archived patient cannot be checked in (409). (Assumption: carries over the rule that archived patients are hidden.)
- R6. The doctor can list today's waiting entries ordered by check-in time, first one marked as next.
- R7. The doctor can call the next patient; the entry state changes from waiting to called and the call time is stored.
- R8. Calling when nobody is waiting returns 404 and changes nothing.
- R9. The call display shows the most recently called entry and updates without a manual reload.
- R10. The call display exposes no more than concern 2 allows; until then it shows the queue number only. (Assumption.)
- R11. All timestamps and the day boundary come from `clock.py`, never `datetime.now()`.
- R12. No new network exposure: the backend stays on 127.0.0.1 and tests use fake data only.

## Design
### Data model
**queue_entries**: `id`, `patient_id` (FK), `queue_date` (clinic date), `queue_number` (int, unique together with `queue_date`), `checked_in_at`, `state` (`waiting` or `called`), `called_at` (nullable).
- `queue_number` is `max(queue_number) + 1` for the date, computed in the same transaction as the insert; the unique constraint rejects a race.
- States after `called` (no-show, left, done) are not defined; see concern 5.
- Entries are never hard-deleted.
### Screens
1. **Check-in** (reception): search a patient by name or phone, same search as the patient list, then "Check in"; shows the queue number.
2. **Waiting queue** (doctor): today's waiting entries with patient name, queue number, check-in time; a "Call next" button.
3. **Call display**: a read-only page with the current called number, polling the backend.
### API
| Method | Path | Purpose |
|---|---|---|
| POST | `/queue/check-in` | check in `{patient_id}`, returns the entry with its queue number |
| GET | `/queue?date=` | entries of a day, waiting ones first by check-in time |
| POST | `/queue/call-next` | call the oldest waiting entry |
| GET | `/queue/display` | the last called entry (number only until concern 2 is settled) |
### Errors
- Unknown patient -> 404.
- Archived patient, or patient already waiting or called today -> 409.
- Call next with nobody waiting -> 404.
- Route order: `/queue/display` and `/queue/call-next` are declared before any `/queue/{id}` route, with a test.
### Layout
```
clinic-app/
  backend/app/{models.py, routers/queue.py}
  backend/tests/test_queue.py
  frontend/src/{pages/QueuePage.tsx, pages/CallDisplayPage.tsx, __tests__/}
```

## Testing
- Test-first, like `test_visits.py`: pytest with in-memory SQLite. Cover check-in, duplicate and archived rejection, number uniqueness and daily reset (clock patched), call-next order, empty queue, route order.
- Frontend: vitest for the check-in search and the call display refresh.
- Fake data only.

## Data safety
- The call display must not show patient names until concern 2 is settled.
- The backend binds to 127.0.0.1 and has no login; showing the display on a second screen needs a decision (concern 3).
- Do not log request bodies that contain patient data.

## How each constraint in the intent is met
| Constraint | Met by |
| :---- | :---- |
| None stated: the intent says "TBD". | Not met yet. Carried forward as concern 7; R11 and R12 hold the repo-level rules meanwhile. |

## Open questions from the intent
- How does the clinic handle walk-ins versus booked appointments, and urgent cases, in the queue order? Not answered. Carried forward as concern 1.
- Does the call display show the patient's name, the queue number, or both? Is there a privacy limit on what may be shown publicly? Not answered. Carried forward as concern 2.
- What screen or device is available in the waiting area? Not answered. Carried forward as concern 3.
- Who calls the next patient: the doctor, reception, or both? Not answered. Carried forward as concern 4.
- What happens to a patient who is called but does not respond, or who leaves? Not answered. Carried forward as concern 5.
- Is the queue per doctor or one queue for the clinic? Not answered. Carried forward as concern 6.

## Areas of concern
1. Queue order for walk-ins, booked patients and urgent cases is undefined; R6 "who is next" is only first-come-first-served until it is. Owner: thanhtruong-agilityio (product).
2. What the public call display may show is undefined; a patient name in a waiting room may be a privacy issue, and it blocks the final form of R9 and R10. Owner: thanhtruong-agilityio (product).
3. The waiting-area screen or device is unknown. A second device on the network conflicts with the 127.0.0.1-only rule (R12) because there is no login. Owner: thanhtruong-agilityio (technical).
4. Who may call the next patient is undefined, so permissions on `POST /queue/call-next` cannot be specified; the app has no roles today. Owner: thanhtruong-agilityio (product).
5. The no-show and left-the-clinic path is undefined, so the states after `called` cannot be specified. Owner: thanhtruong-agilityio (product).
6. One queue per clinic or per doctor is undefined; it changes the data model and the numbering in R2 and R3. Owner: thanhtruong-agilityio (product).
7. The intent lists no constraints (deadline, device, hosting, privacy rules) and its problem has no baseline (current wait time, where the paper process breaks). Owner: thanhtruong-agilityio (product).
