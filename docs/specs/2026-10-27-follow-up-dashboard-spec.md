# Spec: follow-up dashboard for the doctor

- Source: [intent](../intents/2026-10-27-follow-up-dashboard.md)
- Author: ThanhTruong (playing the BA)
- Date: 2026-10-27
- Status: draft, waiting for client answers (section 5)

## 1. Intent in one line

The doctor wants one screen that shows which patients need to come back for a visit, as soon as possible.

## 2. What exists today (read from the code)

- `GET /visits/follow-ups?date=` ([reports.py](../../clinic-app/backend/app/routers/reports.py)) returns visits whose `follow_up_date` equals the given day. The day defaults to today in clinic time (`clock.today()`, `Asia/Ho_Chi_Minh`).
- It excludes soft-deleted visits and archived patients, and sorts by patient name.
- Each row has `visit_id`, `patient_id`, `full_name`, `phone`, `follow_up_date`.
- The patient list page shows a "Follow-ups today" list ([FollowUps.tsx](../../clinic-app/frontend/src/components/FollowUps.tsx)). It is hidden when empty and each name opens the patient record.
- The data model has no "contacted" or "done" status for a follow-up. A follow-up is only a date on a visit.

## 3. Requirements as understood

R1. The doctor can see, on one screen, the patients who need to come back.
R2. The screen is reachable without searching for a patient.
R3. Archived patients and soft-deleted visits never appear (existing rule, keep it).
R4. Data stays local, with no new ports and no real patient data in tests (repo security rules).

R1 is the only requirement the client stated. R2 to R4 are inferred and need confirmation. The rest of this spec depends on the answers in section 5.

## 4. Gaps between the brief and today's behavior

| # | Gap | Why it matters |
|---|---|---|
| G1 | The endpoint matches one exact date, so a missed follow-up (date in the past) disappears. | The doctor would not see patients who never came back. |
| G2 | No range: nothing shows next week's follow-ups. | "Who needs to come back" may mean upcoming, overdue, or both. |
| G3 | A patient who already came back still shows as due if the old visit carries the date. | Needs a rule for when a follow-up counts as done. |
| G4 | One patient with two visits on the same follow-up date appears twice (one row per visit). | A dashboard row should probably be one per patient. |
| G5 | Row shows only name and phone. | The doctor may need diagnosis, last visit date or days overdue to prioritize. |
| G6 | The list is a block on the patient list page, not a dashboard. | "Dashboard" is not defined: a page, a block, counts, a chart? |

## 5. Flagged concerns and open questions for the client

Not answered here. Answers go into the tickets.

**Meaning of "need to come back"**
1. Does it mean follow-ups due today, overdue, upcoming, or all of these? If upcoming, how far ahead (a week, a month)?
2. When does a follow-up stop being due: when the patient has a newer visit, when the doctor marks it done, or when the date passes?
3. Should a very old overdue follow-up (for example 6 months) still show, or is there a cutoff?

**What the dashboard shows**
4. What does "dashboard" mean here: a list, summary counts, a calendar, or a mix? Is a plain sorted list enough for the first version?
5. Which fields per patient: name and phone only, or also diagnosis, last visit date, days overdue?
6. Sort order: by date, by days overdue, or by name?
7. One row per patient or one row per visit?

**Actions**
8. Should the doctor be able to mark a patient as contacted or done from this screen? (This adds data that does not exist today.)
9. Should the screen link to the patient record only, or also to creating a new visit?

**Rules and edge cases**
10. Archived patients: stay hidden (current rule), or shown with a marker?
11. Is the follow-up date always entered by the doctor in the visit form, or should the app suggest it?
12. Patients with no phone number: show them anyway?

**Delivery**
13. What does "as soon as possible" mean: before the Day 15 demo? Which part must be there first if time is short?
14. Anything explicitly out of scope (export, printing, SMS or email reminders)? The base design already lists SMS reminders as out of scope.

## 6. Constraints from the repo

- One user (the doctor), no login, so no roles or permissions question applies.
- "Today" always comes from `clock.py`, never `datetime.now()` (timezone bug in ticket 05).
- Backend validates input (422). `types.ts` stays in step with backend models.
- Every behavior change ships with a test; `make test` runs it.
- Test data is fake only.

## 7. Next steps

1. Client answers section 5 in this file.
2. BA splits the spec into a ticket pack (one ticket per PR), each with acceptance criteria and the client's answers.
3. QA drafts the test matrix from the acceptance criteria.
4. Dev produces a plan for the first ticket without asking questions outside the ticket.
