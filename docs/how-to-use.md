# How to use this

## 1. Pick services

Start with the [catalog](catalog/index.md). A good no-card starting set:

| Need | Sign up for |
|---|---|
| Fast general use | [Groq](catalog/providers.md#groq), [Google AI Studio](catalog/providers.md#gemini) |
| Private work | [Groq](catalog/providers.md#groq), [Cloudflare Workers AI](catalog/providers.md#cloudflare), [Z.ai](catalog/providers.md#zai), plus [Ollama](local/index.md) |
| Embeddings | [Cloudflare Workers AI](catalog/providers.md#cloudflare), [Mistral](catalog/providers.md#mistral), Ollama `nomic-embed-text` |
| Many models, one key | [OpenRouter](catalog/providers.md#openrouter) (turn the training opt-out on) |

Use **one account per provider**, and read each one's terms (linked from its row).

## 2. Run the router

Follow [router setup](router/index.md): copy `router/.env.example` to `router/.env`, add your keys,
pin the image, `docker compose up -d`. Then check it:

```bash
uv run --env-file router/.env python scripts/probe_keys.py           # each key
uv run --env-file router/.env python scripts/probe_keys.py --router  # each lane
```

## 3. Point your tools at it

- Coding agents: [Claude Code](agents/claude-code.md), [Cline](agents/cline.md), [aider](agents/aider.md),
  [opencode](agents/opencode.md), [Codex](agents/codex.md).
- Your own code: any OpenAI SDK with `base_url=http://127.0.0.1:4000/v1` and a lane as the model
  ([Python](apps/python.md), [TypeScript](apps/typescript.md)).

## 4. Keep the data current

Limits change every few weeks. To update a row, open the provider's own limits page, edit
`providers.yml` (set `last_verified` to today), then:

```bash
uv run python scripts/gen_catalog.py
uv run python scripts/gen_router.py
uv run python scripts/check_links.py
uv run mkdocs build --strict
```

A weekly workflow checks links, probes keyless endpoints and diffs us against the
[upstream lists](related.md), then opens an issue with anything that changed.
