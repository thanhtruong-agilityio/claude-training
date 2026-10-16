---
name: clinic-add-endpoint
description: Use when adding or changing a clinic-app API endpoint and the screen that uses it
---

# Add or change a clinic-app endpoint

1. Write the failing pytest first in `backend/tests/` (use the `client` and `patient` fixtures from `conftest.py`).
2. Implement in `backend/app/`: model in `models.py`, query in `queries.py`, route in the matching `routers/*.py`. Get time from `clock.py`.
3. Update the frontend: `types.ts`, `api.ts`, then the page or component in `frontend/src/`.
4. Add or update a vitest test in `frontend/src/__tests__/`.
5. Run `make test` (see `clinic-run-tests`) and report the real result.
6. Check `clinic-data-safety` before committing.
