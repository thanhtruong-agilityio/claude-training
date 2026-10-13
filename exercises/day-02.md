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
| #41 | | |
| #42 | | |

### Partner comparison

| # | Partner's analysis | Same | Different | Who caught what |
|---|---|---|---|---|
| #38 | Claude Code (ticket text only, no code): same two expected outcomes; more unknowns listed (before/after the OpenAI call, billing, retry, partial save); reproduce locally and capture log and traceback; 5 questions | Both saw the two outcomes the reporter did not choose, the missing model name and exact error, and reproduce locally as the first step | Claude Code listed far more unknowns and was longer; it left unmarked inferences. I kept three sentences and added "a clear error may be enough" and "ask the reporter in parallel" | Claude Code: billing, retry, partial save, tier scope, previous value, traceback. Me: clear-error option, parallel ask |
| #39 | Claude Code (ticket text only, no code): asks the change to apply to every chat; unknowns: how long it took, which chats (new or existing, users, instances), whether "different" means new or old model, whether it went away by itself; reproduce on staging with fresh chats and check Langfuse; 5 questions | Both saw that only some chats were affected, that more detail is needed on which chats, and that Langfuse traces are the first place to look | Claude Code added the new-versus-existing-chat and "different means which model" questions and only guessed at cache. I added flow, agent scope and a concrete TTL hypothesis, and compared trace times with the save time | Claude Code: chat age, instances, meaning of "different", other agents, admin reload. Me: flow, cache TTL |
| #41 | | | | |
| #42 | | | | |

---

## Role-play: reporter and dev

- **Task:** In pairs, one plays the reporter and one the dev. The dev asks the clarifying questions, the reporter answers only what the ticket author would know.
- **Pair:**
- **Tickets played:**

| Question I asked | Answer | Useful? Why |
|---|---|---|
| | | |

- **Question that worked best:**
- **Question that was too vague:**

### Where AI surprised me

**Good**
-

**Bad**
