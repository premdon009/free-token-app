"""Load and validate providers.yml (the single source of truth).

Every generator imports load(). Validation errors stop the build with one line per problem.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = ROOT / "providers.yml"

STALE_DAYS = 45

KINDS = {"provider", "inference", "aggregator", "local"}
FREE_TYPES = {"permanent", "renewable-credit", "trial", "keyless", "local"}
STATUSES = {"active", "unclear", "retired"}
TRAINS = {"yes", "no", "opt-out", "unknown"}
COMMERCIAL = {"yes", "no", "unknown"}
APIS = {"openai", "anthropic", "native"}
LANES = ("coding", "fast", "private", "embed", "local")
REQUIRED = (
    "id", "name", "kind", "free_type", "status", "card_required", "api", "base_url",
    "signup_url", "docs_url", "limits_source", "limits", "trains_on_prompts",
    "commercial_use", "models", "router", "last_verified",
)
CODING_MIN_CONTEXT = 64_000


def _yn(value: Any) -> Any:
    """YAML turns bare yes/no into booleans; map them back."""
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return value


def _date(value: Any) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def validate(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    key_envs: dict[str, str] = {}
    for i, p in enumerate(rows):
        where = p.get("id") or f"row {i}"
        for f in REQUIRED:
            if f not in p or p[f] is None or p[f] == "":
                errors.append(f"{where}: missing '{f}'")
        if p.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(p.get("id"))
        checks = (
            ("kind", KINDS), ("free_type", FREE_TYPES), ("status", STATUSES),
            ("trains_on_prompts", TRAINS), ("commercial_use", COMMERCIAL), ("api", APIS),
        )
        for field, allowed in checks:
            if field in p and p[field] not in allowed:
                errors.append(f"{where}: {field}={p[field]!r} not in {sorted(allowed)}")
        src = str(p.get("limits_source", ""))
        if src and not src.startswith(("https://", "http://")):
            errors.append(f"{where}: limits_source must be a URL")
        if _date(p.get("last_verified")) is None:
            errors.append(f"{where}: last_verified must be YYYY-MM-DD")
        if not isinstance(p.get("limits"), dict):
            errors.append(f"{where}: limits must be a mapping")
        router = p.get("router") or {}
        for lane in router.get("lanes", []):
            if lane not in LANES:
                errors.append(f"{where}: unknown lane {lane!r}")
        if "private" in router.get("lanes", []) and p.get("trains_on_prompts") != "no":
            errors.append(f"{where}: private lane needs trains_on_prompts 'no'")
        env = router.get("key_env")
        if env:
            if env in key_envs:
                errors.append(f"{where}: key_env {env} also used by {key_envs[env]}")
            key_envs[env] = where
        if router.get("include") and p.get("status") != "active":
            errors.append(f"{where}: only active providers can be in the router")
        if router.get("include") and p.get("kind") != "local" and not env and p.get("free_type") != "keyless":
            errors.append(f"{where}: router.include needs router.key_env")
        for m in p.get("models") or []:
            if "id" not in m:
                errors.append(f"{where}: model without id")
            for lane in m.get("lanes", []) or []:
                if lane not in LANES:
                    errors.append(f"{where}/{m.get('id')}: unknown lane {lane!r}")
    return errors


def load(path: Path = PROVIDERS) -> list[dict]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(rows, list):
        raise SystemExit(f"{path.name}: top level must be a list")
    for p in rows:
        for f in ("trains_on_prompts", "commercial_use"):
            if f in p:
                p[f] = _yn(p[f])
        p["last_verified"] = _date(p.get("last_verified")) or p.get("last_verified")
        p.setdefault("router", {})
        p.setdefault("models", [])
        p["models"] = p["models"] or []
    errors = validate(rows)
    if errors:
        raise SystemExit("providers.yml is invalid:\n  " + "\n  ".join(errors))
    return rows


def is_stale(p: dict, today: dt.date | None = None) -> bool:
    today = today or dt.date.today()
    lv = p.get("last_verified")
    return isinstance(lv, dt.date) and (today - lv).days > STALE_DAYS


def model_lanes(p: dict, m: dict) -> list[str]:
    """Lanes this model can serve, from its capabilities and the provider's router.lanes."""
    provider_lanes = (p.get("router") or {}).get("lanes", [])
    explicit = m.get("lanes")
    candidates = explicit if explicit is not None else provider_lanes
    local = p.get("kind") == "local"
    out = []
    for lane in candidates:
        if lane not in provider_lanes:
            continue
        if lane == "embed":
            if m.get("embedding"):
                out.append(lane)
            continue
        if m.get("embedding"):
            continue
        if lane == "coding" and not local:
            if not (m.get("tools") and (m.get("context") or 0) >= CODING_MIN_CONTEXT):
                continue
        if lane == "coding" and local and not m.get("tools"):
            continue
        if lane == "private" and p.get("trains_on_prompts") != "no":
            continue
        if lane == "local" and not local:
            continue
        out.append(lane)
    return out


def all_urls(rows: list[dict]) -> list[tuple[str, str]]:
    """(where, url) for every public URL in providers.yml."""
    out = []
    for p in rows:
        for f in ("signup_url", "docs_url", "limits_source", "trains_source"):
            url = p.get(f)
            if url and str(url).startswith("https://"):
                out.append((f"{p['id']}.{f}", str(url)))
    return out
