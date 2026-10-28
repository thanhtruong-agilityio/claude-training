# 17 - [CI] Run the clinic-app tests on every pull request

- Issue: to be created after approval
- Blocked by: none

## Story
As a developer, I want the backend and frontend tests to run automatically on every pull request, so that "CI is green" in `docs/definition-of-done.md` means something and a broken change is seen before it is merged.

## Context
The only workflow today is `.github/workflows/claude.yml`. It runs only when a comment, review or issue contains `@claude`, so no test runs on a pull request. During the follow-up dashboard work, tests were run by hand with `make test-backend` and `make test-frontend` (Docker). The definition of done asks for green CI, which cannot be met today.

## Business rules
- BR1 The workflow runs on every pull request targeting `main`, and on every new push to that pull request.
- BR2 It runs the same commands as a developer: `make test-backend` and `make test-frontend` from `clinic-app/`. No separate test commands are invented for CI.
- BR3 The check fails when either suite fails. Both suites always run, so one failure does not hide the other.
- BR4 The workflow has read-only access to the repository and no access to secrets.
- BR5 Test data stays fake. Nothing from test output is posted anywhere outside the Actions log.

## Exceptions
- A pull request that changes only Markdown files under `docs/` still runs the tests (simpler, and the suite is small). Skipping by path is out of scope.
- If Docker or the image build fails, the check fails with the build log, not a silent pass.

## Scope
In:
- New file `.github/workflows/ci.yml`.
- A short note in `docs/definition-of-done.md` only if the wording "CI is green" needs to name the workflow.

Out:
- Linting, type checks as separate jobs, coverage reports, deploys.
- Changes to `claude.yml`.
- Required-check rules in branch protection (a repository setting, done by the owner on GitHub).
- Caching of Docker layers (add later if the run is too slow).

## Acceptance Criteria
- [ ] AC1 Given a pull request is opened against `main`, when it is opened, then a check named `tests` starts without any comment.
- [ ] AC2 Given the pull request has passing tests, when the check finishes, then it is green.
- [ ] AC3 Given a backend test fails on the pull request, when the check finishes, then it is red and the log shows the failing test name.
- [ ] AC4 Given a frontend test fails on the pull request, when the check finishes, then it is red and the log shows the failing test name.
- [ ] AC5 Given both suites fail, when the check finishes, then the log shows failures from both suites.
- [ ] AC6 Given a new commit is pushed to the pull request, when it is pushed, then the check runs again on the new commit.
- [ ] AC7 Given the workflow file, when it is read, then it declares `contents: read` as the only permission and uses no secret.
- [ ] AC8 Given the existing `claude.yml`, when this ticket is merged, then `claude.yml` is unchanged.

## Open questions
| # | Question | Owner | Working default until answered |
|---|---|---|---|
| OQ1 | Should the check be marked required in branch protection? | Owner of the repository | No: left as a repository setting, not part of this ticket |
| OQ2 | Is a run of about a few minutes acceptable, or is Docker layer caching needed from the start? | Owner | No caching until a run is too slow |

## Technical Notes
- `ubuntu-latest` has Docker and Compose. `make test-*` uses `docker compose run --rm --no-deps`, so no ports are published.
- Pin action versions (`actions/checkout@v4`, as `claude.yml` does).
- AC3 to AC5 are proved on a throwaway branch with a deliberately failing test, never on `main`. The throwaway branch and its pull request are closed afterwards (deleting needs an explicit yes).
- The GitHub token used for pushes may lack the Workflows permission, so pushing the file may need that permission or a manual merge on the web.

## Dependencies
- Blocked by: none.
- Blocks: none. Later pull requests get a real check once this is merged.

## Estimate
S
