# Free Token App

A checked catalog of free AI API services, plus a local router that falls back across them, for
coding agents and your own apps.

**Site:** <https://premdon009.github.io/free-token-app/>

- **Catalog**: about 20 services (permanent free tiers, renewable credits, trials, keyless, local),
  each with an official limits link, the date it was last checked, and whether it trains on your prompts.
- **Router**: [LiteLLM](https://github.com/BerriAI/litellm) in Docker on `127.0.0.1:4000`, pinned by
  digest. Ask for a lane (`free/coding`, `free/fast`, `free/private`, `free/embed`, `local`) and it
  falls back from one provider to the next on 429s and errors.
- **Agent configs** for Claude Code, Cline, aider, opencode and Codex, and app examples in Python
  and TypeScript.
- **Paid plans**: subscriptions, pay-per-token prices and coding-tool quotas, for when free isn't
  enough, plus a design for letting a strong model orchestrate cheap ones.
- **Add-ons** (optional): Serena, Headroom, claude-mem and open-code-review, with when each helps or hurts.

Free tiers and the router come from [`providers.yml`](providers.yml); paid plans from [`plans.yml`](plans.yml).

## Quick start

```bash
uv sync
cp router/.env.example router/.env && chmod 600 router/.env   # add your keys
uv run python scripts/pin_image.py litellm
docker compose -f router/compose.yaml up -d
uv run --env-file router/.env python scripts/probe_keys.py --router
```

Then see [coding agents](https://premdon009.github.io/free-token-app/agents/) or
[apps](https://premdon009.github.io/free-token-app/apps/).

## Rules

One account per provider, used within its terms. No key pools, no multi-account rotation, no
resold or third-party keys. Don't send secrets or private code to providers that train on prompts;
use `free/private` or `local` for that. Free models are much weaker than paid frontier models at
agentic coding.

## Updating the data

```bash
$EDITOR providers.yml                       # check the provider's own page; set last_verified
uv run python scripts/gen_catalog.py
uv run python scripts/gen_router.py
uv run python scripts/gen_plans.py          # after editing plans.yml
uv run python scripts/check_links.py
uv run mkdocs build --strict
```

Related lists we diff against: [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis),
[mvalentsev/awesome-free-ai-coding](https://github.com/mvalentsev/awesome-free-ai-coding).

MIT licence.
