#!/usr/bin/env python3
"""Detect §9 hygiene issues: duplicate D headings, empty Status, orphan registry anchors."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCH = REPO_ROOT / "docs" / "architecture"
REGISTRY = ARCH / "project" / "DECISION_REGISTRY.md"

HEADING_RE = re.compile(r"^### (D\d+):\s*(.+)$", re.M)
STATUS_RE = re.compile(r"\*\*Status:\*\*\s*(\S.*)?$", re.M)
REGISTRY_ANCHOR_RE = re.compile(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|[^|]*\|\s*([^|]+?)\s*\|", re.M)


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s+", "-", slug)


def section9(text: str) -> str:
    if "## 9. Architecture Decisions" not in text:
        return ""
    part = text.split("## 9. Architecture Decisions", 1)[1]
    return part.split("## 10.", 1)[0]


def find_duplicate_d_headings(sad_path: Path) -> list[str]:
    text = sad_path.read_text(encoding="utf-8")
    s9 = section9(text)
    seen: dict[str, int] = {}
    dups: list[str] = []
    for m in HEADING_RE.finditer(s9):
        did = m.group(1)
        seen[did] = seen.get(did, 0) + 1
        if seen[did] > 1:
            dups.append(f"{sad_path.relative_to(REPO_ROOT)}: duplicate {did}")
    return dups


def find_empty_status(sad_path: Path) -> list[str]:
    """Report only; not a default --check failure (use --strict)."""
    issues: list[str] = []
    text = sad_path.read_text(encoding="utf-8")
    s9 = section9(text)
    for m in HEADING_RE.finditer(s9):
        did = m.group(1)
        start = m.start()
        nxt = HEADING_RE.search(s9, m.end())
        block = s9[start : nxt.start() if nxt else len(s9)]
        sm = STATUS_RE.search(block)
        if not sm or not sm.group(1) or not sm.group(1).strip():
            issues.append(f"{sad_path.relative_to(REPO_ROOT)}: {did} missing Status value")
    return issues


def _legacy_find_empty_status(sad_path: Path) -> list[str]:
    return find_empty_status(sad_path)


def find_orphan_registry_anchors() -> list[str]:
    if not REGISTRY.is_file():
        return ["DECISION_REGISTRY.md missing"]
    registry = REGISTRY.read_text(encoding="utf-8")
    issues: list[str] = []
    for m in REGISTRY_ANCHOR_RE.finditer(registry):
        adr_id, anchor = m.group(1), m.group(2).strip()
        if adr_id == "ex-ADR-ID" or anchor in ("—", "-", ""):
            continue
        if anchor == "—" or not anchor.startswith("["):
            issues.append(f"registry: {adr_id} has empty SAD anchor")
            continue
        link_m = re.search(r"\(([^)]+)\)", anchor)
        if not link_m:
            continue
        target = ARCH / "project" / link_m.group(1).split("#")[0]
        if link_m.group(1).startswith("../components/"):
            target = ARCH / link_m.group(1).split("#")[0].replace("../", "")
        elif link_m.group(1).startswith("../project/"):
            target = ARCH / "project" / link_m.group(1).split("#")[0].replace("../project/", "")
        elif "/" in link_m.group(1) and not link_m.group(1).startswith("http"):
            rel = link_m.group(1).split("#")[0]
            if rel.startswith("mvp-"):
                target = ARCH / "project" / rel
            elif rel.startswith("../"):
                target = (REGISTRY.parent / rel).resolve()
            else:
                target = ARCH / "project" / rel
        if not target.is_file():
            issues.append(f"registry: {adr_id} anchor target missing: {target.relative_to(REPO_ROOT)}")
    return issues


def iter_sads() -> list[Path]:
    paths: list[Path] = []
    for base in (ARCH / "components", ARCH / "project"):
        if not base.is_dir():
            continue
        for sad in sorted(base.glob("*/architecture.md")):
            if sad.parent.name.startswith("_"):
                continue
            paths.append(sad)
    return paths


def run_check(*, strict: bool = False) -> int:
    issues: list[str] = []
    for sad in iter_sads():
        issues.extend(find_duplicate_d_headings(sad))
        if strict:
            issues.extend(find_empty_status(sad))
    if strict:
        issues.extend(find_orphan_registry_anchors())
    if issues:
        print("SAD §9 hygiene FAILED:")
        for line in issues:
            print(f"  - {line}")
        return 1
    print("SAD §9 hygiene OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit 1 on duplicate D headings")
    parser.add_argument("--strict", action="store_true", help="Also fail on empty Status and orphan registry anchors")
    args = parser.parse_args()
    if args.check or args.strict:
        return run_check(strict=args.strict)
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
