# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=3.55"]
# ///
"""Plain and streamed chat through a router lane.

    uv run examples/python/chat.py "Explain HTTP 429 in one line"
"""

import sys

from _client import client

prompt = " ".join(sys.argv[1:]) or "Say hi in five words."
c = client()

r = c.chat.completions.create(model="free/fast", messages=[{"role": "user", "content": prompt}])
print(f"[{r.model}] {r.choices[0].message.content}\n")

print("streamed: ", end="", flush=True)
stream = c.chat.completions.create(
    model="free/fast", messages=[{"role": "user", "content": prompt}], stream=True
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
