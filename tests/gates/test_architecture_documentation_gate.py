"""Architecture documentation gate — SAD/UML rollout completeness."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCH = REPO_ROOT / "docs" / "architecture"
ROLLOUT = ARCH / "project" / "ROLLOUT.md"
ADR_README = REPO_ROOT / "docs" / "ADR" / "README.md"
DECISION_REGISTRY = ARCH / "project" / "DECISION_REGISTRY.md"
NORMATIVE_INDEX = REPO_ROOT / "docs" / "dev" / "contracts" / "normative-contracts-index.md"
RUNTIME_CONTRACTS = ARCH / "contracts" / "runtime"
LINK_AUDIT = REPO_ROOT / "scripts" / "architecture_link_audit.py"
CONTRACT_PLACEMENT_AUDIT = REPO_ROOT / "scripts" / "contract_placement_audit.py"

ARCHITECTURE_ROOT_ALLOWLIST = frozenset(
    {"README.md", "START-HERE.md", "QUALITY-STANDARD.md", "DOC-HEALTH.md"}
)

REQUIRED_SECTIONS = [
    "Introduction & Goals",
    "Constraints",
    "Context & Scope",
    "Solution Strategy",
    "Building Block View",
    "Runtime View",
    "Deployment View",
    "Crosscutting Concepts",
    "Architecture Decisions",
    "Quality Requirements",
    "Risks & Technical Debt",
    "Glossary",
]

COMPLETE_SADS = [
    ARCH / "components" / "world-engine" / "architecture.md",
    ARCH / "components" / "backend" / "architecture.md",
    ARCH / "components" / "ai-stack" / "architecture.md",
    ARCH / "components" / "story-runtime-core" / "architecture.md",
    ARCH / "components" / "frontend" / "architecture.md",
    ARCH / "components" / "administration-tool" / "architecture.md",
    ARCH / "components" / "mcp-server" / "architecture.md",
    ARCH / "components" / "content-authority" / "architecture.md",
    ARCH / "project" / "ecosystem-topology" / "architecture.md",
    ARCH / "project" / "governance" / "architecture.md",
    ARCH / "project" / "documentation-supply-chain" / "architecture.md",
    ARCH / "project" / "quality-gates" / "architecture.md",
    ARCH / "project" / "observability-traceability" / "architecture.md",
    ARCH / "project" / "security-governance" / "architecture.md",
    ARCH / "project" / "mvp-live-runtime-completion" / "architecture.md",
]

WORLD_ENGINE_UML = [
    REPO_ROOT / "UML" / "Components" / "world-engine" / "components" / "c4-context.md",
    REPO_ROOT / "UML" / "Components" / "world-engine" / "components" / "c4-container.md",
    REPO_ROOT / "UML" / "Components" / "world-engine" / "components" / "c4-component.md",
    REPO_ROOT / "UML" / "Components" / "world-engine" / "sequence" / "world-engine-primary-turn-sequence.md",
    REPO_ROOT / "UML" / "Components" / "world-engine" / "sequence" / "world-engine-degraded-turn-sequence.md",
    REPO_ROOT / "UML" / "Components" / "world-engine" / "states" / "world-engine-story-session-states.md",
    REPO_ROOT / "UML" / "Components" / "world-engine" / "TRACEABILITY.md",
]

UML_MINIMUM = ("README.md", "components/c4-context.md", "sequence", "TRACEABILITY.md")

ROLLOUT_UML_MAP = {
    "world-engine": REPO_ROOT / "UML" / "Components" / "world-engine",
    "backend": REPO_ROOT / "UML" / "Components" / "backend",
    "ai-stack": REPO_ROOT / "UML" / "Components" / "ai-stack",
    "story-runtime-core": REPO_ROOT / "UML" / "Components" / "story-runtime-core",
    "frontend": REPO_ROOT / "UML" / "Components" / "frontend",
    "administration-tool": REPO_ROOT / "UML" / "Components" / "administration-tool",
    "mcp-server": REPO_ROOT / "UML" / "Components" / "mcp-server",
    "content-authority": REPO_ROOT / "UML" / "Components" / "content-authority",
    "ecosystem-topology": REPO_ROOT / "UML" / "Project" / "ecosystem-topology",
    "documentation-supply-chain": REPO_ROOT / "UML" / "Project" / "documentation-supply-chain",
    "observability-traceability": REPO_ROOT / "UML" / "Project" / "observability-traceability",
    "security-governance": REPO_ROOT / "UML" / "Project" / "security-governance",
    "mvp-live-runtime-completion": REPO_ROOT / "UML" / "Project" / "mvp-live-runtime-completion",
}


def slugify_heading(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def _section9_decision_ids(text: str) -> list[str]:
    if "## 9. Architecture Decisions" not in text:
        return []
    section = text.split("## 9. Architecture Decisions", 1)[1]
    section = section.split("## 10.", 1)[0]
    return re.findall(r"\|\s*(D\d+)\s*\|", section)


def _heading_slugs(text: str) -> set[str]:
    return {slugify_heading(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", text, re.M)}


def _parse_rollout_uml_systems() -> list[str]:
    text = ROLLOUT.read_text(encoding="utf-8")
    systems: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "System" in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 4:
            continue
        system, _sad, uml, status = parts[0], parts[1], parts[2], parts[3]
        if status != "Complete" or uml == "—":
            continue
        systems.append(system)
    return systems


@pytest.mark.parametrize("sad_path", COMPLETE_SADS, ids=lambda p: p.parent.name)
def test_sad_exists_with_arc42_sections(sad_path: Path) -> None:
    assert sad_path.is_file(), f"missing SAD: {sad_path.relative_to(REPO_ROOT)}"
    text = sad_path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert f"## " in text and section in text, f"{sad_path.name} missing section: {section}"
    prose = re.sub(r"\|.*\|", "", text)
    prose = re.sub(r"```.*?```", "", prose, flags=re.S)
    assert len(prose.split()) >= 200, f"{sad_path.name} too thin (linklist risk)"


@pytest.mark.parametrize("sad_path", COMPLETE_SADS, ids=lambda p: p.parent.name)
def test_sad_section9_has_decision_anchors(sad_path: Path) -> None:
    text = sad_path.read_text(encoding="utf-8")
    decision_ids = _section9_decision_ids(text)
    if not decision_ids:
        return
    slugs = _heading_slugs(text)
    for did in decision_ids:
        prefix = did.lower()
        assert any(s.startswith(prefix) for s in slugs), (
            f"{sad_path.relative_to(REPO_ROOT)}: missing ### {did} heading anchor"
        )


def test_world_engine_uml_package_complete() -> None:
    for path in WORLD_ENGINE_UML:
        assert path.is_file(), f"missing UML: {path.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize("system", list(ROLLOUT_UML_MAP.keys()))
def test_uml_packages_for_rollout_complete_rows(system: str) -> None:
    if system not in _parse_rollout_uml_systems():
        pytest.skip(f"{system} not marked Complete with UML in ROLLOUT")
    base = ROLLOUT_UML_MAP[system]
    assert (base / "README.md").is_file()
    assert (base / "components" / "c4-context.md").is_file()
    assert (base / "TRACEABILITY.md").is_file()
    seq_dir = base / "sequence"
    assert seq_dir.is_dir() and any(seq_dir.glob("*.md")), f"missing sequence in {base}"


def test_architecture_entry_not_redirect_only() -> None:
    readme = (ARCH / "README.md").read_text(encoding="utf-8")
    assert "Capability catalog" in readme
    assert "redirect" not in readme.lower()[:200]


def test_start_here_and_quality_standard_exist() -> None:
    assert (ARCH / "START-HERE.md").is_file()
    assert (ARCH / "QUALITY-STANDARD.md").is_file()


def test_migrated_contracts_present() -> None:
    for name in (
        "turn_execution_contract.md",
        "session_authority_contract.md",
    ):
        assert (ARCH / "contracts" / name).is_file(), name


def test_runtime_contracts_listed_in_normative_index() -> None:
    index = NORMATIVE_INDEX.read_text(encoding="utf-8")
    runtime_files = sorted(
        p.relative_to(RUNTIME_CONTRACTS).as_posix()
        for p in RUNTIME_CONTRACTS.rglob("*.md")
        if p.name != "README.md"
    )
    missing = [name for name in runtime_files if name not in index]
    assert not missing, f"normative index missing runtime contracts: {missing}"


def test_architecture_root_has_no_stray_contracts() -> None:
    stray: list[str] = []
    for path in ARCH.glob("*.md"):
        if path.name in ARCHITECTURE_ROOT_ALLOWLIST:
            continue
        if "contract" in path.name.lower() or path.name == "mvp_definition.md":
            stray.append(path.name)
    assert not stray, f"stray contract or mvp_definition in architecture root: {stray}"


def test_contract_placement_audit_clean() -> None:
    result = subprocess.run(
        [sys.executable, str(CONTRACT_PLACEMENT_AUDIT), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_decision_registry_exists() -> None:
    assert DECISION_REGISTRY.is_file()
    registry = DECISION_REGISTRY.read_text(encoding="utf-8")
    assert "ex-ADR-ID" in registry
    assert "ADR-0001" in registry


def test_no_active_adr_files() -> None:
    """After retirement, docs/ADR/ contains only README stub (no adr-*.md)."""
    adr_dir = REPO_ROOT / "docs" / "ADR"
    if not adr_dir.is_dir():
        pytest.skip("ADR directory removed")
    active = [
        p
        for p in adr_dir.rglob("*.md")
        if p.name != "README.md" and (p.name.startswith("adr-") or p.name.startswith("ADR"))
    ]
    assert not active, f"active ADR files remain: {[p.relative_to(REPO_ROOT) for p in active[:10]]}"


def test_sad_decision_prose_minimum() -> None:
    """§9 decision blocks must include Status, Origin, and substantive body."""
    for sad_path in COMPLETE_SADS:
        text = sad_path.read_text(encoding="utf-8")
        if "## 9. Architecture Decisions" not in text:
            continue
        section = text.split("## 9. Architecture Decisions", 1)[1].split("## 10.", 1)[0]
        blocks = re.findall(r"^### (?:D\d+|MVP\d+-\d+|ADR-\d{4}):.*?(?=^### |\Z)", section, re.M | re.S)
        for block in blocks:
            assert "**Status:**" in block, f"{sad_path.name}: decision missing Status"
            assert "**Origin:**" in block or "**Migrated from:**" in block, (
                f"{sad_path.name}: decision missing Origin"
            )
            body = re.sub(r"\*\*[^*]+\*\*", "", block)
            assert len(body.split()) >= 15, f"{sad_path.name}: decision block too thin"


def test_architecture_link_audit_clean() -> None:
    result = subprocess.run(
        [sys.executable, str(LINK_AUDIT), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_rollout_lists_world_engine_complete() -> None:
    text = ROLLOUT.read_text(encoding="utf-8")
    assert "world-engine" in text and "Complete" in text
