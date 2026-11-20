# Coding agents

Every agent talks to the same router at `http://127.0.0.1:4000` and uses your
`LITELLM_MASTER_KEY` as its API key. The config files in `configs/` are generated from
`providers.yml`, so they always match the lanes. Goose and Pi are set up by hand.

| Agent | API it speaks | Config | Lane |
|---|---|---|---|
| [Claude Code](claude-code.md) | Anthropic Messages | `configs/claude-code.sh` / `.fish` | `free/coding` (haiku → `free/fast`) |
| [Cline](cline.md) | OpenAI-compatible | `configs/cline.json` | `free/coding` |
| [aider](aider.md) | OpenAI-compatible | `configs/aider.conf.yml` | `free/coding` (weak → `free/fast`) |
| [opencode](opencode.md) | OpenAI-compatible | `configs/opencode.json` | `free/coding` (small → `free/fast`) |
| [Codex CLI](codex.md) | OpenAI Responses | `configs/codex.toml` | `free/coding` |
| [Goose](goose.md) | LiteLLM (built in) | hand-written | `free/coding` |
| [Pi](pi.md) | OpenAI-compatible | hand-written | `free/coding` |

!!! warning "Set your expectations"
    Free models are much weaker than Claude or GPT-5-class models at agentic coding. They lose
    track in long sessions, call tools with bad arguments, and have smaller context windows. Use
    them for small, well-scoped edits, explanations and boilerplate. Review every diff.

## General tips

- **Small tasks, fresh sessions.** Context fills fast and free models degrade before the limit.
- **Use `free/private` for code you can't share.** `free/coding` includes providers that train on
  prompts (Gemini, NVIDIA). Switch the model to `free/private` in the agent's config.
- **Watch the router logs** (`docker compose -f router/compose.yaml logs -f litellm`) to see which
  provider answered and when one goes on cooldown.
- Don't like running LiteLLM, or want to know about another agent? See
  [alternatives](alternatives.md).
- To have a strong model plan and review while cheap models do the work, see
  [orchestration](orchestration.md).
