# Serena

!!! note "Expected effect, not yet measured"
    The verdict below comes from Serena's docs and from using it day to day on this machine. The
    plain / +Serena / +Headroom comparison on a router lane hasn't been run yet; it needs the
    router running ([add-ons](index.md#measuring)).

[Serena](https://github.com/oraios/serena) is an MCP server that gives an agent IDE-style tools:
find a symbol, read one function's body, list references, rename across files, replace one
function. It works through language servers (or a JetBrains IDE). Licence: GPL-3.0-or-later for the
application, MIT for its language-server layer. Latest release when checked: v2.1.0 (2026-10-19).

**Verdict: worth turning on for the orchestrator and for capable workers. Leave it off for small
models.**

## When it helps, when it hurts

| Helps | Hurts |
|---|---|
| Reads one function instead of a whole file. That matters most where context and tokens per minute are tight: free lanes and pay-per-token workers | Its tool list adds a few thousand tokens to **every** request |
| Edits by symbol, so there are fewer broken search-and-replace edits | Small models (the `local` lane, small free models) pick tools worse when there are more of them |
| Finds references across the project without grepping | Needs a language server per language; some must be installed separately |
| Works in every MCP client this repo configures: Claude Code, opencode, Cline, Codex | Writes a `.serena/` folder into each project |
| Its tool output is plain text, so it isn't mangled by context-compression proxies | aider has no MCP support; aider's own repo map does a similar job there |

## Which lanes

| Lane or agent | Serena? | Why |
|---|---|---|
| Orchestrator (Claude Code on a subscription, or a paid strong model) | **On** | Saves context on big repos; the model uses the tools well |
| Paid worker with ≥128K context and good tool calling | **On** | Fewer tokens per task is real money on pay-per-token |
| `free/coding` and other free lanes with low tokens-per-minute limits | Trim it | The tool list itself eats into a small TPM budget. Keep the read tools, drop the rest |
| `local` lane, small models | **Off** | Too many tools for a small model |

## Set it up

Install with `uv`:

```bash
uv tool install -p 3.13 serena-agent
serena init
```

Serena's README warns against installing it from MCP or plugin marketplaces; their commands are
out of date.

Add it to Claude Code for every project, picking up the project from the current directory:

```bash
claude mcp add --scope user serena -- serena start-mcp-server --context claude-code --project-from-cwd
```

For Codex, `serena setup codex` writes the config. For other clients see
[Serena's client guide](https://oraios.github.io/serena/02-usage/030_clients.html).

## Trim the tools for weaker models

The tool set comes from `excluded_tools` and `included_optional_tools` in the global config
(`~/.serena/serena_config.yml`), the context, the modes, and the project's `.serena/project.yml`.
For a low-TPM lane, exclude the editing and memory tools and keep the read tools
(`find_symbol`, `get_symbols_overview`, `find_referencing_symbols`). See
[Serena's configuration guide](https://oraios.github.io/serena/02-usage/050_configuration.html).

Add this to your projects' `.gitignore`, unless you want to commit Serena's project config:

```gitignore
.serena/
```

## Privacy

Serena runs locally and talks only to your language servers, apart from an anonymous usage report
it sends on startup. Turn that off with `SERENA_USAGE_REPORTING=false`. The code it reads still goes to
whichever model your agent uses, so the [trains on prompts](../terms-and-privacy.md) rules apply as
usual.
