# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=3.55"]
# ///
"""Cache answers on disk so repeated prompts cost no quota.

    uv run examples/python/cache.py "What is a token?"
"""

import hashlib
import json
import sys
from pathlib import Path

from _client import client

CACHE = Path(".cache/llm")
CACHE.mkdir(parents=True, exist_ok=True)


def ask(prompt: str, model: str = "free/fast") -> str:
    key = hashlib.sha256(json.dumps([model, prompt]).encode()).hexdigest()
    path = CACHE / f"{key}.txt"
    if path.exists():
        return path.read_text()
    r = client().chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}])
    text = r.choices[0].message.content or ""
    path.write_text(text)
    return text


print(ask(" ".join(sys.argv[1:]) or "What is a token? One sentence."))
