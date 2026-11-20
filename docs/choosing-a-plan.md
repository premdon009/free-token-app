# Choosing a paid plan

The [paid plans](paid/index.md) tables list the facts. This page says what to do with them: which
plan to pay for, roughly what it costs, and where your prompts end up. Figures were read on
2026-11-20. Prices change often, so check the source link in the tables before you buy.

## Short answer

1. **Get the strong model through a subscription, not the API.** For daily agentic coding, a Claude
   subscription in Claude Code costs a fraction of the same Opus usage billed per token (see the
   scenarios below). Pro ($20) is enough for light use. Max 5x ($100) covers daily use, and
   Ultra ($200) heavy multi-agent work.
2. **Pay per token for the cheap workers, and only use no-training providers.** A subscription
   login can't go through the [router](router/index.md) or a third-party tool, so the worker lane
   needs its own API key. Good worker picks whose terms say they don't train on prompts:
   [Anthropic](paid/pay-per-token.md#anthropic-api) Haiku 5.5 and
   [OpenAI](paid/pay-per-token.md#openai-api) GPT-6 Luna ($0.50 per 1M output tokens),
   [DeepInfra](paid/pay-per-token.md#deepinfra) DeepSeek V4.1 Flash ($0.42, a temporary
   discount), and [Together](paid/pay-per-token.md#together) (turn prompt storage off first).
3. **Keep DeepSeek direct, Z.ai, MiniMax and the free lanes for open-source work.** They're cheap,
   but they either train on prompts by default or don't publish a policy.
4. **Want a flat price for the workers instead?** These are the coding-tool plans that also give you
   an API: [Command Code](paid/harnesses.md#command-code) GOAT ($10 for up to $100 of usage; set
   `CMD_ZDR=1`) and the [MiniMax M Plan](paid/subscriptions.md#minimax-m-plan) ($22 and up).
   [OpenCode Go](paid/harnesses.md#opencode) ($10) blocks endpoints that train, but it is meant
   for opencode itself.

How the two halves work together, the strong model planning and reviewing while the cheap one does
the work: [orchestration](agents/orchestration.md).

## Three cost scenarios

The token counts are assumptions, not measurements. Agentic coding resends the conversation on
every turn, so most input is a cached prefix, and the scenarios assume **80% of input is cached**.
Prices are from [pay per token](paid/pay-per-token.md); off-peak and batch discounts are ignored.

| Scenario | Input / month | Output / month | What it looks like |
|---|---|---|---|
| **Light** | 5M | 0.3M | A few agent sessions a week on side projects |
| **Daily** | 200M | 10M | One agent most of the working day, about 20 days a month |
| **Heavy** | 600M | 30M | Several agents or subagents in parallel, every day |

Cost per month if every token went to one model, compared with a mixed setup in which the
strong model handles 20% of tokens (planning and review) and the worker handles 80%:

| Scenario | All Opus 5.5 (API) | All DeepSeek V4.1 Flash | All Haiku 5.5 | Mixed: Opus 20% + Flash 80% | Mixed: Opus 20% + Haiku 80% | Subscription for the Opus part |
|---|---|---|---|---|---|---|
| Light | ≈ $11 | ≈ $0.70 | ≈ $0.30 | ≈ $2.70 | ≈ $2.40 | Claude Pro, $20 |
| Daily | ≈ $392 | ≈ $25 | ≈ $11 | ≈ $98 | ≈ $87 | Claude Max 5x, $100 |
| Heavy | ≈ $1,176 | ≈ $75 | ≈ $32 | ≈ $295 | ≈ $261 | Claude Ultra, $200 |

How the numbers are worked out, using the daily scenario on Opus as the example: 40M fresh input × $4
+ 160M cached × $0.20 + 10M output × $20 = $392. Output is most of the bill, so a model that writes
less (or a worker that writes the bulk) matters more than the input price.

What this means:

- **Light:** use the free lanes and a Claude Pro subscription. A worker key is optional.
- **Daily:** Claude Max 5x for the orchestrator plus a worker key. At this level the worker costs
  about $10–25, which is less than one subscription tier step.
- **Heavy:** Claude Ultra plus a worker key, and push as much bulk work as you can to the worker.
  On the API, the Opus share alone would cost more than Ultra.
- A subscription has 5-hour and weekly limits. If you hit them every week, the next tier up is
  cheaper than the API overflow.
- Haiku 5.5's price only holds for prompts under 100K tokens. Above that it costs 5× as much
  ($0.50 input, $2.50 output), and long agent sessions cross 100K, so plan on Flash-level cost
  unless the worker gets short, fresh prompts. Delegated tasks usually do.
- The cheap models are not equal to Opus at agentic coding. The mixed numbers only hold if the
  delegated tasks are bounded and reviewed; see [what to delegate](agents/orchestration.md).

## Privacy risks

| Risk | Plans it applies to | What to do |
|---|---|---|
| **Trains on prompts by default** | Claude, ChatGPT and Copilot consumer plans; DeepSeek API; Kiro; Qoder; Warp; OpenRouter (`data_collection` defaults to allow); Command Code free models | Opt out in settings before first use, and check it stuck. On OpenRouter, send `data_collection: deny` and `zdr: true` |
| **No published training policy** | Z.ai, MiniMax, Alibaba (without zero data retention), Groq paid, Fireworks, Cursor, Kimi and Alibaba plans, most coding-tool plans | Treat as "trains": open-source work only |
| **Prompts stored by default** | Together AI; OpenAI (30-day abuse logs); Alibaba (30 days without ZDR) | Turn storage off where you can; assume logs exist |
| **Data held in another jurisdiction** | DeepSeek (PRC), Z.ai (Singapore) | Not for client code or anything regulated |
| **Router or third-party use against the terms** | Claude, Google AI and Gemini CLI logins; Alibaba, Z.ai and Kimi plans outside their supported tools | Use them only in their own tools. Put API keys, never subscription logins, behind the router |
| **Resold usage with a markup or fee** | OpenRouter (5.5% on credits), Kilo gateway (5%), Augment (+40%), Zed (+10% overage), OpenCode Zen (4.6% + $0.31 per top-up) | Fine if the convenience is worth it; compare against the direct API |

**Real or client data never goes to a provider whose "trains on prompts" isn't `no`.** That
includes any project under an NDA and any data covered by a contract. For that work, use a no-training
API key, or a [local model](local/index.md). How this sorts work into lanes:
[which work goes where](terms-and-privacy.md#which-work-goes-where).
