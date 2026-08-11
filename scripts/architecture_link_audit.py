#!/usr/bin/env python3
"""Audit internal markdown doc links under architecture docs and UML."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_PATHS = [
    REPO_ROOT / "docs" / "architecture" / "system",
    REPO_ROOT / "docs" / "architecture" / "components",
    REPO_ROOT / "docs" / "architecture" / "project",
    REPO_ROOT / "docs" / "architecture" / "scenarios",
    REPO_ROOT / "docs" / "architecture" / "data",
    REPO_ROOT / "docs" / "architecture" / "concepts",
    REPO_ROOT / "docs" / "architecture" / "decisions",
    REPO_ROOT / "docs" / "architecture" / "violations",
    REPO_ROOT / "docs" / "architecture" / "evidence",
    REPO_ROOT / "docs" / "architecture" / "START-HERE.md",
    REPO_ROOT / "docs" / "architecture" / "README.md",
    REPO_ROOT / "docs" / "architecture" / "QUALITY-STANDARD.md",
    REPO_ROOT / "docs" / "architecture" / "DOC-HEALTH.md",
    REPO_ROOT / "docs" / "architecture" / "AKDB-AUTHORITY.md",
    REPO_ROOT / "docs" / "architecture" / "AKDB-MIGRATION.md",
    REPO_ROOT / "docs" / "ADR" / "README.md",
    REPO_ROOT / "docs" / "dev" / "contracts" / "normative-contracts-index.md",
    REPO_ROOT / "UML",
]
SKIP_FILE_PARTS = {"_template", "<slug>"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)


def slugify_heading(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def collect_headings(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {slugify_heading(m.group(1)) for m in HEADING_RE.finditer(text)}


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for entry in SCAN_PATHS:
        if entry.is_file():
            files.append(entry)
        elif entry.is_dir():
            files.extend(entry.rglob("*.md"))
    out: list[Path] = []
    for md in files:
        if any(part in SKIP_FILE_PARTS for part in md.parts):
            continue
        if "<slug>" in md.name:
            continue
        out.append(md)
    return out


def resolve_link(source: Path, target: str) -> tuple[Path | None, str | None]:
    target = target.strip()
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None, None
    if target.startswith("#"):
        return source, target[1:]
    fragment: str | None = None
    path_part = target
    if "#" in target:
        path_part, fragment = target.split("#", 1)
    if not path_part:
        return source, fragment
    # Doc-to-doc only: ignore code tree links and bare directories
    if not path_part.endswith(".md"):
        return None, None
    return (source.parent / path_part).resolve(), fragment


def audit() -> list[str]:
    errors: list[str] = []
    for md in iter_markdown_files():
        text = md.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            raw = match.group(1).split()[0]
            resolved, fragment = resolve_link(md, raw)
            if resolved is None:
                continue
            if not resolved.is_file():
                errors.append(f"{md.relative_to(REPO_ROOT)}: missing target {raw}")
                continue
            if fragment:
                headings = collect_headings(resolved)
                if fragment not in headings:
                    errors.append(
                        f"{md.relative_to(REPO_ROOT)}: fragment #{fragment} not found in "
                        f"{resolved.relative_to(REPO_ROOT)}"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit architecture markdown links.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if any broken links.")
    parser.add_argument("--report", type=Path, help="Write markdown report to path.")
    args = parser.parse_args()
    errors = audit()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Architecture link audit",
            "",
            f"Broken links: **{len(errors)}**",
            "",
        ]
        if errors:
            lines.append("## Findings")
            lines.append("")
            for e in errors:
                lines.append(f"- {e}")
        else:
            lines.append("No broken internal doc links in scanned paths.")
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1 if args.check else 0
    print("OK: no broken links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
