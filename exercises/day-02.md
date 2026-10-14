# Day 02 exercises

## Ticket analysis (workshop)

- **Task:** For each of 5 trip-planner-api tickets, write a three-sentence analysis (what it asks, what is ambiguous, first step). Use Claude to find gaps and draft clarifying questions, then compare with a partner.
- **Source:** https://github.com/thanhtruong-agilityio/trip-planner-api/issues (#38, #39, #41, #42)

### Tickets

| # | Title | Reported by |
|---|---|---|
| [#38](https://github.com/thanhtruong-agilityio/trip-planner-api/issues/38) | Every chat turn fails after I set a different default model in .env | not stated |
| [#39](https://github.com/thanhtruong-agilityio/trip-planner-api/issues/39) | Changed an agent's model in admin, but some chats still use the old one | QA |
| [#41](https://github.com/thanhtruong-agilityio/trip-planner-api/issues/41) | My saved max tokens for an agent disappeared | not stated |
| [#42](https://github.com/thanhtruong-agilityio/trip-planner-api/issues/42) | Can't pick a newer model for Chitchat, the form rejects it | not stated |

### My analysis

| # | Asks | Ambiguous | First step |
|---|---|---|---|
| #38 | After changing the default model in `.env`, every chat turn fails, and the reporter wants either startup to reject the model or the turn to work, and to know whether the model name is correct. | It is unclear which model name the reporter set in `.env`, what the exact price error in the logs says, and whether a clear error from the API would be enough or the turn must work. | Reproduce it locally by setting a newer model in `MODEL_ROUTER_STD_TIER` and reading the router log, while asking the reporter for the exact value they used. |
| #39 | After QA changed the Respond agent's model in admin on staging, some chats still use the old model, and the reporter sees both models in Langfuse. | It is unclear which flows (create_trip, edit_trip) use the new model and which still use the old one, whether only the Respond agent is affected or all agents are, and whether a cached config explains why the old model persists. | In the Langfuse traces, list which model each flow used, and compare it with the time of the admin save and, if possible, with the cache TTL. |
| #41 | Stop saving one field in the admin form from resetting other fields, because changing only the model on Itinerary builder reset max tokens to the default. | Whether the reporter really left max tokens alone, whether it resets on every save or only sometimes, which other fields reset, and whether the colleague's report is the same case. | Reproduce it: set max tokens, change only the model, save, and check whether the value resets in the UI and in the stored data. |
| #42 | Allow any model name (for example gpt-4.1) for Chitchat in admin instead of the two allowed values, for an experiment this week. | Whether this is a bug or an intended allowlist, why only two values are allowed, and whether "any model" is needed or just gpt-4.1. | Find out why the form restricts the model to two values (code and history), then ask the reporter whether adding gpt-4.1 is enough. |

### Using Claude to find gaps

| Ver | Prompt | What was wrong / good |
|---|---|---|
| v1 | Here is a bug ticket from trip-planner-api. Write a three-sentence analysis:<br>1. Asks: what the ticket asks for<br>2. Ambiguous: what is unclear or missing<br>3. First step: the first thing you would do<br><br>Rules:<br>- Use only the ticket text below. Do not read the code yet.<br>- Do not guess a root cause. If you infer anything, mark it [GUESS].<br>- After the three sentences, list up to 5 clarifying questions for the reporter.<br><br>Ticket:<br><ticket> (#38, title and body) | Followed the rules: said "no code read", marked one [GUESS]. Too long: 2 to 3 sentences per field. Two inferences not marked ("unsupported model", "the router's known list"). Broader than me: asked about billing, retry, partial save, other tiers, previous value |
| v2 | | |
| v3 | | |

**Gaps**
- Claude found that I missed (#38): whether the failure happens before or after the OpenAI call, whether the turn is billed, retried or partly saved, whether only the std tier fails, the previous value, the full traceback
- Claude found that I missed (#39): chats opened before the change versus new chats, which users and instances, whether "different replies" means the new or the old model, whether other agents show the same mix, whether the admin screen keeps the new value after a reload
- I found that Claude missed (#38): a clear API error might be enough instead of making the turn work; ask the reporter in parallel while reproducing
- I found that Claude missed (#39): which flow (create_trip or edit_trip) uses which model, and a specific cache hypothesis (config cached with a TTL; the 24h value still needs checking in the code)

### Clarifying questions

| # | Mine | Claude's |
|---|---|---|
| #38 | Which model name did you set in `.env`? What is the exact price error in the logs? Is a clear error from the API enough, or must the turn work? | Which exact model name did you set, and what was the previous value? Can you paste the full log line and traceback? Do failed turns show as failed, and is anything saved to the trip or chat history? Does it hit every tier or only the standard one? Which outcome do you prefer: startup validation or a turn that works with a fallback? |
| #39 | Did you clear the cache or log out after changing the model? How do you know which model each chat used, and did you match each chat to its Langfuse trace? Which flow (create_trip or edit_trip) used the old model? | About what time did you save the change, and when did you last see the old model in a trace? Were the old-model chats already open before the change, or all new? Which model do the other traces show, and is it always the same? Do other agents show the same mix? Does the admin screen still show the new value after a reload? |

### Partner comparison

| # | Partner's analysis | Same | Different | Who caught what |
|---|---|---|---|---|
| #38 | Claude Code (ticket text only, no code): same two expected outcomes; more unknowns listed (before/after the OpenAI call, billing, retry, partial save); reproduce locally and capture log and traceback; 5 questions | Both saw the two outcomes the reporter did not choose, the missing model name and exact error, and reproduce locally as the first step | Claude Code listed far more unknowns and was longer; it left unmarked inferences. I kept three sentences and added "a clear error may be enough" and "ask the reporter in parallel" | Claude Code: billing, retry, partial save, tier scope, previous value, traceback. Me: clear-error option, parallel ask |
| #39 | Claude Code (ticket text only, no code): asks the change to apply to every chat; unknowns: how long it took, which chats (new or existing, users, instances), whether "different" means new or old model, whether it went away by itself; reproduce on staging with fresh chats and check Langfuse; 5 questions | Both saw that only some chats were affected, that more detail is needed on which chats, and that Langfuse traces are the first place to look | Claude Code added the new-versus-existing-chat and "different means which model" questions and only guessed at cache. I added flow, agent scope and a concrete TTL hypothesis, and compared trace times with the save time | Claude Code: chat age, instances, meaning of "different", other agents, admin reload. Me: flow, cache TTL |

### Claude Code analysis (`/analyze-ticket`, with code cross-reference)

#### Analysis of issue #38: "Every chat turn fails after I set a different default model in .env"

**Summary**

This ticket asks for an unpriced default model to either be rejected at startup or work, and for no OpenAI call to be made on a turn that is going to fail.

It is ambiguous on the exact `MODEL_ROUTER_STD_TIER` value, on why startup passed, and on whether "works" means adding a price or refusing the model.

My first step is to send the reporter the four questions below. While waiting, I'd read `app/core/model_router.py` lines 158-215 and the startup check in `get_model_router()` to see how startup could pass.

**Core**

| Field | Content |
|---|---|
| What | "every message I send in a trip chat now comes back as a failed turn", with a price error in the logs. "The OpenAI usage page shows calls for the failed turns". |
| For whom | A developer running locally (`fastapi dev`, Postgres via docker compose) who changes `MODEL_ROUTER_STD_TIER`. The billing exposure also applies to any deployment. |
| Done when | The reporter's text: "Either startup rejects the model, or the turn works." |
| Done when (proposed) | 1. A model with no price is refused before any provider call, so `await_count == 0`.<br>2. Startup fails with a clear error if the default tier model is unpriced. This is already true per the comment.<br>3. A per-agent override to an unpriced model is rejected at save time or refused before the call. (inferred)<br>4. The repro test `tests/core/test_model_router/test_unpriced_default_model_repro.py` passes. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Partial | Local `fastapi dev` and docker Postgres are given. The env var value, commit and restart method are missing. The comment's probe ran on `feat/update-docs @ ab6cab9`, not on this branch. |
| Steps to reproduce | Partial | The reporter gave none. The comment reproduces the billing half only. |
| Expected vs actual | Present | Both are stated. |
| Attachments (logs) | Missing | The price error and the startup logs are not pasted. |
| Related tickets / PRs | Missing | None linked. Branch `fix/39-agent-config-stale-cache` and its untracked `*_repro.py` tests look related. (inferred) |

**Codebase**

| Location | Relevance |
|---|---|
| `app/core/model_router.py:158` | `_invoke_once` runs the model call. |
| `app/core/model_router.py:215` | `_enforce_cost_cap` runs after the call, so the billing happens first. |
| `app/core/model_router.py:327-368` | `_call_cost_usd` raises `ModelPriceUnknownError` when the model has no price. |
| `app/core/model_router.py:378-388` | The streaming path only logs on `ModelPriceUnknownError`. This is a possible inconsistency. |
| `get_model_router()`, called from `app/main.py` | The startup guard on the default tier. I haven't read it yet. |
| `tests/core/test_model_router/test_unpriced_default_model_repro.py` | Untracked repro test. |
| `tests/schemas/test_agent_config_model_allowlist_repro.py` | Untracked repro test, covering the per-agent override path. |

**Assumptions**

- The price table is `MODEL_PRICES_PER_1K_USD`, and an unlisted model counts as unpriced.
- The "starts fine" half is explained by something other than the default tier. A per-agent override saved in the admin screen is the likeliest cause. (inferred)
- Refusing before the call is the desired fix, rather than guessing a price.

**Gaps (most blocking first)**

1. Why startup passed is unexplained. The comment's probe shows startup rejecting gpt-4.1, so the reporter's setup differs somehow.
2. The model name and error text are unknown. Without them the failing path can't be confirmed.
3. Scope is undecided. The ticket doesn't say whether the fix is "check price first", "validate overrides on save", or "add a price".
4. The streaming path is unclear. It only logs on a missing price, so it may still bill silently.

**Questions**

| # | Question | Ask |
|---|---|---|
| 1 | What exact value did you set for `MODEL_ROUTER_STD_TIER`? | Reporter |
| 2 | Can you paste the failed-turn log lines, including the model name in the price error, and the startup logs? | Reporter |
| 3 | Did you save a per-agent model override in the admin screen? | Reporter |
| 4 | Did `fastapi dev` restart fully or hot-reload? | Reporter |
| 5 | Should an unpriced model be refused before the call, or should the missing price be added to the table? | PO / dev lead |
| 6 | Should the streaming path also refuse an unpriced model before the call? | Dev lead |

I made no edits and posted no comments.

---

#### Analysis of issue #39: "Changed an agent's model in admin, but some chats still use the old one"

**Summary**

This ticket asks that, after an admin changes an agent's model, every chat uses the new model, not just some.

It is ambiguous on staging's real setup (`REDIS_URL`, number of tasks) and on how fresh a change must be. It also doesn't say whether "straight away" is a requirement.

My first step is to send QA/infra the questions below to confirm the cause on staging. Meanwhile I'd check whether commit `90a9b01` (30s TTL) already fixes this, since it says "Refs #39".

**Core**

| Field | Content |
|---|---|
| What | "I switched the Respond agent to gpt-5.6-sol in the admin screen… replies look different in some and unchanged in others. The Langfuse traces show both models." |
| For whom | QA/admins on staging, and any multi-process deployment. |
| Done when | The ticket states no criteria. |
| Done when (proposed) | 1. After an admin save, all processes use the new model within a stated time bound.<br>2. The repro test passes, or its expectation is updated to match the bound.<br>3. If a bound rather than immediate consistency is chosen, the admin screen or docs say so. (inferred) |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | Partial | Only "staging". Version, `REDIS_URL` and task count are not given. The repro comment notes it was run on `feat/update-docs @ ab6cab9`. |
| Steps to reproduce | Present | The comment has router-free steps with two resolvers and separate in-memory caches. This is a code-level repro, not a staging one. |
| Expected vs actual | Present | The ticket and the comment both give them. |
| Attachments (logs, screenshots, links) | Missing | The Langfuse traces are mentioned but not linked. |
| Related tickets / PRs | Partial | Commit `90a9b01` "Refs #39" is on the current branch, `fix/39-agent-config-stale-cache`. No PR is open yet. |

**Codebase**

| Location | Relevance |
|---|---|
| `app/core/agent_config_resolver.py` | `invalidate()` evicts only the local cache. The resolver caches with `AGENT_CONFIG_CACHE_TTL_SECONDS`. |
| `app/core/constants.py:322` | TTL is now 30. The repro comment says it was 24h. |
| `app/core/cache.py` (`_build_cache_service`) | Falls back to a per-process in-memory cache when `redis_url` is unset. |
| `app/services/agent_config_service.py` | `update_agent_override` saves and then invalidates. |
| `tests/core/test_agent_config_resolver.py` | Edited by `90a9b01`. |
| `tests/core/test_agent_config_resolver_multi_process.py` | Exists. It may be the repro test. The comment cites `test_agent_config_resolver_repro.py`, which is not in `tests/core`. |
| `tests/services/test_agent_config_service_repro.py` | Untracked repro test. |

**Assumptions**

- Staging runs more than one task or worker with `REDIS_URL` unset.
- A bounded stale window of 30s is acceptable. The existing commit already assumes this.
- Restarting the API would make the old model disappear. This is unverified.

**Gaps (most blocking first)**

1. Is the cause confirmed on staging? Neither `REDIS_URL` nor the task count is known.
2. What staleness is acceptable? The 30s TTL leaves a window. It's unknown whether the product needs instant propagation, for example through Redis in staging or pub/sub invalidation.
3. Is the work done? `90a9b01` changed the TTL. It's unclear whether the ticket is closed by that or needs more, such as a shared cache.
4. The repro test name doesn't match. The comment names `tests/core/test_agent_config_resolver_repro.py`, but that file isn't in `tests/core`.
5. "After lunch" implies a long window. That fits the old 24h TTL, but the reporter hasn't re-tested against a fix.

**Questions**

| # | Question | Ask |
|---|---|---|
| 1 | Is `REDIS_URL` set on staging, and how many API tasks or workers run? | QA / infra |
| 2 | Does restarting the API make both models stop appearing? | QA |
| 3 | Is a delay of up to 30s after an admin save acceptable, or must the change apply immediately? | PO |
| 4 | Should staging and production require Redis, so the shared cache removes the per-process problem? | Dev lead |
| 5 | Can you link the Langfuse traces showing both models? | QA |
| 6 | Where is the repro test the comment refers to? Is it `test_agent_config_resolver_multi_process.py`? | Reporter (comment author) |

I made no edits and posted no comments.

---

#### Analysis of issue #41: "My saved max tokens for an agent disappeared"

**Summary**

This ticket asks for saving one agent-config field (the model) to stop resetting the other saved fields, such as max tokens, to the default.

It is ambiguous on whether a partial save should keep unsent fields, how an admin clears an override on purpose, and which UI or client sent the request.

My first step is to run the PATCH repro below, then confirm with the reporter that the admin screen sends only the changed field.

**Core**

| Item | Detail |
|---|---|
| What | "I changed only its model. After saving, the token limit goes back to the default." Also: "It looks like saving one field wipes the others." |
| For whom | Admins using the agent-config screen. Reporter is "fairly sure" they didn't touch the field, and a colleague "saw the same". |
| Done when (proposed) | PATCHing only model leaves the saved max_tokens, temperature and provider unchanged.<br>There is still a defined way to clear a field back to the default.<br>A regression test covers the partial update. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | missing | No env, branch or build. |
| Steps to reproduce | partial | Set max tokens, then change only the model and save. No exact UI or API call. |
| Expected vs actual | present | The saved max tokens should survive and instead reverts to the default. |
| Attachments | missing | No request payload, screenshot or logs. |
| Related tickets / PRs | missing | No comments or links. |

**Codebase cross-reference**

The code explains the symptom, so this looks like a real bug and not user error. I haven't run it yet.

| File | Finding |
|---|---|
| `app/services/agent_config_service.py:94-98` | `update_agent_override` assigns all four fields unconditionally. Any field missing from the payload is None, which overwrites the saved value. |
| `app/schemas/agent_config.py:13-25` | Every field defaults to None, so "omitted" and "explicitly null" look the same after parsing. |
| `app/api/v1/admin/agent_configs.py:50` | The route is PATCH, but the service has full-replace (PUT) semantics. |
| `app/core/agent_config_resolver.py` | A None override falls back to the default, which matches the reported "back to default". |
| `tests/api/test_admin_agent_configs_routes.py:41` | The existing patch test doesn't cover a partial update. |

The likely fix is to apply only `payload.model_fields_set` in the service. That keeps omitted fields and still lets an explicit null clear one.

**Assumptions**

| Assumption | Why it matters |
|---|---|
| "Itinerary builder" is `AgentName.ITINERARY_BUILDER`, in `app/core/constants.py:185`. | It's the only match. |
| The UI sends only the changed field. | If it sends all fields, the cause is on the client side. |
| "Back to the default" means the override became None and the resolver fell back to the default. | I haven't confirmed this against the resolver. |

**Gaps (most blocking first)**

1. It's unknown whether the UI sends only model or the full form with max_tokens null.
2. The intended semantics are undefined: does omitted mean keep, and does null mean clear?
3. There is no confirmed repro, and the reporter admits "could be me".
4. The same bug affects the other three fields. The ticket mentions only max tokens.

**Questions to ask**

| # | Question | To |
|---|---|---|
| 1 | Does the admin screen send only the edited field or all four in the PATCH body? | Reporter / frontend dev |
| 2 | For PATCH, should an omitted field keep its value and an explicit null reset it to default? | PO / dev lead |
| 3 | Can you share the request payload (browser network tab) from a failing save? | Reporter |
| 4 | Is max_tokens the only field seen reverting, or also temperature and provider? | Reporter / colleague |

**First step**

Run `PATCH /admin/agent-configs/itinerary_builder` with `{"max_tokens": 4000}`, then with `{"model": "<priced model>"}`. Then GET the list. If `override.max_tokens` is back to null, the bug is confirmed. After that, send Q1 and Q2. I haven't changed any files, posted comments or contacted anyone.

---

#### Analysis of issue #42: "Can't pick a newer model for Chitchat, the form rejects it"

**Summary**

This ticket asks for the admin agent-config save to accept gpt-4.1 for Chitchat, or any model name, so the reporter can run a tone experiment this week.

It is ambiguous on whether the goal is "any model name" or just "add gpt-4.1". It also doesn't say what should happen to cost tracking for models without a known price.

My first step is to ask the PO and dev lead whether this rejection is a deliberate guard. If it isn't, the smallest change is adding gpt-4.1 and its price to the allowlist.

**Core**

| Item | Detail |
|---|---|
| What | "I tried to set the Chitchat agent to gpt-4.1 … the admin screen says the model must be one of two values." Asks: "Can we make it accept any model name?" |
| For whom | Admins using the agent-config screen. The reporter wants "a quick experiment this week", so the request is time-sensitive. |
| Observed / Expected | Observed: a 422 listing two allowed models. Expected: "The save succeeds." |
| Done when (proposed) | Saving gpt-4.1 for `chitchat_agent` returns 200 and `effective.model` shows it.<br>Calls with that model are priced and checked against the cost cap, with no `ModelPriceUnknownError`.<br>Models outside the allowed set are still rejected with a clear 422, unless the PO decides "any name" is wanted.<br>A test covers the new model. |

**Missing info**

| Item | Status | Note |
|---|---|---|
| Environment | missing | No env, branch or build. |
| Steps to reproduce | partial | The agent and model are named. The exact request or UI path isn't. |
| Expected vs actual | present | 422 vs success. |
| Attachments | missing | No payload or screenshot of the 422 body. |
| Related tickets / PRs | missing | None linked. |

**Codebase cross-reference**

This is not a bug. The 422 is deliberate and documented in the code.

| File | Finding |
|---|---|
| `app/schemas/agent_config.py:28-33` | `_model_is_priced` rejects any model not in `MODEL_PRICES_PER_1K_USD`. The message is "model must be one of [...]". |
| `app/core/constants.py:325-333` | The allowlist has only gpt-4o-mini and gpt-5.6-sol. The comment says a model "must be listed here before an admin can select it, so the cost cap always knows what a call costs". |
| `app/core/model_router.py:340-342` | An unpriced model raises `ModelPriceUnknownError` at call time. |
| `app/core/model_router.py:414` | Startup also checks that the standard tier is priced. |
| `app/core/constants.py:182` | `CHITCHAT_AGENT` is registered, so the agent itself is not the issue. |

Accepting any name would skip this guard. Every call would then fail at the cost cap, or the cap would have to be bypassed.

**Assumptions**

| Assumption | Why it matters |
|---|---|
| gpt-4.1 is a valid model on the project's OpenAI account. | I haven't verified it, and a price entry is useless otherwise. |
| The reporter wants this model only for Chitchat, not globally. | Overrides are per agent, so this should be fine. |
| The reporter doesn't have a code or deploy path of their own. | Adding a model is a code change and a deploy, not an admin action. |

**Gaps (most blocking first)**

1. It's unknown whether "any model name" is a requirement or just a way of saying "let me use gpt-4.1". This sets the scope: one new allowlist entry, or removing the cost guard.
2. We don't have gpt-4.1 per-1k input and output prices, which the allowlist entry needs.
3. It's unclear whether the cost cap should still apply to experimental models.
4. The ticket doesn't say whether the experiment needs a deploy this week, or whether a config or env path could avoid a code release.

**Questions to ask**

| # | Question | To |
|---|---|---|
| 1 | Do you need arbitrary model names, or is adding gpt-4.1 enough for this experiment? | Reporter / PO |
| 2 | Is the price allowlist a deliberate guard we keep, with a new model needing a price entry? | Dev lead |
| 3 | What are the current OpenAI per-1k input and output prices for gpt-4.1? | Dev lead / whoever owns billing |
| 4 | Should unpriced models be allowed with the cost cap skipped or estimated? | PO / dev lead |
| 5 | Is a deploy this week acceptable, or does the experiment need a no-deploy route? | Reporter |

**First step**

Send Q1 and Q2 today. If the answer is "just gpt-4.1", the smallest fix is one new entry in `MODEL_PRICES_PER_1K_USD`, once Q3 gives the prices, and a test in `tests/api/test_admin_agent_configs_routes.py` next to the existing unpriced-model rejection test. I haven't changed any files, posted comments or contacted anyone.
