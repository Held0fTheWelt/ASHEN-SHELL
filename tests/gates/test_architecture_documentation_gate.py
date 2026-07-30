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
ADR_RETIREMENT_AUDIT = REPO_ROOT / "scripts" / "adr_retirement_audit.py"

DECISION_PROSE_MIN_WORDS = 50

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
    ARCH / "project" / "architecture-assurance" / "architecture.md",
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
    """After retirement, the ADR stub directory contains only README (no adr-*.md)."""
    adr_dir = REPO_ROOT / "docs" / "ADR"
    if not adr_dir.is_dir():
        pytest.skip("ADR directory removed")
    active = [
        p
        for p in adr_dir.rglob("*.md")
        if p.name != "README.md" and (p.name.startswith("adr-") or p.name.startswith("ADR"))
    ]
    assert not active, f"active ADR files remain: {[p.relative_to(REPO_ROOT) for p in active[:10]]}"


def _decision_body_word_count(block: str) -> int:
    """Count substantive words; strip heading and metadata lines only (keep bold prose)."""
    body = re.sub(r"^###[^\n]+\n", "", block)
    body = re.sub(
        r"^\*\*(Status|Origin|Migrated from|Supersedes):\*\*.*$",
        "",
        body,
        flags=re.M,
    )
    return len(body.split())


def test_sad_decision_prose_minimum() -> None:
    """§9 decision blocks must include Status, Origin, and substantive body (≥50 words)."""
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
            words = _decision_body_word_count(block)
            assert words >= DECISION_PROSE_MIN_WORDS, (
                f"{sad_path.name}: decision block too thin ({words} < {DECISION_PROSE_MIN_WORDS} words)"
            )


def test_adr_retirement_audit_clean() -> None:
    """Retired ADR registry coverage and SAD prose parity must pass audit --check."""
    result = subprocess.run(
        [
            sys.executable,
            str(ADR_RETIREMENT_AUDIT),
            "--check",
            "--parity-threshold",
            "0.70",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


MVP1_REQUIRED_IDS = (
    "MVP1-001",
    "MVP1-002",
    "MVP1-003",
    "MVP1-005",
    "MVP1-006",
    "MVP1-016",
)

MVP_SAD = ARCH / "project" / "mvp-live-runtime-completion" / "architecture.md"


def test_mvp1_required_sad_blocks_present() -> None:
    """FIX-012: each required MVP1 decision has a ### MVP1-xxx block in MVP SAD §9."""
    text = MVP_SAD.read_text(encoding="utf-8")
    section = text.split("## 9. Architecture Decisions", 1)[1].split("## 10.", 1)[0]
    for mvp_id in MVP1_REQUIRED_IDS:
        assert f"### {mvp_id}:" in section, f"Missing SAD §9 block for {mvp_id}"


def test_mvp1_decisions_registered() -> None:
    """FIX-012: required MVP1 ids map to SAD anchors in DECISION_REGISTRY."""
    registry = DECISION_REGISTRY.read_text(encoding="utf-8")
    for mvp_id in MVP1_REQUIRED_IDS:
        assert f"| {mvp_id} |" in registry, f"{mvp_id} missing from DECISION_REGISTRY"


def test_mvp1_sad_blocks_include_evidence() -> None:
    """FIX-012: required MVP1 SAD blocks include Decision and Evidence sections."""
    text = MVP_SAD.read_text(encoding="utf-8")
    section = text.split("## 9. Architecture Decisions", 1)[1].split("## 10.", 1)[0]
    for mvp_id in MVP1_REQUIRED_IDS:
        start = section.index(f"### {mvp_id}:")
        end = section.find("\n### ", start + 1)
        block = section[start:] if end == -1 else section[start:end]
        assert "**Evidence.**" in block, f"{mvp_id} missing Evidence"
        assert "**Decision.**" in block, f"{mvp_id} missing Decision"


def test_architecture_link_audit_clean() -> None:
    result = subprocess.run(
        [sys.executable, str(LINK_AUDIT), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


PILOT_COMPONENTS = ("world-engine", "ai-stack")

FULL_CATALOG_COMPONENTS = frozenset(
    {"world-engine", "ai-stack", "backend", "story-runtime-core", "mcp-server"}
)

LIGHT_CATALOG_COMPONENTS = frozenset(
    {"frontend", "content-authority", "administration-tool"}
)


def _section9_headings(text: str) -> list[str]:
    if "## 9. Architecture Decisions" not in text:
        return []
    section = text.split("## 9. Architecture Decisions", 1)[1].split("## 10.", 1)[0]
    return re.findall(r"^### (D\d+):", section, re.M)


@pytest.mark.parametrize("slug", PILOT_COMPONENTS)
def test_pilot_has_mechanism_catalog(slug: str) -> None:
    catalog = ARCH / "components" / slug / "mechanism-catalog.md"
    matrix = ARCH / "components" / slug / "evidence-matrix.md"
    assert catalog.is_file(), f"missing mechanism-catalog for {slug}"
    assert matrix.is_file(), f"missing evidence-matrix for {slug}"
    rows = [ln for ln in catalog.read_text(encoding="utf-8").splitlines() if ln.startswith("|") and "---" not in ln]
    assert len(rows) >= 10, f"{slug} mechanism-catalog needs >=10 rows, got {len(rows)}"


@pytest.mark.parametrize("slug", PILOT_COMPONENTS)
def test_no_duplicate_section9_headings(slug: str) -> None:
    sad = ARCH / "components" / slug / "architecture.md"
    headings = _section9_headings(sad.read_text(encoding="utf-8"))
    dups = [h for h in headings if headings.count(h) > 1]
    assert not dups, f"{slug}: duplicate §9 headings {sorted(set(dups))}"


@pytest.mark.parametrize("slug", sorted(FULL_CATALOG_COMPONENTS | LIGHT_CATALOG_COMPONENTS))
def test_mechanism_catalog_for_complete_components(slug: str) -> None:
    catalog = ARCH / "components" / slug / "mechanism-catalog.md"
    assert catalog.is_file(), f"missing mechanism-catalog for {slug}"
    rows = [ln for ln in catalog.read_text(encoding="utf-8").splitlines() if re.search(r"\|\s*[A-Z]{2,3}-M\d+", ln)]
    min_rows = 5 if slug in LIGHT_CATALOG_COMPONENTS else 8
    assert len(rows) >= min_rows, f"{slug} catalog needs >={min_rows} mechanism rows"


def test_decision_registry_complete() -> None:
    registry = DECISION_REGISTRY.read_text(encoding="utf-8")
    empty: list[str] = []
    for line in registry.splitlines():
        if not line.startswith("|") or "---" in line or "ex-ADR-ID" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        adr_id, anchor = parts[1], parts[3]
        if anchor in ("—", "", "-"):
            empty.append(adr_id)
    assert not empty, f"registry rows missing SAD anchor: {empty[:15]}{'...' if len(empty)>15 else ''}"


def test_sad_section9_hygiene_clean() -> None:
    hygiene = REPO_ROOT / "scripts" / "sad_section9_hygiene.py"
    result = subprocess.run(
        [sys.executable, str(hygiene), "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_rollout_lists_world_engine_complete() -> None:
    text = ROLLOUT.read_text(encoding="utf-8")
    assert "world-engine" in text and "Complete" in text
