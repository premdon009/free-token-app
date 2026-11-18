"""Shared OpenAI client pointed at the local router."""

import os

from openai import OpenAI

BASE_URL = os.environ.get("ROUTER_URL", "http://127.0.0.1:4000/v1")


def client() -> OpenAI:
    key = os.environ.get("LITELLM_MASTER_KEY")
    if not key:
        raise SystemExit("export LITELLM_MASTER_KEY first (the value from router/.env)")
    # max_retries=2: the SDK retries 429/5xx with backoff; the router already falls back
    # across providers, so a couple of retries is enough.
    return OpenAI(base_url=BASE_URL, api_key=key, max_retries=2, timeout=120)
