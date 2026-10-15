# 03 - Add due date to todos

## Context
Users want to set a deadline and see overdue todos.

## Scope
- BE: optional `due_date` (date) on create/update; stored in DB.
- FE: date input in the form; overdue todos (not done, past due) shown in red.

## Open questions
- Timezone handling? Existing DB rows need a migration?

## Acceptance Criteria
- [ ] `due_date` is optional and nullable
- [ ] Invalid date returns 422
- [ ] Overdue styling on FE
- [ ] Tests for BE and FE
