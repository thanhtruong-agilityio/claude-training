---
description: Draft the "3. Key takeaways" section for the current training day from this branch's changes
allowed-tools: Bash(git branch:*), Bash(git log:*), Bash(git diff:*), Bash(git status:*)
---

Draft key takeaways for the current training day. $ARGUMENTS

1. Get the branch with `git branch --show-current`. If it is not `training/day-NN`, say so and stop.
2. Read `docs/day-NN.md` for that branch and the changes: `git log main..HEAD --oneline` and `git diff main...HEAD --stat`.
3. Write a draft of `## 3. Key takeaways` following `.claude/rules/notes-style.md`: English, terse, tables and one-liners, no prose.
4. Use only what the notes and changes show. Don't invent course content, links or badges.
5. Print the draft in chat. Don't edit any file; I will paste what I want.
