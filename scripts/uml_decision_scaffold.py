#!/usr/bin/env python3
"""Scaffold UML decision markdown from archive ADR mermaid blocks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = REPO_ROOT / "docs" / "archive" / "adr-retired-2026"
UML_ROOT = REPO_ROOT / "UML"

MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.S)


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug)[:80]


def find_adr_file(adr_id: str) -> Path | None:
    num = adr_id.replace("ADR-", "")
    for path in ARCHIVE.rglob(f"adr-{num}*.md"):
        if path.name in ("adr-template.md",):
            continue
        return path
    return None


def extract_mermaid(adr_path: Path) -> str | None:
    text = adr_path.read_text(encoding="utf-8")
    m = MERMAID_RE.search(text)
    return m.group(1).strip() if m else None


def decision_path(component: str, d_num: int, title: str) -> Path:
    return (
        UML_ROOT
        / "Components"
        / component
        / "decisions"
        / f"d{d_num}-{slugify(title)}.md"
    )


def scaffold(component: str, d_num: int, title: str, origin: str, *, apply: bool) -> Path:
    out = decision_path(component, d_num, title)
    if out.is_file():
        return out
    diagram = ""
    adr = find_adr_file(origin)
    if adr:
        mm = extract_mermaid(adr)
        if mm:
            diagram = f"\n## Diagram\n\n```mermaid\n{mm}\n```\n"
    body = f"""# D{d_num}: {title}

**Owner SAD:** [ai-stack SAD](../../../docs/architecture/components/{component}/architecture.md#d{d_num}-{slugify(title)})
**Origin:** {origin} (retired)
**Status:** Accepted

## Context

See owning SAD §9 D{d_num} for normative context.

## Decision

Distilled normative statement lives in the component SAD §9 block.
{diagram}
## Evidence

See SAD §9 D{d_num} **Evidence.** row and [mechanism catalog](../../../docs/architecture/components/{component}/mechanism-catalog.md).
"""
    if apply:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        print(f"created {out.relative_to(REPO_ROOT)}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True)
    parser.add_argument("--d-num", type=int, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--origin", required=True, help="ADR-00xx")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    scaffold(args.component, args.d_num, args.title, args.origin, apply=args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
