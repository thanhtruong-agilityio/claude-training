# 02 - Bug: DELETE returns 200 with a body

## Context
API consumers expect a successful delete to return `204 No Content`.

## Actual
`DELETE /todos/1` returns `200` with `{"ok": true}`.

## Expected
`DELETE /todos/1` returns `204` with an empty body. Missing id still returns `404`.

## Notes
FE `api.ts` parses JSON on every response, so check it still works after the fix.

## Acceptance Criteria
- [ ] Status 204, empty body
- [ ] Regression test added
- [ ] FE delete still works
