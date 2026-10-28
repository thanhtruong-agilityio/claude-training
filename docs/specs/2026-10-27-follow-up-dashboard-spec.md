# Spec: follow-up dashboard for the doctor

- Source: [intent](../intents/2026-10-27-follow-up-dashboard.md)
- Author: ThanhTruong (playing the BA)
- Date: 2026-10-27
- Status: built (tickets 14, 15, 16 merged); decisions from the build are in section 7, open questions still waiting for an owner are in section 8

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

## 7. Decisions made during the build

| # | Decision | Where it lives | Made by |
|---|---|---|---|
| D1 | Patient names are ordered by plain text comparison (database default): case-sensitive, accents not folded. | Ticket 14 BR5, AC9b, AC9c | BA, during test planning |
| D2 | `as_of` accepts only `YYYY-MM-DD`. Compact (`20261027`) and ISO week (`2026-W44-2`) forms are rejected with 422 even though the parser would accept them. | Ticket 14 BR7, AC12 | BA, after the review of PR #42 |
| D3 | The follow-up date is shown as `YYYY-MM-DD`. | Ticket 15 BR3 | BA (working default) |
| D4 | The list has three states with fixed texts: "Loading follow-ups...", "No patients to call", "Could not load follow-ups" with "Try again". Every failure (4xx, 5xx, network) looks the same and nothing from the response is shown or logged. | Ticket 16 BR1 to BR4, AC6, AC7 | BA (working default) |
| D5 | A visit on the follow-up date itself counts as the patient coming back. | Ticket 14 OQ1, AC5c | BA (working default) |

## 8. Open questions still waiting for an answer

| # | Ticket | Question | Owner | Working default until answered |
|---|---|---|---|---|
| OQ1 | 14 | Does a patient who comes back on the follow-up date itself count as having come back? The client said "after". | Client | Yes (AC5c) |
| OQ2 | 14 | When `as_of` is a past date, should a visit after `as_of` still count as the patient having come back? BR3 has no upper bound, so today it does. Matters only if the endpoint is used to ask what was due on a given day. | BA, then client | Yes (BR3 as written) |
| OQ1 | 15 | Which date format does the doctor want to read in the list? | Client | `YYYY-MM-DD` |
| OQ1 | 16 | Is the wording of the four messages acceptable? | Client | The texts in D4 |

## 9. Next steps

1. Client answered section 5 (done).
2. BA splits the spec into a ticket pack (done: tickets 14 to 16).
3. QA drafts the test matrix from the acceptance criteria (done).
4. Build tickets 14 to 16 (done, PRs #42, #43, #45).
5. Get answers to section 8 and update the tickets if a working default changes.
