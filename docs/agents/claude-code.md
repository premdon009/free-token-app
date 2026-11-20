# Claude Code

LiteLLM serves the Anthropic Messages API (`/v1/messages`), so Claude Code can use the router
without any proxy of its own. Claude Code sends Anthropic-style requests; LiteLLM translates them
for each free provider and back. Claude Code itself is proprietary (Anthropic's Commercial Terms);
this page was checked against v2.1.329 (2026-11-19).

!!! warning "Unsupported by Anthropic"
    Anthropic's gateway docs say it "doesn't support routing Claude Code to non-Claude models
    through any gateway". The router setup works, but you're on your own when something breaks.

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

## The router replaces your subscription login

Once `ANTHROPIC_AUTH_TOKEN` (or `ANTHROPIC_API_KEY`, or an `apiKeyHelper`) is set, Claude Code
sends that credential instead of your claude.ai login. Every request then goes to the router,
including the Opus slot. You can't keep the subscription for the main model and send only some
requests to the router in the same session. To keep the subscription as the orchestrator, give it
a delegate tool instead; see [orchestration](orchestration.md).

## Which model does what

| Setting | What it controls |
|---|---|
| `ANTHROPIC_MODEL` | The model the session starts with |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`, `_SONNET_MODEL`, `_FABLE_MODEL` | What the `opus`, `sonnet` and `fable` aliases resolve to. `opusplan` uses the Opus slot in plan mode and the Sonnet slot otherwise |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | The `haiku` alias, **and background work such as session titles**. Unset, those calls ask the router for a Haiku name it doesn't serve |
| Subagent `model:` frontmatter | `sonnet`, `opus`, `haiku`, `fable`, a full model ID or `inherit` |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Subagents with no `model:` of their own. It doesn't change the built-in Explore and Plan subagents |
| `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` | Forces `CLAUDE_CODE_SUBAGENT_MODEL` on every subagent, ignoring their `model:` (v2.1.257+) |

The order for a subagent is: the model passed for that one call, then its `model:` frontmatter,
then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model. To run exploration cheaply, define your own
subagent named `Explore` with `model: haiku`; it overrides the built-in one.

## Known problems

| Symptom | Why | What to do |
|---|---|---|
| "prompt is too long" or cut-off answers | Claude Code's system prompt and tools are large; some free models have 32K–128K context | `/clear` often; keep tasks small; drop small-context models from `free/coding` |
| Tool calls printed as text, or bad JSON | Model can't follow Anthropic tool format well after translation | Retry; the next provider in the chain may do better |
| Slow first answer | Fallback walked past several providers that were rate-limited | Check router logs; add keys for more providers |
| Thinking / extended reasoning errors | Free models don't support Anthropic thinking blocks | `drop_params: true` in the router already strips unsupported fields |
| "Unexpected value(s)" or "Extra inputs are not permitted" | Pre-release `anthropic-beta` fields the gateway rejects | `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` |
| Remote Control is gone | Since v2.1.196 it turns off when the base URL isn't `api.anthropic.com` | Expected; use a normal session |

## Privacy and quota

`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` (set by the script) stops most telemetry and
background calls that would use up free quota. It also turns off auto-updates. For finer control:
`DISABLE_TELEMETRY=1`, `DISABLE_ERROR_REPORTING=1`, `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1`.
