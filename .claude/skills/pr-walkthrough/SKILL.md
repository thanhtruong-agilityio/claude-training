---
name: pr-walkthrough
description: Use when a pull request is ready for review and a teammate needs a walkthrough - publishes an Artifact explaining what changed, why, and how to test, and drafts the message to send the peer
---

# PR walkthrough

Turn one pull request into a short Artifact that walks a teammate through it: what changed, why, how to test. The reader should be able to review the PR without asking you questions.

## Input

- A PR number or URL. If none is given, use the PR of the current branch (`gh pr view`).
- If no PR can be found, stop and ask. Don't guess a number.

## Steps

1. Read the PR: title, body, linked ticket, commits and diff (`gh pr view <n>`, `gh pr diff <n>`, or the GitHub MCP tools).
2. Scan the PR text and diff for secrets or customer data. If any show up, stop and ask the user to remove them first.
3. Build the page with these sections, in this order:
   - **What changed**: files grouped by purpose, one line each. A table is fine.
   - **Why**: the reason, from the PR body and ticket. If it isn't stated, write "not stated in the PR". Don't invent a motive.
   - **How to test**: concrete steps from the PR's test plan. If the PR has none, say so and propose steps, labeled `Added by Claude`. This repo has no build or test suite for Markdown, so for docs-only PRs the steps are "what to read and check".
4. Load the `artifact-design` skill, write one self-contained `.html` file (scratchpad directory if the system prompt lists one), then publish it with the Artifact tool. Title: the PR's subject, not "PR walkthrough". Add a one-sentence description. On the first publish pass `icon` (for example `review`); omit it on republish. The page needs no runtime capability.
5. Reply with the link and a short message for the peer, ready to paste:
   > Hi <name>, here is a walkthrough of PR #<n> (<title>): <artifact link>. It covers what changed, why, and how to test. Could you take a look?

## Rules

- Page and message are in English.
- Short and scannable beats complete. Tables and bullets, not prose.
- Never present a guess as if it came from the PR. Mark it `Added by Claude` or "not stated".
- The Artifact is private by default. Tell the user to share it themselves; the peer can't open it until they do.
- Never send the message to anyone. The user sends it.
- No secrets or customer data on the page.
