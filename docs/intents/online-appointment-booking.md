# Intent: Online appointment booking for patients
Author: ThanhTruong (role TBD).

## Problem
Patients have no way to book an appointment online. Why this is needed now (current process, pain point, who asked): TBD.

## Proposed outcome
A patient can book an appointment online by:
- choosing a doctor,
- choosing from that doctor's free time slots,
- without ever creating a double booking (no two appointments in the same slot for the same doctor).

## Affected users and systems
Patients (primary). Doctors (their availability and schedule). clinic-app (backend and frontend). Other users, such as reception staff: TBD.

## Constraints
TBD. Known context: `docs/specs/2026-10-15-clinic-app-design.md` lists "appointment booking" as out of MVP, so this reverses that scope decision. Fake data only (as in the follow-up dashboard intent).

## Open questions
- What problem or pain point triggers this, and who asked for it?
- Do patients have accounts or logins, or do they book as guests? (the design doc says single-user, no multi-user)
- How are a doctor's free slots defined (working hours, slot length, days off)? Who maintains them?
- Can a patient cancel or reschedule? Until when?
- Is the same patient allowed two overlapping appointments with different doctors?
- Are confirmations or reminders needed (email/SMS were out of MVP)?
- Time zone handling for slots (see bug #9, visits booked on the wrong day).
- Deadline or priority: TBD.
