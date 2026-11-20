# Cline

Cline (Apache-2.0) is a VS Code and JetBrains extension and a CLI. Both talk to any
OpenAI-compatible endpoint. Checked against extension v4.1.26 and CLI v3.0.74 (2026-10-26).

## Setup (extension)

1. Cline › **Settings** › API Provider: **OpenAI Compatible**.
2. Fill in the values from `configs/cline.json`:

```json
--8<-- "configs/cline.json"
```

- **Base URL**: `http://127.0.0.1:4000/v1`
- **API key**: your `LITELLM_MASTER_KEY`
- **Model ID**: `free/coding` (or `free/private` for code you can't share)
- **Context window**: leave it at 32768 unless you've trimmed the lane to large-context models.

## Setup (CLI)

```bash
npm i -g cline
cline auth      # pick the OpenAI Compatible provider; -b base URL, -k key, -m model
```

Use the same base URL, key and model as above. Settings live in `~/.cline/data/settings/`.

## Plan and Act models

The extension can use a different model for **Plan** and for **Act** mode. Put the strong model on
Plan and a cheap lane on Act. That's the [orchestration](orchestration.md) split inside one tool.

## Privacy

Telemetry is on by default, also with your own keys. It doesn't include code or prompts except
for requests to Cline's own providers. Turn it off in the extension's settings; for the CLI, set
`"telemetryOptOut": true` in `~/.cline/data/settings/global-settings.json`.

## Known problems

- Cline's system prompt is long. Small-context models in the chain may refuse or truncate.
- Cline uses its own XML-style tool format in plain text, so it works even when a model's native
  tool calling is weak, but small models still get the format wrong. Retry, or use plan mode for
  thinking and act mode for short edits.
- "Auto-approve" with a free model is risky: review each step.
