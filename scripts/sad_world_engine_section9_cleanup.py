#!/usr/bin/env python3
"""One-off hygiene: demote nested ADR ### headings to #### in world-engine SAD §9."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WE = REPO_ROOT / "docs" / "architecture" / "components" / "world-engine" / "architecture.md"

# Lines that are ADR sub-sections pasted as ### Dn — (not top-level SAD decisions)
SUB_HEADING_RE = re.compile(
    r"^### (D\d+[a-z]?)\s*[—\-]\s*(.+)$",
    re.M,
)

TOP_LEVEL_RE = re.compile(
    r"^### (D\d+): .+$",
    re.M,
)


def demote_sub_headings(text: str) -> str:
    top_level_positions = {m.start() for m in TOP_LEVEL_RE.finditer(text)}
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        m = SUB_HEADING_RE.match(line.rstrip("\n"))
        if m and line.startswith("### "):
            # Only demote if this looks like sub-heading (em dash or hyphen after Dn)
            out.append(f"#### {m.group(2).strip()}\n")
        else:
            out.append(line)
    return "".join(out)


def move_d16_after_d15(text: str) -> str:
    s9_start = text.index("## 9. Architecture Decisions")
    s10_start = text.index("## 10. Quality Requirements", s9_start)
    section = text[s9_start:s10_start]
    d16_m = re.search(
        r"(### D16: Retire Legacy Narrator.*?(?=### D7:))",
        section,
        re.S,
    )
    if not d16_m:
        return text
    d16_block = d16_m.group(1)
    section_wo = section[: d16_m.start()] + section[d16_m.end() :]
    d15_m = re.search(r"(### D15: W5 Narrator Strict.*)$", section_wo, re.S)
    if not d15_m:
        return text
    insert_at = d15_m.end()
    new_section = section_wo[:insert_at] + "\n\n" + d16_block.rstrip() + "\n"
    return text[:s9_start] + new_section + text[s10_start:]


STATUS_MAP = {
    "### D1:": "Accepted",
    "### D2:": "Accepted",
    "### D3:": "Accepted",
    "### D4:": "Accepted",
    "### D5:": "Accepted",
    "### D6:": "Partially implemented",
    "### D7:": "Accepted",
    "### D8:": "Accepted",
    "### D9:": "Accepted",
    "### D10:": "Partially implemented",
    "### D11:": "Accepted",
    "### D12:": "Accepted",
    "### D13:": "Accepted",
    "### D14:": "Accepted",
    "### D15:": "Proposed",
    "### D16:": "Proposed",
}


def fill_empty_status(text: str) -> str:
    for heading, status in STATUS_MAP.items():
        pattern = re.compile(
            rf"({re.escape(heading)}[^\n]*\n\n\*\*Status:\*\*)\s*\n",
            re.M,
        )
        text = pattern.sub(rf"\1 {status}\n", text, count=1)
    return text


def fix_decision_inline_headers(text: str) -> str:
    text = text.replace("**Decision.** ### D1 —", "**Decision.**\n\n####")
    text = text.replace("**Decision.** ### D1 -", "**Decision.**\n\n####")
    return text


def main() -> None:
    text = WE.read_text(encoding="utf-8")
    text = fix_decision_inline_headers(text)
    text = demote_sub_headings(text)
    text = move_d16_after_d15(text)
    text = fill_empty_status(text)
    WE.write_text(text, encoding="utf-8")
    print("world-engine §9 cleaned")


if __name__ == "__main__":
    main()
