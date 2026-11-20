# Headroom

!!! note "Expected effect, not yet measured"
    The verdict below comes from Headroom's docs and from using it on this machine. It hasn't been
    measured on the router yet ([add-ons](index.md#measuring)).

[Headroom](https://github.com/headroomlabs-ai/headroom) (PyPI `headroom-ai`, Apache-2.0, latest
v0.44.0 on 2026-11-10) is a local proxy. It compresses tool output, logs, files and history before
they reach the model, and keeps the originals locally so the model can fetch one back if it needs it.

**Verdict: mixed. Treat it as experimental, run it in cache mode only, and never put it in front of
`free/private` or `local`.**

## When it helps, when it hurts

| Helps | Hurts |
|---|---|
| Fewer input tokens per request. That's real money on pay-per-token workers | It's a second proxy hop in front of LiteLLM, and both have had supply-chain trouble: Headroom's dependency `ast-grep-cli` 0.44.1 shipped a trojan |
| Fewer 429s on free lanes with low tokens-per-minute limits; Claude Code's own prompt is already large | `token` mode rewrites earlier turns. That's lossy, and weak models cope with it much worse than Opus does |
| Cache mode compresses only the newest turn, so the provider's prompt cache keeps hitting | On this machine we saw injection-shaped `<headroom_proactive_expansion>` blocks and leaked tool-search text (issue #2492) in the context |
| | Docs warn that translating routes such as LiteLLM are "not claimed to preserve" Claude Code's auto-mode classifier protocol, which can fall back to a billed client-side check |

## Settings to use

| Setting | Value | Why |
|---|---|---|
| Mode | `--mode cache` (the default, also `HEADROOM_MODE=cache`) | Keeps earlier turns unchanged; no lossy rewrites |
| Memory | Leave `--memory` off (the default) | Memory injection was the source of the fake instruction blocks |
| Prompt logging | Leave `--log-file` and `--log-messages` unset (the defaults) | Otherwise full prompts are written to disk |
| No disk state | `--stateless` (`HEADROOM_STATELESS=1`) | Writes nothing to disk; also turns off logs and memory |
| Telemetry | `HEADROOM_OFFLINE=1`, or `HEADROOM_BEACON=off` and `HEADROOM_UPDATE_CHECK=off` | The usage beacon is on by default. It sends counts and model IDs, not prompts |
| Tool search | `HEADROOM_TOOL_SEARCH=0` | On by default for Anthropic requests with many tools; see the leak above |

## In front of the router

Headroom can send its output to LiteLLM instead of a provider. The chain is
**agent → Headroom → LiteLLM → provider**:

```bash
pip install "headroom-ai[proxy]"     # pin a release at least 7 days old
headroom proxy --port 8787 --mode cache --stateless \
  --openai-api-url http://127.0.0.1:4000 \
  --anthropic-api-url http://127.0.0.1:4000
```

Then point the agent at `http://127.0.0.1:8787` instead of `:4000`. If you leave out
`--openai-api-url`, Headroom sends your key to OpenAI's real API, which rejects it with 401.

`headroom wrap claude` (and `wrap` for Codex, Aider, opencode, Cline and others) starts the proxy for
one session and launches the agent through it. `headroom unwrap <tool>` undoes any lasting changes.

## Never on the private lanes

Even with logging off, Headroom keeps tool-output originals locally unless you run `--stateless`
or `--no-ccr`, and it's one more program that sees every prompt. Don't use it for `free/private`,
`local`, or any real or client data.
