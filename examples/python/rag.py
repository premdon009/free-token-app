# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=3.55"]
# ///
"""Tiny in-memory RAG: embed a few notes, find the closest, answer from it.

    uv run examples/python/rag.py "How long is a cooldown?"
"""

import math
import sys

from _client import client

NOTES = [
    "A deployment that fails is skipped for 120 seconds.",
    "free/private only uses providers that don't train on prompts.",
    "Cloudflare's free daily allowance resets at 00:00 UTC.",
    "The router listens on 127.0.0.1 port 4000 only.",
]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


question = " ".join(sys.argv[1:]) or "How long is a cooldown?"
c = client()

# One batched call for all notes plus the question: fewer requests against free limits.
# Embeddings from different models don't mix, so embed everything in the same call.
emb = c.embeddings.create(model="free/embed", input=[*NOTES, question])
vectors = [d.embedding for d in emb.data]
q = vectors.pop()
best = max(range(len(NOTES)), key=lambda i: cosine(q, vectors[i]))
print(f"closest note ({emb.model}): {NOTES[best]}")

r = c.chat.completions.create(
    model="free/private",
    messages=[
        {"role": "system", "content": f"Answer only from this note: {NOTES[best]}"},
        {"role": "user", "content": question},
    ],
)
print(r.choices[0].message.content)
