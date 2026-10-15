# 06 - Bug: PUT /visits/{id} without `visited_at` moves the visit to "now"

## Context
`PUT /visits/{id}` replaces the whole visit. `VisitWrite.visited_at` defaults to `datetime.now`, so a request that omits it overwrites the stored value.

## Actual
`PUT /visits/1` with `{"fee": 100000, "paid_amount": 100000}` changes `visited_at` to the current time. Revenue is booked on the visit date, so past days' totals change silently.

## Expected
`PUT` keeps the stored `visited_at` when the field is missing, or rejects the request (422). `POST` still defaults to now.

## Notes
The frontend always sends `visited_at` on edit, so the UI is not affected today. Decide between "keep stored value" and "require the field" and write the decision in the PR.

## Acceptance Criteria
- [ ] Regression test: PUT without `visited_at` does not change it (or returns 422)
- [ ] POST without `visited_at` still defaults to now
- [ ] Existing visit and report tests pass
