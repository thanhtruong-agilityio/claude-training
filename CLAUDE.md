# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

This is a personal training log for a Claude/AI-fluency course, not a software project. There is no source code, build system, linter, or test suite — only Markdown. Don't invent build/test commands.

- [README.md](README.md) is just the repo title.
- [docs/](docs/) holds one notes file per training day (`docs/day-NN.md`), e.g. [docs/day-01.md](docs/day-01.md).

## Conventions observed

- One branch per training day: `training/day-NN` (main branch is `main`). Commit messages look like `add(notes): add notes for day NN <topic>`.
- Each day note follows the same structure: header (date, trainee, branch), status line, `1. Setup check`, `2. Courses` (checkbox lists per course, with badge/verification links), `3. Key takeaways` (condensed tables/bullets). Match this structure when adding a new day, and keep checkboxes accurate (unchecked = pending, e.g. Claude 101 in day 01).
- Notes are written in English, terse, in the trainee's own summarizing voice (tables, one-liners) — preserve that style when editing rather than expanding into prose.

# Working agreements

- One ticket per branch, named `<type>/<ticket>-<slug>` (ticket id in lowercase).
- Commits follow Conventional Commits with a lowercase subject. PRs follow `.github/pull_request_template.md`.
- Tickets are done per `docs/definition-of-done.md`.
- Start work with `/cl-core:ticket <ticket>`.

## Never do

- Never commit or push to `main`, `master`, `develop` or `release/*`.
- Never paste client secrets or customer data into any AI tool. AI output is a proposal until it has been run.

## Ask first

- Ask before every push, merge, branch deletion and deploy.

## Advisor

An advisor model (Opus) is configured for this repository. Consult it:

- before you commit to a plan or an approach:
  - during brainstorming, consult it once, on the written design, before you ask the user to approve it (not on every question);
  - for small tickets that skip design, do not consult it at this point;
- when the same error has happened twice;
- before you report the work as done.

Say in one line what you are asking it. If its guidance conflicts with the code or the test output, say so instead of following it blindly.
