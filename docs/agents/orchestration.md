# Orchestration: a strong model plans, cheap models work

The idea: a strong model (Claude Opus, or another top model) does the planning and the review,
where quality matters most. Cheap models (DeepSeek Flash, Haiku, Qwen, GLM, the free lanes) do the
bounded, mechanical work, which is most of the tokens. [Choosing a plan](../choosing-a-plan.md)
shows what that saves; this page shows how to set it up.

This page is design and setup notes only. The repo has no code for it yet; see
[not built yet](#not-built-yet).

## The short answer

1. **Keep Claude Code on your Claude subscription** for planning and review. Don't point it at the
   router: that replaces your login (see [Claude Code](claude-code.md#the-router-replaces-your-subscription-login)).
2. **Send the work to a cheap model through a delegate.** Either an MCP tool inside Claude Code
   that calls a router lane, or a second agent ([opencode](opencode.md), [Goose](goose.md),
   [Pi](pi.md), [aider](aider.md)) running on the router in its own terminal.
3. **Review twice.** A cheap first pass with [Open Code Review](../addons/open-code-review.md),
   then the strong model and you.

## Ways to split the work

Checked 2026-11-20.

| Pattern | How | Keeps the Claude subscription? | Setup | Notes |
|---|---|---|---|---|
| **A. Delegate MCP** in Claude Code | An MCP server gives Claude a tool that sends a task to another model and returns the answer | **Yes**: Claude Code still logs in as you; only the tool calls go elsewhere | Medium | [Houtini LM](https://github.com/houtini-ai/houtini-lm) (Apache-2.0) supports a LiteLLM router. [PAL MCP](https://github.com/BeehiveInnovations/pal-mcp-server) does more, but has had no update since 2025-12-15. [codexmcp](https://github.com/GuDaStudio/codexmcp) and [gemini-mcp-tool](https://github.com/jamubc/gemini-mcp-tool) hand tasks to Codex CLI or Gemini CLI instead |
| **B. Claude Code through a gateway** | `ANTHROPIC_BASE_URL` plus per-slot models: Opus slot to a strong model, Haiku slot and subagents to cheap ones | No: needs an API key, so the strong model is billed per token | Low | Anthropic doesn't support non-Claude models behind a gateway. Fine for an all-API setup |
| **C. Claude Code subagents** | A subagent with `model: haiku`, or your own `Explore` with `model: haiku` | Yes | Low | The worker is still Claude and uses plan quota. Cheaper per task, but the savings are smaller than A |
| **D. A separate worker agent** | opencode, Goose or Pi on a router lane; the strong model writes the task, you paste it, it reports back | Yes | Low | Most control and the least magic. Goose and opencode can also give their own subagents a cheaper model |
| **E. aider architect / editor** | `--architect --model <strong> --editor-model <cheap>` | No (API keys) | Low | Simple and proven, but aider is slowly maintained and has no MCP |
| **F. claude-code-router v3** | Routes Claude Code requests by task type, and per subagent via a model tag | No (API keys) | Medium | See [alternatives](alternatives.md) |
| **G. Codex** | `review_model` and `agents.default_subagent_model` set cheaper models for review and subagents | Depends on the profile | Low | See [Codex](codex.md) |

**Recommended:** A or D. They are the only patterns that keep the subscription for the strong
model, which is the cheapest way to get a lot of Opus (see the cost scenarios). Use C as well for
read-only exploration. Use B or E only if you've decided to pay per token for everything.

## The loop

1. **Plan on the strong model.** Break the work into small tasks, each with the exact files, the
   change, and how to check it (a test command, or the expected output). A task should fit in one
   short session.
2. **Implement on the cheap model.** One fresh session or tool call per task. Give it only the
   files it needs.
3. **First-pass review on a cheap lane.** Run [Open Code Review](../addons/open-code-review.md)
   on the diff; it catches the obvious problems for very little.
4. **Final review on the strong model.** It reads the diff and the test output against the plan,
   and either accepts it or writes a smaller, clearer task.
5. **You merge.** See [human review](#human-review).

If a cheap model fails the same task twice, don't try a third time: do it on the strong model or
split it further. The cheapest models can take 2–3 times the turns on multi-step work, which
eats the savings.

## What to delegate

| Delegate to the cheap model | Keep on the strong model |
|---|---|
| Boilerplate, renames, repeated edits across files | Planning, architecture and API design |
| Writing tests to a spec the strong model wrote | Deciding what to test |
| Summarising logs, diffs and long files | Security-sensitive code: auth, secrets, input validation, crypto |
| Docs and comments from finished code | Debugging that has already failed once |
| First-pass review | The final review and anything about to be merged |
| Searching and reading code (read-only) | Anything that touches production data or deploys |

## Which lane for which data

The worker sees everything you send it: file contents, command output, error messages. Choose the
lane by the data, not by the price. The rule is in
[terms and privacy](../terms-and-privacy.md#which-work-goes-where); in short:

- Open-source code: any lane, including free lanes that train on prompts.
- Private code that isn't sensitive: `free/private`, or a paid API that doesn't train.
- Real or client data: a paid plan with no-training terms, or [local models](../local/index.md)
  only. Never a free lane.

The same goes for add-ons that send context to a model, such as
[claude-mem](../addons/claude-mem.md).

## Human review

The strong model reviewing the diff is not the last step. Read the diff yourself before merging,
and run the tests yourself.

[plannotator](https://github.com/backnotprop/plannotator) is a useful aid: it opens agent plans
and diffs in a local browser page where you can annotate them and send the notes back to the
agent. It works with Claude Code, Codex, opencode and Gemini CLI. Run it local-only: set
`NO_ANON_PING=1` (it otherwise sends a small daily usage ping) and `PLANNOTATOR_SHARE=disabled`
(turns off share links).

## Pacing

Work in batch sessions, not all-day loops. Plan a batch of tasks, run them, review them, stop.
Long unattended loops burn through free quotas and subscription limits, and errors pile up
before anyone looks.

## References

- [superpowers](https://github.com/obra/superpowers): a method and skill set for this loop. Its
  `subagent-driven-development` skill sends each task to a fresh subagent, reviews it twice, and
  says to use the least powerful model that can do each role, naming the model explicitly every
  time.
- [Open Code Review](../addons/open-code-review.md): the cheap first-pass reviewer.
- [Serena](../addons/serena.md): reads one function instead of a whole file, which keeps worker
  prompts short.

## Not built yet

Possible follow-ups, not in the repo:

- A `cheap/worker` router lane made of paid no-training worker models, next to the free lanes.
- A small delegate MCP tool that sends a task to that lane and returns the diff, so pattern A
  works without a third-party server.
