# Day 05 Memory, context, sessions

- **Date:** 2026-10-16
- **Trainee:** thanh.truong
- **Branch:** `training/day-05`
- **Track:** Developer

**Status:** Notes drafted. All exercises pending (not yet run).

---

## 1. Setup check

- [x] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training
- [ ] Auto memory on (check `/memory`)

---

## 2. Exercises

- [ ] Write the repo's CLAUDE.md as a team: build/run commands, conventions, "never do" list, under one screen
- [ ] Auto memory + compaction: run a long session, `/compact`, observe what survives
- [ ] Checkpointing: make a bad edit, `/rewind` it
- [ ] Prove context matters: same task in a fresh session vs. one that has read the codebase

---

## 3. Key takeaways

**Where context lives**

| Mechanism | Holds | Survives new session | Survives `/compact` |
|---|---|---|---|
| CLAUDE.md | Repo rules, commands, never-do list | Yes (loaded every session) | Yes (reloaded) |
| Auto memory | Facts Claude saved for itself | Yes | Yes |
| Conversation | Everything said and read so far | No (`--resume` brings it back) | Summarized only |

**Compaction**
- `/compact` replaces history with a summary: frees window, loses detail
- Put durable rules in CLAUDE.md, not in chat: chat is what gets summarized away

**`/rewind` (checkpoints)**
- Every Claude file edit is checkpointed: rewind code, conversation, or both
- Does not track changes made via bash commands or outside Claude: don't rely on it for those
- Not a replacement for git

**Sessions**
- One topic per session: clean context, cheaper, sharper
- Resume with `--resume` / `--continue` instead of re-explaining

---

## 4. Context experiment

Task (same in both): _to fill_

| | Fresh session | Session that read the codebase |
|---|---|---|
| Quality of result | | |
| Follow-up questions needed | | |
| Tokens (`/context`, `/cost`) | | |
| Verdict | | |

---

## 5. Observations

- Compaction: what survived / what was lost: _to fill_
- Rewind: what was restored: _to fill_
