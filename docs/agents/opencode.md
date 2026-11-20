# opencode

opencode (MIT, now at [anomalyco/opencode](https://github.com/anomalyco/opencode)) has two release
lines: **2.x** (v2.3.2 on 2026-11-18) and **1.19.x** (v1.19.6 on 2026-11-17, still labelled
"Latest" on GitHub). Our config works in both.

## Setup

Copy `configs/opencode.json` to `opencode.json` in your project root (or merge it into
`~/.config/opencode/opencode.json`), export the key and start:

```bash
export LITELLM_MASTER_KEY=sk-...
opencode
```

```json
--8<-- "configs/opencode.json"
```

`/models` inside opencode lists the lanes as `free-token/free/coding` and so on.

## opencode 2

opencode 2's migration guide says "the V1 config format remains supported": it reads the same
files and converts V1 fields in memory. So `configs/opencode.json` loads unchanged. If you write
native V2 config instead:

| V1 (our config) | V2 |
|---|---|
| `provider.<id>` with `npm` and `options.baseURL` | `providers.<id>` with `package` and `settings.baseURL` |
| `agent.<name>` | `agents.<name>`, with `prompt` renamed `system` |
| `small_model` | `agents.title.model` (the hidden `title` agent) |
| `mcp.<name>` | `mcp.servers.<name>` |

Don't mix the two formats inside one provider or agent entry. V1 plugins don't run in V2.

## More than one model

Each agent can have its own `model`. A subagent with no model uses its parent session's model.
So a strong primary agent can hand bounded tasks to a subagent on `free/coding`. See
[orchestration](orchestration.md).

## Known problems

- opencode relies on native tool calling. If a model returns tool calls as plain text, the router
  can't fix that; the next provider might, or pick a different lane.
- The `small_model` (`free/fast`) is used for titles and summaries, which spends quota too.
  Without it, opencode uses a cheaper model from the same provider if there is one, otherwise the
  main model. Our config sets it so those calls stay on the router.
