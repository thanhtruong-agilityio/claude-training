---
name: sync-gitlab
description: Use when the user wants to sync the merged GitHub main to the GitLab mirror - pushes a sync/day-NN branch to the gitlab remote so a merge request into GitLab main can be opened, never pushes gitlab main directly
---

# Sync GitHub main to GitLab

GitLab (`gitlab` remote) is the mirror. GitHub (`origin`) is where PRs merge. The two `main` histories differ (GitHub squashes, GitLab merges `sync/day-NN` branches), so the sync is always a branch plus a merge request, never a push to `main`.

## Rules

- Never push to `gitlab` `main`, never use `--force` or `--force-with-lease`. A non-fast-forward rejection is expected and is not a reason to force.
- Ask before the push (CLAUDE.md: ask before every push).
- Branch from `origin/main`, not from local `main` (local `main` may hold stray merge commits). Don't touch local `main`.
- Leave uncommitted changes alone (for example `.claude/settings.json`); don't stash, reset or commit them.

## Steps

1. Ask for the day number NN (two digits) if the user didn't give one. Default suggestion: the highest `docs/day-NN.md` on `origin/main`.
2. `git fetch origin` and `git fetch gitlab`. Stop and say so if either fails.
3. Check what is missing on GitLab: `git log --oneline gitlab/main..origin/main` is not meaningful (histories differ), so compare content instead: `git diff --stat gitlab/main origin/main`. If the diff is empty, report "already in sync" and stop.
4. Branch name is `sync/day-NN`. If `git ls-remote --heads gitlab sync/day-NN` already lists it, show it and ask whether to pick another name or update it; never overwrite silently.
5. Create the branch from `origin/main` without switching away from the current work: `git branch sync/day-NN origin/main`.
6. Show the user the diffstat from step 3 and the push command, and wait for an explicit yes:
   `git push gitlab sync/day-NN`
7. After the push, print the merge request link GitLab returns (or `https://gitlab.asoft-python.com/thanh.truong/claude-training/-/merge_requests/new?merge_request[source_branch]=sync/day-NN`), and tell the user to open the MR into `main` and merge it there. There is no GitLab tool: don't claim the MR was opened or merged.
8. Local cleanup (deleting `sync/day-NN`) is a branch deletion: ask first.

## Report

Say what was pushed (branch, commit), what was not done (MR, merge), and anything skipped.
