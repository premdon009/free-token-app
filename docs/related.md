# Related projects

We don't rebuild these. We link them, learn from them, and diff our data against the first two
(`scripts/diff_upstream.py`). Checked 2026-11-19; star counts are approximate.

| Project | What it is | Stars | Licence | How we use it |
|---|---|---|---|---|
| [mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis) | Permanent free tiers only, with a source for every limit (`data.json`, `sources.json`) | ~13.6k | CC0 | Main upstream for the weekly diff |
| [mvalentsev/awesome-free-ai-coding](https://github.com/mvalentsev/awesome-free-ai-coding) | Probes entries twice a week from `registry.yaml`; generates agent configs | ~250 | MIT | Second upstream; the model for our probes and generated configs |
| cheahjs/free-llm-api-resources | The original list (free tiers and trial credits) | ~29k | — | Returned 404 on 2026-11-19; only forks and mirrors are reachable |
| [nejib1/Free-LLM](https://github.com/nejib1/Free-LLM) | 74+ providers and an npm "Free-LLM Router" on port 4000 | ~1.1k | MIT | A ready-made alternative router ([comparison](agents/alternatives.md)) |
| [open-free-llm-api/awesome-freellm-apis](https://github.com/open-free-llm-api/awesome-freellm-apis) | Large list mirroring freellm.net | ~5.8k | MIT | Link only: numbers are inconsistent |
| [ClawLabsAI/free-ai-models](https://github.com/ClawLabsAI/free-ai-models) | Daily ranking of free models | ~280 | MIT | Model quality hints. Its endpoint is a hosted router run by them, so we don't use it |
| [musistudio/claude-code-router](https://github.com/musistudio/claude-code-router) | Local gateway for coding agents, port 3456, web UI | ~38k | MIT | Alternative for coding agents ([comparison](agents/alternatives.md)) |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | Python gateway, OpenAI and Anthropic APIs, fallbacks | very high | MIT (core) | **Our router engine**, pinned by digest |
| [maximhq/bifrost](https://github.com/maximhq/bifrost) | Go gateway with failover | — | Apache-2.0 | Planned fallback engine if LiteLLM fails our checks |

## What this repo adds

A smaller list (about 20 services) checked against each provider's own page, picked for coding
agents, app APIs and India-region use. One data file generates both these docs **and** the router
config, a probe checks your own keys, and the weekly diff flags what the upstream lists added or dropped.
