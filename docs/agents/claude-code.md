# Claude Code

LiteLLM serves the Anthropic Messages API (`/v1/messages`), so Claude Code can use the router
without any proxy of its own. Claude Code sends Anthropic-style requests; LiteLLM translates them
for each free provider and back.

## Setup

```bash
export LITELLM_MASTER_KEY=sk-...        # same value as in router/.env
source configs/claude-code.sh && claude  # bash / zsh
```

```fish
set -gx LITELLM_MASTER_KEY sk-...
source configs/claude-code.fish; and claude
```

The script sets:

```bash
--8<-- "configs/claude-code.sh"
```

Inside Claude Code, `/status` should show `http://127.0.0.1:4000` as the base URL. `/model` lists
the Opus/Sonnet/Haiku slots; they all map to router lanes.

To stop using the router, open a new shell (the variables only live in the one you sourced them in).

## Known problems

| Symptom | Why | What to do |
|---|---|---|
| "prompt is too long" or cut-off answers | Claude Code's system prompt and tools are large; some free models have 32K–128K context | `/clear` often; keep tasks small; drop small-context models from `free/coding` |
| Tool calls printed as text, or bad JSON | Model can't follow Anthropic tool format well after translation | Retry; the next provider in the chain may do better |
| Slow first answer | Fallback walked past several providers that were rate-limited | Check router logs; add keys for more providers |
| Thinking / extended reasoning errors | Free models don't support Anthropic thinking blocks | `drop_params: true` in the router already strips unsupported fields |

`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` stops Claude Code from sending telemetry and
background calls that would use up free quota.
