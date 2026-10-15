# 01 - Filter todos by status

## Context
Users with many todos want to see only open or only done ones.

## Scope
- BE: `GET /todos?status=open|done` filters the list. No param returns all.
- FE: add All / Open / Done buttons above the list.

## Acceptance Criteria
- [ ] `?status=open` returns only `done=false`
- [ ] `?status=done` returns only `done=true`
- [ ] Invalid status returns 422
- [ ] FE filter persists after toggling a todo
- [ ] Tests for BE and FE
