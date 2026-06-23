#!/usr/bin/env python3
"""Bootstrap docs/architecture/project/DECISION_REGISTRY.md from ADR README + filesystem."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_README = REPO_ROOT / "docs" / "ADR" / "README.md"
REGISTRY = REPO_ROOT / "docs" / "architecture" / "project" / "DECISION_REGISTRY.md"

SKIP_FILES = frozenset(
    {
        "README.md",
        "adr-template.md",
        "migration_from_archive_2026-04-17.md",
        "adr-0058-director-driven-pulse-and-block-stream-bus.md",
        "adr-0021-runtime-authority.md",
    }
)

MVP_SAD = "[mvp-live-runtime-completion §9](mvp-live-runtime-completion/architecture.md#9-architecture-decisions)"

ANCHOR_OVERRIDES: dict[str, str] = {
    "ADR-0006": "[governance D6](../project/governance/architecture.md#d6-revision-review-state-machine)",
    "ADR-0007": "[governance D7](../project/governance/architecture.md#d7-revision-conflict-governance-objects)",
    "ADR-0009": "[governance D8](../project/governance/architecture.md#d8-evaluation-as-promotion-gate)",
    "ADR-0010": "[governance D9](../project/governance/architecture.md#d9-event-driven-governance-workflows)",
    "ADR-0013": "[world-engine D12](../components/world-engine/architecture.md#d12-preview-session-isolation)",
    "ADR-0014": "[ai-stack D11](../components/ai-stack/architecture.md#d11-player-affect-enum-signals)",
    "ADR-0018": "[ai-stack D8](../components/ai-stack/architecture.md#d8-role-aware-aidecisionlog)",
    "ADR-0019": "[ai-stack D9](../components/ai-stack/architecture.md#d9-proposalsource-and-responder-gating)",
    "ADR-0024": "[governance D10](../project/governance/architecture.md#d10-decision-boundary-record-schema)",
    "ADR-0035": "[world-engine D13](../components/world-engine/architecture.md#d13-story-opening-economy-and-warmup)",
    "ADR-0037-CONTENT": "[content-authority D3](../components/content-authority/architecture.md#d3-content-locale-removal-language-boundaries)",
    "ADR-0038": "[world-engine D5](../components/world-engine/architecture.md#d5-canonical-turn-lifecycle-single-commit-path)",
    "ADR-0041": "[ai-stack D12](../components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority)",
    "ADR-0044": "[ai-stack D3](../components/ai-stack/architecture.md#d3-rag-fabric-routing)",
    "ADR-0045": "[ai-stack D4](../components/ai-stack/architecture.md#d4-memory-indexes-retrieval-writes)",
    "ADR-0046": "[frontend D2](../components/frontend/architecture.md#d2-typewriter-cinematic-direction)",
    "ADR-0058": "[ai-stack D12](../components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority)",
    "ADR-0059": "[ai-stack D12](../components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority)",
    "ADR-0060": "[ai-stack D7](../components/ai-stack/architecture.md#d7-player-guidance-and-souffleuse-lanes)",
    "ADR-0061": "[ai-stack D12](../components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority)",
    "ADR-0063": "[world-engine D6](../components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view)",
    "ADR-0065": "[world-engine D15](../components/world-engine/architecture.md#d15-w5-actor-tracking-follow-up)",
    "ADR-0071": "[world-engine D16](../components/world-engine/architecture.md#d16-retire-legacy-narrator-consequence-area-fields)",
    "ADR-0005": "[ai-stack D10](../components/ai-stack/architecture.md#d10-research-may-draft-but-not-publish)",
    "ADR-0008": "[world-engine D11](../components/world-engine/architecture.md#d11-explicit-configurable-validation-strategy)",
    "ADR-0042": "[ai-stack D13](../components/ai-stack/architecture.md#d13-meta-narrative-awareness-opt-in)",
    "ADR-0043": "[ai-stack D14](../components/ai-stack/architecture.md#d14-adaptive-meta-narrative-awareness)",
    "ADR-0055": "[world-engine D14](../components/world-engine/architecture.md#d14-semantic-player-input-translation-ingress)",
    "MVP4-TEST-GATE-PLAN": "[quality-gates MVP4-TEST-GATE-PLAN](../project/quality-gates/architecture.md#mvp4-test-gate-plan-mvp4-test-gate-plan-5-core-contracts)",
    "ADR-0022": "[mvp-live-runtime-completion ADR-0022](../project/mvp-live-runtime-completion/architecture.md#adr-0022-mvp-expansion-decision-rule-when-not-to-expand-the-platform)",
    "ADR-0023": "[governance D11](../project/governance/architecture.md#d11-decision-framework-risk-and-kill-criteria)",
    "ADR-0030": "[ecosystem-topology D2](../project/ecosystem-topology/architecture.md#d2-docker-up-complete-bootstrap)",
    "ADR-0031": "[governance D12](../project/governance/architecture.md#d12-env-configuration-governance)",
    "ADR-0032": "[mvp-live-runtime-completion ADR-0032](../project/mvp-live-runtime-completion/architecture.md#adr-0032-mvp4-live-runtime-setup-requirements)",
    "ADR-0064": "[quality-gates D3](../project/quality-gates/architecture.md#d3-python-314-unified-interpreter-standard)",
    "LANGFUSE-OBSERVABILITY": "[observability D6](../project/observability-traceability/architecture.md#d6-langfuse-canonical-observability-provider)",
    "OBSERVABILITY-REDACTION-POLICY": "[observability D7](../project/observability-traceability/architecture.md#d7-observability-redaction-policy)",
}


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


def parse_readme_anchors() -> dict[str, tuple[str, str]]:
    text = ADR_README.read_text(encoding="utf-8")
    out: dict[str, tuple[str, str]] = {}
    row_re = re.compile(
        r"^\|\s*\[(ADR-\d{4})\]\([^)]+\)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
        re.M,
    )
    for m in row_re.finditer(text):
        adr_id, _title, status, anchor = (g.strip() for g in m.groups())
        out[adr_id] = (status, anchor)
    return out


def read_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines()[:20]:
        if line.startswith("## Status"):
            return re.sub(r"\s*—.*$", "", line.split("## Status", 1)[1]).strip(" :")
    return "Unknown"


def default_anchor(aid: str) -> str:
    if aid.startswith("MVP"):
        return MVP_SAD
    if aid.startswith("LANGFUSE") or aid.startswith("OBSERVABILITY"):
        return "[observability-traceability SAD](../project/observability-traceability/architecture.md#9-architecture-decisions)"
    if aid == "MVP4-TEST-GATE-PLAN":
        return "[quality-gates SAD](../project/quality-gates/architecture.md#9-architecture-decisions)"
    if aid == "ADR-0021":
        return "[world-engine D1](../components/world-engine/architecture.md#d1-runtime-authority-in-world-engine) (superseded)"
    return "—"


def iter_adr_sources() -> list[Path]:
    """Active ADR tree, or archive mirror after retirement."""
    active = [
        p
        for p in sorted((REPO_ROOT / "docs" / "ADR").rglob("*.md"))
        if p.name not in SKIP_FILES and adr_id_from_path(p)
    ]
    if active:
        return active
    archive = REPO_ROOT / "docs" / "archive" / "adr-retired-2026"
    return [
        p
        for p in sorted(archive.rglob("*.md"))
        if p.name not in SKIP_FILES and p.name != "README.md" and adr_id_from_path(p)
    ]


def main() -> None:
    readme = parse_readme_anchors() if ADR_README.is_file() else {}
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for path in iter_adr_sources():
        aid = adr_id_from_path(path)
        if not aid:
            continue
        if aid in readme:
            status, anchor = readme[aid]
            anchor = anchor.replace("../architecture/", "../")
        else:
            status = read_status(path)
            anchor = default_anchor(aid)
            if aid == "ADR-0037-CONTENT":
                anchor = "[content-authority D1](../components/content-authority/architecture.md#d1-canonical-authored-content-model)"
            elif aid == "ADR-0044":
                anchor = "[ai-stack D3](../components/ai-stack/architecture.md#d3-rag-fabric-routing)"
            elif aid == "ADR-0045":
                anchor = "[ai-stack D4](../components/ai-stack/architecture.md#d4-memory-indexes-retrieval-writes)"
            elif aid == "ADR-0046":
                anchor = "[frontend D2](../components/frontend/architecture.md#d2-typewriter-cinematic-direction)"
            elif aid in {"ADR-0058", "ADR-0059", "ADR-0060", "ADR-0061"}:
                anchor = "[ai-stack D12](../components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority)"
        if aid in ANCHOR_OVERRIDES:
            anchor = ANCHOR_OVERRIDES[aid]
        waiver = "yes" if aid in {"ADR-0021", "LANGFUSE-OBSERVABILITY", "OBSERVABILITY-REDACTION-POLICY", "MVP4-TEST-GATE-PLAN"} else ""
        rows.append((aid, status, anchor, "—", "—", "", waiver))

    lines = [
        "# Decision registry (ex-ADR → SAD)",
        "",
        "Maps every retired ADR file to its **normative SAD §9 anchor**.",
        "Normative text lives in SAD §9 + UML; ADR files are read-only under",
        "`docs/archive/adr-retired-2026/`.",
        "",
        "Governance: [governance SAD D5](governance/architecture.md#d5-sad-only-decision-retirement).",
        "",
        "| ex-ADR-ID | Status | SAD anchor | UML | Gate | Archive SHA | Waiver |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    REGISTRY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {REGISTRY.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
