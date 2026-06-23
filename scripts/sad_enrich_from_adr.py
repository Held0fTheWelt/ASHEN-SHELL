#!/usr/bin/env python3
"""Extract ADR prose sections for SAD §9 enrichment (report-only helper)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_ROOT = REPO_ROOT / "docs" / "ADR"

SKIP_SECTIONS = frozenset(
    {
        "status",
        "date",
        "supersedes",
        "intellectual property rights",
        "privacy and confidentiality",
        "related adrs",
        "diagrams",
        "testing",
        "references",
    }
)


def extract_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            if current and current not in SKIP_SECTIONS:
                sections[current] = "\n".join(buf).strip()
            current = line[3:].strip().lower()
            buf = []
        elif current is not None:
            buf.append(line)
    if current and current not in SKIP_SECTIONS:
        sections[current] = "\n".join(buf).strip()
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Print ADR sections for manual SAD enrichment.")
    parser.add_argument("adr_path", type=Path, help="Path under docs/ADR/")
    args = parser.parse_args()
    path = args.adr_path if args.adr_path.is_absolute() else REPO_ROOT / args.adr_path
    text = path.read_text(encoding="utf-8")
    sections = extract_sections(text)
    for name, body in sections.items():
        print(f"## {name.title()}\n")
        print(body)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
