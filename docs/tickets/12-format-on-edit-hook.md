# 12 - Format files automatically after Claude edits them

## Context
Claude edits files in clinic-app without a formatter, so style drifts between edits.

## Scope
- PostToolUse hook on Edit and Write that formats the edited file.
- Backend `*.py` with ruff, frontend `src/**/*.{ts,tsx}` with prettier.
- Add both tools as dev dependencies. Format existing code once, in its own commit.

## Acceptance Criteria
- [ ] Editing a `.py` file and a `.tsx` file leaves them formatted
- [ ] Other file types are left alone
- [ ] A formatter failure never blocks the edit
- [ ] `make test` passes
