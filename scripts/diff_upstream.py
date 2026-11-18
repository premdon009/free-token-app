"""Compare our providers with two upstream lists and print a Markdown report.

    uv run python scripts/diff_upstream.py                 # print the report
    uv run python scripts/diff_upstream.py -o report.md    # also write it to a file

Upstreams (both permissively licensed):
  - mnfst/awesome-free-llm-apis  data.json  (CC0)  matched on providers.yml `upstream.mnfst` (provider name)
  - mvalentsev/awesome-free-ai-coding  registry.yaml  (MIT)  matched on `upstream.mv` (entry id)

The report lists what upstream has that we don't (candidates to verify, never to copy blindly),
our rows that upstream dropped or marks delisted/retired, and base URL differences.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

import yaml

from _providers import load

MNFST = "https://raw.githubusercontent.com/mnfst/awesome-free-llm-apis/main/data.json"
MV = "https://raw.githubusercontent.com/mvalentsev/awesome-free-ai-coding/main/registry.yaml"
MV_CATEGORIES = {"api-free-tier", "aggregator"}


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "free-token-app-diff"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def norm(url: str | None) -> str:
    return (url or "").rstrip("/").lower()


def report(rows: list[dict], mnfst: dict, mv: dict) -> str:
    ours_m = {p["upstream"].get("mnfst"): p for p in rows if (p.get("upstream") or {}).get("mnfst")}
    ours_v = {p["upstream"].get("mv"): p for p in rows if (p.get("upstream") or {}).get("mv")}
    m_by_name = {e["name"]: e for e in mnfst.get("providers", [])}
    v_entries = [e for e in mv.get("entries", []) if e.get("category") in MV_CATEGORIES]
    v_by_id = {e["id"]: e for e in v_entries}

    lines = ["# Upstream diff", ""]
    lines.append(f"mnfst data.json lastUpdated **{mnfst.get('lastUpdated', '?')}**, "
                 f"{len(m_by_name)} providers · mvalentsev registry: {len(v_by_id)} API/aggregator entries.")
    lines.append("")

    new_m = sorted(n for n in m_by_name if n not in ours_m)
    new_v = sorted(i for i, e in v_by_id.items()
                   if i not in ours_v and not e.get("delisted") and not e.get("retired_on"))
    lines += ["## Upstream has, we don't (verify on the provider's own page before adding)", ""]
    lines += [f"- mnfst: **{n}** · {m_by_name[n].get('baseUrl') or m_by_name[n].get('url', '')}" for n in new_m] or ["- mnfst: none"]
    lines += [f"- mv: **{v_by_id[i].get('name', i)}** (`{i}`) · {v_by_id[i].get('url', '')}" for i in new_v] or ["- mv: none"]
    lines.append("")

    lines += ["## Ours, but upstream dropped or delisted it", ""]
    gone = []
    for name, p in sorted(ours_m.items()):
        if name not in m_by_name and p["status"] == "active":
            gone.append(f"- `{p['id']}`: not in mnfst any more (was **{name}**)")
    for vid, p in sorted(ours_v.items()):
        e = v_by_id.get(vid) or next((x for x in mv.get("entries", []) if x.get("id") == vid), None)
        if e is None and p["status"] == "active":
            gone.append(f"- `{p['id']}`: not in mv registry any more (was `{vid}`)")
        elif e and (e.get("delisted") or e.get("retired_on")) and p["status"] == "active":
            why = (e.get("delisted") or {}).get("reason") if isinstance(e.get("delisted"), dict) else e.get("retired_on")
            gone.append(f"- `{p['id']}`: mv marks it delisted/retired: {why}")
    lines += gone or ["- none"]
    lines.append("")

    lines += ["## Base URL differences", ""]
    diffs = []
    for name, p in ours_m.items():
        e = m_by_name.get(name)
        if e and e.get("baseUrl") and norm(e["baseUrl"]) != norm(p["base_url"]):
            diffs.append(f"- `{p['id']}`: ours `{p['base_url']}` · mnfst `{e['baseUrl']}`")
    for vid, p in ours_v.items():
        e = v_by_id.get(vid)
        base = ((e or {}).get("api") or {}).get("base_url")
        if base and norm(base) != norm(p["base_url"]):
            diffs.append(f"- `{p['id']}`: ours `{p['base_url']}` · mv `{base}`")
    lines += diffs or ["- none"]
    lines.append("")

    lines += ["## Training-policy differences (mv `data_use.trains`)", ""]
    tdiff = []
    for vid, p in ours_v.items():
        e = v_by_id.get(vid) or {}
        theirs = str(((e.get("data_use") or {}).get("trains")) or "").lower()
        if theirs and theirs != p["trains_on_prompts"]:
            tdiff.append(f"- `{p['id']}`: ours `{p['trains_on_prompts']}` · mv `{theirs}`")
    lines += tdiff or ["- none"]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--mnfst-file", type=Path, help="use a local copy of data.json")
    ap.add_argument("--mv-file", type=Path, help="use a local copy of registry.yaml")
    args = ap.parse_args()
    mnfst = json.loads(args.mnfst_file.read_bytes() if args.mnfst_file else get(MNFST))
    mv = yaml.safe_load(args.mv_file.read_bytes() if args.mv_file else get(MV))
    text = report(load(), mnfst, mv)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
