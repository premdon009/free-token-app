# Open Code Review

!!! note "Expected effect, not yet measured"
    The verdict comes from the project's docs. It hasn't been run against the router yet.

[Open Code Review](https://github.com/alibaba/open-code-review) (`ocr`, Apache-2.0, latest
v1.13.13 on 2026-11-19) reads a Git diff, picks the files that matter with fixed rules, and has a
model agent write line-level review comments. It needs Git 2.41 or newer.

**Verdict: a good fit for the [orchestration](../agents/orchestration.md) loop.** Let it do the
first review on a cheap lane, fix what it finds, then have the strong model do the final review.
This way the strong model spends its tokens on design and correctness, not on typos and missed
null checks.

## Two ways to run it

| Mode | Which model reviews | Use it for |
|---|---|---|
| **Native**: `ocr` calls its own configured provider | Whatever you configure, e.g. a router lane | The cheap first pass |
| **Delegation**: a plugin or skill inside Claude Code, Codex, opencode, Cursor or Kimi Code | The host agent's own model and login | When you want the strong model to drive it |

## Point it at the router

`ocr` accepts any OpenAI- or Anthropic-compatible URL:

```bash
npm install -g @alibaba-group/open-code-review   # pin a release at least 7 days old
ocr config set provider litellm
ocr config set providers.litellm.url http://127.0.0.1:4000/v1
ocr config set providers.litellm.api_key <your LITELLM_MASTER_KEY>
```

Then choose a lane as the model: `free/coding` for open-source repos, `free/private` or a paid
no-training worker for anything private. Config lives in `~/.opencodereview/config.json`.

## Privacy

OpenTelemetry export is off by default, and we found no other telemetry in its docs. The diff and
the selected files go to the review model, so the usual
[trains on prompts](../terms-and-privacy.md) rules apply.
