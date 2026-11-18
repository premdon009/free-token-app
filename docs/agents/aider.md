# aider

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

## Tips

- aider's **whole** or **diff** edit formats need the model to repeat code exactly. Small models
  often fail; try `--edit-format whole` for short files.
- Use `/add` for only the files you need. A big repo map uses up the context window.
- `--model openai/free/private` for code you can't share.
