# Spec: follow-up dashboard for the doctor

- Source: [intent](../intents/2026-10-27-follow-up-dashboard.md)
- Author: ThanhTruong (playing the BA)
- Date: 2026-10-27
- Status: client answered (section 5); next is the ticket pack

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

## 5. Open questions and client answers

Answers are from the client. "Assumption" marks a question the client did not decide; the BA proceeds on that assumption.

**Meaning of "need to come back"**
1. Does it mean follow-ups due today, overdue, upcoming, or all of these? If upcoming, how far ahead?
   - **Answer:** today and overdue. Upcoming is not needed for the first version.
2. When does a follow-up stop being due?
   - **Answer:** when the patient has a newer visit after the follow-up date. No "done" button for now (see 8).
3. Should a very old overdue follow-up still show?
   - **Answer:** cut off at 30 days overdue.

**What the dashboard shows**
4. What does "dashboard" mean: a list, summary counts, a calendar, or a mix?
   - **Answer:** a simple list, plus one total at the top (for example "5 patients to call"). No calendar or chart.
5. Which fields per patient?
   - **Answer:** name, phone, follow-up date, days overdue. Diagnosis is not needed.
6. Sort order?
   - **Answer:** most overdue first, then today.
7. One row per patient or per visit?
   - **Answer:** one row per patient. If a patient has several matches, use the most recent follow-up date.

**Actions**
8. Should the doctor be able to mark a patient as contacted or done from this screen?
   - **Answer:** no, not in this version. Out of scope.
9. Link to the patient record only, or also to creating a new visit?
   - **Answer:** the patient record only, as the current list does.

**Rules and edge cases**
10. Archived patients: hidden or shown with a marker?
    - **Answer:** hidden, as today.
11. Is the follow-up date always entered by the doctor, or should the app suggest it?
    - **Assumption (client undecided):** the doctor keeps entering it by hand in the visit form, as today.
12. Patients with no phone number: show them anyway?
    - **Answer:** yes, with an empty phone cell.

**Delivery**
13. What does "as soon as possible" mean? Which part must be there first if time is short?
    - **Answer:** within two weeks. If time is short, the list of overdue and today patients comes first; the total at the top comes last.
14. Anything explicitly out of scope?
    - **Answer:** SMS and email reminders are out (already out in the base design).
    - **Assumption (client undecided):** export and printing are out of scope too.

## 6. Constraints from the repo

- One user (the doctor), no login, so no roles or permissions question applies.
- "Today" always comes from `clock.py`, never `datetime.now()` (timezone bug in ticket 05).
- Backend validates input (422). `types.ts` stays in step with backend models.
- Every behavior change ships with a test; `make test` runs it.
- Test data is fake only.

## 7. Next steps

1. Client answered section 5 (done).
2. BA splits the spec into a ticket pack (one ticket per PR), each with acceptance criteria and the client's answers.
3. QA drafts the test matrix from the acceptance criteria.
4. Dev produces a plan for the first ticket without asking questions outside the ticket.
