# Add-ons (optional)

Tools that sit next to an agent and change how many tokens it uses or what it remembers. **All of
them are off by default.** None of them touches `providers.yml`, the router config or the
generated `configs/`. Facts on these pages were read on 2026-11-20.

| Add-on | What it does | Verdict | Use on |
|---|---|---|---|
| [Serena](serena.md) | MCP server with symbol-level read, search and edit tools backed by language servers | **Good**: fewer tokens per task for capable models | Orchestrator and capable workers; trim or off for small models |
| [Headroom](headroom.md) | Proxy that compresses tool output and history before it reaches the model | **Mixed, experimental**: saves tokens, but adds a hop and has a rough history | Pay-per-token workers, cache mode only; never `free/private` or `local` |
| [claude-mem](claude-mem.md) | Records agent sessions; a second "observer" model summarises them into memory for later sessions | **Only with strict settings**: the observer sees everything the agent sees | Open-source repos only, with a no-training or local observer |
| [Open Code Review](open-code-review.md) | Review CLI: picks the changed files and has a model write line-level comments | **Good fit**: a cheap first-pass reviewer before the strong model | Any repo whose code may go to the review model |

Two more projects are used as references, with nothing to install:
[plannotator](../agents/orchestration.md#human-review) for the human review step, and
[superpowers](../agents/orchestration.md#the-loop) for the plan → implement → review method.

## Measuring

The verdicts come from each project's docs and, for Serena and Headroom, from using them on this
machine. They haven't been measured on the router yet. The plan is one small fixed task (an edit
plus a test in a throwaway repo), run through `free/coding` and one paid worker model, four ways:
plain, with Serena, with Headroom, and with both. For each run, record the input tokens, the 429s
and whether the test passes. That needs the router running in Docker, so until then each page
carries an "expected effect, not yet measured" banner.

## Rules for every add-on

- **Pin it.** Install a release at least 7 days old, the same rule the repo uses for LiteLLM.
  Several of these projects ship releases every few days.
- **Turn telemetry off.** Each page gives the switch.
- **The privacy rules still apply.** Anything an add-on sends to a model counts as a prompt to that
  provider. See [which work goes where](../terms-and-privacy.md#which-work-goes-where).
