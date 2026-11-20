# Goose

Goose ([aaif-goose/goose](https://github.com/aaif-goose/goose), Apache-2.0) is a desktop app and
CLI agent. Checked against v1.60.2 (2026-11-20). It has a built-in **LiteLLM** provider, so it
talks to the router directly.

There's no generated config for Goose; set it up by hand as below.

## Setup

Run `goose configure` and pick the LiteLLM provider. It writes `~/.config/goose/config.yaml`,
which ends up roughly like this (check the provider id `goose configure` writes):

```yaml
GOOSE_PROVIDER: litellm
GOOSE_MODEL: free/coding
LITELLM_HOST: http://127.0.0.1:4000
```

Keep the key out of the file; export it instead:

```bash
export LITELLM_API_KEY=$LITELLM_MASTER_KEY
goose session
```

`LITELLM_BASE_PATH` changes the API path if you ever put the router behind another prefix.

## More than one model

`GOOSE_SUBAGENT_PROVIDER` and `GOOSE_SUBAGENT_MODEL` set the model that subagents use. So the main
session can run on a strong model while subagents run on `free/coding`. Goose also has a
lead/worker setting for switching models within one session; we haven't tested it with the
router. See [orchestration](orchestration.md).

## Extensions and privacy

- Extensions are MCP servers, so the [add-ons](../addons/index.md) that are MCP servers (Serena)
  work here too.
- Telemetry is off unless you turn it on (`GOOSE_TELEMETRY_ENABLED` defaults to false).
