# Troubleshooting

## Every call returns 401

The client must send `LITELLM_MASTER_KEY` (from `router/.env`) as its API key, not a provider key.

## A provider is always skipped

Run `uv run --env-file router/.env python scripts/probe_keys.py`.

| Result | Meaning |
|---|---|
| `skipped: X not set` | No key in `router/.env`; the router skips it too (logs an auth error, then falls back) |
| `bad key (401)` | Wrong or revoked key; make a new one on the provider's key page |
| `not found (404)` | Base URL wrong, or (NVIDIA) a new key that can list but not call models |
| `rate limited (429)` | Quota spent; the `retry-after` / `x-ratelimit-*` values show when it resets |

## Lots of 429s

- Free limits are small: Groq 30 RPM per model, OpenRouter 50 requests per day without credits,
  Cohere 1,000 calls per month. Coding agents make many calls per task.
- A deployment that fails is skipped for 120 seconds (`cooldown_time`), so the lane moves on.
- Daily limits reset at different times (Cloudflare at 00:00 UTC, which is 05:30 IST).

## Tool calls fail or come back as plain text

Not every free model handles tools well. The `free/coding` lane only uses models marked
`tools: true` with at least 64K context, but quality still varies. If an agent keeps breaking:

- use a smaller task, or
- move the model that misbehaves lower (or out) in `providers.yml`, then regenerate.

## Claude Code says the context is too long

Claude Code assumes a large context window. Free models have 32K–1M. Start a fresh session more
often (`/clear`), and keep the repo context small.

## The local model is very slow

On a CPU-only laptop with 8 GB RAM, a 3B model gives a few tokens per second. Use `qwen2.5-coder:1.5b`
for speed, close other apps, and keep local as the last hop rather than the first.

## The container doesn't start

- `docker compose -f router/compose.yaml config` shows errors in the compose file or `.env`.
- `image: ...:PIN_ME` means you haven't run `scripts/pin_image.py litellm` yet.
- `network_mode: host` works on Linux. On Docker Desktop (macOS/Windows), replace it with
  `ports: ["127.0.0.1:4000:4000"]`, change `--host` to `0.0.0.0`, and set
  `OLLAMA_API_BASE=http://host.docker.internal:11434`.
