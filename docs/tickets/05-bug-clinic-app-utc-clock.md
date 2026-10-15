# 05 - Bug: clinic-app books visits on the wrong day (container runs UTC)

## Context
`clinic-app` stores `visited_at` as local clinic time (`datetime.now()`) and uses `date.today()` for "today's follow-ups" and the birth-year limit. The backend container has no timezone set, so it runs in UTC.

## Actual
In Vietnam (UTC+7), a visit created between 00:00 and 07:00 local time is stored with the previous day's date. Daily revenue, today's follow-ups and the "birth year cannot be in the future" check are off in the same window.

## Expected
All "now" and "today" values use the clinic's local time (`Asia/Ho_Chi_Minh`).

## Scope
- `clinic-app/docker-compose.yml` / `backend/Dockerfile`: set the container timezone to `Asia/Ho_Chi_Minh`.
- Check that the frontend's "today" (`RevenuePage`) and the backend agree.

## Notes
Reproduce by running the backend with `TZ=UTC` and freezing the clock at 01:00 local time (18:00 UTC the day before).

## Acceptance Criteria
- [ ] A test fails before the fix: at 01:00 local time, a new visit is booked on the local date
- [ ] Follow-ups "today" and the revenue default range use the local date
- [ ] Container reports `Asia/Ho_Chi_Minh` (`docker compose exec backend date`)
- [ ] README mentions the timezone setting
