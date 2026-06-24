#!/usr/bin/env python3
"""Fill empty **Status:** in component SAD §9 blocks."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCH = REPO_ROOT / "docs" / "architecture" / "components"

DEFAULT_STATUS = "Accepted"


def fill_sad(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    if "## 9. Architecture Decisions" not in text:
        return 0
    s9 = text.split("## 9. Architecture Decisions", 1)[1].split("## 10.", 1)[0]
    count = 0
    blocks = re.split(r"(?=^### )", s9, flags=re.M)
    new_blocks = []
    for block in blocks:
        if not block.strip():
            new_blocks.append(block)
            continue
        if "**Status:**" in block and re.search(r"\*\*Status:\*\*\s*$", block, re.M):
            block = re.sub(r"(\*\*Status:\*\*)\s*$", rf"\1 {DEFAULT_STATUS}", block, count=1, flags=re.M)
            count += 1
        elif "**Status:**" in block and re.search(r"\*\*Status:\*\*\s*\n", block):
            block = re.sub(r"(\*\*Status:\*\*)\s*\n", rf"\1 {DEFAULT_STATUS}\n", block, count=1)
            count += 1
        new_blocks.append(block)
    if count:
        new_s9 = "".join(new_blocks)
        text = (
            text.split("## 9. Architecture Decisions", 1)[0]
            + "## 9. Architecture Decisions"
            + new_s9
            + text.split("## 10.", 1)[1]
        )
        path.write_text(text, encoding="utf-8")
    return count


def main() -> None:
    total = 0
    for sad in sorted(ARCH.glob("*/architecture.md")):
        if sad.parent.name.startswith("_"):
            continue
        n = fill_sad(sad)
        if n:
            print(f"{sad.parent.name}: filled {n} status fields")
            total += n
    print(f"total {total}")


if __name__ == "__main__":
    main()
