# 14 - [BE] Add due follow-ups report endpoint

- Spec: [follow-up dashboard](../specs/2026-10-27-follow-up-dashboard-spec.md)
- Issue: https://github.com/thanhtruong-agilityio/claude-training/issues/37
- Blocks: 15

## Story
As the doctor, I want a list of patients whose follow-up is due today or overdue, so that I know whom to call back without searching patient by patient.

## Context
Today `GET /visits/follow-ups` only matches one exact date, so a missed follow-up disappears the next day. The dashboard (ticket 15) needs a list of patients whose follow-up is due today or overdue.

## Client answers that apply
- Due means today or overdue. Upcoming is not needed (Q1).
- A follow-up stops being due once the patient has a newer visit (Q2).
- Overdue is cut off at 30 days (Q3).
- Sorted most overdue first, then today (Q6).
- One row per patient, most recent follow-up date wins (Q7).
- Archived patients stay hidden (Q10).
- Patients without a phone are included (Q12).
- Names are compared with a plain text comparison; no accent or case folding (follow-up to Q6, answered during test planning).

## Business rules
- BR1 A visit is a candidate when `follow_up_date` is set, the visit is not soft-deleted and the patient is not archived.
- BR2 `days_overdue` = `as_of` minus `follow_up_date` in days; `0` means due today. A candidate needs `0 <= days_overdue <= 30`.
- BR3 A candidate is dropped when the same patient has another non-deleted visit whose `visited_at` date is on or after the `follow_up_date`. The visit that carries the follow-up date never counts against itself.
- BR4 One item per patient: among the remaining candidates keep the one with the latest `follow_up_date`.
- BR5 Order: `days_overdue` descending, then `full_name` ascending by plain text comparison (the database default, as the current follow-ups endpoint does: case-sensitive, accents not folded), then `patient_id` ascending.
- BR6 `as_of` is optional and defaults to `clock.today()` (clinic time).
- BR7 `as_of` accepts only `YYYY-MM-DD`.

## Exceptions
- Invalid, impossible, empty or non-`YYYY-MM-DD` `as_of`: 422.
- No due patients: 200 with `{"total": 0, "items": []}`, not 404.
- Patient without a phone: listed, `phone` is `null`.

## Scope
In:
- New endpoint `GET /reports/follow-ups?as_of=YYYY-MM-DD`.
- Response:
  ```json
  {
    "total": 2,
    "items": [
      {"patient_id": 1, "full_name": "...", "phone": "...", "follow_up_date": "2026-10-20", "days_overdue": 7}
    ]
  }
  ```
  `total` = number of items.

Out:
- Upcoming follow-ups, a "contacted/done" status, export, SMS or email reminders.
- Changing or removing `GET /visits/follow-ups` (it stays as is).
- Any frontend change.

## Acceptance Criteria
All examples use `as_of=2026-10-27`.

- [ ] AC1 Given patient A has a visit with `follow_up_date` 2026-10-27, when the endpoint is called, then A is listed with `days_overdue` 0.
- [ ] AC2 Given patient A has a visit with `follow_up_date` 2026-10-20, when the endpoint is called, then A is listed with `days_overdue` 7.
- [ ] AC3a Given `follow_up_date` 2026-09-27 (30 days overdue), when the endpoint is called, then the patient is listed with `days_overdue` 30.
- [ ] AC3b Given `follow_up_date` 2026-09-26 (31 days overdue), when the endpoint is called, then the patient is not listed.
- [ ] AC4 Given `follow_up_date` 2026-10-28, when the endpoint is called, then the patient is not listed.
- [ ] AC5a Given a visit with `follow_up_date` 2026-10-20 and another non-deleted visit of the same patient on 2026-10-22, when the endpoint is called, then the patient is not listed.
- [ ] AC5b Given the same data as AC5a but the 2026-10-22 visit is soft-deleted, when the endpoint is called, then the patient is listed.
- [ ] AC5c Given a visit with `follow_up_date` 2026-10-20 and another non-deleted visit of the same patient on 2026-10-20, when the endpoint is called, then the patient is not listed.
- [ ] AC5d Given a single visit on 2026-10-20 whose own `follow_up_date` is 2026-10-20, when the endpoint is called, then the patient is listed.
- [ ] AC5e Given a visit with `follow_up_date` 2026-10-20 and another non-deleted visit of the same patient on 2026-10-19, when the endpoint is called, then the patient is listed.
- [ ] AC6 Given the only visit with a `follow_up_date` is soft-deleted, when the endpoint is called, then the patient is not listed.
- [ ] AC7 Given an archived patient with `follow_up_date` 2026-10-20, when the endpoint is called, then the patient is not listed.
- [ ] AC8 Given patient A has visit 1 (visited 2026-10-01, follow-up 2026-10-20) and visit 2 (visited 2026-10-05, follow-up 2026-10-25), when the endpoint is called, then A is listed once, with `follow_up_date` 2026-10-25 and `days_overdue` 2.
- [ ] AC9a Given A overdue 3 days, B overdue 10 days and C due today, when the endpoint is called, then the order is B, A, C.
- [ ] AC9b Given patients "Ánh", "Bình" and "an", all overdue 5 days, when the endpoint is called, then the order is "Bình", "an", "Ánh".
- [ ] AC9c Given two patients both named "An" with ids 1 and 2, both overdue 5 days, when the endpoint is called, then id 1 comes before id 2.
- [ ] AC10 Given a due patient without a phone, when the endpoint is called, then the item is listed with `phone` null (not an empty string).
- [ ] AC11 Given no patient is due, when the endpoint is called, then the status is 200 and the body is `{"total": 0, "items": []}`.
- [ ] AC12 Given `as_of` is `banana`, `2026-02-30`, `27-10-2026` or empty, when the endpoint is called, then the status is 422.
- [ ] AC13a Given no `as_of` and the clinic clock reads 2026-10-28 01:00 (2026-10-27 18:00 UTC), when the endpoint is called, then today is 2026-10-28 and a follow-up dated 2026-10-27 has `days_overdue` 1.
- [ ] AC13b Given `as_of=2026-10-20` while the clock reads 2026-10-27, when the endpoint is called, then 2026-10-20 is used as today.
- [ ] AC14 Given two due patients, when the endpoint is called, then `total` is 2 and each item has exactly `patient_id`, `full_name`, `phone`, `follow_up_date`, `days_overdue`.
- [ ] AC15 Given the new endpoint exists, when `GET /visits/follow-ups?date=2026-10-27` is called, then it behaves as before this change.
- [ ] AC16 Given a visit with no `follow_up_date`, when the endpoint is called, then that visit is ignored.

## Open questions
| # | Question | Owner | Working default until answered |
|---|---|---|---|
| OQ1 | Does a patient who comes back on the follow-up date itself count as having come back? The client said "after". | Client | Yes (AC5c) |
| OQ2 | When `as_of` is a past date, should a visit after `as_of` still count as the patient having come back? BR3 has no upper bound, so today it does. This matters only if the endpoint is used to ask what was due on a given day. | BA, then client | Yes (BR3 as written) |

## Technical Notes
- Add the route in `backend/app/routers/reports.py` and the response models in `backend/app/models.py`. Use `clock.today()`, never `datetime.now()`.
- `/reports/follow-ups` does not clash with other routes, so no route-order change is needed.
- Tests go in `backend/tests/test_reports.py`, written first. Fake patient data only. Run with `make test-backend`.

## Dependencies
- Blocked by: none.
- Blocks: 15.

## Estimate
M
