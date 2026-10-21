# 11 - Add the @claude GitHub Action

## Context
Day 09 exercise needs `@claude review` to answer on a PR. The repo has no workflows.

## Scope
- Add `.github/workflows/claude.yml` using `anthropics/claude-code-action`.
- Trigger on comments, review comments, reviews and issues that mention `@claude`.

## Acceptance Criteria
- [ ] Commenting `@claude review` on a PR starts the workflow
- [ ] The API key comes from the `ANTHROPIC_API_KEY` repo secret, never from a file
