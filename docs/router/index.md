# Router setup

One local endpoint, `http://127.0.0.1:4000`, that speaks both the **OpenAI API** (apps, Cline,
aider, opencode, Codex) and the **Anthropic Messages API** (Claude Code). It's
[LiteLLM](https://github.com/BerriAI/litellm) in Docker, configured entirely from `providers.yml`.

!!! danger "Why the image is pinned by digest"
    LiteLLM shipped credential-stealing releases twice in 2026 (1.82.7 and 1.82.8 in March; 1.107.0
    and the moving `latest` / `main-stable` Docker tags in October). So the image is pinned by
    digest to a release at least 7 days old, the container gets only free-tier provider keys, and it
    listens on `127.0.0.1` only. `scripts/pin_image.py` also skips any release covered by a
    published LiteLLM security advisory.

    **Exception:** if the newest 7-day-old release has a *high* or *critical* advisory, waiting
    would leave a known hole open. The script then pins the oldest release that fixes it, as long
    as it's at least 24 hours old, and prints `EXCEPTION`. Still check the [LiteLLM security advisories](https://github.com/BerriAI/litellm/security)
    before you accept a version bump.

## Needs

- Docker or Podman with compose (`docker compose version`)
- [uv](https://docs.astral.sh/uv/) for the helper scripts
- Optional: [Ollama](../local/index.md) for the local last hop

## Steps

```bash
git clone https://github.com/premdon009/free-token-app && cd free-token-app
uv sync

# 1. keys
cp router/.env.example router/.env && chmod 600 router/.env
python3 -c "import secrets; print('sk-' + secrets.token_urlsafe(32))"   # paste as LITELLM_MASTER_KEY
$EDITOR router/.env                                                      # add the keys you have

# 2. pin the image (newest LiteLLM release ≥ 7 days old with no advisory; high/critical fixes ≥ 24 h)
uv run python scripts/pin_image.py litellm
uv run python scripts/pin_image.py --check --advisories

# 3. start
docker compose -f router/compose.yaml up -d
docker compose -f router/compose.yaml logs -f litellm      # Ctrl-C when "Uvicorn running"

# 4. check
uv run --env-file router/.env python scripts/probe_keys.py
uv run --env-file router/.env python scripts/probe_keys.py --router
```

A quick manual call:

```bash
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" -H "Content-Type: application/json" \
  -d '{"model": "free/fast", "messages": [{"role": "user", "content": "Say hi"}]}'
```

## Check that fallback works

Put a wrong key in the first provider of a lane (see [lanes](lanes.md)), restart, and call that lane.
The answer should still come back, from the second provider, and the logs show the first one going
on cooldown. Put the right key back afterwards.

```bash
docker compose -f router/compose.yaml restart litellm
uv run --env-file router/.env python scripts/probe_keys.py --router --chat-only
```

## Changing the chain

Edit `router` (include, priority, lanes) or `models` in `providers.yml`, then:

```bash
uv run python scripts/gen_router.py
docker compose -f router/compose.yaml restart litellm
```

`router/litellm.yaml` is generated: don't edit it by hand. See [troubleshooting](troubleshooting.md)
for 429s, tool-call failures and slow local models.

## If LiteLLM has another incident

Stop the container (`docker compose -f router/compose.yaml down`), and don't update the pin until
the advisory names a clean version. The planned fallback engine is
[Bifrost](https://github.com/maximhq/bifrost), generated from the same `providers.yml`.
