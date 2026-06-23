#!/usr/bin/env python3
"""Audit ADR retirement readiness: registry coverage, SAD prose parity, UML diagrams."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_ROOT = REPO_ROOT / "docs" / "ADR"
ARCH = REPO_ROOT / "docs" / "architecture"
REGISTRY = ARCH / "project" / "DECISION_REGISTRY.md"
UML_ROOT = REPO_ROOT / "UML"
EVIDENCE_DEFAULT = ARCH / "evidence" / "adr-retirement-audit.md"

SKIP_ADR_FILES = frozenset(
    {
        "README.md",
        "adr-template.md",
        "migration_from_archive_2026-04-17.md",
        "adr-0058-director-driven-pulse-and-block-stream-bus.md",
        "adr-0021-runtime-authority.md",
    }
)

SKIP_SCAN_PREFIXES = (
    "'fy'-suites",
    "docs/archive",
    "node_modules",
    ".git",
)

BOILERPLATE_SECTIONS = frozenset(
    {
        "status",
        "date",
        "supersedes",
        "intellectual property rights",
        "privacy and confidentiality",
        "related adrs",
        "implementation status",
    }
)

OPEN_STATUSES = frozenset({"not finished", "proposed", "legacy"})

REGISTRY_ROW_RE = re.compile(
    r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|"
)


@dataclass
class RegistryEntry:
    adr_id: str
    status: str = ""
    sad_anchor: str = ""
    uml: str = ""
    gate: str = ""
    archive_sha: str = ""
    waiver: str = ""


@dataclass
class AuditResult:
    ready: list[str] = field(default_factory=list)
    enrich: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    missing_registry: list[str] = field(default_factory=list)
    inbound_refs: list[str] = field(default_factory=list)
    diagram_gaps: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


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
    for path in sorted(ADR_ROOT.rglob("*.md")):
        if path.name in SKIP_ADR_FILES:
            continue
        if adr_id_from_path(path) is None:
            continue
        files.append(path)
    return files


def parse_registry(text: str) -> dict[str, RegistryEntry]:
    entries: dict[str, RegistryEntry] = {}
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "ex-ADR-ID" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        adr_id = cells[0]
        if not REGISTRY_ROW_RE.match(f"| {adr_id} |"):
            continue
        entries[adr_id] = RegistryEntry(
            adr_id=adr_id,
            status=cells[1] if len(cells) > 1 else "",
            sad_anchor=cells[2] if len(cells) > 2 else "",
            uml=cells[3] if len(cells) > 3 else "",
            gate=cells[4] if len(cells) > 4 else "",
            archive_sha=cells[5] if len(cells) > 5 else "",
            waiver=cells[6] if len(cells) > 6 else "",
        )
    return entries


def read_adr_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines()[:30]:
        if line.startswith("## Status"):
            return line.split("## Status", 1)[1].strip(" :—-")
    m = re.search(r"^## Status\s*\n+(.+)$", text, re.M)
    return m.group(1).strip() if m else "Unknown"


def prose_words(text: str) -> set[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text.lower())
    words = {w for w in text.split() if len(w) > 3}
    return words


def adr_body_words(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks: list[str] = []
    current = []
    in_section = False
    section_title = ""
    for line in text.splitlines():
        if line.startswith("## "):
            if current and section_title.lower() not in BOILERPLATE_SECTIONS:
                chunks.append("\n".join(current))
            section_title = line[3:].strip()
            current = []
            in_section = True
            continue
        if in_section:
            current.append(line)
    if current and section_title.lower() not in BOILERPLATE_SECTIONS:
        chunks.append("\n".join(current))
    return prose_words("\n".join(chunks))


def normalize_anchor(anchor: str) -> str:
    return anchor.replace("../architecture/", "../").replace("(open exception) ", "")


def resolve_sad_anchor(anchor: str) -> Path | None:
    anchor = anchor.strip()
    if not anchor or anchor.lower() in {"—", "-", "open", "tbd", "(open)"}:
        return None
    anchor = normalize_anchor(anchor)
    for m in re.finditer(r"\]\(([^)]+)\)", anchor):
        raw = m.group(1).split()[0]
        if raw.startswith("http"):
            continue
        path_part = raw.split("#", 1)[0]
        if not path_part.endswith(".md"):
            continue
        candidate = (REGISTRY.parent / path_part).resolve()
        if candidate.is_file():
            return candidate
    return None


def sad_section_words(sad_path: Path, adr_id: str) -> set[str]:
    text = sad_path.read_text(encoding="utf-8", errors="replace")
    if "## 9. Architecture Decisions" not in text:
        return prose_words(text)
    section = text.split("## 9. Architecture Decisions", 1)[1]
    section = section.split("## 10.", 1)[0]
    # Try to find ### D block mentioning ADR
    blocks = re.split(r"(?=^### D\d+)", section, flags=re.M)
    for block in blocks:
        if adr_id.replace("ADR-", "ADR-") in block or adr_id in block:
            return prose_words(block)
    return prose_words(section)


def parity_ratio(adr_words: set[str], sad_words: set[str]) -> float:
    if not adr_words:
        return 1.0
    if not sad_words:
        return 0.0
    return len(adr_words & sad_words) / len(adr_words)


def has_mermaid(path: Path) -> bool:
    return "```mermaid" in path.read_text(encoding="utf-8", errors="replace")


def uml_has_mermaid_for_adr(adr_id: str) -> bool:
    needle = adr_id.lower().replace("adr-", "adr-")
    for md in UML_ROOT.rglob("*.md"):
        content = md.read_text(encoding="utf-8", errors="replace").lower()
        if needle in content and "```mermaid" in content:
            return True
    return False


def scan_inbound_adr_refs() -> list[str]:
    hits: list[str] = []
    scan_roots = [
        REPO_ROOT / "docs",
        REPO_ROOT / "tests",
        REPO_ROOT / "backend",
        REPO_ROOT / "world-engine",
        REPO_ROOT / "ai_stack",
        REPO_ROOT / "frontend",
        REPO_ROOT / "administration-tool",
        REPO_ROOT / "scripts",
    ]
    extra_files = [REPO_ROOT / "mkdocs.yml"]
    paths: list[Path] = list(extra_files)
    for root in scan_roots:
        if root.is_dir():
            paths.extend(root.rglob("*"))
    for path in paths:
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(rel.startswith(p) for p in SKIP_SCAN_PREFIXES):
            continue
        if path.suffix not in {".md", ".py", ".yml", ".yaml", ".ts", ".tsx", ".js"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "docs/ADR/" not in text and "docs\\ADR\\" not in text:
            continue
        if path.resolve() == REGISTRY.resolve():
            continue
        count = text.count("docs/ADR/")
        hits.append(f"{rel} ({count} refs)")
    return sorted(hits)


def audit(*, parity_threshold: float = 0.70) -> AuditResult:
    result = AuditResult()
    if not REGISTRY.is_file():
        result.errors.append(f"missing registry: {REGISTRY.relative_to(REPO_ROOT)}")
        return result

    registry = parse_registry(REGISTRY.read_text(encoding="utf-8"))
    adr_files = iter_adr_files()
    file_by_id: dict[str, Path] = {}
    for path in adr_files:
        aid = adr_id_from_path(path)
        if aid:
            file_by_id[aid] = path

    for path in adr_files:
        aid = adr_id_from_path(path)
        assert aid
        if aid not in registry:
            result.missing_registry.append(f"{aid} ({path.relative_to(REPO_ROOT)})")
            continue

        entry = registry[aid]
        status_line = read_adr_status(path).lower()
        is_open = any(s in status_line for s in OPEN_STATUSES) or any(
            s in entry.status.lower() for s in OPEN_STATUSES
        )

        if entry.waiver.lower() in {"yes", "waived", "true"}:
            result.ready.append(f"{aid} (waived)")
            continue

        if is_open:
            sad = resolve_sad_anchor(entry.sad_anchor)
            if not sad:
                result.blocked.append(f"{aid}: open status without SAD open-exception anchor")
            else:
                sad_text = sad.read_text(encoding="utf-8", errors="replace")
                ratio = parity_ratio(adr_body_words(path), sad_section_words(sad, aid))
                if aid in sad_text and ratio >= parity_threshold:
                    result.ready.append(f"{aid}: open exception (SAD enriched {ratio:.0%})")
                elif aid not in sad_text:
                    result.blocked.append(f"{aid}: open status; SAD anchor missing ADR reference")
                else:
                    result.blocked.append(f"{aid}: open exception — enrich SAD before archive ({ratio:.0%})")
            continue

        if has_mermaid(path) and not entry.uml.strip() and not uml_has_mermaid_for_adr(aid):
            result.diagram_gaps.append(aid)

        sad_path = resolve_sad_anchor(entry.sad_anchor)
        if not sad_path:
            result.enrich.append(f"{aid}: registry SAD anchor unresolved")
            continue

        ratio = parity_ratio(adr_body_words(path), sad_section_words(sad_path, aid))
        if ratio < parity_threshold:
            result.enrich.append(f"{aid}: prose parity {ratio:.0%} < {parity_threshold:.0%}")
        else:
            result.ready.append(f"{aid}: prose parity {ratio:.0%}")

    archive_root = REPO_ROOT / "docs" / "archive" / "adr-retired-2026"
    adr_readme = REPO_ROOT / "docs" / "ADR" / "README.md"
    active_adrs = list((REPO_ROOT / "docs" / "ADR").rglob("adr-*.md")) if adr_readme.is_file() else []
    post_retirement = archive_root.is_dir() and adr_readme.is_file() and not active_adrs
    for aid in sorted(set(registry) - set(file_by_id)):
        if post_retirement:
            continue
        result.errors.append(f"registry entry without ADR file: {aid}")

    result.inbound_refs = scan_inbound_adr_refs()
    return result


def render_report(result: AuditResult) -> str:
    today = date.today().isoformat()
    lines = [
        f"# ADR retirement audit — {today}",
        "",
        "Generated by [`scripts/adr_retirement_audit.py`](../../../scripts/adr_retirement_audit.py).",
        "",
        "## Summary",
        "",
        f"| Bucket | Count |",
        f"| --- | ---: |",
        f"| Ready | {len(result.ready)} |",
        f"| Enrich | {len(result.enrich)} |",
        f"| Blocked (open exceptions) | {len(result.blocked)} |",
        f"| Missing registry | {len(result.missing_registry)} |",
        f"| Diagram gaps | {len(result.diagram_gaps)} |",
        f"| Inbound ref files (scoped) | {len(result.inbound_refs)} |",
        "",
    ]
    for title, items in (
        ("Ready", result.ready),
        ("Enrich", result.enrich),
        ("Blocked", result.blocked),
        ("Missing registry", result.missing_registry),
        ("Diagram gaps (ADR mermaid, no UML)", result.diagram_gaps),
        ("Errors", result.errors),
    ):
        lines.append(f"## {title}")
        lines.append("")
        if items:
            for item in items:
                lines.append(f"- {item}")
        else:
            lines.append("- (none)")
        lines.append("")

    lines.append("## Inbound `docs/ADR/` references (excludes fy-suites, archive)")
    lines.append("")
    if result.inbound_refs:
        for item in result.inbound_refs[:80]:
            lines.append(f"- {item}")
        if len(result.inbound_refs) > 80:
            lines.append(f"- … and {len(result.inbound_refs) - 80} more")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit ADR retirement readiness.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if missing registry or blocked gaps.")
    parser.add_argument("--report", type=Path, nargs="?", const=EVIDENCE_DEFAULT)
    parser.add_argument("--parity-threshold", type=float, default=0.70)
    args = parser.parse_args()

    result = audit(parity_threshold=args.parity_threshold)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(result), encoding="utf-8")
        print(f"Wrote {args.report.relative_to(REPO_ROOT)}")

    if result.errors or result.missing_registry:
        for e in result.errors + [f"missing: {m}" for m in result.missing_registry]:
            print(e, file=sys.stderr)
        return 1 if args.check else 0

    if args.check and result.blocked:
        hard_blocked = [b for b in result.blocked if "missing ADR reference" in b]
        if hard_blocked:
            print(f"blocked: {hard_blocked}", file=sys.stderr)
            return 1

    print(
        f"OK: ready={len(result.ready)} enrich={len(result.enrich)} "
        f"blocked={len(result.blocked)} inbound_files={len(result.inbound_refs)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
