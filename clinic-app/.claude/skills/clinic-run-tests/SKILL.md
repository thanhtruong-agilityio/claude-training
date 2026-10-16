---
name: clinic-run-tests
description: Use when you need to run or verify the clinic-app tests, or before claiming a clinic-app change works
---

# Run clinic-app tests

1. `cd clinic-app`
2. Run `make test` (or `make test-backend` / `make test-frontend` if only one side changed). These run in containers; do not run `pytest` or `npm test` on the host.
3. Read the output. Report pass/fail with the failing test names; never say "passes" without having seen the run.
4. If a test fails twice for the same reason, stop and diagnose before changing more code.

Needs Docker running. If Docker is unavailable, say so and don't claim the tests passed.
