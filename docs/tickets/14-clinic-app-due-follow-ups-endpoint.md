# 14 - [BE] Add due follow-ups report endpoint

- Spec: [follow-up dashboard](../specs/2026-10-27-follow-up-dashboard-spec.md)
- Issue: https://github.com/thanhtruong-agilityio/claude-training/issues/37
- Blocks: 15

## Context
The doctor wants to know which patients need to come back. Today `GET /visits/follow-ups` only matches one exact date, so a missed follow-up disappears the next day. The dashboard needs a list of patients whose follow-up is due today or overdue.

## Client answers that apply
- Due means today or overdue. Upcoming is not needed (Q1).
- A follow-up stops being due once the patient has a newer visit (Q2).
- Overdue is cut off at 30 days (Q3).
- One row per patient, most recent follow-up date wins (Q7).
- Sorted most overdue first, then today (Q6).
- Archived patients stay hidden (Q10).
- Patients without a phone are included (Q12).

## Scope
In:
- New endpoint `GET /reports/follow-ups?as_of=YYYY-MM-DD`. `as_of` is optional and defaults to `clock.today()`.
- Response:
  ```json
  {
    "total": 2,
    "items": [
      {"patient_id": 1, "full_name": "...", "phone": "..." , "follow_up_date": "2026-10-20", "days_overdue": 7}
    ]
  }
  ```
  `phone` is `null` when the patient has none. `days_overdue` = `as_of` minus `follow_up_date` in days, `0` for today. `total` = number of items.
- Rules:
  - A visit is a candidate when `follow_up_date` is set, the visit is not soft-deleted and the patient is not archived.
  - Candidate when `0 <= days_overdue <= 30`. A follow-up 31 days overdue is excluded.
  - A candidate is dropped when the same patient has another non-deleted visit with `visited_at` date on or after the `follow_up_date`. The visit that carries the follow-up date does not count against itself.
  - One item per patient: keep the candidate with the latest `follow_up_date`.
  - Order: `days_overdue` descending, then `full_name` ascending.

Out:
- Upcoming follow-ups, a "contacted/done" status, export, SMS or email reminders.
- Changing or removing `GET /visits/follow-ups` (it stays as is).
- Any frontend change.

## Acceptance Criteria
- [ ] AC1 Given a visit with follow-up date today, when the endpoint is called, then the patient is listed with `days_overdue` 0.
- [ ] AC2 Given a follow-up 7 days ago, then the patient is listed with `days_overdue` 7.
- [ ] AC3 Given a follow-up 30 days ago, then the patient is listed; given 31 days ago, then the patient is not listed.
- [ ] AC4 Given a follow-up date in the future, then the patient is not listed.
- [ ] AC5 Given a patient with a newer non-deleted visit on or after the follow-up date, then the patient is not listed. Given that newer visit is soft-deleted, then the patient is listed.
- [ ] AC6 Given a soft-deleted visit with a follow-up date, then it is ignored.
- [ ] AC7 Given an archived patient, then the patient is not listed.
- [ ] AC8 Given a patient with two due visits, then one item is returned, with the later follow-up date.
- [ ] AC9 Given patients with different overdue days, then the most overdue is first. Given the same overdue days, then the order is by name ascending.
- [ ] AC10 Given a patient without a phone, then the item is listed with `phone` null.
- [ ] AC11 Given no due patients, then the response is `{"total": 0, "items": []}` with status 200.
- [ ] AC12 Given `as_of` is not a valid date, then the status is 422.
- [ ] AC13 Given no `as_of`, then today is `clock.today()` (clinic time), not the server's local date.

## Technical Notes
- Add the route in `backend/app/routers/reports.py` and the response models in `backend/app/models.py`. Use `clock.today()`, never `datetime.now()`.
- `/reports/follow-ups` does not clash with other routes, so no route-order change is needed.
- Tests go in `backend/tests/test_reports.py`, written first. Fake patient data only. Run with `make test-backend`.

## Dependencies
- Blocked by: none.
- Blocks: 15.

## Assumptions
- [ASSUMPTION] A visit on the same day as the follow-up date counts as the patient having come back (the client said "after"; same day was not decided).

## Estimate
M
