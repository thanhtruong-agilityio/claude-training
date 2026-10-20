# Day 07 Agent skills

- **Date:** 2026-10-20
- **Trainee:** thanh.truong
- **Branch:** `training/day-07`

**Status:** Introduction to Agent Skills done (lessons 1-6; no course quiz).

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### Introduction to Agent Skills

- [x] What are skills?
- [x] Creating your first skill
- [x] Configuration and multi-file skills
- [x] Skills vs. other Claude Code features
- [x] Sharing skills
- [x] Troubleshooting skills

---

## 3. Key takeaways

**Introduction to Agent Skills: what are skills?**
- Problem: re-explaining the same things (review criteria, commit format, team standards) → skill removes the repetition
- Skill = folder of instructions/resources; core file `SKILL.md` = frontmatter (`name`, `description`) + instructions
- Claude matches each request against skill **descriptions** and activates the fits → the description decides whether a skill gets used
- Personal: `~/.claude/skills` (all projects) · Project: `.claude/skills` in repo (shared via git)
- Good for: code review standards, commit formats, brand guidelines, doc templates, debugging checklists. Rule of thumb: keep explaining the same thing → make it a skill

| | CLAUDE.md | Skills | Slash commands |
|---|---|---|---|
| Loads | Every conversation | On demand, when request matches | Only when typed |
| Activation | Always | Automatic (description) | Manual |
| Context | Always occupies | Only name + description at first | On invoke |
| Best for | Always-on preferences | Task-specific expertise | Explicit actions |

**Introduction to Agent Skills: creating your first skill**
- Skill = directory with `SKILL.md` (frontmatter `name` + `description`, then instructions). Directory name matches skill name
- Sample: personal `~/.claude/skills/pr-description` → diff vs main, fixed What / Why / Changes template
- Skills load at startup → restart Claude Code after create/edit/delete; verify in skills list, then ask for a PR description on a branch with changes
- Startup loads only name + description. Request is compared to descriptions by **semantic matching** (wording needn't match). After a match Claude asks you to confirm, then loads full `SKILL.md`
- Update = edit `SKILL.md` · remove = delete directory
- Name clash priority: **Enterprise** (managed settings) > **Personal** (`~/.claude/skills`) > **Project** (`.claude/skills`) > **Plugins**. Use specific names (`frontend-review`, `backend-review`) to avoid collisions

**Introduction to Agent Skills: configuration and multi-file skills**
- Frontmatter: `name` + `description` required · `allowed-tools`, `model` optional
- `name`: lowercase, numbers, hyphens, ≤64 chars, matches directory · `description`: ≤1,024 chars, used for matching
- Good description = what the skill does + when to use it + keywords users actually say → better triggering
- `allowed-tools` **pre-approves** listed tools while skill is active (no permission prompts); does NOT restrict Claude to them. Omitted = nothing pre-approved. `disallowed-tools` (Claude Code) removes tools
- Plain `Bash` pre-approves shell broadly (trusted skills only); narrow with a pattern like `Bash(git status *)`
- Progressive disclosure: essentials in `SKILL.md` (<500 lines), link to supporting files read only when needed. Suggested dirs: `scripts/`, `references/`, `assets/`
- Scripts: tell Claude to **run**, not read → only output costs tokens

**Introduction to Agent Skills: skills vs. other Claude Code features**
- Wrong feature = unnecessary complexity. Core principle: **each feature handles its own specialty**
- CLAUDE.md = always loaded · Skill = on demand, adds to current conversation · Subagent = separate isolated context, returns results · Hook = event-driven (save, tool call) · MCP server = external tools/integrations
- Skills are **request-driven**; hooks are **event-driven**

| Feature | Activation | Context | Best for |
|---|---|---|---|
| CLAUDE.md | Always | Every conversation | Project-wide standards, constraints, style |
| Skills | Request matches | Adds to current conversation | Task-specific expertise, detailed procedures |
| Subagents | Delegated a task | Separate, isolated | Delegated work, different tool access, isolation |
| Hooks | Event occurs | Automated side effects | Every-save actions, pre-tool validation |
| MCP servers | Via integrations | External tools/services | Outside systems and data |

- Typical setup combines all five. Review CLAUDE.md for content that belongs in a skill (e.g. PR review checklist)

**Introduction to Agent Skills: sharing skills**

| Method | Where | Who gets it | Best for |
|---|---|---|---|
| Repository | `.claude/skills` in Git repo | Anyone who clones | Team standards, project workflows |
| Plugin | Skills folder in plugin, via marketplace | Anyone who installs | Broadly useful, less project-specific |
| Enterprise managed | Org managed settings | Whole org | Mandatory standards, compliance (highest priority) |

- Managed skills override personal/project/plugin of same name; `strictKnownMarketplaces` limits where plugins can be installed from
- **Subagents don't inherit skills**: fresh context. Built-in agents (Explorer, Plan, Verify) can't use skills at all
- Custom subagent: skills exist in `.claude/skills` → create via `/agents` or `.claude/agents/*.md` → list them in frontmatter `skills` field. Loaded at subagent **start**, not on demand
- Helps for: isolated delegation with specific expertise · different skills per subagent (frontend vs backend reviewer) · enforcing standards without relying on prompts alone


**Introduction to Agent Skills: troubleshooting skills**
- Run the **skills validator** first (install with `uv`): catches structure problems before other debugging

| Symptom | Likely cause | Fix |
|---|---|---|
| Never triggers | Description lacks matching language | Add trigger phrases, test variations |
| Missing from skills list | Wrong path/filename or YAML error | `SKILL.md` inside a named dir, exact name; `claude --debug` |
| Wrong skill used | Descriptions too similar | Make them distinct |
| Personal skill ignored | Same-name enterprise skill wins (shadowing) | Rename or ask admin |
| Plugin skills absent | Stale cache / bad structure | Clear cache, restart, reinstall; validate |
| Script fails | Deps, permissions, paths | Install packages, `chmod +x`, forward slashes (even on Windows) |

- Priority hierarchy: Enterprise > Personal > Project > Plugins

Source: What are skills? · Introduction to Agent Skills — https://academy.claude.com/courses/introduction-to-agent-skills/what-are-skills
Source: Creating your first skill · Introduction to Agent Skills — https://academy.claude.com/courses/introduction-to-agent-skills/creating-your-first-skill
Source: Configuration and multi-file skills · Introduction to Agent Skills — https://academy.claude.com/courses/introduction-to-agent-skills/configuration-and-multi-file-skills
Source: Skills vs. other Claude Code features · Introduction to Agent Skills — https://academy.claude.com/courses/introduction-to-agent-skills/skills-vs-other-claude-code-features
Source: Sharing skills · Introduction to Agent Skills — https://academy.claude.com/courses/introduction-to-agent-skills/sharing-skills
Source: Troubleshooting skills · Introduction to Agent Skills — https://academy.claude.com/courses/introduction-to-agent-skills/troubleshooting-skills
