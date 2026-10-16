---
name: artifact-note
description: Use when the user has short learning notes (key idea, a table, an example per lesson) and wants them turned into a structured, reviewable guide as an Artifact, with course content marked apart from their own additions
---

# Artifact note

Turn the trainee's short notes into one structured study guide, published as an Artifact. The point is quick review and applying the 4Ds (Delegation, Description, Discernment, Diligence) in daily work.

## Input

- The notes: per lesson, a key idea, one table, one example. A `docs/day-NN.md` file is a typical source.
- The course material to check against (pasted text, a file, or a link the user can share). If none is given, ask for it. Don't invent what the course says and don't claim to have checked against it.

## Steps

1. Read the notes fully. Keep the user's numbers, names and terms.
2. Check each point against the course material, if supplied, and give it one origin tag:
   - `Course`: stated in the course material
   - `Mine`: from the user's notes, not found in the course material
   - `Added`: something you (Claude) add to make the guide complete; keep these few and plainly labeled
   - `Unchecked`: no course material was available to verify
3. Build the guide with these sections, skipping one only when the notes give it nothing to hold:
   - **Steps**: the process in order, one line each
   - **Checklists**: things to verify before or after the task
   - **Templates**: reusable prompts or skeletons with `<placeholders>`
   - **Glossary**: term, one-line meaning
   - **Quiz**: 5-8 questions from the notes; answer hidden until the user reveals it
   - **Apply the 4Ds**: one short action per D for daily work
4. Every item carries its origin tag, shown as a small visible badge.
5. Load the `artifact-design` skill, write one self-contained `.html` file (scratchpad directory if the system prompt lists one), then publish it with the Artifact tool. Use a distinctive title (the topic, not "Study guide") and a one-sentence description. The page needs no runtime capability.
6. Reply with the link and a count of items per origin tag. List the `Added` and `Unchecked` items so the user can review them first.

## Rules

- Short and scannable beats complete. Tables, checklists and one-liners, not prose.
- Never present an `Added` or `Unchecked` item as if it came from the course.
- No secrets or customer data in the notes or the page; ask the user to remove them first.
- The Artifact is private by default. Don't share it unless the user asks.
