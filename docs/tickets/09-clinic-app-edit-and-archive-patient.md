# 09 - Clinic app: edit and archive a patient in the UI

## Context
`PATCH /patients/{id}` can edit a patient, archive and unarchive. The frontend has no screen for it, so a typo in a name or an old patient can only be fixed through the API.

## Scope
- FE: on the patient record page, an "Edit" form for all administrative fields (name, birth year, sex, phone, address, allergies, medical history) and an "Archive" / "Unarchive" button.
- FE: list page option to show archived patients (`include_archived`).
- BE: accept an empty `sex` (spec: "or empty") and store it as `null`. Today `sex: ""` returns 422.
- Out of scope: restoring deleted visits in the UI (separate ticket if wanted).

## Acceptance Criteria
- [ ] Edit saves trimmed values; blank name is rejected with a message
- [ ] Archive hides the patient from the list and follow-ups; unarchive brings them back
- [ ] "Show archived" toggle on the list page
- [ ] `sex: ""` is accepted and stored as `null`; invalid values still return 422
- [ ] Tests for BE and FE
