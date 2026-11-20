# Codex CLI

Codex speaks the OpenAI **Responses** API. LiteLLM serves `/v1/responses` and translates it to
chat completions for each free provider. Codex is Apache-2.0; this page was checked against
rust-v0.171.0 (2026-11-20).

## Setup

Since Codex 0.134.0, a profile is its own file, `~/.codex/<name>.config.toml`, laid over
`~/.codex/config.toml`. Codex no longer reads `[profiles.<name>]` tables inside `config.toml`. Save
`configs/codex.toml` as `~/.codex/free.config.toml`:

```toml
--8<-- "configs/codex.toml"
```

```bash
cp configs/codex.toml ~/.codex/free.config.toml
export LITELLM_MASTER_KEY=sk-...
codex --profile free
```

If you added the old `[profiles.free]` table to `config.toml` earlier, delete it.

## More than one model

- `review_model` sets the model that `/review` uses, so a cheap lane can do a first-pass review.
- `agents.default_subagent_model` sets the model for subagents.

See [orchestration](orchestration.md) for how to split work between a strong and a cheap model.

## Privacy

Set `analytics.enabled = false` to turn off OpenAI analytics, and `feedback.enabled = false` to
turn off the feedback prompt.

## Known problems

- Codex is tuned for OpenAI's own models. With free models it often stops early or repeats tool
  calls. Keep tasks short.
- Codex no longer accepts `wire_api = "chat"`; it only speaks `responses`, which the router serves.
- Reasoning settings (`model_reasoning_effort`) are ignored by most free models.
