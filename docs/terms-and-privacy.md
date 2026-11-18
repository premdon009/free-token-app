# Terms and privacy

Free tiers are paid for somehow. Often it's your prompts: some providers use them to train models,
and trial programmes record inputs and outputs. Each catalog row records this as
**trains on prompts**, with a link to the provider's policy where we found one.

| Value | Meaning | Safe for private code or client data? |
|---|---|---|
| 🟢 `no` | The provider's terms say API inputs aren't used for training | Better, but it still leaves your machine |
| 🟠 `opt-out` | Used unless you switch it off in account settings | Only after you opt out, and check it stuck |
| 🔴 `yes` | Free-tier prompts are used to improve their products | No |
| ⚪ `unknown` | No clear published policy | No |

## Rules this repo follows

1. **One account per provider, within its terms.** Making extra accounts to multiply a free quota
   breaks most providers' terms and can get every account banned. The router doesn't rotate keys;
   it falls back to a *different* provider.
2. **No resold keys or "free GPT/Claude key" sites.** Those are usually stolen or abused keys.
3. **No hosted third-party proxy in the default chain.** Each key goes straight to its own provider
   from your machine. Services that are themselves gateways to unnamed hosts are listed but left
   out of the router.
4. **Commercial use**: several free tiers (for example Cohere trial keys and NVIDIA's trial
   endpoints) are for evaluation only. Check the **commercial use** column before shipping an app.
5. **Never send secrets** (passwords, API keys, tokens, personal data) to any model you don't run yourself.

## What the lanes do with this

- `free/private` only uses providers with `trains_on_prompts: no`, then local Ollama. The generator
  refuses to put any other provider in that lane.
- `free/coding` and `free/fast` include providers that train on prompts (Gemini, NVIDIA). Don't use
  them on code you aren't allowed to share.

## Retired or unclear free tiers

- **GitHub Models**: closed to new users on 2026-06-16 and fully retired on 2026-07-30.
- **Hugging Face Inference Providers**: free accounts no longer get monthly credit.
- **Ollama Cloud**: a starter allowance was announced, but the current pricing page doesn't show it.
- **Pollinations**: only the legacy keyless text endpoint is still free; the new API needs credits.

## India notes

- Most providers here work from India without a card. NVIDIA needs phone verification in a supported country.
- [Sarvam AI](catalog/providers.md#sarvam) is India-hosted and focuses on Indian languages; it has a
  one-time ₹100 starter credit.
- Cerebras' trial needs a verified payment method.
