# aider

aider (Apache-2.0) still works well, but development has slowed: the latest PyPI release is 0.86.2
(2026-02-12) and the last commit was in May 2026. It has no MCP support.

## Setup

```bash
cp configs/aider.conf.yml .aider.conf.yml          # or ~/.aider.conf.yml
export OPENAI_API_KEY=$LITELLM_MASTER_KEY
aider
```

```yaml
--8<-- "configs/aider.conf.yml"
```

`configs/aider.model.metadata.json` tells aider the lanes are free and how much context to assume,
so it doesn't warn about unknown models or show made-up costs. If you copy the config outside this
repo, change `model-metadata-file` to an absolute path.

## Architect and editor

`--architect` sends your request to the main model, which proposes a change. A second request then
asks the **editor** model (`--editor-model`) to turn that proposal into file edits. That's a
strong-plans, cheap-edits split in one command:

```bash
aider --architect --model <strong model> --editor-model openai/free/coding
```

If you don't set `--editor-model`, aider picks a default based on the main model, which may not be
a model you meant to pay for. Set it explicitly. The same goes for `--weak-model`, used for commit
messages and chat summaries; our config already points it at `free/fast`. See
[orchestration](orchestration.md).

## Tips

- aider's **whole** or **diff** edit formats need the model to repeat code exactly. Small models
  often fail; try `--edit-format whole` for short files.
- Use `/add` for only the files you need. A big repo map uses up the context window.
- `--model openai/free/private` for code you can't share.
- Analytics are opt-in; `--analytics-disable` turns off the question for good.
