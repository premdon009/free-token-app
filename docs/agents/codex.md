# Codex CLI

Codex speaks the OpenAI **Responses** API. LiteLLM serves `/v1/responses` and translates it to
chat completions for each free provider.

## Setup

Append `configs/codex.toml` to `~/.codex/config.toml`:

```toml
--8<-- "configs/codex.toml"
```

```bash
export LITELLM_MASTER_KEY=sk-...
codex --profile free
```

## Known problems

- Codex is tuned for OpenAI's own models. With free models it often stops early or repeats tool
  calls. Keep tasks short.
- If your Codex version complains about `wire_api = "responses"`, set it to `"chat"`; LiteLLM
  serves both.
- Reasoning settings (`model_reasoning_effort`) are ignored by most free models.
