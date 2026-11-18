# opencode

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

## Known problems

- opencode relies on native tool calling. If a model returns tool calls as plain text, the router
  can't fix that; the next provider might, or pick a different lane.
- The `small_model` (`free/fast`) is used for titles and summaries, which spends quota too.
