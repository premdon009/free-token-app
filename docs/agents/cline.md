# Cline

Cline (VS Code extension) talks to any OpenAI-compatible endpoint.

## Setup

1. Cline › **Settings** › API Provider: **OpenAI Compatible**.
2. Fill in the values from `configs/cline.json`:

```json
--8<-- "configs/cline.json"
```

- **Base URL**: `http://127.0.0.1:4000/v1`
- **API key**: your `LITELLM_MASTER_KEY`
- **Model ID**: `free/coding` (or `free/private` for code you can't share)
- **Context window**: leave it at 32768 unless you've trimmed the lane to large-context models.

## Known problems

- Cline's system prompt is long. Small-context models in the chain may refuse or truncate.
- Cline uses its own XML-style tool format in plain text, so it works even when a model's native
  tool calling is weak, but small models still get the format wrong. Retry, or use plan mode for
  thinking and act mode for short edits.
- "Auto-approve" with a free model is risky: review each step.
