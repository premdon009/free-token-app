# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=3.55"]
# ///
"""One tool-call round trip on the free/coding lane.

    uv run examples/python/tools.py
"""

import json

from _client import client

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }
]


def get_weather(city: str) -> dict:
    return {"city": city, "temp_c": 31, "sky": "hazy"}  # stand-in for a real API


c = client()
messages = [{"role": "user", "content": "What's the weather in Chennai?"}]
r = c.chat.completions.create(model="free/coding", messages=messages, tools=TOOLS)
msg = r.choices[0].message

if not msg.tool_calls:
    print("model answered without a tool:", msg.content)
    raise SystemExit(0)

messages.append(msg.model_dump(exclude_none=True))
for call in msg.tool_calls:
    args = json.loads(call.function.arguments or "{}")
    result = get_weather(**args)
    messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

final = c.chat.completions.create(model="free/coding", messages=messages, tools=TOOLS)
print(f"[{final.model}] {final.choices[0].message.content}")
