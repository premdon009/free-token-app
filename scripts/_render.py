"""Small Markdown helpers shared by the page generators (gen_catalog.py, gen_plans.py)."""

from __future__ import annotations

from pathlib import Path

STATUS_BADGE = {"active": "", "unclear": " ⚠️ unclear", "retired": " ❌ retired"}
TRAINS_LABEL = {"yes": "🔴 yes", "no": "🟢 no", "opt-out": "🟠 opt-out", "unknown": "⚪ unknown"}


def esc(text: object) -> str:
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def yesno(v: object) -> str:
    return "yes" if v else "no"


def fmt_int(n: object) -> str:
    if n is None or n == "":
        return "—"
    n = int(n)
    if n >= 1_000_000 and n % 1_000_000 == 0:
        return f"{n // 1_000_000}M"
    if n >= 1_000_000:
        return f"{n / 1_048_576:.0f}M" if n % 1_048_576 == 0 else f"{n:,}"
    if n >= 1000 and n % 1000 == 0:
        return f"{n // 1000}K"
    if n >= 1000 and n % 1024 == 0:
        return f"{n // 1024}K"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def write_or_check(pages: dict[Path, str], root: Path, check: bool, what: str, regen: str) -> int:
    """Write generated pages, or with check=True report the ones that are out of date."""
    if check:
        stale_files = [p for p, text in pages.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        for p in stale_files:
            print(f"out of date: {p.relative_to(root)}")
        if stale_files:
            print(f"run: {regen}")
            return 1
        print(f"{what} up to date ({len(pages)} pages)")
        return 0
    for p, text in pages.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print(f"wrote {len(pages)} pages")
    return 0
