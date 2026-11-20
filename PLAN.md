# Plan: `free-token-app`, a catalog of free AI APIs plus a local router

## Context
The owner wants to build AI apps and use coding agents without a paid plan, or after a paid
quota runs out. Many providers have free tiers, but their limits, models and terms change
every few weeks, and each one has its own key and endpoint. This repo does two things:

1. **Catalog.** A short, verified list of free AI API services: free type, limits, models,
   whether they train on your prompts, and how to connect. It's published as a site and
   readable on GitHub.
2. **Router.** One local endpoint that both coding agents (Claude Code, Cline, aider, opencode,
   Codex) and the owner's own apps call. It falls back from one free provider to the next
   when a limit is hit, and ends on a local model, so work doesn't stop.

Decisions already made (owner, 2026-11-19):
- Scope is the catalog plus the router. Both coding agents and apps calling the API are in scope.
- New **public** GitHub repo `premdon009/free-token-app`, with the site on **GitHub Pages**.
- Same structure as `cyber-cookbook`: one data file → generated docs → link check → Pages.

## What already exists (researched 2026-11-19)
We don't rebuild these. We link them, learn from them, and diff against their data.

| Project | What it is | Stars | Licence | Use it for |
|---|---|---|---|---|
| [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis) | Permanent free tiers only, sourced limits, `data.json` + `sources.json` | ~13.6k | CC0 | Main upstream to diff against; its data can be reused freely |
| [cheahjs/free-llm-api-resources](https://www.star-history.com/cheahjs/free-llm-api-resources/) | The original list (free + trial credits) | ~29k | — | Returned **404 on 2026-11-19**; only forks/mirrors are reachable. Link a mirror, don't depend on it |
| [mvalentsev/awesome-free-ai-coding](https://github.com/mvalentsev/awesome-free-ai-coding) | Probes entries twice a week from `registry.yaml`; generated configs for opencode, Codex, Claude Code, LiteLLM | ~250 | MIT | The model for our probe and config generation; second upstream to diff |
| [nejib1/Free-LLM](https://github.com/nejib1/Free-LLM) | 74+ providers, plus "Free-LLM Router" (npm, localhost:4000, OpenAI + Anthropic, auto-fallback) | ~1.1k | MIT | Alternative ready-made router; compare against ours |
| [open-free-llm-api/awesome-freellm-apis](https://github.com/open-free-llm-api/awesome-freellm-apis) | Large list, mirrors freellm.net | ~5.8k | MIT | Link only: inconsistent numbers, marketing funnel |
| [ClawLabsAI/free-ai-models](https://github.com/ClawLabsAI/free-ai-models) | Daily ranking of free models (benchmarks + Arena) | ~280 | MIT | Model quality ranking; its "endpoint" is a **hosted** router run by them (not used) |
| [musistudio/claude-code-router](https://github.com/musistudio/claude-code-router) | Local gateway for coding agents (Claude Code, Codex, OpenCode…), port 3456, web UI | ~38k | MIT | Coding-agent alternative to our router; document as option |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | Python gateway, 140+ providers, OpenAI + Anthropic Messages API, fallbacks | very high | MIT (core) | **Our router engine**; see the security note below |
| [maximhq/bifrost](https://github.com/maximhq/bifrost) | Go gateway, failover, virtual keys, Apache-2.0 | — | Apache-2.0 | Named fallback if LiteLLM fails our checks |

**What this repo adds:** a smaller list we've verified ourselves (about 20–30 providers, not 100+),
picked for the owner's actual uses (coding agents, app APIs, India-region notes). One data file
generates both the docs **and** the router config. A probe checks the owner's own keys, and a
script flags providers that upstream lists added or removed.

## Router choice (recommendation)
**LiteLLM proxy in Docker, pinned and fenced.** Why it: it has the widest provider coverage,
it serves both the OpenAI API (apps, Cline, aider) and the Anthropic Messages API (Claude Code
via `ANTHROPIC_BASE_URL`) from one process, fallbacks on 429 are built in, and the owner already
uses it in telecom-sentinel's gateway design.

**Security note:** LiteLLM shipped credential-stealing releases twice in 2026 (1.82.7/1.82.8 on
2026-03-24; 1.107.0 and the `latest`/`main-stable` Docker tags on 2026-10-21). So:
- Image pinned **by digest** to a release ≥ 7 days old that has a clean provenance record. Never `latest`.
  Exception: a fix for a high/critical advisory may be pinned once it's ≥ 24 hours old.
- Renovate proposes bumps; a human checks the advisory feed before merging.
- The container gets **only the free-tier provider keys**: no cloud credentials, no other secrets,
  no home directory mount. Bound to `127.0.0.1`, master key required.
- Fallback plan: if LiteLLM fails the P2 checks or has another incident, swap the generated
  config to Bifrost (same `providers.yml`, a second generator).

## Usage rules (never break)
- **One account per provider, within its terms.** No key pools, no multiple accounts to get
  around limits, no "free GPT/Claude key" resellers. The router only falls back across
  *different* providers.
- Every provider row records `trains_on_prompts`. Router lanes marked "private" skip providers
  that train on prompts or whose policy is unknown. Docs warn never to send secrets, client
  data or private code to those.
- No hosted third-party proxy in the default chain. Everything runs on the owner's machine,
  and each key goes only to its own provider.

## Repo layout
```
free-token-app/
├── pyproject.toml, uv.lock      # mkdocs-material, mkdocs-awesome-nav, pyyaml, httpx (uv-managed)
├── mkdocs.yml
├── providers.yml                # SINGLE SOURCE OF TRUTH (schema below)
├── scripts/
│   ├── gen_catalog.py           # providers.yml → docs/catalog/*.md tables (--check in CI)
│   ├── gen_router.py            # providers.yml → router/litellm.yaml (+ agent configs, --check)
│   ├── check_links.py           # every URL in providers.yml (stdlib only)
│   ├── probe_keys.py            # local only: hits each configured key, reports ok / 401 / 429 / limits
│   └── diff_upstream.py         # compares our ids with mnfst data.json + mvalentsev registry
├── router/
│   ├── compose.yaml             # litellm (digest-pinned) + optional ollama, 127.0.0.1 only
│   ├── litellm.yaml             # GENERATED
│   └── .env.example             # one *_API_KEY per provider; real .env is git-ignored, mode 600
├── configs/                     # GENERATED: claude-code.sh, cline, aider, opencode.json, codex profile
├── docs/
│   ├── index.md, how-to-use.md, terms-and-privacy.md
│   ├── catalog/                 # GENERATED: by free type, by use (coding / chat / embeddings / vision)
│   ├── router/                  # setup, lanes, troubleshooting (429s, tool-calling failures)
│   ├── agents/                  # Claude Code, Cline, aider, opencode, Codex: config + quality caveats
│   ├── apps/                    # Python + TypeScript SDK examples, retries, caching, budgets
│   ├── local/                   # Ollama, llama.cpp, LM Studio: models that fit the owner's hardware
│   └── related.md               # the "What already exists" table, kept current
└── .github/workflows/           # pages.yml (build --strict + deploy), checks.yml (weekly links + diff)
```

## `providers.yml` schema
```yaml
- id: groq
  name: Groq
  kind: inference            # provider | inference | aggregator | local
  free_type: permanent       # permanent | renewable-credit | trial | keyless
  card_required: false
  phone_required: false
  region_notes: ""           # e.g. blocked regions, India availability
  api: openai                # openai | anthropic | native
  base_url: https://api.groq.com/openai/v1
  signup_url: …
  docs_url: …
  limits_source: …           # URL that proves the limits below (required)
  limits: {rpm: 30, rpd: 1000, tpm: 8000, tpd: 200000}
  trains_on_prompts: no      # yes | no | opt-out | unknown
  commercial_use: yes        # yes | no | unknown
  models:
    - {id: llama-3.3-70b-versatile, context: 131072, tools: true, vision: false}
  router: {include: true, lanes: [fast, coding]}
  last_verified: 2026-11-19
  notes: ""
```
A row isn't merged without `limits_source` and `last_verified`. A row with `last_verified` more than
45 days old is flagged "stale" in the docs.

## Router lanes (model names apps and agents ask for)
| Lane | For | Chain (filled from `providers.yml`, best first) |
|---|---|---|
| `free/coding` | Claude Code, Cline, aider | Models with tool calling and a ≥ 64k context → … → local Ollama coder model |
| `free/fast` | Chat, small app calls | Low-latency hosts (Groq, Cerebras…) → … → local |
| `free/private` | Anything sensitive | Only `trains_on_prompts: no` providers → local |
| `free/embed` | RAG / search | Free embedding endpoints → local `nomic-embed-text` |
| `local` | Offline / no quota left | Ollama only |

Retries: on 429 or 5xx, go to the next provider in the lane, and put a provider that returned 429
on cooldown until its window resets. Claude Code points at `http://127.0.0.1:4000` with the model
set to `free/coding`. The docs say plainly that free models are weaker than Claude at agentic
coding.

## Phases (one session each; a phase ends committed + pushed)
- **P0 Scaffold:** `git init`, uv project, mkdocs, schema + 10 seed providers verified by hand,
  `gen_catalog.py`, `check_links.py`, workflows, README, `related.md`. Create the public GitHub repo,
  push, enable Pages (**owner's go before the repo is created and before the first push**).
- **P1 Full catalog:** about 20–30 providers across all free types plus local tools, a page per use,
  `terms-and-privacy.md`, `diff_upstream.py` and the first diff report.
- **P2 Router:** `gen_router.py`, `router/compose.yaml` (digest-pinned), lanes, cooldowns,
  `probe_keys.py`. Check: an OpenAI SDK call, a streamed call and a tool call through each lane,
  and Claude Code running one small edit through `free/coding`. If LiteLLM can't do this,
  switch to Bifrost here.
- **P3 Coding agents:** generated `configs/` for Claude Code, Cline, aider, opencode, Codex; a
  page per agent with setup, which lane to use, and known failure modes; a comparison with
  claude-code-router and Free-LLM Router.
- **P4 Apps:** Python and TypeScript examples (chat, streaming, tools, embeddings/RAG), retry and
  caching patterns, how to stay within free limits.
- **P5 Automation:** a weekly workflow runs link checks, keyless endpoint probes and the upstream
  diff, and opens an issue with the changes; Renovate for the image digest and Python deps.
- **P6 Paid plans** (added 2026-11-20): `plans.yml` (subscriptions, pay-per-token hosts, coding-tool
  plans) → `gen_plans.py` → `docs/paid/`, never the router; a hand-written `choosing-a-plan.md`
  with cost scenarios; `docs/agents/orchestration.md` (strong model plans and reviews, cheap
  models work; design only); optional add-ons in `docs/addons/`; Pi and Goose agent pages.

## Verification ("done" for every phase)
- `uv run mkdocs build --strict` passes
- `uv run python scripts/gen_catalog.py --check`, `gen_router.py --check` and `gen_plans.py --check` (generated files current)
- `uv run python scripts/check_links.py`: 0 FAIL
- `uv lock --check`
- From P2: `docker compose -f router/compose.yaml up -d`, then `probe_keys.py` reports each key,
  `curl 127.0.0.1:4000/v1/chat/completions` works on every lane, and a forced 429 (a fake key at
  the top of the chain) falls through to the next provider
- Pages workflow green; site loads at `https://premdon009.github.io/free-token-app/`
