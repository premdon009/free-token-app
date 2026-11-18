"""Check the owner's own keys, keyless endpoints, or the running router. Never prints a key.

    uv run --env-file router/.env python scripts/probe_keys.py           # each provider key: GET /models
    uv run python scripts/probe_keys.py --keyless                         # keyless endpoints only (CI-safe)
    uv run --env-file router/.env python scripts/probe_keys.py --router   # one tiny call per lane on :4000
    uv run --env-file router/.env python scripts/probe_keys.py --router --chat-only

Reports: ok / 401 bad key / 403 / 404 / 429 rate limited / missing key, plus any x-ratelimit-* headers.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

from _providers import load

UA = "free-token-app-probe"
ROUTER = "http://127.0.0.1:4000"
LANE_MODELS = ("free/coding", "free/fast", "free/private", "local")


def request(url: str, key: str | None = None, body: dict | None = None, timeout: int = 60):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(), time.monotonic() - t0
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read(), time.monotonic() - t0
    except Exception as e:  # noqa: BLE001
        return None, {}, type(e).__name__.encode(), time.monotonic() - t0


def verdict(status: int | None) -> str:
    return {
        200: "ok", 401: "bad key (401)", 403: "forbidden (403)", 404: "not found (404)",
        429: "rate limited (429)",
    }.get(status or 0, f"error ({status})" if status else "unreachable")


def limits(headers: dict) -> str:
    keep = {k.lower(): v for k, v in headers.items()
            if k.lower().startswith(("x-ratelimit", "retry-after", "ratelimit"))}
    return " ".join(f"{k}={v}" for k, v in sorted(keep.items()))


def base_url(p: dict) -> str | None:
    env = p["router"].get("base_url_env")
    if env and p["kind"] != "local":
        return os.environ.get(env) or None
    return p["base_url"].rstrip("/")


def probe_providers(rows: list[dict], keyless_only: bool) -> int:
    bad = 0
    for p in rows:
        if p["status"] == "retired" or p["kind"] == "local":
            continue
        env = p["router"].get("key_env")
        keyless = p["free_type"] == "keyless"
        if keyless_only and not keyless:
            continue
        key = os.environ.get(env, "") if env else ""
        if not keyless and not key:
            print(f"{p['id']:14} skipped: {env or 'no key_env'} not set")
            continue
        url = base_url(p)
        if not url:
            print(f"{p['id']:14} skipped: {p['router'].get('base_url_env')} not set")
            continue
        status, headers, _body, dt_ = request(f"{url.rstrip('/')}/models", key or None, timeout=30)
        v = verdict(status)
        bad += status != 200
        print(f"{p['id']:14} {v:20} {dt_:5.1f}s {limits(headers)}")
    return bad


def probe_router(chat_only: bool) -> int:
    key = os.environ.get("LITELLM_MASTER_KEY")
    if not key:
        print("LITELLM_MASTER_KEY not set (run with: uv run --env-file router/.env ...)")
        return 1
    bad = 0
    for lane in LANE_MODELS:
        body = {"model": lane, "max_tokens": 16, "messages": [{"role": "user", "content": "Reply with: ok"}]}
        status, headers, raw, dt_ = request(f"{ROUTER}/v1/chat/completions", key, body, timeout=180)
        served = headers.get("x-litellm-model-id") or headers.get("x-litellm-model-api-base", "")
        text = ""
        if status == 200:
            try:
                text = json.loads(raw)["choices"][0]["message"]["content"].strip()[:40]
            except (KeyError, IndexError, ValueError, AttributeError):
                text = "?"
        bad += status != 200
        print(f"{lane:13} {verdict(status):20} {dt_:5.1f}s {text!r} {served}")
    if not chat_only:
        body = {"model": "free/embed", "input": ["hello"]}
        status, _h, raw, dt_ = request(f"{ROUTER}/v1/embeddings", key, body, timeout=120)
        dims = ""
        if status == 200:
            try:
                dims = f"dims={len(json.loads(raw)['data'][0]['embedding'])}"
            except (KeyError, IndexError, ValueError):
                dims = "?"
        bad += status != 200
        print(f"{'free/embed':13} {verdict(status):20} {dt_:5.1f}s {dims}")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyless", action="store_true", help="only keyless endpoints (no secrets needed)")
    ap.add_argument("--router", action="store_true", help="call each lane on the local router")
    ap.add_argument("--chat-only", action="store_true", help="with --router: skip the embeddings lane")
    args = ap.parse_args()
    if args.router:
        bad = probe_router(args.chat_only)
    else:
        bad = probe_providers(load(), args.keyless)
    print(f"\n{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
