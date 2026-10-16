---
name: status-report
description: Use when the user wants a status report, daily report, daily notes or progress report to send by Gmail or Slack
---

# Status report (Gmail or Slack)

## Flow

1. Ask the user to pick a style: `Gmail` or `Slack` (AskUserQuestion if available). Skip if the request already names one.
2. Ask for input: links (PR, ticket, commit, doc), raw text, or a mix.
3. Process the input with the general rules below.
4. Output the report in the chosen style inside one code block so formatting survives copy-paste. No intro or explanation outside the block.

## General rules (both styles)

### Classifying input

1. Split the input into single items (one PR, ticket or task each).
2. Classify when the status is clear:
   - PR merged, ticket Closed/Done -> finished
   - PR open, waiting for review -> in review
   - user says "working on it", "WIP" -> in progress
   - user describes a blocker -> ISSUE
3. If any item's status is unclear, ask ONE question for ALL of them, with numbered choices (ask in the user's language):

```
I'm not sure about the status of these items, please pick:
1. <item A> -> (a) Done (b) In review (c) In progress
2. <item B> -> (a) Done (b) In review (c) In progress
Also: any ISSUE to record? Keep the default NEXT PLAN or change it?
```

4. If the user doesn't mention ISSUE or NEXT PLAN, use the style's default; don't ask.
5. Ask only about what is missing. Don't re-confirm clear items. With enough information, output the report right away.

### Title (level-1 bullet)

- Topic or task name, at most ~10 words.
- Start with a base-form verb for actions (Implement, Fix, Refactor, Add, Review, Update, Migrate); use a noun for course or module names (`Claude Code 101`, `Day 05: Memory, context, sessions`).
- Name the object and the purpose. Good: `Implement conversation memory/checkpointer for multi-turn queue resumption`. Bad: `Work on memory`.
- Keep a ticket id first: `[PROJ-123] Fix ...`.
- For a PR or ticket link, use its original title, shortened if long, same meaning.
- No trailing period. Capitalize the first letter only, except proper names and terms.

### Subtitle (level-2 bullet)

- Add only when the title needs scope or has sub-items.
- At most 5 per title, each at most ~8 words, short phrases not full sentences, no trailing period.
- Don't repeat the title or another subtitle.
- A subtitle may list or choose within one concept group (`Permission modes: default / acceptEdits / plan / auto`).

### Links

- Don't guess the content of a link you can't open: ask the user for the title and status.
- Never put a long raw URL in the middle of a sentence.

### Raw text

- Long or messy text: extract the key points and rewrite as title/subtitle; don't copy verbatim.
- One paragraph with several jobs: split into several titles.
- Keep numbers, proper names and terms the user used. Add no detail that isn't in the input.

### Formatting

- The whole report is in English. Keep technical terms as they are.
- Section headings: UPPERCASE on their own line, one blank line before the heading and one after it.
- Bullets use `*`, at most 2 levels (level 2 indented 3 spaces).
- No bold, emoji, tables or markdown headings.
- An empty section gets exactly one bullet `None`. Never drop a section.
- Each item appears in one section only.
- Never invent information. If a link, hash or repo is missing, omit that line.

## Style: Gmail

Order:

1. Opening line: `Below is the status report today:`
2. FINISHED
3. IN PROGRESS
4. ISSUES
5. NEXT PLAN
6. Closing line: `Thanks & Regards!`

Gmail rules:

- FINISHED: completed work. If there is a repo, add `Git repository: <ssh-url>` with the subtitle `Latest commit: <7-char-hash>`.
- IN PROGRESS: unfinished work. Items waiting for review also go here, with the suffix `(in review)`.
- NEXT PLAN default: `Continue in-progress tasks`
- Gmail doesn't render markdown: write the plain hash, no `[text](url)`.

Example:

```
Below is the status report today:

FINISHED

* Claude Code 101
   * Install, tour, first session
   * Permission modes: default / acceptEdits / plan / auto
   * Subagents, Skills, MCP, Hooks
* Completed Claude Code in action
* Exercise: Bug ticket through the full loop
* Git repository: git@github.com:<org>/<repo>.git
   * Latest commit: ae92307

IN PROGRESS

* Day 05: Memory, context, sessions

ISSUES

* None

NEXT PLAN

* Continue in-progress tasks

Thanks & Regards!
```

## Style: Slack

Order:

1. Opening line: `Hi team, please find my notes below.`
2. DONE
3. IN-REVIEW
4. IN-PROGRESS
5. ISSUE
6. NEXT PLAN

No closing line.

Slack rules:

- DONE: merged or closed.
- IN-REVIEW: PR sent, waiting for review. Add the PR link if there is one: `* <task> ([PR #123](url))`.
- IN-PROGRESS: unfinished work.
- Every bullet starts with a base-form verb.
- NEXT PLAN default: `Continue the in-progress tasks.` (with a trailing period, the only exception to the no-period rule).

Example:

```
Hi team, please find my notes below.

DONE

* None

IN-REVIEW

* None

IN-PROGRESS

* Implement conversation memory/checkpointer for multi-turn queue resumption

ISSUE

* None

NEXT PLAN

* Continue the in-progress tasks.
```
