# claude-mem

[claude-mem](https://github.com/thedotmack/claude-mem) (Apache-2.0, latest v16.0.1 on 2026-11-19)
records what an agent does, has a second "observer" model compress it into short observations, and
gives later sessions a small index plus a search tool over them. It works with Claude Code, Codex,
opencode, Gemini CLI, Cursor, Pi, DeepSeek Harness and others.

**Verdict: optional, with strict settings. Open-source repos only.**

It's itself a "cheap model does the background work" setup: the observer can be any cheap model,
including a router lane. The catch is that **the observer sees everything the agent sees**: file
contents, command output, your prompts. Whatever model you pick for it receives all of that.

## Risks

| Risk | What to do |
|---|---|
| The observer gets every file and command output the agent saw | Use an observer with `trains_on_prompts: "no"`, or a local model. Never `free/coding` |
| The installer asks you to sign in and offers a 30-day hosted trial that needs a card | Install with an explicit `--provider` and `CLAUDE_MEM_ONLINE_OPTIN=false` |
| Telemetry is on by default (anonymous counts and redacted errors, no prompts or code) | `npx claude-mem telemetry disable`, or `DO_NOT_TRACK=1` |
| Ships very fast: v15 to v16 in two days | Pin a release at least 7 days old |
| It injects remembered context into new sessions, which can carry stale or wrong instructions | Read what it injects for the first few sessions; turn it off if it drifts |
| A worker restart can drop observations still in the queue; several troubleshooting fixes delete data | Back up `~/.claude-mem` before an update or a fix |

## Point the observer at the router

The router speaks the Anthropic API, so use claude-mem's gateway mode. In `~/.claude-mem/.env`:

```bash
CLAUDE_MEM_PROVIDER=claude
CLAUDE_MEM_CLAUDE_AUTH_METHOD=gateway
ANTHROPIC_BASE_URL=http://127.0.0.1:4000
ANTHROPIC_AUTH_TOKEN=<your LITELLM_MASTER_KEY>
CLAUDE_MEM_MODEL=free/private
```

claude-mem doesn't translate model names, so `CLAUDE_MEM_MODEL` must be a lane name the router
knows. This only changes the background observer; Claude Code itself is unaffected.

For an OpenAI-compatible endpoint (a paid no-training worker, or a local Ollama), use
`CLAUDE_MEM_PROVIDER=openai-compatible` with `CLAUDE_MEM_OPENAI_COMPAT_BASE_URL`,
`CLAUDE_MEM_OPENAI_COMPAT_MODEL` and `CLAUDE_MEM_OPENAI_COMPAT_API_KEY`. See
[claude-mem's configuration docs](https://docs.claude-mem.ai/configuration).

## Install

```bash
CLAUDE_MEM_ONLINE_OPTIN=false npx claude-mem install --provider claude
npx claude-mem telemetry disable
```

Memory lives in `~/.claude-mem` (SQLite plus a vector store). Cloud sync is opt-in; leave it off.

**Never use it on a repo with real, client or confidential data.** It keeps a lasting copy of that
data on disk, and sends it to the observer model.
