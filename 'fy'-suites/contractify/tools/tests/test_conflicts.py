"""Conflict passes — hermetic repo from ``conftest`` plus direct unit checks."""
from __future__ import annotations

from pathlib import Path

import contractify.tools.repo_paths as repo_paths
from contractify.tools.conflicts import (
    detect_all_conflicts,
    detect_duplicate_normative_index_targets,
    detect_projection_fingerprint_mismatch,
    detect_projection_orphan_source_contract,
)
from contractify.tools.models import ProjectionRecord


def test_duplicate_normative_index_targets_fixture() -> None:
    root = repo_paths.repo_root()
    hits = detect_duplicate_normative_index_targets(root)
    assert any(c.classification == "normative_anchor_ambiguity" for c in hits)


def test_adr_vocabulary_overlap_fixture() -> None:
    root = repo_paths.repo_root()
    conflicts = detect_all_conflicts(root, [])
    voc = [c for c in conflicts if c.conflict_type == "adr_vocabulary_overlap"]
    assert voc, "expected bounded ADR vocabulary overlap signal"


def test_active_index_row_vs_retired_adr_fixture() -> None:
    root = repo_paths.repo_root()
    conflicts = detect_all_conflicts(root, [])
    life = [c for c in conflicts if c.classification == "superseded_still_referenced_as_current"]
    assert life, "expected Active/Binding row vs retired ADR signal"


def test_projection_orphan_source_contract_unit() -> None:
    pr = ProjectionRecord(
        id="PRJ-ORPH",
        title="orphan",
        path="x.md",
        audience="developer",
        mode="easy",
        source_contract_id="CTR-MISSING-999",
        anchor_location="docs/x.md",
        authoritative=False,
        confidence=0.5,
        evidence="test",
    )
    hits = detect_projection_orphan_source_contract([pr], frozenset({"CTR-API-OPENAPI-001"}))
    assert len(hits) == 1
    assert hits[0].kind == "projection_to_anchor_mismatch"


def test_projection_fingerprint_mismatch_unit(tmp_path: Path) -> None:
    # Shares ``tmp_path`` with the autouse hermetic repo; ``docs/api`` may already exist.
    api_dir = tmp_path / "docs" / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    openapi = api_dir / "openapi.yaml"
    openapi.write_bytes(b"openapi: 3\ninfo:\n  version: '1'\n")
    wrong = "deadbeef" * 4
    pr = ProjectionRecord(
        id="PRJ-TEST",
        title="t",
        path="x.json",
        audience="developer",
        mode="specialist",
        source_contract_id="CTR-API-OPENAPI-001",
        anchor_location="docs/api/openapi.yaml",
        authoritative=False,
        confidence=0.9,
        evidence="unit",
        contract_version_ref=wrong[:16],
    )
    hits = detect_projection_fingerprint_mismatch(tmp_path, [pr])
    assert len(hits) == 1
    assert hits[0].classification == "projection_anchor_mismatch"
