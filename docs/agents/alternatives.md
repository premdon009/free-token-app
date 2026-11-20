# Alternatives

## Other routers

You don't have to use LiteLLM. Two other local options, compared with ours:

| | This repo (LiteLLM) | [claude-code-router](https://github.com/musistudio/claude-code-router) v3 | [Free-LLM Router](https://github.com/nejib1/Free-LLM) |
|---|---|---|---|
| Runs as | Docker container | Desktop / web app | npm package |
| APIs served | OpenAI + Anthropic + Responses | Anthropic (for Claude Code, Codex, opencode) | OpenAI |
| Config | Generated from `providers.yml` | Its UI; stored in `~/.claude-code-router/config.sqlite` | Built-in provider list |
| Fallback | Per-lane chains, cooldown on failure | Routes by task type (background, thinking, long context) and custom rules | Automatic across its providers |
| Per-subagent model | Pick a lane per agent | Yes: a `<CCR-SUBAGENT-MODEL>` tag in the subagent prompt | No |
| Privacy lane | Yes (`free/private`) | Manual | No |

**claude-code-router v3** (v3.1.5, read 2026-11-20) is a different product from the old `ccr` npm
CLI. It reads an old `config.json` once, to migrate it; later edits to that file do nothing. Pick
it if you mainly use Claude Code and want routing by task type with a UI to edit it.

**Pick Free-LLM Router** if you want something running in one command and don't mind its default
provider list. It also defaults to port 4000, so run only one of it and this router, or change a
port.

**Stay with this repo** if you want one config for agents and apps, a privacy lane, and limits you
can check against each provider's own page.

Either way, keep the same rules: one account per provider, no shared or resold keys.

## Other agents we checked (2026-11-20)

| Agent | Verdict | Why |
|---|---|---|
| [Kilo CLI](https://github.com/Kilo-Org/kilocode) | Works, no page | An MIT fork of opencode (v7.8.31). Point `provider.<id>.options.baseURL` in `kilo.json` at the router, as on the [opencode](opencode.md) page. Telemetry is on by default: set `KILO_TELEMETRY_LEVEL=off`. Its own login and gateway may be the default path, so check which endpoint it's using |
| DeepSeek Harness (`dsh`) | **No, for now** | MIT, but only pre-releases exist (latest `dsh-v0.2.2-rc.5`, 2026-11-18). The README calls it a developer preview with "COMPATIBILITY-BREAKING CHANGES", and SAFETY.md says it hasn't had a security audit. It runs model-written code and loads third-party plugins, and one plugin (`dsh-plugin-blender-3d@0.2.1`, OSV `MAL-2026-18321`) installed a crypto-miner. Look again after a stable release |
| Antigravity CLI | Skip | Its docs don't describe a custom endpoint, so it can't use the router. Its free quota is listed under [coding tools](../paid/harnesses.md) |
| Cursor | Skip | Requests go through Cursor's servers even with your own key, so the router and the privacy lane don't apply |
| Replicas | Skip | A cloud platform; we found no documented custom endpoint, licence or privacy terms |

[Pi](pi.md) and [Goose](goose.md) have their own pages.
