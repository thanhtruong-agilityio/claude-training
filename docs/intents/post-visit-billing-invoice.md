# Intent: Post-visit payment and invoice
Author: ThanhTruong (role TBD).

## Problem
After a visit, doctors and reception staff cannot show an invoice for it. Today's billing process (how fees are collected and recorded, who asked for this): TBD.

## Proposed outcome
After a visit, a doctor or reception staff member can:
- see the payment and invoice for that visit, itemized into the consultation fee and the medicine,
- export the invoice as a PDF.

## Affected users and systems
Doctors and reception staff (primary). Patients (receive the invoice): TBD. clinic-app (backend and frontend).

## Constraints
TBD. Fake data only (as in the other intents).

## Open questions
- What problem or pain point triggers this, and who asked for it?
- Is a payment recorded (paid/unpaid, method, amount), or is only the invoice shown?
- Which payment methods are needed (cash, card, transfer)?
- Where do the consultation fee and medicine prices come from (fixed price list, entered per visit)?
- Are tax, discounts or insurance needed?
- What must the PDF contain (clinic details, invoice number, language)?
- Can an invoice be edited, voided or re-issued after it is created?
- Do patients get a copy (download, email), or is it internal only?
- Deadline or priority: TBD.
