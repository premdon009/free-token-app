# Pi

Pi ([earendil-works/pi](https://github.com/earendil-works/pi), MIT) is a small terminal coding
agent. It ships few built-in tools and is extended with packages. Checked against v1.5.2
(released 2026-11-10, read 2026-11-20). It needs Node 22.19 or newer.

There's no generated config for Pi; set it up by hand as below.

## Setup

```bash
npm install -g @earendil-works/pi-coding-agent
export LITELLM_MASTER_KEY=sk-...
```

Add the router as a provider in Pi's `models.json`, in Pi's agent directory (usually
`~/.pi/agent/`; Pi's configuration docs give the exact path):

```json
{
  "providers": {
    "free-token": {
      "baseUrl": "http://127.0.0.1:4000/v1",
      "api": "openai-completions",
      "apiKey": "$LITELLM_MASTER_KEY",
      "models": [
        { "id": "free/coding" },
        { "id": "free/private" },
        { "id": "free/fast" }
      ]
    }
  }
}
```

`apiKey` reads an environment variable when it starts with `$`, so the key never goes in the
file. The router also serves `openai-responses` and `anthropic-messages`, the other two values
`api` accepts.

## Privacy

`enableInstallTelemetry` is on by default: anonymous install and update reports, plus provider
attribution headers on requests. Turn it off in Pi's settings before the first run.
`enableAnalytics` is off by default.

## What it lacks

- No built-in subagents or plan mode. For a strong-plans, cheap-works split, run Pi as the
  worker on a cheap lane and plan elsewhere; see [orchestration](orchestration.md).
- MCP comes through the `builtin:mcp` extension (`pi mcp add ...`), not out of the box.
