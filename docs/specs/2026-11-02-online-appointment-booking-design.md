# Online appointment booking for patients design

Date: 2026-11-02 · Status: draft for review
Ticket: 59 · Intent: docs/intents/online-appointment-booking.md (ThanhTruong, role TBD)

## Goal
Patients cannot book an appointment online. A patient chooses a doctor, picks one of that doctor's free time slots and books it, and the system never allows two appointments in the same slot for the same doctor.

## Scope
- In: doctors and their bookable slots, listing free slots, booking a slot, a double-booking guard. Extends `clinic-app/` (FastAPI + SQLModel + SQLite, React).
- Out (not now): login or accounts for patients, cancel and reschedule, email or SMS confirmations and reminders, payments, links to the walk-in queue, reception-side booking screens.

## Requirements
- R1. The patient can list the doctors available for booking.
- R2. The patient can list one doctor's free slots for a given date; booked slots are not returned.
- R3. The patient can book a free slot by sending the doctor, the slot and the patient's name and phone; the response returns the appointment. (Assumption: guest booking, since the intent does not say how patients identify themselves.)
- R4. A slot that is already booked cannot be booked again (409), including when two bookings for the same slot arrive at the same time; exactly one succeeds.
- R5. A slot in the past, or one that does not exist for that doctor, cannot be booked (404 or 422, see Errors).
- R6. Empty or whitespace-only name or phone is rejected (422); text fields are trimmed, like the rest of the app.
- R7. All timestamps and "now" come from `clock.py`, never `datetime.now()`. (Assumption: slots are stored as local clinic time, like `visited_at`; see concern 6.)
- R8. Appointments are never hard-deleted. (Assumption: keeps room for cancel and reschedule later.)
- R9. No new network exposure: the backend stays on 127.0.0.1 and tests use fake data only.

## Design
### Data model
**doctors**: `id`, `full_name` (required), `is_active` (default true).
**slots**: `id`, `doctor_id` (FK), `starts_at`, `ends_at`. Unique together on (`doctor_id`, `starts_at`). How slots are generated (working hours, slot length, days off) is undefined; see concern 3. Until then slots are seeded or inserted directly.
**appointments**: `id`, `slot_id` (FK, unique), `patient_name`, `patient_phone`, `created_at`.
- Double booking is blocked in the database: the unique `slot_id` on `appointments` rejects a second booking, and the router maps that error to 409.
- Whether a booking links to an existing `patients` row is undecided; see concern 2.
### Screens
1. **Choose doctor**: list of active doctors.
2. **Choose slot**: date picker and the doctor's free slots for that date.
3. **Confirm booking**: name and phone form, then a confirmation with the appointment details.
### API
| Method | Path | Purpose |
|---|---|---|
| GET | `/doctors` | doctors available for booking |
| GET | `/doctors/{id}/slots?date=` | free slots of a doctor on a date |
| POST | `/appointments` | book `{slot_id, patient_name, patient_phone}` |
### Errors
- Required field empty or whitespace -> 422.
- Unknown doctor or slot -> 404.
- Slot already booked -> 409.
- Slot start is in the past -> 422.
- Booking and its uniqueness check happen in one transaction: all or nothing.
### Layout
```
clinic-app/
  backend/app/{models.py, routers/{doctors,appointments}.py}
  backend/tests/test_appointments.py
  frontend/src/{pages/BookingPage.tsx, __tests__/}
```

## Testing
- Test-first, like `test_visits.py`: pytest with in-memory SQLite. Cover free-slot listing, successful booking, booked slot hidden and rejected (409), concurrent double booking (one wins), past slot, unknown doctor or slot, blank fields, clock patched.
- Frontend: vitest for the slot list and the booking form.
- Fake data only.

## Data safety
- Patient name and phone are personal data: do not log request bodies, and never commit `*.db`.
- The backend binds to 127.0.0.1 and has no login; "online" booking by patients from another device conflicts with this rule until concern 1 is settled.
- No real patient data in any AI tool or in tests.

## How each constraint in the intent is met
| Constraint | Met by |
| :---- | :---- |
| TBD (no deadline, hosting or privacy rules stated). | Not met yet. Carried forward as concern 7; R7 and R9 hold the repo-level rules meanwhile. |
| `2026-10-15-clinic-app-design.md` lists "appointment booking" as out of MVP, so this reverses that scope decision. | Scope above lists what is now in; the older design doc needs an update once this spec is accepted. Carried forward as concern 7. |
| Fake data only (as in the follow-up dashboard intent). | R9 and Testing: fake data only. |

## Open questions from the intent
- What problem or pain point triggers this, and who asked for it? Not answered. Carried forward as concern 7.
- Do patients have accounts or logins, or do they book as guests? Not answered. Carried forward as concern 1; R3 assumes guests.
- How are a doctor's free slots defined (working hours, slot length, days off)? Who maintains them? Not answered. Carried forward as concern 3.
- Can a patient cancel or reschedule? Until when? Not answered. Carried forward as concern 4; out of scope until decided.
- Is the same patient allowed two overlapping appointments with different doctors? Not answered. Carried forward as concern 5.
- Are confirmations or reminders needed (email/SMS were out of MVP)? Not answered. Carried forward as concern 4.
- Time zone handling for slots (see bug #9, visits booked on the wrong day). Not answered. Carried forward as concern 6; R7 uses `clock.py` meanwhile.
- Deadline or priority: TBD. Not answered. Carried forward as concern 7.

## Areas of concern
1. The clinic is single-user and local with no login, while the intent wants patients to book "online". Reaching the backend from a patient's device conflicts with the 127.0.0.1-only rule (R9), and guest versus account booking (R3) is undecided. Owner: thanhtruong-agilityio (technical).
2. Whether a booking links to an existing patient record or stays a free-text name and phone is undefined; it changes the data model and duplicates patients. Owner: thanhtruong-agilityio (product).
3. How slots are defined and who maintains them (working hours, slot length, days off) is undefined, so slot creation cannot be specified. The app also has one user and no doctors table today. Owner: thanhtruong-agilityio (product).
4. Cancel, reschedule and confirmations or reminders are undefined; they are out of scope here and change the appointment states and data model later. Owner: thanhtruong-agilityio (product).
5. Whether one patient may hold overlapping appointments with different doctors is undefined; with guest booking there is no patient identity to check it against. Owner: thanhtruong-agilityio (product).
6. Time zone handling for slots is undefined; bug #9 (visits booked on the wrong day) shows the risk. Owner: thanhtruong-agilityio (technical).
7. The intent has no baseline for the problem, no deadline, and reverses the "appointment booking is out of MVP" decision in the clinic app design. Owner: thanhtruong-agilityio (product).
