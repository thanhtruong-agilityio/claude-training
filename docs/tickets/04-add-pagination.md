# 04 - Add pagination to GET /todos

## Context
The list will grow; returning everything will not scale.

## Scope
- BE: `limit` (default 20, max 100) and `offset` (default 0).
- FE: "Load more" button.

## Open questions
- Return a plain list or `{items, total}`? This changes the response shape.

## Acceptance Criteria
- [ ] Defaults applied, limit capped at 100
- [ ] Stable ordering by id
- [ ] FE loads next page without losing existing items
- [ ] Tests for BE and FE
