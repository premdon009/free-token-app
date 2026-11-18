# Your own apps

Any OpenAI SDK works. Set two things:

| Setting | Value |
|---|---|
| Base URL | `http://127.0.0.1:4000/v1` |
| API key | your `LITELLM_MASTER_KEY` |
| Model | a lane: `free/fast`, `free/coding`, `free/private`, `free/embed`, `local` |

The response's `model` field tells you which provider actually answered.

- [Python](python.md): chat, streaming, tools, RAG, caching
- [TypeScript](typescript.md): chat and streaming
- [Staying within limits](staying-within-limits.md)

!!! warning "Shipping an app"
    Several free tiers are for evaluation only (Cohere trial keys, NVIDIA trial endpoints), and the
    router is meant for your own machine. Check the **commercial use** column in the
    [catalog](../catalog/index.md) and each provider's terms before you put real users on it.
