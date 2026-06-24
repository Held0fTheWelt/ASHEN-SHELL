#!/usr/bin/env python3
"""Bulk-enrich SAD §9 decision blocks from ADR source files (ADR retirement Phase 2)."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "docs" / "architecture" / "project" / "DECISION_REGISTRY.md"
RETIRED_DATE = date.today().isoformat()

SKIP_ADR_FILES = frozenset(
    {
        "README.md",
        "adr-template.md",
        "migration_from_archive_2026-04-17.md",
        "adr-0058-director-driven-pulse-and-block-stream-bus.md",
        "adr-0021-runtime-authority.md",
    }
)

# When registry anchor is a contract (no §9), map to component SAD D slot
CONTRACT_OVERRIDES: dict[str, tuple[str, int]] = {
    "ADR-0042": ("docs/architecture/components/ai-stack/architecture.md", 13),
    "ADR-0043": ("docs/architecture/components/ai-stack/architecture.md", 14),
    "ADR-0055": ("docs/architecture/components/world-engine/architecture.md", 14),
    "MVP4-TEST-GATE-PLAN": ("docs/architecture/project/quality-gates/architecture.md", 2),
    "ADR-0023": ("docs/architecture/project/governance/architecture.md", 11),
    "ADR-0030": ("docs/architecture/project/ecosystem-topology/architecture.md", 2),
    "ADR-0031": ("docs/architecture/project/governance/architecture.md", 12),
    "ADR-0064": ("docs/architecture/project/quality-gates/architecture.md", 3),
}

# ADRs indexed in mvp SAD with ADR-* headings (not MVP*-*)
MVP_PROGRAM_ADRS = frozenset({"ADR-0022", "ADR-0032"})

# Extra SAD targets beyond registry primary anchor (adr_id -> list of (sad_rel, d_num))
SECONDARY_TARGETS: dict[str, list[tuple[str, int]]] = {
    "ADR-0039": [
        ("docs/architecture/project/quality-gates/architecture.md", 1),
    ],
}

# Special new D slots when anchor is generic §9
SPECIAL_D_SLOT: dict[str, int] = {
    "LANGFUSE-OBSERVABILITY": 6,
    "OBSERVABILITY-REDACTION-POLICY": 7,
}

SECTION_LABELS = (
    ("context", "Context"),
    ("1. context", "Context"),
    ("decision", "Decision"),
    ("2. decision", "Decision"),
    ("consequences", "Consequences"),
    ("3. consequences", "Consequences"),
    ("implementation status", "Implementation status"),
    ("affected services", "Affected services"),
    ("affected services/files", "Affected services"),
    ("follow-ups", "Follow-ups"),
    ("follow ups", "Follow-ups"),
    ("risks", "Risks"),
    ("testing", "Testing"),
)


def adr_id_from_path(path: Path) -> str | None:
    name = path.stem
    if name == "LANGFUSE_OBSERVABILITY":
        return "LANGFUSE-OBSERVABILITY"
    if name == "OBSERVABILITY_REDACTION_POLICY":
        return "OBSERVABILITY-REDACTION-POLICY"
    if name == "MVP4_TEST_GATE_PLAN":
        return "MVP4-TEST-GATE-PLAN"
    mvp = re.match(r"adr-mvp(\d+)-(\d+)", name)
    if mvp:
        return f"MVP{mvp.group(1)}-{mvp.group(2).zfill(3)}"
    if name == "adr-0037-content-locale-story-runtime":
        return "ADR-0037-CONTENT"
    m = re.match(r"adr-(\d{4})", name)
    if m:
        return f"ADR-{m.group(1)}"
    return None


def iter_adr_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted((REPO_ROOT / "docs" / "ADR").rglob("*.md")):
        if path.name in SKIP_ADR_FILES:
            continue
        if adr_id_from_path(path) is None:
            continue
        files.append(path)
    return files


def parse_registry(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "ex-ADR-ID" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        entries[cells[0]] = cells[2]
    return entries


def resolve_sad_anchor(anchor: str) -> Path | None:
    anchor = anchor.replace("../architecture/", "../")
    for m in re.finditer(r"\]\(([^)]+)\)", anchor):
        raw = m.group(1).split()[0].split("#", 1)[0]
        if raw.startswith("http") or not raw.endswith(".md"):
            continue
        candidate = (REGISTRY.parent / raw).resolve()
        if candidate.is_file():
            return candidate
    return None


def parse_d_from_anchor(anchor: str) -> int | None:
    m = re.search(r"#d(\d+)-", anchor, re.I)
    if m:
        return int(m.group(1))
    m2 = re.search(r"\bD(\d+)\b", anchor)
    if m2:
        return int(m2.group(1))
    return None


def strip_absorption_banner(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    skip = 0
    for line in lines:
        if skip and line.strip() == "":
            skip = 0
            continue
        if "> **Absorption" in line or line.strip().startswith("> **Absorption"):
            skip = 1
            continue
        if skip:
            continue
        out.append(line)
    return "\n".join(out)


def extract_sections(text: str) -> dict[str, str]:
    text = strip_absorption_banner(text)
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        if re.match(r"^## \d+\.\s+", line) or (line.startswith("## ") and not line.startswith("### ")):
            if current:
                sections[current] = "\n".join(buf).strip()
            title = re.sub(r"^##\s+", "", line).strip()
            title = re.sub(r"^\d+\.\s+", "", title)
            current = title.lower()
            buf = []
        elif current is not None:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def adr_title(path: Path) -> str:
    text = strip_absorption_banner(path.read_text(encoding="utf-8", errors="replace"))
    for line in text.splitlines():
        if line.startswith("# "):
            raw = line[2:].strip()
            if ":" in raw:
                return raw.split(":", 1)[1].strip()
            return raw
    return path.stem


def read_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Status\*\*:\s*([^\n*]+)", text, re.I)
    if m:
        return m.group(1).strip(" -*")
    for line in text.splitlines()[:25]:
        if line.startswith("## Status"):
            return line.split("## Status", 1)[1].strip(" :—-")
        if line.startswith("- **Status:**"):
            return line.split(":", 1)[1].strip()
    return "Accepted"


def rel_evidence_path(adr_path: Path) -> str:
    rel = adr_path.relative_to(REPO_ROOT).as_posix()
    depth = len(adr_path.relative_to(REPO_ROOT).parts) - 1
    prefix = "../" * (depth + 3)
    return f"`{rel}` (archived — see `docs/archive/adr-retired-2026/`)"


def build_d_block(
    d_num: int | None,
    mvp_id: str | None,
    title: str,
    adr_id: str,
    status: str,
    sections: dict[str, str],
    adr_path: Path,
) -> str:
    if mvp_id:
        heading = f"### {mvp_id}: {title}"
    else:
        assert d_num is not None
        heading = f"### D{d_num}: {title}"

    lines = [
        heading,
        "",
        f"**Status:** {status}",
        f"**Origin:** {adr_id} (retired {RETIRED_DATE})",
        "",
    ]
    used: set[str] = set()
    for key, label in SECTION_LABELS:
        body = sections.get(key, "")
        if not body or label in used:
            continue
        used.add(label)
        lines.append(f"**{label}.** {body}")
        lines.append("")

    if "Evidence" not in used:
        lines.append(f"**Evidence.** {rel_evidence_path(adr_path)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def split_section9(text: str) -> tuple[str, str, str]:
    if "## 9. Architecture Decisions" not in text:
        raise ValueError("missing §9")
    before, rest = text.split("## 9. Architecture Decisions", 1)
    if "## 10." not in rest:
        raise ValueError("missing §10")
    section9, after = rest.split("## 10.", 1)
    return before, section9, after


def replace_d_block(section9: str, d_num: int, new_block: str) -> str:
    pattern = re.compile(
        rf"^### D{d_num}:.*?(?=^### (?:D\d+:|MVP\d+-\d+:|ADR-\d{4}:)|\Z)",
        re.M | re.S,
    )
    m = pattern.search(section9)
    replacement = new_block.rstrip() + "\n\n"
    if m:
        return section9[: m.start()] + replacement + section9[m.end() :]
    return section9.rstrip() + "\n\n" + new_block


def replace_mvp_block(section9: str, mvp_id: str, new_block: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(mvp_id)}:.*?(?=^### (?:D\d+:|MVP\d+-\d+:|ADR-\d{4}:)|\Z)",
        re.M | re.S,
    )
    m = pattern.search(section9)
    replacement = new_block.rstrip() + "\n\n"
    if m:
        return section9[: m.start()] + replacement + section9[m.end() :]
    return section9.rstrip() + "\n\n" + new_block


def apply_enrichment(sad_path: Path, updates: list[tuple[str, int | str, str]]) -> bool:
    text = sad_path.read_text(encoding="utf-8")
    before, section9, after = split_section9(text)
    for kind, key, block in updates:
        if kind == "d":
            section9 = replace_d_block(section9, int(key), block)
        else:
            section9 = replace_mvp_block(section9, str(key), block)
    new_text = before + "## 9. Architecture Decisions" + section9 + "## 10." + after
    if new_text != text:
        sad_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def enrich_langfuse_section8(sad_path: Path, langfuse_text: str, redaction_text: str) -> None:
    text = sad_path.read_text(encoding="utf-8")
    block = (
        "## 8. Crosscutting Concepts\n\n"
        "Langfuse is the canonical AI/runtime observability provider when enabled; "
        "redaction policy applies before trace export.\n\n"
        "**Langfuse policy (ex-LANGFUSE_OBSERVABILITY).** "
        + strip_absorption_banner(langfuse_text).split("## Affected Services", 1)[0].strip()[:2000]
        + "\n\n"
        "**Redaction policy (ex-OBSERVABILITY_REDACTION_POLICY).** "
        + strip_absorption_banner(redaction_text).split("## ", 2)[0].strip()[:1200]
        + "\n\n"
        "Player input observability fields on spans (ADR-0033 §13.6).\n"
    )
    if "## 8. Crosscutting Concepts" in text:
        text = re.sub(
            r"## 8\. Crosscutting Concepts.*?(?=## 9\.)",
            block + "\n",
            text,
            count=1,
            flags=re.S,
        )
        sad_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk-enrich SAD §9 from ADR files.")
    parser.add_argument("--apply", action="store_true", help="Write SAD files (default: dry-run).")
    parser.add_argument("--adr-id", action="append", help="Limit to one ex-ADR-ID.")
    args = parser.parse_args()

    if not REGISTRY.is_file():
        print(f"missing registry: {REGISTRY}", file=sys.stderr)
        return 1

    registry = parse_registry(REGISTRY.read_text(encoding="utf-8"))
    pending: dict[Path, list[tuple[str, int | str, str]]] = {}
    count = 0

    for adr_path in iter_adr_files():
        aid = adr_id_from_path(adr_path)
        assert aid
        if args.adr_id and aid not in args.adr_id:
            continue
        if aid not in registry:
            print(f"skip {aid}: not in registry", file=sys.stderr)
            continue

        anchor = registry[aid]
        sad_path = resolve_sad_anchor(anchor)
        d_num = parse_d_from_anchor(anchor) or SPECIAL_D_SLOT.get(aid)
        if aid in CONTRACT_OVERRIDES:
            sad_rel, d_num = CONTRACT_OVERRIDES[aid]
            sad_path = (REPO_ROOT / sad_rel).resolve()
        if aid in MVP_PROGRAM_ADRS and not sad_path:
            sad_path = (REPO_ROOT / "docs/architecture/project/mvp-live-runtime-completion/architecture.md").resolve()

        if not sad_path:
            print(f"skip {aid}: unresolved anchor", file=sys.stderr)
            continue

        sections = extract_sections(adr_path.read_text(encoding="utf-8", errors="replace"))
        status = read_status(adr_path)
        title = adr_title(adr_path)
        if d_num is None:
            d_num = parse_d_from_anchor(anchor) or SPECIAL_D_SLOT.get(aid)

        if aid.startswith("MVP") or aid in MVP_PROGRAM_ADRS:
            block = build_d_block(None, aid, title, aid, status, sections, adr_path)
            pending.setdefault(sad_path, []).append(("mvp", aid, block))
        elif d_num:
            block = build_d_block(d_num, None, title, aid, status, sections, adr_path)
            pending.setdefault(sad_path, []).append(("d", d_num, block))
        else:
            print(f"skip {aid}: no D slot", file=sys.stderr)
            continue

        for sad_rel, sec_d in SECONDARY_TARGETS.get(aid, []):
            sec_path = (REPO_ROOT / sad_rel).resolve()
            block2 = build_d_block(sec_d, None, title, aid, status, sections, adr_path)
            pending.setdefault(sec_path, []).append(("d", sec_d, block2))

        count += 1

    if args.apply:
        obs = REPO_ROOT / "docs/architecture/project/observability-traceability/architecture.md"
        lf = REPO_ROOT / "docs/architecture/project/observability-traceability/architecture.md#d6-langfuse-canonical-observability-provider"
        rp = REPO_ROOT / "docs/architecture/project/observability-traceability/architecture.md#d7-observability-redaction-policy"
        if lf.is_file() and rp.is_file() and obs.is_file():
            enrich_langfuse_section8(
                obs,
                lf.read_text(encoding="utf-8"),
                rp.read_text(encoding="utf-8"),
            )

        changed = 0
        for sad_path, updates in sorted(pending.items(), key=lambda x: str(x[0])):
            if apply_enrichment(sad_path, updates):
                changed += 1
                print(f"updated {sad_path.relative_to(REPO_ROOT)} ({len(updates)} blocks)")
        print(f"enriched {count} ADRs across {changed} SAD files")
    else:
        print(f"dry-run: would enrich {count} ADRs across {len(pending)} SAD files")
        for sad_path, updates in sorted(pending.items(), key=lambda x: str(x[0])):
            print(f"  {sad_path.relative_to(REPO_ROOT)}: {len(updates)} blocks")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
