# Day 11 AI-native SDLC

- **Date:** 2026-10-23
- **Trainee:** thanh.truong
- **Branch:** `training/day-11`

**Status:** The AI-native SDLC playbook — lessons 1-14 noted (course content complete).

---

## 1. Setup check

- [ ] Training repo cloned: https://github.com/thanhtruong-agilityio/claude-training

---

## 2. Courses

### The AI-native SDLC playbook

- [x] Introduction
- [x] Capture as intent.md
- [x] Requirements and design
- [x] Plan mode
- [x] The CLAUDE.md
- [x] Skills as Institutional Knowledge
- [x] Parallel sessions and subagents
- [x] Give Claude a Feedback Loop
- [x] Continuous Evals in CI
- [x] AI in the PR Review Loop
- [x] Hooks as Approval Gates
- [x] CI/CD integration and deployment
- [x] Closing the Loop on Metrics
- [x] Closing Thoughts and Resources

### Developer Checkpoint 3

- [x] One skill merged: `day-note` (#21)
- [x] One hook merged: `format-on-edit` + `notify-on-finish` (#29)
- [x] One MCP tool used end-to-end: GitHub MCP + Playwright (day 08), Claude in Chrome (day 11)
- [x] One review report acted on: `/code-review` on PR #35, 2 of 7 findings fixed, table on the PR
- [x] Role-day exercise: clinic-app browser test with Claude in Chrome, see [exercises/day-11.md](../exercises/day-11.md)
- [ ] PR #35 (archive/unarchive UI, ticket 09) merged: no CI checks and no human review yet

---

## 3. Key takeaways

**The AI-native SDLC playbook: introduction**
- Coding sped up, surrounding processes didn't (approvals, reviews, handoffs, policies still at human speed)
- Traditional SDLC = 6 stages (Plan, Design, Build, Test, Deploy, Maintain), roles own stages, handoffs via documents/tickets/sign-offs
- Code stops being the bottleneck → (1) bottleneck moves to plan, review/test, deploy (2) human-oriented controls stop fitting (line-by-line review) (3) governance cost rises (exceptions wait for meetings)
- Security example: teams sized for human output → agents either grow queues or ship under-reviewed code; regulated orgs can't accept either
- AI-native SDLC = continuous loop, AI at each point, automated handoffs, humans above the loop (direct + govern)
- Each stage ends by committing an artifact; next stage reads it. Early = Markdown (humans + agents); from Build = code + records. Commit history = audit trail
- 12 plays across the stages; each: what changes, how to start, steps, governance, measures; modular with prerequisites
- Adoption is gradual: prompt each step by hand first; goal = each accepted artifact triggers the next gate

| Stage | Traditional | AI-native |
|---|---|---|
| Plan | Committees/workshops, hand-written | Claude synthesizes pain points into `intent.md` |
| Design | Analysts write specs, designers interpret | One agent session, versioned skills |
| Build | Hand-written tests/code, docs later | AI generates tests/code; knowledge in `CLAUDE.md` + skills |
| Test | QA gates at stage boundaries | Continuous evals during implementation |
| Deploy | Humans review every line | Layered agentic review; humans on regulated/critical code; hooks as approval gates |
| Maintain | Humans watch production | Agents monitor; breached controls feed a new `intent.md` |

**The AI-native SDLC playbook: capture as intent.md** (Stage 1: Plan)
- Intent enters via a person's idea, a filed ticket, or an incident surfaced by an alert (links to Stage 6: Maintain)
- Idea → conversation with Claude → Markdown proto-spec saved as `intent.md`. Originator keeps ownership in own terms; **product owner always reviews/corrects** before commit
- Setup once: technical team member creates the **intent home** (`intent/` folder in product repo; dedicated repo only if intent spans many repos; directory in a monorepo) and decides who can write. Non-engineers use a version-control connector (e.g. GitHub) via claude.ai or Cowork, no Git needed
- Steps: describe problem in own words → Claude brainstorms (analyst questions) → generate `intent.md` from org template (problem, proposed outcome, affected users/systems, constraints, open questions) → correct → commit
- Prerequisites: none. Needs: Claude access for non-engineers, agreed template (can live in a skill), shared intent home, connector
- Governance: Git history = evidence (author, timestamp, revisions); accept/reject recorded as merge or closing review → Stage 2: Design
- Measure: leading = time from first conversation to committed `intent.md` (weeks → hours); lagging = survival rate + number of `intent.md` changes after first `spec.md`

| | Traditional | AI-native |
|---|---|---|
| Path | Backlog, user stories, points, refinement meetings | Originator brainstorms with Claude → `intent.md` |
| Ownership | Transfers at each handoff | Stays with originator |
| Repeated processes | Meetings, manual steps | Encoded as skills |

**The AI-native SDLC playbook: requirements and design** (Stage 2: Design)
- Approved `intent.md` → Claude produces `spec.md` (requirements + design in one session), constrained by org **skills** (brand, security, compliance, UX). Goal: spec engineering can plan against, risky areas flagged in advance
- Product owner **reviews, doesn't write**: checks spec solves the stated problem, open questions from `intent.md` answered or carried forward. **Flagged concerns** (what an analyst would escalate, e.g. conflicting policies) resolved with each policy owner before engineering sees it
- Front-end: owner mocks up in Claude Design (beta) from `intent.md`, iterates, exports to Claude Code
- `intent.md` + `spec.md` committed together = record of what was asked and decided. Human decides go-ahead (consult tech lead for higher risk); accepting starts plan mode in Stage 3
- Prerequisites: `intent.md` + policies as skills. Needs: product owner with Claude, no engineering skill
- Execute: manual prompt (reference intent, state constraints, require flagged concerns) → save as org slash command → automate: merge of `intent.md` triggers non-interactive job that opens a PR with `spec.md` (CI/CD play, Stage 5)
- Governance: live policies applied while writing, not found in review weeks later; spec, prompt and skill versions logged in version control
- Measure: leading = time from `intent.md` commit to `spec.md` commit; lagging = `spec.md` commits after first `plan.md` commit (rework)

| | Traditional | AI-native |
|---|---|---|
| Phases | Requirements, then design | One prompted session |
| Teams | Analysts, then designers | Product owner + Claude |
| Constraints | Applied late, found in review | Skills applied while writing |
| Accountability | Via separation | Review, sign-off, logging |

**The AI-native SDLC playbook: plan mode** (Stage 3: Build)
- Start Claude Code sessions in **plan mode**: Claude reads the codebase but can't edit until the plan is accepted → design review enforced by the mode itself
- Give it `intent.md` + `spec.md`; ask for a plan naming files to change, order of work, tests that prove it
- Interrogate: what could this break? riskiest step? which alternatives rejected? Iterate until **self-contained** (an engineer who never saw the chat could implement it)
- Commit as `plan.md` (audit trail; Stage 5 PR review checks the diff against it). Solid plan → often one-pass implementation. If code diverges, update `plan.md` in the same commit (hook can enforce)
- Governance: plans, revisions, approvers logged; routine = engineer approves, higher risk = tech lead/architect
- Measure: leading = first-pass merge rate, time from plan approval to merge; lagging = rework cycles, how closely merged diff matches `plan.md`
- **Auto mode**: engineer approves plan, Claude applies without per-edit prompts. Needs guardrails: tuned `CLAUDE.md`, policy skills, safety hooks, runnable tests. Review shifts to artifacts after longer sessions. With worktrees → parallel work, Stage 6 autonomous loop
- Prerequisites: intent artifact if exists, `CLAUDE.md` helps. Needs: Claude Code with repo access

| | Traditional | AI-native |
|---|---|---|
| Start | Read design, start coding | Written plan in plan mode |
| Details | In engineer's head / ticket comment | Reviewable plan |
| Review | Finished diff only | Plan before code exists |
| Rework cost | High (late) | Low (edit the plan) |
| Record | Informal | `plan.md` |

- **Legacy systems** (Jira, requirements tools, Figma, change boards): one source of truth per artifact. (1) Repo as truth: Markdown authoritative, legacy tools reference commits (2) Legacy as truth: Jira/ServiceNow authoritative, Markdown = working copy, Claude reads at session start and writes back via MCP connector (3) Linkage minimum: artifacts cite record ID, legacy records carry commit SHA (two sources of truth, OK during transition)


**The AI-native SDLC playbook: CLAUDE.md** (Stage 3: Build)
- `CLAUDE.md` = context a new joiner needs, read by Claude every session; moves tribal/wiki knowledge into a file
- Steps: run `/init` → trim to day-one needs (build/test/lint commands, key conventions, repeated mistakes) → commit at repo root (changes via PR review) → mistake-twice rule: add the correction → keep under one page (stale text wastes context)
- Example (payments service): Commands, Conventions (`BigDecimal` for money, no new Lombok, every endpoint needs integration test), Architecture (generated Kafka classes never hand-edited), Things Claude Gets Wrong (don't bump platform-owned deps, legacy package frozen)
- Governance: version-controlled, auditable, code owners approve changes
- Measure: leading = repeated mistakes CLAUDE.md should prevent (via Git history); lagging = time to new member's first merged PR


**The AI-native SDLC playbook: skills as institutional knowledge** (Stage 3: Build)
- Write a skill for knowledge that must be applied **consistently** (security standard, API convention, brand rule). Project-how-it-works → `CLAUDE.md`/prompt, not a skill
- Steps: pick one inconsistently enforced policy → write `SKILL.md` (frontmatter = when to trigger, body = what to do; from policy owner's source of truth) → place at `.claude/skills/<name>/` or ship via plugin → test triggering with several phrasings → on policy change update + owner approves → engineers get it next session
- Example: `secure-api-review` (gateway auth except health route, validate vs OpenAPI + reject unknown fields, audit event on state changes, no PII in logs; runs checker script)
- Governance: skill = **advisory control**; policy that must always hold needs **deterministic backstop** (hook or PR check). Skill invocations in session traces; skill changes reviewed like code
- Measure: leading = time from policy approval to merged skill update; lagging = PR review findings citing the policy (should trend to 0; if not, skill isn't triggering or text drifted)
- **Build-phase hooks**: block edits to protected paths (generated/frozen code), run formatter/linter after each edit, keep credentials out of diff, enforce skill policy. Keep fast, per changed file; full test suite at commit/PR time. Human-approval hooks belong in Stage 5 Deploy (no person on critical path of parallel sessions)


**The AI-native SDLC playbook: parallel sessions and subagents** (Stage 3: Build)
- **Parallel session** = separate Claude Code instance, own task, own Git worktree; sessions don't know each other, engineer steers. **Subagent** = scoped helper inside one session (own context window + tool limits) for recurring jobs
- Traditional: one task at a time. AI-native: several sessions in worktrees; engineer orchestrates, later builds/monitors loops
- Prereqs: `CLAUDE.md`; Stage 4 feedback loop (self-verifying sessions need less supervision). Infra: Git repo (worktrees), permission settings tuned to avoid prompts for safe commands
- Steps: split work into tasks touching different files (use plan from plan mode; shared files = sequential in one session) → one worktree per task → start with 2-3 sessions (limit = what you can review well) → repeated jobs → subagents in `.claude/agents/*.md` (name, when-to-use description, allowed tools), committed to Git. Examples: code simplifier, verifier, researcher
- Example `verifier.md` (tools: Bash, Read): start app, exercise changed behavior + two nearest flows, report what ran/observed/mismatches vs plan; reports only, no fixes
- Governance: controls in repo config (hooks, permissions apply to all sessions); actions logged and attributed to the engineer
- Measure: leading = concurrent sessions per engineer (OpenTelemetry export) while review quality holds, share of day steering vs waiting; lagging = changes merged per engineer/week + rework rate


**The AI-native SDLC playbook: give Claude a feedback loop** (Stage 4: Test)
- Let Claude verify its own work (tests, build, screenshot diff) so it fixes mistakes before an engineer reviews → engineer gets output that already passed, no late-signal bottleneck (traditional: CI minutes later, testers days, prod weeks)
- Loop ≠ verifier subagent: loop runs throughout the task; verifier = fresh-context final check
- Infra: test suite + build each runnable locally with one command; UI work needs browser/screenshot tool (e.g. via MCP)
- Steps: wrap checks in one command exiting non-zero (`make test`) → list commands + healthy output in `CLAUDE.md` Commands → measurable target (named tests pass, screenshot matches mock, endpoint 200 with new field) → bug fix: write failing repro test, commit, make it pass without editing test → UI: implement, screenshot, compare, adjust (2-3 rounds) → "done" = run tests + show output (CLAUDE.md rule) → protect loop: hook blocks test-file edits during fix tasks, or reject diffs touching tests
- Example CLAUDE.md block: `make build` → "Build succeeded."; `make test` all green, never skip/delete failing tests; `make lint` zero warnings; paste output; fix code not test
- Governance: enforced via hooks (verify before done, no test edits); evidence = literal toolchain output; logs = transcript via OpenTelemetry + PR check run; code owner reviews intent/risk
- Measure: leading = first-pass CI success rate of agent changes; lagging = review time per PR (should fall), change failure rate


**The AI-native SDLC playbook: continuous evals in CI** (Stage 4: Test)
- Evals = AI-native stage-gate QA: suite runs when agent config changes (new model, rewritten prompt, `CLAUDE.md`/skills/hooks) → shows if agent still meets the quality bar. Living asset: as models improve, cases stop discriminating → add new cases from monitoring. Some teams prefer offline evals on fixed cadence
- Prereqs: `CLAUDE.md` + feedback loop (lesson 8). Infra: CI that runs Claude Code non-interactively; API key with eval budget
- Steps: platform engineer collects 20-50 real tasks with expected outcomes → each becomes an eval (prompt + checks: tests pass, lint clean, behavior unchanged, policy followed) → run non-interactively in CI on schedule + when `CLAUDE.md`/skills/hooks change (config steers agent → regression-test like code) → gate config changes (skill change lowering pass rate is reviewed before merge) → every production incident becomes an eval, written by owning team, kept as regression test
- Example `agent-evals.yml` (GitHub Actions): triggers on PRs touching `CLAUDE.md` / `.claude/` + daily schedule; install Claude Code CLI; loop over `evals/*.json`, run non-interactive with eval prompt, tools limited to read, edit, `make test`; `check.sh` decides pass; API key from repo secrets
- Governance: pass-rate threshold enforced as merge check; runs logged for comparison over time; config owner team approves
- Measure: leading = eval pass rate over time, time for incident to become permanent eval; lagging = regressions caught in CI vs found in production


**The AI-native SDLC playbook: AI in the PR review loop** (Stage 5: Deploy)
- Claude reviews incoming PRs against org policy and addresses review comments on its own PRs → humans focus on intent and risk. Traditional: PR waits for reviewer, quality varies with load. AI-native: every PR gets identical review passes, findings ranked by severity
- Prereqs: updated `CLAUDE.md`, skills (if passes enforce policy), defined subagents. Infra: managed Code Review (research preview, admin enables) or `claude-code-action` in own CI; Bedrock/Vertex/Foundry if needed; branch protection requiring code owner approval
- Steps: choose setup (managed = fastest; action = pipeline control / own cloud agreement) → tech lead writes `REVIEW.md` (passes: bugs, security, compliance with `spec.md`/`plan.md`/design; Important vs Nit; skips) → human threshold: findings never approve/block alone, code owner still approves; severity counts in check run are machine-readable if merges gated → fix loop: `@claude` on a comment fixes and pushes (`@claude review` = fresh review in managed); babysit own PRs to green via custom slash command → repeat finding goes into `CLAUDE.md` (reviews also flag outdated `CLAUDE.md`) → tune monthly (rate findings, cap nits, exclude generated paths and CI-enforced items)
- Example `REVIEW.md`: 3 passes tagged per finding; Important = breaks behavior / leaks data / breaches policy; max 5 nits then count; skip `src/gen/` and CI-enforced
- Governance: separation of duties (author agent can't approve); uniform policy; PR history = audit record; human approval via branch protection
- Measure: leading = time to first review (minutes), share of comments resolved without human touching branch; lagging = defects/vulns caught before merge vs escaped to prod


**The AI-native SDLC playbook: hooks as approval gates** (Stage 5: Deploy; hooks also used in Stages 3-4)
- Build-phase hooks allow/block without a human; a hook can also **ask** = pause until a specific person approves → needed for release gating. Other uses: block edits to migrations/infra without change ticket (Stage 3), block test-file edits in fix tasks (Stage 4)
- Infra: written list of approvals the change process requires
- Steps: leadership + change mgmt + compliance define gates (change sign-off, release authorization, protected paths) → platform engineer writes hook scripts that allow/ask/block before Claude acts → place by scope: team hooks in `.claude/settings.json` (committed), non-negotiable in managed settings (platform/IT admin, engineers can't disable) → blocks explain themselves (reason + path to approval in Claude's output)
- Example: `PreToolUse` hook matching Bash runs gate script; if command has "deploy" + "production" and `RELEASE_APPROVAL` empty → message + exit 2 (blocks, message to Claude); else exit 0
- Managed settings (regulated enterprise, via MDM/admin console): deny list (secrets, web fetch/curl/wget), allow list for routine cmds (git, make build/test/lint), bypass mode disabled, only managed permission rules; OS sandbox with network domain allowlist (Claude Code won't start if it can't initialize); deny SSH/AWS credential reads, strip token from sandbox env; only managed hooks run; sideloading rejected, approved-marketplace plugins + platform-approved MCP servers only; minimum version floor. Starting point only: each deny removes capability, balance by data classification
- Governance: gate applies to every user/session; allow/block decisions logged with timestamps; gate defines what counts as approval
- Measure: leading = wait time at each gate (hook decisions exported to OpenTelemetry); lagging = gate violations reaching production before vs after hooks


**The AI-native SDLC playbook: CI/CD integration and deployment** (Stage 5: Deploy)
- Four parts: run Claude non-interactively in CI/CD; sandbox agent jobs; expose deploy tooling via MCP; rehearse rollback. Traditional: deterministic scripts, judgment tasks (flaky test triage, changelog, broken build diagnosis) wait for a human, runbooks under pressure. AI-native: Claude does judgment steps in sandbox with scoped creds; workflow that wrote/tested a change can ship and roll it back within per-environment gates
- Prereqs: AI in the PR review loop; hooks as approval gates (gates must exist before automation speeds passage). Infra: CI with `claude-code-action` or any runner able to call `claude -p`; Claude API or Bedrock/Foundry/Vertex; MCP server per deploy target; sandbox profile with no standing prod credentials
- Steps: start read-only (`claude -p` for triage/summary/changelog) → add write steps behind existing gates (fix lint, update generated docs, `@claude` review comments; changes arrive as PRs under branch protection, agent can't push to main) → sandbox: containers, network policy, short-lived scoped tokens, no prod creds → deploy/status/rollback as MCP tools scoped per environment (allowlist, not shell script with embedded creds) → tier autonomy: dev = deploys freely, staging = intermediate, production = agent prepares release, release manager authorizes, hook enforces → rehearse rollback: single command the agent can run, practiced in staging (Stage 6 relies on rollback when a control band is breached)
- Example: "Triage failed build" step, runs only when a prior step fails; `claude -p` reads build log, identifies likely cause, classifies flaky vs real, writes 3-line summary to a triage file for the PR thread
- Governance: agent may act up to the production gate but cannot pass it; branch protection routes output into PRs; prod deploy hook blocks until named release manager authorizes; non-interactive runs use agent's own identity so logs separate agent from engineer; per-environment permission tiers
- Measure: leading = share of pipeline failures triaged without paging a human; lagging = DORA metrics


**The AI-native SDLC playbook: closing the loop on metrics** (Stage 6: Maintain)
- Earlier stages need a person to start them; Stage 6 runs Claude **headless/autonomously** so the loop closes unprompted (e.g. monitoring agent opens `intent.md` on a bug ticket → requirements → plan → build → test → review). Independent **confidence gate** between stages (deterministic check or adversarial reviewing agent) decides: move forward or go to human
- Traditional: reactive, missed alerts, backlogs, post-mortem actions never reach code. AI-native: triggered by control-band breach / ticket / chat message / schedule; Claude diagnoses, acts only via gated routes, records findings as `intent.md`; human triages and reviews
- Prereqs: `intent.md`, Claude-accelerated PR reviews, hooks as action boundaries, rollback path. Infra: metrics store (Prometheus / CI API), repo read access, non-interactive Claude Code in CI or Agent SDK service for webhooks
- Steps: choose one metric with stable rolling baseline (CI test failure rate, post-deploy 5xx, PR cycle time) → deterministic detection script (rolling mean/stddev + Western Electric rules → slow drift and spikes; version controlled, unit tested, no model) → tiers in `bands.yaml`: 1σ log only, 2σ read-only diagnose, 3σ act only via PR into review gate or pre-approved runbook → trigger layer (scheduled workflow, monitoring webhook, in-network cron); Claude stateless + non-interactive in CI step or Agent SDK in sandboxed container → record diagnosis as `intent.md` (anomaly + evidence, proposed outcome, affected systems, open questions) → triage queue: service owner/on-call fixes now, schedules, or dismisses (dismissals tune bands); product-facing → product owner → add an eval per incident once fix ships
- Examples: CI failure rate 3σ → quarantine flaky test or revert PR (review gate decides); post-deploy 5xx 3σ + recent deploy → trigger existing rollback pipeline; PR cycle time drift → report to eng leadership (works for process metrics too)
- Governance: tier boundaries from version-controlled config; permissions/managed settings deny prod access; invocations/findings/triage logged; runbooks pre-approved; changes through standard PR review
- Measure: leading = time from band breach to `intent.md` in triage queue vs old incident-to-post-mortem; lagging = share of findings that become merged fixes, repeat incidents of same class (should decline as evals grow)
- **Claude Tag** (public beta, Slack): Claude as channel member with own identity = first responder to incidents; conversation + knowledge stay in channel (auditable); via MCP confirms metric back to baseline in thread, writes post-mortem to version-controlled lessons file; also triages tagged tickets (small fixes → PR, larger → `intent.md` for Stage 1)


**The AI-native SDLC playbook: closing thoughts and resources**
- Better models + agent harnesses → transform the whole SDLC, not just code writing; human judgment stays central; account for enterprise governance/regulation. Guide = practices Applied AI team uses daily with customers
- Resources for platform team, roughly rollout order: org setup → settings (precedence, managed-only keys) → server-managed settings (admin console) → permissions → sandboxing → hooks → skills → plugins/private marketplaces → managed MCP → enterprise deployment (Bedrock/Vertex/Foundry) → network config → monitoring (OpenTelemetry) + analytics → Compliance API → security model (docs at code.claude.com/docs)

Source: Introduction · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/introduction
Source: Capture as intent.md · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/capture-intent
Source: Requirements and design · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/requirements-and-design
Source: Claude Code plan mode as the default starting point · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/plan-mode
Source: The CLAUDE.md · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/claude-md
Source: Skills as Institutional Knowledge · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/skills-as-institutional-knowledge
Source: Parallel sessions and subagents · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/parallel-sessions-and-subagents
Source: Give Claude a Feedback Loop · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/give-claude-a-feedback-loop
Source: Continuous Evals in CI · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/continuous-evals-in-ci
Source: AI in the PR Review Loop · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/ai-in-the-pr-review-loop
Source: Hooks as Approval Gates · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/hooks-as-approval-gates
Source: CI/CD integration and deployment · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/ci-cd-integration-and-deployment
Source: Closing the Loop on Metrics · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/closing-the-loop-on-metrics
Source: Closing Thoughts and Resources · The AI-native SDLC playbook — https://academy.claude.com/courses/ai-native-sdlc-playbook/closing-thoughts-and-resources
