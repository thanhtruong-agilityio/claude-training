---
name: check-day-note
description: Use before committing or opening a PR for a docs/day-NN.md training note - checks structure, branch match and honest checkboxes
---

# Check a day note

Read `docs/day-NN.md` and compare it with `docs/day-01.md`. Report findings; do not edit unless the user asks.

- [ ] Header has title, `Date`, `Trainee`, `Branch`; the branch equals the current branch (`git branch --show-current`).
- [ ] A `**Status:**` line exists and matches the checkboxes (nothing "done" that is unchecked, nothing checked that is pending).
- [ ] Sections `1. Setup check`, `2. Courses` (or `2. Exercises`), `3. Key takeaways` exist in that order.
- [ ] Every checked box is something the user actually did. Unrun exercises stay unchecked.
- [ ] Badge and artifact URLs were supplied by the user, not invented.
- [ ] Style: English, terse, tables and one-liners.
- [ ] No client secrets or customer data.

List each failed item with the line number. If the structure differs from day-01, say how and let the user decide.
