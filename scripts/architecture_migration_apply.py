#!/usr/bin/env python3
"""Apply ADR absorption banners and migrate contract files for architecture migration."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

ABSORPTION_MAP: dict[str, str] = {
    "adr-0001": "world-engine SAD D1",
    "adr-0002": "backend SAD D1",
    "adr-0004": "world-engine SAD D2 / ai-stack SAD D1",
    "adr-0016": "backend SAD D2",
    "adr-0017": "governance SAD D1",
    "adr-0025": "content-authority SAD D1",
    "adr-0026": "mcp-server SAD D1",
    "adr-0027": "mcp-server SAD D2",
    "adr-0028": "mcp-server SAD D3",
    "adr-0029": "governance SAD D2",
    "adr-0033": "world-engine SAD D3 (partial)",
    "adr-0034": "frontend SAD D1",
    "adr-0037": "backend SAD D3",
    "adr-0039": "governance SAD D3 / quality-gates SAD D1",
    "adr-0040": "ai-stack SAD D2 / observability SAD D5",
    "adr-0044": "ai-stack SAD D3",
    "adr-0045": "ai-stack SAD D4",
    "adr-0046": "frontend SAD D2",
    "adr-0048": "mcp-server SAD D4",
    "adr-0049": "security-governance SAD D5",
    "adr-0050": "security-governance SAD D1",
    "adr-0051": "security-governance SAD D2",
    "adr-0052": "security-governance SAD D3 / backend SAD D4",
    "adr-0053": "ai-stack SAD D6",
    "adr-0056": "ai-stack SAD D7",
    "adr-0060": "ai-stack SAD D7",
    "adr-0062": "world-engine SAD D4",
    "adr-0003": "world-engine SAD D7",
    "adr-0005": "ai-stack constraints",
    "adr-0008": "world-engine crosscutting",
    "adr-0011": "world-engine SAD D8",
    "adr-0012": "world-engine SAD D8",
    "adr-0015": "world-engine SAD D9",
    "adr-0018": "ai-stack building blocks",
    "adr-0019": "ai-stack building blocks",
    "adr-0020": "administration-tool SAD D1",
    "adr-0022": "mvp-live-runtime-completion SAD",
    "adr-0023": "governance SAD",
    "adr-0030": "ecosystem-topology deployment",
    "adr-0031": "governance constraints",
    "adr-0032": "mvp-live-runtime-completion SAD",
    "adr-0036": "world-engine SAD D10",
    "adr-0042": "meta_narrative contract",
    "adr-0043": "meta_narrative contract",
    "adr-0054": "ai-stack SAD D7",
    "adr-0055": "player_input contract",
    "adr-0057": "ai-stack SAD D7",
    "adr-0064": "quality-gates deployment",
    "adr-0066": "world-engine SAD D6",
    "adr-0067": "world-engine SAD D6",
    "adr-0068": "world-engine SAD D6",
    "adr-0069": "world-engine SAD D6",
    "adr-0070": "world-engine SAD D6",
}

BANNER = "Absorbed into [{target}](../architecture/components/{slug}/architecture.md) (2026-06-23)."


def _slug_for_adr(adr_id: str) -> str:
    mapping = {
        "adr-0001": "world-engine",
        "adr-0002": "backend",
        "adr-0004": "ai-stack",
        "adr-0033": "world-engine",
        "adr-0062": "world-engine",
    }
    for key, slug in mapping.items():
        if adr_id.startswith(key.split("-")[0] + "-" + key.split("-")[1]):
            pass
    if adr_id in ("adr-0001", "adr-0033", "adr-0062", "adr-0038"):
        return "world-engine"
    if adr_id in ("adr-0002", "adr-0016", "adr-0037", "adr-0052"):
        return "backend"
    if adr_id.startswith("adr-0026") or adr_id.startswith("adr-0027") or adr_id.startswith("adr-0028") or adr_id == "adr-0048":
        return "mcp-server"
    if adr_id in ("adr-0017", "adr-0029", "adr-0039"):
        return "project/governance"
    if adr_id == "adr-0025":
        return "content-authority"
    if adr_id in ("adr-0034", "adr-0046"):
        return "frontend"
    if adr_id in ("adr-0040", "adr-0044", "adr-0045", "adr-0053", "adr-0056", "adr-0060"):
        return "ai-stack"
    if adr_id in ("adr-0050", "adr-0051", "adr-0049", "adr-0047"):
        return "project/security-governance"
    if adr_id in ("adr-0022", "adr-0032"):
        return "project/mvp-live-runtime-completion"
    if adr_id in ("adr-0023", "adr-0031"):
        return "project/governance"
    if adr_id in ("adr-0030", "adr-0064"):
        return "project/ecosystem-topology"
    if adr_id in ("adr-0003", "adr-0011", "adr-0012", "adr-0015", "adr-0036", "adr-0066", "adr-0067", "adr-0068", "adr-0069", "adr-0070"):
        return "world-engine"
    if adr_id in ("adr-0005", "adr-0018", "adr-0019", "adr-0054", "adr-0055", "adr-0057"):
        return "ai-stack"
    if adr_id == "adr-0020":
        return "administration-tool"
    return "project/ecosystem-topology"


def apply_banners() -> int:
    count = 0
    for adr_id, _label in ABSORPTION_MAP.items():
        path = REPO / "docs" / "ADR" / f"{adr_id}*.md"
        matches = list((REPO / "docs" / "ADR").glob(f"{adr_id}*.md"))
        if not matches:
            continue
        path = matches[0]
        text = path.read_text(encoding="utf-8")
        if "Absorbed into" in text:
            continue
        slug = _slug_for_adr(adr_id)
        link = f"../architecture/components/{slug}/architecture.md" if not slug.startswith("project/") else f"../architecture/{slug}/architecture.md"
        note = f"\n> **Absorption (2026-06-23):** Normative summary lives in [{_label}]({link}).\n\n"
        if "## Status" in text:
            text = text.replace("## Status\n", f"## Status\n{note}", 1)
        else:
            text = note + text
        path.write_text(text, encoding="utf-8")
        count += 1
    return count


def migrate_root_contracts() -> None:
    src = REPO / "docs" / "contracts"
    dst = REPO / "docs" / "architecture" / "contracts"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.md"):
        target = dst / f.name
        if not target.exists():
            shutil.copy2(f, target)
        stub = (
            f"# Moved\n\nThis contract now lives at "
            f"[`docs/architecture/contracts/{f.name}`](../architecture/contracts/{f.name}).\n"
        )
        f.write_text(stub, encoding="utf-8")


def migrate_runtime_contracts() -> None:
    src = REPO / "docs" / "technical" / "runtime"
    dst = REPO / "docs" / "architecture" / "contracts" / "runtime"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.md"):
        if f.name == "README.md":
            continue
        target = dst / f.name
        if not target.exists():
            shutil.copy2(f, target)
        rel = f.name
        stub = (
            f"# Moved\n\nRuntime contract relocated to "
            f"[`docs/architecture/contracts/runtime/{rel}`](../../architecture/contracts/runtime/{rel}).\n"
            f"Owning narrative: [world-engine SAD](../../architecture/components/world-engine/architecture.md) "
            f"and [ai-stack SAD](../../architecture/components/ai-stack/architecture.md).\n"
        )
        f.write_text(stub, encoding="utf-8")


def stub_legacy_architecture_docs() -> None:
    stubs = {
        "mvp_definition.md": "project/mvp-live-runtime-completion/architecture.md",
        "session_runtime_contract.md": "components/world-engine/architecture.md",
        "current_service_boundaries.md": "project/ecosystem-topology/architecture.md",
        "ai_story_contract.md": "components/ai-stack/architecture.md",
        "god_of_carnage_module_contract.md": "components/content-authority/architecture.md",
        "god_of_carnage_current_contract.md": "components/content-authority/architecture.md",
        "runtime_profile_vs_content_contract.md": "boundaries/content-vs-runtime-profile.md",
        "observability_traceability_contract.md": "project/observability-traceability/architecture.md",
    }
    base = REPO / "docs" / "architecture"
    for name, target in stubs.items():
        path = base / name
        if not path.exists():
            continue
        path.write_text(
            f"# Moved\n\nContent absorbed into [`{target}`](./{target}).\n",
            encoding="utf-8",
        )


def stub_technical_architecture() -> None:
    mapping = {
        "architecture-overview.md": "project/ecosystem-topology/architecture.md",
        "service-boundaries.md": "project/ecosystem-topology/architecture.md",
        "mvp_definition.md": "project/mvp-live-runtime-completion/architecture.md",
        "backend-runtime-classification.md": "components/backend/architecture.md",
        "ai_story_contract.md": "components/ai-stack/architecture.md",
        "god_of_carnage_module_contract.md": "components/content-authority/architecture.md",
        "session_runtime_contract.md": "components/world-engine/architecture.md",
        "canonical_runtime_contract.md": "components/world-engine/architecture.md",
        "canonical-player-flow-contract.md": "components/frontend/architecture.md",
        "MultilingualArchitecture.md": "components/world-engine/architecture.md",
        "runtime_profile_vs_content_contract.md": "boundaries/content-vs-runtime-profile.md",
    }
    base = REPO / "docs" / "technical" / "architecture"
    for name, target in mapping.items():
        path = base / name
        if not path.exists():
            continue
        path.write_text(
            f"# Moved\n\nSee [`docs/architecture/{target}`](../../architecture/{target}).\n",
            encoding="utf-8",
        )
    spine = REPO / "docs" / "technical" / "runtime" / "world_engine_authoritative_runtime_and_system_interactions.md"
    if spine.exists():
        spine.write_text(
            "# Moved\n\n"
            "Spine absorbed into [world-engine SAD](../../architecture/components/world-engine/architecture.md).\n"
            "See §5–§6 for building blocks and runtime views.\n",
            encoding="utf-8",
        )


def fix_adr_duplicates() -> None:
    dup = REPO / "docs" / "ADR" / "adr-0058-director-driven-pulse-and-block-stream-bus.md"
    if dup.exists():
        dup.write_text(
            "# Deprecated duplicate ADR-0058\n\n"
            "Canonical file: [adr-0058-director-driven-pulse-block-stream-bus.md]"
            "(adr-0058-director-driven-pulse-block-stream-bus.md).\n"
            "See [Governance SAD D4](../architecture/project/governance/architecture.md#d4-adr-duplicate-resolution).\n",
            encoding="utf-8",
        )
    root21 = REPO / "docs" / "ADR" / "adr-0021-runtime-authority.md"
    if root21.exists():
        root21.write_text(
            "# Superseded stub\n\n"
            "Use [ADR-0001](adr-0001-runtime-authority-in-world-engine.md) and "
            "[world-engine SAD](../architecture/components/world-engine/architecture.md).\n"
            "Legacy copy: [legacy/adr-0021-runtime-authority.md](legacy/adr-0021-runtime-authority.md).\n",
            encoding="utf-8",
        )


def main() -> None:
    n = apply_banners()
    migrate_root_contracts()
    migrate_runtime_contracts()
    stub_legacy_architecture_docs()
    stub_technical_architecture()
    fix_adr_duplicates()
    print(f"Applied {n} ADR banners; migrated contracts and stubs.")


if __name__ == "__main__":
    main()
