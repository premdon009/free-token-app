# Staying within free limits

Free tiers run out fast once an app is in a loop. Ways to use less:

1. **Cache.** Same prompt, same answer: store it ([example](python.md#caching)). Even a few hours
   of cache cuts a lot of calls during development.
2. **Batch embeddings.** One `embeddings.create` with a list of inputs is one request, not many.
3. **Pick the smallest lane that works.** `free/fast` for classification, short replies and
   summaries; `free/coding` only when you need tools.
4. **Cap output.** Set `max_tokens`. Token-per-day limits count output too.
5. **Trim context.** Send the last few messages and a summary, not the whole history.
6. **Back off on 429.** The SDKs retry with backoff (`max_retries`). Don't add tight retry loops
   on top; the router has already tried every provider in the lane.
7. **Log which provider answered** (`response.model`) so you know whose limit you're spending.
8. **Develop against `local`.** Ollama has no quota. Switch to a hosted lane when the logic works.

## Where the limits are

Every row in the [catalog](../catalog/providers.md) lists requests and tokens per minute and per
day, with a link to the provider's own limits page. Many providers also return
`x-ratelimit-remaining-*` headers; `scripts/probe_keys.py` prints them for each key.
