---
name: new-day-note
description: Use when starting a new training day in this repo - creates the day branch and a docs/day-NN.md note in the established structure
---

# New training day note

1. Ask the user for the day number (NN, two digits) and the topic. Don't guess either.
2. Branch: `training/day-NN` from `main`. Training-day branches are the one exception to the `<type>/<ticket>-<slug>` rule (see CLAUDE.md), so don't run `cl-core:branch` on them: it rejects `training/`. If the branch already exists, switch to it instead of recreating it.
3. Copy the structure of `docs/day-01.md` into `docs/day-NN.md`:
   - Header: title `# Day NN <topic>`, then `Date`, `Trainee`, `Branch` (must equal the real branch name).
   - `**Status:**` one line, then any artifact-link lines (`**4Ds:** <url>`) the user supplies, then a `---` separator. Put a `---` between sections too.
   - `## 1. Setup check` (checkboxes)
   - `## 2. Courses` (checkbox lists per course, with badge links) - use `## 2. Exercises` when the day has no course.
   - `## 3. Key takeaways` (condensed tables and bullets)
4. Leave every checkbox unchecked and every badge/URL empty until the user supplies it. Never invent links.
5. Style: English, terse, the trainee's own summarizing voice (tables, one-liners), not prose.
6. Commit with `cl-core:commit`, e.g. `docs(notes): add notes for day NN <topic>`. Ask before any push.
