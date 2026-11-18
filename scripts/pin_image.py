"""Pin container images in router/compose.yaml by digest (stdlib only).

    uv run python scripts/pin_image.py litellm               # newest LiteLLM release >= 7 days old
    uv run python scripts/pin_image.py litellm --version 1.109.0
    uv run python scripts/pin_image.py --check              # exit 1 unless every image is tag@sha256
    uv run python scripts/pin_image.py --check --advisories # ...or the pinned LiteLLM has an advisory

LiteLLM shipped credential-stealing releases in 2026 (1.82.7, 1.82.8, 1.107.0 and the moving
`latest` / `main-stable` tags). So: never a moving tag, never a release younger than 7 days,
never a version on the blocklist below, and never a version covered by a published LiteLLM
GitHub security advisory (checked live; fails closed if the advisories can't be fetched). Read https://github.com/BerriAI/litellm/security before
bumping, and let Renovate propose the bump as a PR you review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request

from _providers import ROOT

COMPOSE = ROOT / "router" / "compose.yaml"
MIN_AGE_DAYS = 7
BLOCKLIST = {"1.82.7", "1.82.8", "1.107.0"}
MOVING = {"latest", "main-stable", "main-latest", "stable", "main"}
ACCEPT = ", ".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])
IMAGES = {
    "litellm": {"registry": "ghcr.io", "repo": "berriai/litellm",
                "token": "https://ghcr.io/token?scope=repository:berriai/litellm:pull"},
}
LINE_RE = {
    "litellm": re.compile(r"^(\s*image:\s*)ghcr\.io/berriai/litellm:\S+$", re.M),
}


def get_json(url: str, headers: dict | None = None):
    req = urllib.request.Request(url, headers={"User-Agent": "free-token-app-pin", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r), dict(r.headers)


def token(img: dict) -> str:
    data, _ = get_json(img["token"])
    return data.get("token") or data.get("access_token")


def tags(img: dict, tok: str) -> list[str]:
    url = f"https://{img['registry']}/v2/{img['repo']}/tags/list?n=100000"
    out: list[str] = []
    while url:
        data, headers = get_json(url, {"Authorization": f"Bearer {tok}"})
        out += data.get("tags") or []
        nxt = re.search(r"<([^>]+)>;\s*rel=\"next\"", headers.get("Link", ""))
        url = f"https://{img['registry']}{nxt.group(1)}" if nxt else ""
    return out


def digest(img: dict, tok: str, tag: str) -> str:
    url = f"https://{img['registry']}/v2/{img['repo']}/manifests/{tag}"
    req = urllib.request.Request(url, method="HEAD", headers={
        "Authorization": f"Bearer {tok}", "Accept": ACCEPT, "User-Agent": "free-token-app-pin"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = r.headers.get("Docker-Content-Digest")
    if not d:
        raise SystemExit(f"no digest returned for {img['repo']}:{tag}")
    return d


ADVISORIES = "https://api.github.com/repos/BerriAI/litellm/security-advisories?per_page=100"


def vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def advisories() -> list[tuple[str, list[tuple[str, tuple[int, ...]]]]]:
    """[(ghsa_id, [(op, bound), ...])] for every pip advisory with an upper bound."""
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    try:
        data, _ = get_json(ADVISORIES, headers)
    except (urllib.error.URLError, OSError) as e:
        raise SystemExit(f"can't fetch LiteLLM advisories ({e}); refusing to pick a version blind")
    out = []
    for adv in data:
        bounds = []
        for vuln in adv.get("vulnerabilities") or []:
            if (vuln.get("package") or {}).get("ecosystem") != "pip":
                continue
            for op, ver in re.findall(r"(<=|<)\s*([\w.\-]+)", vuln.get("vulnerable_version_range") or ""):
                bounds.append((op, vtuple(ver)))
        if bounds:
            out.append((adv.get("ghsa_id", "?"), bounds))
    return out


def affected_by(version: str, advs) -> list[str]:
    """Advisory ids that cover `version`.

    Advisories list one fixed release per release line ("< 1.108.6 | < 1.109.1"). A version is
    affected if it's below the bound for its own X.Y line, or if its line has no bound and it's
    older than the newest bound (conservative: may over-block very old versions, never under-blocks
    a listed line).
    """
    v = vtuple(version)
    hits = []
    for ghsa, bounds in advs:
        same = [(op, b) for op, b in bounds if b[:2] == v[:2]]
        if same:
            hit = any(v < b or (op == "<=" and v == b) for op, b in same)
        else:
            hit = v < max(b for _, b in bounds)
        if hit:
            hits.append(ghsa)
    return hits


def litellm_release(version: str | None) -> tuple[str, dt.datetime]:
    data, _ = get_json("https://pypi.org/pypi/litellm/json")
    now = dt.datetime.now(dt.timezone.utc)
    candidates = []
    for v, files in data["releases"].items():
        if not files or any(f.get("yanked") for f in files) or v in BLOCKLIST:
            continue
        if not re.fullmatch(r"\d+\.\d+\.\d+", v):
            continue  # skip rc / dev / post releases
        uploaded = min(dt.datetime.fromisoformat(f["upload_time_iso_8601"].replace("Z", "+00:00")) for f in files)
        candidates.append((v, uploaded))
    advs = advisories()
    if version:
        hits = affected_by(version, advs)
        if hits:
            raise SystemExit(f"litellm {version} is covered by advisories: {', '.join(hits)}")
        match = [c for c in candidates if c[0] == version]
        if not match:
            raise SystemExit(f"litellm {version}: not on PyPI, yanked, pre-release or blocklisted")
        v, up = match[0]
        if (now - up).days < MIN_AGE_DAYS:
            raise SystemExit(f"litellm {v} is only {(now - up).days} days old (need {MIN_AGE_DAYS})")
        return v, up
    old = [c for c in candidates if (now - c[1]).days >= MIN_AGE_DAYS and not affected_by(c[0], advs)]
    old.sort(key=lambda c: tuple(int(x) for x in c[0].split(".")))
    if not old:
        raise SystemExit("no litellm release is both old enough and free of known advisories")
    return old[-1]


def pick_litellm_tag(all_tags: list[str], version: str) -> str:
    for t in (f"main-v{version}-stable", f"v{version}-stable", f"main-v{version}", f"v{version}"):
        if t in all_tags:
            return t
    near = [t for t in all_tags if version in t][:10]
    raise SystemExit(f"no image tag for litellm {version}; tags containing it: {near}")


def write(name: str, ref: str) -> None:
    text = COMPOSE.read_text(encoding="utf-8")
    new, n = LINE_RE[name].subn(lambda m: f"{m.group(1)}{ref}", text)
    if n != 1:
        raise SystemExit(f"expected one {name} image line in {COMPOSE.name}, found {n}")
    COMPOSE.write_text(new, encoding="utf-8")
    print(f"{COMPOSE.relative_to(ROOT)}: {ref}")


def check(with_advisories: bool = False) -> int:
    text = COMPOSE.read_text(encoding="utf-8")
    advs = advisories() if with_advisories else []
    bad = 0
    for line in re.findall(r"^\s*image:\s*(\S+)", text, re.M):
        tag = line.split("@")[0].rsplit(":", 1)[-1]
        if "@sha256:" not in line or tag in MOVING or "PIN_ME" in line:
            print(f"not pinned by digest: {line}")
            bad += 1
        m = re.search(r"v?(\d+\.\d+\.\d+)", tag)
        if "litellm" in line and m and m.group(1) in BLOCKLIST:
            print(f"blocklisted litellm version: {line}")
            bad += 1
        if "litellm" in line and m and advs and (hits := affected_by(m.group(1), advs)):
            print(f"litellm {m.group(1)} has security advisories {', '.join(hits)}: re-pin")
            bad += 1
    print("all images pinned by digest" if not bad else "run: uv run python scripts/pin_image.py litellm")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", nargs="?", choices=sorted(IMAGES))
    ap.add_argument("--version", help="litellm: exact release (must be >= 7 days old)")
    ap.add_argument("--tag", help="exact image tag (default: picked from the version)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--advisories", action="store_true", help="with --check: also fail on advisories")
    args = ap.parse_args()
    if args.check:
        return check(args.advisories)
    if not args.image:
        ap.error("give an image name or --check")
    img = IMAGES[args.image]
    tok = token(img)
    version, uploaded = litellm_release(args.version)
    tag = args.tag or pick_litellm_tag(tags(img, tok), version)
    if tag in MOVING:
        raise SystemExit(f"refusing moving tag {tag}")
    print(f"litellm {version}, on PyPI since {uploaded:%Y-%m-%d}, image tag {tag}")
    write(args.image, f"{img['registry']}/{img['repo']}:{tag}@{digest(img, tok, tag)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
