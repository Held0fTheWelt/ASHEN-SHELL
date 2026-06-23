#!/usr/bin/env python3
"""Post-retirement fixes: ADR links → archive, sync DECISION_REGISTRY anchors to SAD headings."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCH = REPO_ROOT / "docs" / "architecture"
REGISTRY = ARCH / "project" / "DECISION_REGISTRY.md"
ARCHIVE_PREFIX = "docs/archive/adr-retired-2026/"


def slugify_heading(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def heading_slugs(text: str) -> dict[str, str]:
    """Map D-number -> slug for ### Dn: headings."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^### (D\d+):\s*(.+)$", text, re.M):
        did, title = m.group(1), m.group(2).strip()
        out[did] = slugify_heading(f"{did}: {title}")
    return out


def rewrite_adr_links(text: str, source: Path) -> str:
    archive_root = REPO_ROOT / "docs" / "archive" / "adr-retired-2026"

    def archive_link(archive_rel: str, frag: str = "") -> str:
        target = archive_root / archive_rel.replace("\\", "/")
        if not target.is_file():
            return f"`docs/archive/adr-retired-2026/{archive_rel}`"
        rel = Path(__import__("os").path.relpath(target, source.parent)).as_posix()
        return f"]({rel}{('#' + frag) if frag else ''})"

    def sub_link(m: re.Match[str]) -> str:
        path = m.group(1).replace("\\", "/")
        frag = m.group(2) or ""
        if "MVP_Live_Runtime_Completion/" in path:
            sub = path.split("MVP_Live_Runtime_Completion/", 1)[1]
            return archive_link(f"MVP_Live_Runtime_Completion/{sub}", frag)
        name = path.split("/")[-1]
        return archive_link(name, frag)

    text = re.sub(
        r"\]\((?:\.\./)*(?:docs/)?(?:ADR/)?(?:MVP_Live_Runtime_Completion/)?"
        r"((?:adr-[\w-]+\.md)|(?:adr-mvp[\w-]+\.md)|(?:LANGFUSE_OBSERVABILITY\.md)|"
        r"(?:OBSERVABILITY_REDACTION_POLICY\.md)|(?:MVP4_TEST_GATE_PLAN\.md))"
        r"(?:#([^)]+))?\)",
        sub_link,
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\]\((adr-[\w-]+\.md)(?:#([^)]+))?\)",
        sub_link,
        text,
    )
    text = re.sub(
        r"\]\(docs/archive/adr-retired-2026/([^)#]+)(?:#([^)]+))?\)",
        lambda m: "]("
        + Path(__import__("os").path.relpath(archive_root / m.group(1), source.parent)).as_posix()
        + (f"#{m.group(2)}" if m.group(2) else "")
        + ")",
        text,
    )
    return text


def sync_registry() -> int:
    rows: list[str] = []
    updated = 0
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "ex-ADR-ID" in line:
            rows.append(line)
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            rows.append(line)
            continue
        anchor = cells[2]
        m = re.search(r"\]\(([^)#]+)(#([^)]+))?\)", anchor)
        if not m:
            rows.append(line)
            continue
        path_part = m.group(1).replace("../architecture/", "../")
        sad_path = (REGISTRY.parent / path_part).resolve()
        if not sad_path.is_file():
            rows.append(line)
            continue
        slugs = heading_slugs(sad_path.read_text(encoding="utf-8"))
        dm = re.search(r"\bD(\d+)\b", anchor)
        if dm:
            did = f"D{dm.group(1)}"
            if did in slugs:
                new_frag = slugs[did]
                if m.group(3) != new_frag:
                    new_anchor = re.sub(r"#([^)]+)", f"#{new_frag}", anchor, count=1)
                    cells[2] = new_anchor
                    updated += 1
        rows.append("| " + " | ".join(cells) + " |")
    REGISTRY.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return updated


FRAGMENT_FIXES: dict[str, str] = {
    "#d12-controlled-runtime-capability-authority": "#d3-runtime-rag-context-fabric-routing-and-authority-boundaries",
    "#d2-proposal-only-ai-until-validator-approval": "#d2-runtime-model-output-is-proposal-only-until-validator-approval",
    "#d4-director-realization-thin-path": "#d4-director-realization-thin-path-resolver-director-narrator",
    "#d3-admin-control-plane": "#d3-security-governance-admin-control-plane",
    "#d3-content-locale-removal-language-boundaries": "#d3-remove-content-locale-runtime-lookups",
    "#d3-live-runtime-commit-semantics": "#d3-live-runtime-commit-semantics-for-real-ai-mock-fallback-and-visible-story-output",
    "#d2-quality-lab-mcp-diagnostics": "#d2-quality-lab-mcp-runtime-diagnostics-and-judge-guided-improvement",
    "#d7-observability-redaction-policy": "#d7-observability-redaction-and-trace-correlation-policy",
    "#d6-langfuse-canonical-observability-provider": "#d6-langfuse-as-canonical-airuntime-observability-provider",
    "#adr-0022-mvp-expansion-decision-rule": "#adr-0022-mvp-expansion-decision-rule-when-not-to-expand-the-platform",
    "#d2-mvp4-test-gate-plan": "#mvp4-test-gate-plan-mvp4-test-gate-plan-5-core-contracts",
}

PATH_SUBS: list[tuple[str, str]] = [
    ("](../MVPs/", "](../../../MVPs/"),
    ("](../security/", "](../../../security/"),
    ("](../technical/", "](../../../technical/"),
    ("](../dev/", "](../../../dev/"),
    ("](../testing-setup.md", "](../../../testing-setup.md"),
    ("](../dev/contributing.md", "](../../../dev/contributing.md"),
    ("../../../MVPs/NPC_INTERACTION_AND_INTERACTIVITY_PLAN.md", "../../../../NPC_INTERACTION_AND_INTERACTIVITY_PLAN.md"),
    (
        "../../../archive/adr-retired-2026/adr-mvp5-001-modular-block-rendering-architecture.md",
        "../../../archive/adr-retired-2026/MVP_Live_Runtime_Completion/adr-mvp5-001-modular-block-rendering-architecture.md",
    ),
    (
        "../architecture/components/world-engine/architecture.md",
        "architecture.md",
    ),
    ("../../MVPs/capability_matrix", "../../../MVPs/capability_matrix"),
]


def apply_fragment_and_path_fixes(text: str) -> str:
    for old, new in FRAGMENT_FIXES.items():
        text = text.replace(old, new)
    for old, new in PATH_SUBS:
        text = text.replace(old, new)
    return text


def dedupe_d_blocks(sad_path: Path) -> bool:
    text = sad_path.read_text(encoding="utf-8")
    if "## 9. Architecture Decisions" not in text:
        return False
    before, rest = text.split("## 9. Architecture Decisions", 1)
    s9, after = rest.split("## 10.", 1)
    seen: set[str] = set()
    blocks = re.split(r"(?=^### (?:D\d+|MVP\d+-\d+|ADR-\d{4}):)", s9, flags=re.M)
    out_parts: list[str] = []
    changed = False
    for block in blocks:
        if not block.strip():
            out_parts.append(block)
            continue
        hm = re.match(r"^### (D\d+|MVP\d+-\d+|ADR-\d{4}):", block)
        if not hm:
            out_parts.append(block)
            continue
        key = hm.group(1)
        if key in seen:
            changed = True
            continue
        seen.add(key)
        out_parts.append(block)
    if not changed:
        return False
    sad_path.write_text(before + "## 9. Architecture Decisions" + "".join(out_parts) + "## 10." + after, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for md in ARCH.rglob("*.md"):
        original = md.read_text(encoding="utf-8")
        new = apply_fragment_and_path_fixes(rewrite_adr_links(original, md))
        if new != original:
            md.write_text(new, encoding="utf-8")
            changed += 1
    print(f"rewrote ADR links in {changed} architecture markdown files")
    for sad in ARCH.rglob("architecture.md"):
        if dedupe_d_blocks(sad):
            print(f"deduped {sad.relative_to(REPO_ROOT)}")
    n = sync_registry()
    print(f"synced {n} registry anchor fragments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
