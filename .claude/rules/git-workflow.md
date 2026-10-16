# Git workflow

- There is no source code, build or test suite in this repo (only Markdown); don't invent build or test commands.
- Branches: `training/day-NN` for a training day; anything else is `<type>/<ticket>-<slug>` with the ticket id in lowercase. One ticket per branch.
- Never commit or push to `main`, `master`, `develop` or `release/*`.
- Commits follow Conventional Commits with a lowercase subject, e.g. `docs(notes): add notes for day NN <topic>`.
- PRs follow `.github/pull_request_template.md`; tickets are done per `docs/definition-of-done.md`.
- Ask before every push, merge, branch deletion and deploy.
