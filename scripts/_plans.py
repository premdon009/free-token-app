"""Load and validate plans.yml: paid subscriptions, pay-per-token APIs and coding-harness quotas.

providers.yml stays the source for free API tiers and the router. plans.yml only feeds docs/paid/;
nothing in it reaches router/litellm.yaml or configs/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from _providers import ROOT, STALE_DAYS, TRAINS, _date, _yn  # noqa: F401  (STALE_DAYS re-exported)

PLANS = ROOT / "plans.yml"

KINDS = {"subscription", "payg", "harness"}
STATUSES = {"active", "unclear", "retired"}
API_ACCESS = {"yes", "no", "limited", "unknown"}
ROLES = {"orchestrator", "worker"}
ENDPOINTS = {"openai", "anthropic", "both", "native"}
REQUIRED = (
    "id", "name", "vendor", "kind", "status", "pricing_source", "trains_on_prompts",
    "api_access", "last_verified",
)


def _is_url(value: Any) -> bool:
    return str(value or "").startswith("https://")


def _is_price(value: Any) -> bool:
    return value is None or (isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0)


def validate(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for i, p in enumerate(rows):
        where = p.get("id") or f"row {i}"
        for f in REQUIRED:
            if f not in p or p[f] is None or p[f] == "":
                errors.append(f"{where}: missing '{f}'")
        if p.get("id") in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(p.get("id"))
        for field, allowed in (("kind", KINDS), ("status", STATUSES), ("trains_on_prompts", TRAINS),
                               ("api_access", API_ACCESS)):
            if field in p and p[field] not in allowed:
                errors.append(f"{where}: {field}={p[field]!r} not in {sorted(allowed)}")
        for f in ("pricing_source", "terms_source"):
            if p.get(f) and not _is_url(p[f]):
                errors.append(f"{where}: {f} must be an https URL")
        if _date(p.get("last_verified")) is None:
            errors.append(f"{where}: last_verified must be YYYY-MM-DD")
        kind = p.get("kind")
        if kind in ("subscription", "harness"):
            tiers = p.get("tiers")
            if not tiers:
                errors.append(f"{where}: a {kind} row needs tiers")
            for t in tiers or []:
                tw = f"{where}/{t.get('name', '?')}"
                if not t.get("name"):
                    errors.append(f"{where}: tier without name")
                if not t.get("limits"):
                    errors.append(f"{tw}: tier needs 'limits' (quote the plan page)")
                for f in ("usd_month", "inr_month"):
                    if not _is_price(t.get(f)):
                        errors.append(f"{tw}: {f} must be a number ≥ 0 or empty")
        if kind == "payg":
            if p.get("endpoint") not in ENDPOINTS:
                errors.append(f"{where}: endpoint must be one of {sorted(ENDPOINTS)}")
            models = p.get("models")
            if not models:
                errors.append(f"{where}: a payg row needs models")
            for m in models or []:
                mw = f"{where}/{m.get('id', '?')}"
                if not m.get("id"):
                    errors.append(f"{where}: model without id")
                if m.get("role") not in ROLES:
                    errors.append(f"{mw}: role must be one of {sorted(ROLES)}")
                for f in ("input", "output"):
                    if m.get(f) is None or not _is_price(m.get(f)):
                        errors.append(f"{mw}: '{f}' ($ per 1M tokens) is required and must be ≥ 0")
                if not _is_price(m.get("cached_input")):
                    errors.append(f"{mw}: cached_input must be a number ≥ 0 or empty")
    return errors


def load(path: Path = PLANS) -> list[dict]:
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    if not isinstance(rows, list):
        raise SystemExit(f"{path.name}: top level must be a list")
    for p in rows:
        for f in ("trains_on_prompts", "api_access"):
            if f in p:
                p[f] = _yn(p[f])
        p["last_verified"] = _date(p.get("last_verified")) or p.get("last_verified")
        p["tiers"] = p.get("tiers") or []
        p["models"] = p.get("models") or []
    errors = validate(rows)
    if errors:
        raise SystemExit(f"{path.name} is invalid:\n  " + "\n  ".join(errors))
    return rows


def all_urls(rows: list[dict]) -> list[tuple[str, str]]:
    """(where, url) for every public URL in plans.yml."""
    out = []
    for p in rows:
        for f in ("pricing_source", "terms_source", "docs_url"):
            if _is_url(p.get(f)):
                out.append((f"plans:{p['id']}.{f}", str(p[f])))
    return out


def base_urls(rows: list[dict]) -> set[str]:
    return {str(p.get("base_url") or "").rstrip("/") for p in rows} - {""}
