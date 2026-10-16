# Day 04 Claude Code 101

- **Date:** 2026-10-16
- **Trainee:** thanh.truong
- **Branch:** `training/day-04`

**Status:** Claude Code 101 in progress — lessons 1, 3, 4, 5, 6, 7, 8, 9, 10 noted; lesson 2 and lessons 11-12 pending; Claude Code in Action lessons 1-3, 5-9 noted; lesson 4 pending.

**Learning notes:** https://claude.ai/artifact/GUEjZT9Gg9ZiW8GQ6ocqei

---

## 1. Setup check

- [ ] Claude Code installed (terminal)
- [ ] First prompt run in Plan Mode

---

## 2. Courses

### 2.1 Claude Code 101

- [x] What is Claude Code?
- [ ] How Claude Code works
- [x] Installing Claude Code
- [x] Your first prompt
- [x] The explore → plan → code → commit workflow
- [x] Context management
- [x] Code review
- [x] The CLAUDE.md file
- [x] Subagents
- [x] Skills
- [ ] Lessons 11-12
- [ ] Course quiz + badge

### 2.2 Claude Code in Action

- [x] Steering long sessions
- [x] A CLAUDE.md that follows
- [x] Verification skills
- [x] Hooks
- [x] Routines and headless
- [x] GitHub Actions and Code Review
- [x] Trust it: verifying unsupervised runs
- [x] Plugins
- [ ] Lesson 4 (permission modes)
- [ ] Course quiz + badge

---

## 3. Key takeaways

**Claude Code = agentic coding tool.** Reads, edits, runs commands, connects to dev tools. Works as an **AI Agent** (LLM in a real-time loop + tools).
- vs Claude.ai: direct file / terminal / codebase access, does the work itself (no copy-paste)
- Can: read + explain code · edit across the project · run commands and use the output · search web docs
- Watch: **context window** (working memory, can't hold the whole codebase) · **permissions** · mistakes

**Install / where it runs**

| Option | How | Notes |
|---|---|---|
| Terminal | curl one-liner (macOS/Linux/WSL); PowerShell / CMD (Windows) | Gets new features first |
| Homebrew / winget | package manager | No auto-update |
| VS Code / JetBrains | extension / plugin | Nearly the same as terminal |
| Desktop | "Code" toggle | Chosen folder, permissions, background work |
| Web | claude.ai/code | GitHub repos only, remote work |

First run: `claude` from the project dir → theme + sign-in (Pro/Max/Enterprise or API key). Claude can access that dir + subfolders.

**Modes (Shift + Tab)**

| Mode | Behavior |
|---|---|
| Manual | Asks before every edit and command |
| Auto-accept | Edits auto-approved; commands still ask |
| Auto mode | Background safety check screens each action |
| Plan Mode | Read-only analysis → plan; no edits |

**Workflow: explore → plan → code → commit**

| Step | What |
|---|---|
| Explore | Gather context (Explore subagent can summarize the codebase) |
| Plan | Plan Mode; plan states **success criteria**; best point to course-correct (no code yet) |
| Code | Approve plan, iterate, step in when stuck; add tools/tests as source of truth; recurring fix → `CLAUDE.md` |
| Commit | Test myself → **subagent code reviewer** (fresh context, no session bias) → Claude writes commit message in my style |

Prompt: be as descriptive as possible; use Plan Mode to explore details before any code runs.

**Context management**
- Context = working memory: prompts, files read, commands run, tool results all take space; it is finite
- Window near limit → **automatic compaction** (summarizes, drops unneeded tool results; can lose details)

| Command | What |
|---|---|
| `/compact` | Compact so far, keep a memory of earlier work → mid-feature near the limit |
| `/clear` | Remove everything, start from scratch → new feature, no bias from earlier chat |
| `/context` | Size, biggest categories, visual breakdown |

- Remember across sessions → `CLAUDE.md`
- Save space: specific prompts (vague = more exploring) · turn off unrelated MCP servers (they load all tools upfront; Skills don't) · subagents when only the answer matters (separate window, return a summary)

**Code review**
- Claude's summary ≠ the real change; the session that wrote the code is a weak judge → read the diff myself, then get a clean-context review
- Read the diff: look for unrequested changes · skipped/deleted/loosened tests · new packages · hard-coded URLs/keys

| Command | What |
|---|---|
| `/diff` | Uncommitted changes file by file, incl. what each Claude turn changed |
| `/rewind` (or Esc Esc) | Pick the prompt → "Restore code and conversation". Shell-command changes (e.g. package installs) are not rolled back |
| `/code-review` | Review in a clean context (no session history); reports only, edits nothing unless asked; runs in background, counts against usage |

- Sort each finding: **fix now** · **ask why** (can't verify) · **leave it** (real but minor, batch)
- Challenge a finding: quote it back, ask Claude to check again; ask for evidence with every fix
- Review closely (human + Claude): large, sensitive/destructive, or going to a teammate. One-liners: quick diff check
- Reviewer keeps flagging the same thing → write a rule in `CLAUDE.md`

**CLAUDE.md**
- Persistent project memory: without it Claude starts fresh each session, re-explores the codebase, sometimes assumes
- Markdown file in the project root, read automatically at session start, contents appended to my prompt ("onboarding script for the codebase")
- Put in: stack · dev/test/lint commands · code style rules (indentation, named exports, where API routes live)

| Level | Where | Who |
|---|---|---|
| Project | Project root, committed to version control | Whole team |
| User | My configuration folder | Me, all projects |

- Rule I keep correcting → ask Claude to **save it**, otherwise it may not carry to the next session
- `@README.md` → point Claude to project docs
- Start without a CLAUDE.md, see where I keep correcting, then `/init` → keeps the file compact
- Begin with stack, preferences, commands; build up over time

**Subagents**
- Claude delegates tasks to subagents → they break work down and run parts in parallel; point = context management
- Exploration (tool calls over code, web research) eats the window and most of it isn't relevant to the feature → subagent explores in its **own isolated context**, returns **only a summary**
- Create: `/agents` → "Create new agent" → scope, purpose, tool access, color. Claude generates name, description, prompt; the **description** tells Claude when to call it
- Defined as Markdown + YAML frontmatter
- Customize: **persistent memory** (across conversations) · preload skills with the `skills` key (whole skill loads into the subagent's context)
- Background subagent does the heavy lifting, I get just the answer. More depth: separate course "Introduction to subagents"

**Skills**
- Write standards (team rules, PR review preferences, commit format) once instead of re-explaining
- A skill = markdown file (more broadly a folder of instructions, scripts, resources) → Claude applies it automatically when relevant
- **Description drives activation**: Claude matches my request against skill descriptions (e.g. "review this PR" → PR-review skill)

| Where | Path | Scope |
|---|---|---|
| Personal | `~/.claude/skills` | All my projects, my preferences |
| Project | `.claude/skills` at repo root | Anyone who clones the repo, team standards |

| vs | Difference |
|---|---|
| CLAUDE.md | Always loaded → always-on rules (e.g. "use TypeScript strict mode"). Skills load on demand; only name + description enter context first → don't crowd the window |
| Slash commands | I type them. Skills activate when Claude recognizes the situation |

**Claude Code in Action: steering long sessions**
- Long tasks (multi-file refactors) need two habits: **scope before Claude starts, steer while it runs**
- Scope: Plan Mode = read-only research → plan; read it closely and add to it before execution (iterating on a plan is faster than cleaning up)

| Tool | What |
|---|---|
| `/compact <text>` | Summarize, use summary as new context, delete old messages; the text steers what the summary keeps |
| Checkpoint | Every user prompt creates one |
| Rewind (Esc Esc on empty prompt) | Return to a checkpoint: restore conversation / code / both. "Summarize from here" = everything after it; "Summarize up to here" = everything before (compress a long setup phase, keep implementation) |
| Goal | Completion condition; Claude keeps working across turns until a fast evaluator confirms. Condition must be checkable from the transcript (e.g. test results). Cancel `/goal clear` |
| Loop | Re-run a prompt on an interval (fixed or self-paced), e.g. watch CI/deploy. Stop with Esc |
| Worktree | Own file tree per session → parallel sessions can't overwrite each other. Clean worktree auto-removed on exit |
| `.worktreeinclude` | Repo-root file listing git-ignored files (local config, env) to copy into each worktree |

- Goal when "done" is easier to describe than the steps; worktrees for parallel work

**Claude Code in Action: a CLAUDE.md that follows**
- Trap: file grows a rule after every problem → Claude ignores parts. Not a bug: CLAUDE.md is **guidance, not enforcement**; every line competes for attention → longer file = less reliable adherence to any rule → keep it lean
- **Hard rules that must never break → pre-tool-use hook** (runs before an action, can block it). CLAUDE.md = softer conventions

| Location | Scope |
|---|---|
| Managed policy | Org-level, platform team, can't be excluded |
| User | Personal, all projects |
| Project | Shared, checked in |
| Local | Git-ignored, personal, one repo |

All four load together at launch and stack.
- Imports (`@path/to/file`) tidy a long file but expand inline at launch → **don't reduce context**
- Phrasing: specific + checkable · name the replacement when banning something · save emphasis words (IMPORTANT) for the few rules that matter (only raise priority relative to quieter rules)
- Wrong behavior = bug report against CLAUDE.md → ask Claude to add the corrective rule
- Treat it like production code: delete lines I can't justify

**Claude Code in Action: verification skills**
- Checking Claude's work shouldn't depend on me remembering to ask → **build a verification skill first**
- Triggers on its own when a change matches its description → runs the test suite · reads the diff · checks no test was weakened to pass · reports pass/fail **with evidence**
- Green tests ≠ verified: "done" = gates run and observed, results stated explicitly
- Pattern generalizes (release checklist, migration recipe, pre-PR check). Rule: typed the same multi-step instruction twice → make it a skill
- Skill folder: `skill.md` (name + triggering description + procedure, keep lean) · `reference.md` (read only when needed) · scripts, e.g. `check.sh` (executed, not loaded into context)

| Put it in | When |
|---|---|
| `CLAUDE.md` | Always-on conventions (naming, file locations) |
| Skill | Task-specific procedure / reference material |
| Hook | Rule Claude must not be able to skip (code that runs) |

- Only descriptions load into context until a skill is needed. Check into `.claude/skills` → whole team gets the same checks

**Claude Code in Action: hooks**
- CLAUDE.md rule = request Claude usually follows · hook = deterministic code at a fixed point in the loop → "Claude can't skip it"
- ~30 events; key ones: `PreToolUse` (before call, can stop/rewrite) · `PostToolUse` (after success, format/lint, can't stop) · `Stop` (refuse to end turn) · `SubagentStop` · `PreCompact`/`PostCompact` · `InstructionsLoaded` · `SessionStart`
- `PreToolUse` prints JSON + exit 0 → `permissionDecision`: allow / deny / ask (`defer` only for non-interactive `-p`)
- `updatedInput` rewrites the call, replaces the **whole** input object (keep unchanged fields)
- Redact > block: swap a live-looking secret for a placeholder, command still runs
- `SessionStart` + `compact` matcher → re-inject working-files summary after compaction (PostCompact can't return output to the conversation)

| Exit code | Effect |
|---|---|
| 0 | Success, stdout JSON parsed (plain stdout added to context on SessionStart/UserPromptSubmit/UserPromptExpansion) |
| 2 | Blocking error, stderr fed back to Claude |
| other (incl. 1) | Non-blocking, stderr logged |

- Notification and SessionStart can't be blocked (stderr shown, continues)

**Claude Code in Action: routines and headless**
- Spectrum: routines (low effort, Anthropic cloud) → headless `-p` → Agent SDK (high control, your code). Start with routines, move down only if you need control
- Routine = prompt + repo + connectors + trigger. Create at claude.ai/code/routines or `/schedule`
- Triggers: cron · HTTP POST to API endpoint · GitHub event (e.g. new PR)
- Limits: research preview · recurring at most hourly · fresh clone of default branch each run · pushes only to `claude/` branches by default
- Headless: `-p`/`--print`, stdin → stdout, pipes; skips auto-load of hooks, skills, plugins, MCP, CLAUDE.md (faster, explicit tools)
- JSON schema + JSON output → `structured_output` (use `jq`); `--resume <session-id>` for plan-then-execute; `--bare` for repeatable CI output
- Agent SDK (TS/Python): `query` function, stream messages, `allowedTools` controls actions

| Use | When |
|---|---|
| Routines | Default for recurring work, nothing to host |
| `-p` | Pipeline/data piped through scripts |
| `--bare` | CI needing identical results |
| Agent SDK | Work inside your own product |

**Claude Code in Action: GitHub Actions and Code Review**
- PR = main handoff point. Two routes: managed **Code Review** or self-configured **GitHub Action**
- Code Review: Anthropic-hosted via Claude GitHub app; admin enables it in Claude Code admin settings, picks repos and when it runs (PR opened / every push / `@claude review`)
- Posts inline comments on diff lines, severity-tagged, deduplicated, ranked, summary table in check run. Never approves/blocks PRs, no managed autofix, research preview (team/enterprise)
- Fix locally: `/code-review --fix` applies findings to working tree
- Action `anthropics/claude-code-action@v1`: custom CI (implement from comment, scheduled reports). Setup: `/install-github-app`
- Inputs: `anthropic_api_key` · `github_token` · `trigger_phrase` (default `@claude`) · `use_bedrock`/`use_vertex` · `prompt` · `claude_args`
- Examples: `@claude` on PRs/issues; cron daily rollup (+ `workflow_dispatch` for manual runs)
- Control the run via `claude_args`: `--max-turns` cap · non-prompting permission mode for unattended jobs · allowed tools limited to the job (read-only for reports)

| | Code Review | GitHub Action |
|---|---|---|
| Hosting | Anthropic-managed | Your CI |
| Purpose | PR review findings | Custom jobs, commits, comments |
| Approves/blocks | No | Depends on workflow |
| Autofix | None (use `/code-review --fix`) | Via the run |

**Claude Code in Action: trust it, verifying unsupervised runs**
- Core rule: **the less you watched, the more you verify** (watched session = glance; unattended/CI = reconstruct what happened)
- Keep unattended runs in **auto mode**, not bypass permissions. Classifier flags dangerous actions only, not code correctness → verification bar unchanged
- Diff over summary: `/code-review` to flag issues, then read `git diff` yourself. Planned files first, then anything outside the plan
- Tests = gate, not promise (via hooks): **Stop hook** runs tests, blocks turn end on failure · **PostToolUse hook** lints/type-checks after every edit · `exit 2` sends failure back so Claude fixes it
- Cold second opinion: fresh session or sub-agent with no memory of the build catches what the original run rationalized away
- Headless runs: verify by JSON result + exit code

| Compare | Difference |
|---|---|
| Summary vs diff | Summary = intent, may look tidy · diff = what really changed |
| Auto vs bypass | Auto still screens actions · bypass skips screening |
| Stop vs PostToolUse hook | Stop gates end of turn · PostToolUse checks each edit |
| Claim vs gate | "Tests passed" is a promise · hook running tests is verification |

**Claude Code in Action: plugins**
- Problem: a good `.claude` setup is hard to share (copy files, hope they stay in sync) → plugin = one installable, versioned unit
- Contains: skills, subagents, hooks, MCP configs; also LSP servers, background monitors, themes, narrow slice of `settings.json`
- Install: by name in a session + `/reload-plugins`; teams add a shared marketplace once (private marketplace for own org)
- **Read before install**: plugins run code with your privileges, hooks auto-fire on matching tool calls; review ≠ trust
- Coexist: plugins add, not replace. Hooks stack; skills/agents/commands namespaced `plugin-name:skill-name`
- Package your own: existing `.claude` dir already works (convention-based). `hooks/hooks.json`, `.mcp.json` at plugin root
- Manifest `.claude-plugin/plugin.json` optional, only `name` required, version it like a dependency
- Plugin `settings.json`: only agent key (promotes a subagent to main thread) and subagent status line key; rest ignored

| Compare | Difference |
|---|---|
| Copy files vs plugin | Out of sync, no version vs one version, one install |
| Direct vs marketplace install | By name vs resolved via shared source (discovery, updates) |
| Your hooks vs plugin hooks | Both fire on every match, neither replaces the other |
