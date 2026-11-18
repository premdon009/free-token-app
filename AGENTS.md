# Free Token App — Agent Memory

A catalog of free AI API services plus a local router that falls back across them, for coding
agents and the owner's own apps. Public repo `premdon009/free-token-app`, site on GitHub Pages.

**The approved plan is [PLAN.md](PLAN.md). Read it before starting a phase.**

## Phase status (update this table when a phase lands)

| Phase | Scope | Status |
|---|---|---|
| P0 | Scaffold, schema, 10 seed providers, catalog generator, link check, CI, Pages | ✅ done |
| P1 | Full catalog (20–30 providers + local), use-case pages, upstream diff | ✅ done |
| P2 | Router: generated LiteLLM config, compose, lanes, `probe_keys.py` | 🟡 built; live test pending (needs keys + `docker compose up`) |
| P3 | Coding-agent configs and pages | 🟡 built; not yet run through each agent |
| P4 | App examples (Python, TypeScript) | 🟡 built; not yet run against the router |
| P5 | Weekly automation, Renovate | ✅ done (first weekly run pending) |

## Rules (never break)

1. `providers.yml` is the only source. Catalog pages, `router/litellm.yaml` and `configs/` are
   generated; never edit them by hand.
2. Every provider row needs `limits_source` (an official URL) and `last_verified`. Don't copy
   limits from another list without checking the provider's own page.
3. One account per provider, within its terms. No key pools, multi-account rotation, resold
   keys or hosted third-party proxies in the default chain.
4. Keys live only in `router/.env` (git-ignored, mode 600). Never read, print or commit it.
5. The LiteLLM image is pinned by digest to a release ≥ 7 days old with no known advisory. Never `latest`.
   Exception: if that release has a **high/critical** advisory, pin the oldest fixed release that's ≥ 24 h old
   (`pin_image.py` does this automatically and prints `EXCEPTION`). It gets only
   provider keys and listens on `127.0.0.1` only.
6. Record `trains_on_prompts` for every provider; the `free/private` lane uses only `no`.

## Commands

```bash
uv sync
uv run mkdocs serve
uv run python scripts/gen_catalog.py      # after editing providers.yml
uv run python scripts/gen_router.py
uv run python scripts/check_links.py
```

**Done means:** `mkdocs build --strict`, `gen_catalog.py --check`, `gen_router.py --check`,
`check_links.py` (0 fail) and `uv lock --check` all pass. Then commit (conventional commits)
and push `main` after the owner's go.
