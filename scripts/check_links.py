"""Check every public URL in providers.yml, plans.yml and docs/**/*.md (stdlib only, plus pyyaml via _providers).

    uv run python scripts/check_links.py            # exit 1 if any link FAILs (404/410 or unreachable)
    uv run python scripts/check_links.py --stale    # also list providers not verified in 45 days

WARN (403, 429, 5xx, timeouts on bot-hostile sites) doesn't fail the run: many vendor pages block bots.
API base URLs are skipped: their bare root often returns 404 by design; probe_keys.py checks them.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import _plans
from _providers import ROOT, is_stale, load, all_urls

LINK_RE = re.compile(r"https://[^\s)\]>\"'`|]+")
SKIP = ("127.0.0.1", "localhost", "{", "<", "example.com", "host.docker.internal")
UA = "Mozilla/5.0 (X11; Linux x86_64) free-token-app-link-check"
FAIL_CODES = {404, 410}


def doc_urls() -> list[tuple[str, str]]:
    out = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        for url in LINK_RE.findall(path.read_text(encoding="utf-8")):
            out.append((str(path.relative_to(ROOT)), url.rstrip(".,;:")))
    for name in ("README.md",):
        path = ROOT / name
        if path.exists():
            for url in LINK_RE.findall(path.read_text(encoding="utf-8")):
                out.append((name, url.rstrip(".,;:")))
    return out


def fetch(url: str) -> tuple[str, str]:
    last = ""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return "OK", str(r.status)
        except urllib.error.HTTPError as e:
            last = str(e.code)
            if e.code in FAIL_CODES and method == "GET":
                return "FAIL", last
            if e.code in (405, 403, 404, 410, 400, 501):
                continue
            return "WARN", last
        except Exception as e:  # noqa: BLE001 - network errors of every kind
            last = type(e).__name__
    if last in {str(c) for c in FAIL_CODES}:
        return "FAIL", last
    if last == "URLError":  # DNS failure or connection refused; timeouts and resets only WARN
        return "FAIL", last
    return "WARN", last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stale", action="store_true")
    args = ap.parse_args()
    rows = load()
    plans = _plans.load()
    pairs = all_urls(rows) + _plans.all_urls(plans) + doc_urls()
    bases = ({(p.get("base_url") or "").rstrip("/") for p in rows} | _plans.base_urls(plans)) - {""}
    urls: dict[str, list[str]] = {}
    for where, url in pairs:
        if any(s in url for s in SKIP) or url.rstrip("/") in bases:
            continue
        urls.setdefault(url, []).append(where)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(urls, pool.map(fetch, urls)))
    counts = {"OK": 0, "WARN": 0, "FAIL": 0}
    for url, (state, code) in sorted(results.items(), key=lambda kv: kv[1][0]):
        counts[state] += 1
        if state != "OK":
            print(f"{state:4} {code:>18}  {url}  ({', '.join(sorted(set(urls[url]))[:3])})")
    print(f"\n{len(urls)} URLs: {counts['OK']} ok, {counts['WARN']} warn, {counts['FAIL']} fail")
    if args.stale:
        today = dt.date.today()
        stale = [p for p in rows if is_stale(p, today)]
        for p in stale:
            print(f"STALE {p['id']}: last_verified {p['last_verified']}")
        print(f"{len(stale)} stale providers")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
