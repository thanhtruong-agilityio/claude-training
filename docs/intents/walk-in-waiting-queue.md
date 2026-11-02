# Intent: Walk-in waiting queue (check-in, queue number, call display)
Author: ThanhTruong (role TBD).

## Problem
Patients waiting to see a doctor are tracked on paper at the front desk. Reception and doctors have no shared, current view of who has arrived and who is next. How long patients wait today and where the paper process breaks down: TBD.

## Proposed outcome
- Reception can check a patient in at the front desk when they arrive.
- Each checked-in patient gets a queue number.
- A display shows which patient is being called.
- Doctors can see the waiting queue and who is next.

## Affected users and systems
- Reception (check-in), doctors (see and call the next patient).
- Patients waiting in the clinic (queue number, call display).
- Display screen or device in the waiting area: TBD.

## Constraints
TBD

## Open questions
- How does the clinic handle walk-ins versus booked appointments, and urgent cases, in the queue order?
- Does the call display show the patient's name, the queue number, or both? Is there a privacy limit on what may be shown publicly?
- What screen or device is available in the waiting area?
- Who calls the next patient: the doctor, reception, or both?
- What happens to a patient who is called but does not respond, or who leaves?
- Is the queue per doctor or one queue for the clinic?
