# Alternatives to this router

You don't have to use LiteLLM. Two other local options, compared with ours:

| | This repo (LiteLLM) | [claude-code-router](https://github.com/musistudio/claude-code-router) | [Free-LLM Router](https://github.com/nejib1/Free-LLM) |
|---|---|---|---|
| Runs as | Docker container | Node CLI (`ccr`) | npm package |
| Port | 4000 | 3456 | 4000 |
| APIs served | OpenAI + Anthropic + Responses | Anthropic (for Claude Code, Codex, opencode) | OpenAI |
| Config | Generated from `providers.yml` | Hand-written `~/.claude-code-router/config.json` | Built-in provider list |
| Fallback | Per-lane chains, cooldown on failure | Routes by task type (background, thinking, long context) | Automatic across its providers |
| Privacy lane | Yes (`free/private`) | Manual | No |
| Web UI | No (`NO_DOCS=True`) | Yes (`ccr ui`) | No |

**Pick claude-code-router** if you mainly use Claude Code and want routing by task type (a cheap
model for background calls, a long-context model for big files) and a UI to edit it.

**Pick Free-LLM Router** if you want something running in one command and don't mind its default
provider list.

**Stay with this repo** if you want one config for agents and apps, a privacy lane, and limits you
can check against each provider's own page.

!!! note "Port clash"
    Free-LLM Router and this router both default to port 4000. Run only one, or change one port.

Either way, keep the same rules: one account per provider, no shared or resold keys.
