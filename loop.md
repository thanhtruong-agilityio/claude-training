# Reusable /loop prompts

Copy a block, fill the placeholders, paste it into a Claude Code session.

> **Notes (both prompts)**
> - A `/loop` lives only in the current session: when the session ends (closed, cleared, app quit), the loop stops. Paste the prompt again to restart it.
> - Every tick is a full model turn, so it spends quota even when nothing changed. Use the longest interval that is still useful, and stop the loop as soon as its stop condition is met.
> - Read-only: the loop reports, it never pushes, merges, re-runs jobs or replies to comments (CLAUDE.md: ask first).

## 1. PR: CI + review comments

| | |
|---|---|
| Interval | `15m` |
| Stop when | PR is merged or closed, **or** all checks pass and no unresolved review comment is left |
| Usage | replace `<PR>` with the PR number |

```text
/loop 15m Check PR #<PR> in thanhtruong-agilityio/claude-training: its CI status and its review comments.

### Steps
1. `gh pr view <PR> --json state,reviewDecision,mergeable,url`
2. `gh pr checks <PR>` — read the output, not the exit code (it exits non-zero for failing, pending and "no checks reported"). No checks reported means "no CI configured", not a failure.
3. Unresolved review threads (REST comments have no resolved flag):
   `gh api graphql -f query='query{repository(owner:"thanhtruong-agilityio",name:"claude-training"){pullRequest(number:<PR>){reviewThreads(first:100){nodes{isResolved comments(first:1){nodes{author{login} body}}}}}}}'`
   keep threads with `isResolved: false`.
4. `gh pr view <PR> --comments` — general (non-thread) comments; keep only those new since the last tick.

### Rules
- Read-only: do not fix code, re-run jobs, reply to or resolve comments.
- Stop the loop when the PR is merged or closed, or when all checks pass and no review thread has `isResolved: false`. Say why it stopped, then cancel this loop's scheduled job (CronList → CronDelete).
- If nothing changed since the last tick, answer "no change" only.

### Output Format
- State: <open|merged|closed> · <reviewDecision>
- CI: <pass|fail|pending> · failing jobs: <names or none>
- New comments: <author: one-line summary>, or none
```

## 2. main: CI

| | |
|---|---|
| Interval | `5m` |
| Stop when | the latest run on `main` has finished (success or failure), **or** the repo has no workflow |
| Usage | paste as is |

```text
/loop 5m Check the CI of the latest commit on main in thanhtruong-agilityio/claude-training.

### Steps
1. `gh run list --branch main --limit 3 --json databaseId,headSha,workflowName,status,conclusion,url`
2. If the latest run failed: `gh run view <id> --log-failed | tail -n 40` and name the failing job and step.

### Rules
- Read-only: do not re-run jobs, push or open issues.
- Stop the loop when the latest run on main has finished (report success, or the failure with job and log link), or when no workflow run exists (report once). Then cancel this loop's scheduled job (CronList → CronDelete).
- If the run is still in progress and nothing changed, answer "still running" only.

### Output Format
<short sha> · <workflow> · <status/conclusion> · <url>
```
