from __future__ import annotations

import json
from pathlib import Path

from tools.architecture_assurance.drift_claims import (
    load_claim_catalog,
    project_claim_reconciliation,
    validate_claim_catalog,
)
from tools.architecture_assurance.drift_evidence import (
    build_drift_evidence,
    write_drift_evidence,
)
from tools.architecture_assurance.sad_enricher import enrich_sads
from tools.architecture_assurance.semantic_models import (
    load_model_catalog,
    validate_model_catalog,
    view_requirements,
)


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tools" / "architecture_assurance" / "config.json"
MODEL_CATALOG = (
    ROOT / "tools" / "architecture_assurance" / "model_catalog.json"
)
CLAIM_CATALOG = (
    ROOT / "tools" / "architecture_assurance" / "drift_claim_catalog.json"
)


def test_semantic_catalog_is_source_bound_and_individualized() -> None:
    catalog = load_model_catalog(MODEL_CATALOG)
    assert validate_model_catalog(catalog, ROOT) == []
    assert len(catalog["subsystems"]) == 17
    assert sum(
        len(model["views"]) for model in catalog["subsystems"].values()
    ) == 94

    profiles = {
        subsystem_id: tuple(view["kind"] for view in model["views"])
        for subsystem_id, model in catalog["subsystems"].items()
    }
    assert len(set(profiles.values())) > 1
    assert all(
        "/depth/" not in view["path"].replace("\\", "/")
        for model in catalog["subsystems"].values()
        for view in model["views"]
    )
    assert {
        "activity",
        "class",
        "component",
        "container",
        "context",
        "deployment",
        "sequence",
        "state",
        "usecase",
    }.issubset(
        {
            view["kind"]
            for model in catalog["subsystems"].values()
            for view in model["views"]
        }
    )


def test_semantic_catalog_rejects_retired_placeholder_anchor(tmp_path: Path) -> None:
    retired = tmp_path / "retired.py"
    retired.write_text(
        '"""Retired SOURCE segment — logic lives in the assembled impl module."""\n',
        encoding="utf-8",
    )
    catalog = {
        "subsystems": {
            "sample": {
                "elements": {
                    "runtime": {
                        "type": "component",
                        "name": "Runtime",
                        "responsibility": "Execute behavior",
                        "contract": "Real implementation evidence",
                        "anchor": "retired.py",
                    }
                },
                "relationships": {},
                "views": [
                    {
                        "id": "components",
                        "kind": "component",
                        "path": "components.puml",
                        "concern": "Reject placeholder correspondence",
                        "elements": ["runtime"],
                        "relationships": [],
                    }
                ],
            }
        }
    }

    findings = validate_model_catalog(catalog, tmp_path)
    assert any("retired placeholder source anchor" in item["error"] for item in findings)


def test_view_requirements_capture_semantics_not_fixed_bands() -> None:
    catalog = load_model_catalog(MODEL_CATALOG)
    requirements = view_requirements(catalog, "world-engine")
    assert {item["kind"] for item in requirements} >= {
        "context",
        "container",
        "component",
        "sequence",
        "activity",
        "state",
        "class",
        "deployment",
    }
    assert all(item["concern"] for item in requirements)
    assert all(item["anchors"] for item in requirements)
    assert all(item["element_count"] >= 3 for item in requirements)
    assert all(item["relationship_count"] >= 2 for item in requirements)


def test_generated_views_have_semantic_edges_and_source_links() -> None:
    catalog = load_model_catalog(MODEL_CATALOG)
    for model in catalog["subsystems"].values():
        for view in model["views"]:
            text = (ROOT / view["path"]).read_text(encoding="utf-8-sig")
            assert f"' bt-view-kind: {view['kind']}" in text
            assert "Responsibility:" in text
            assert "Contract:" in text
            assert "contract:" in text
            assert "[[" in text
            assert "evidence for boundary" not in text.lower()


def test_drift_claims_are_current_source_bound_and_project_idempotently(
    tmp_path: Path,
) -> None:
    catalog = load_claim_catalog(CLAIM_CATALOG)
    assert validate_claim_catalog(catalog, ROOT) == []
    assert {claim["status"] for claim in catalog["claims"]} == {
        "confirmed_current",
        "superseded",
        "conflicting",
        "open_target",
    }
    destination = tmp_path / "reconciliation.md"
    first = project_claim_reconciliation(
        CLAIM_CATALOG,
        destination,
        ROOT,
    )
    second = project_claim_reconciliation(
        CLAIM_CATALOG,
        destination,
        ROOT,
    )
    assert first["action"] == "write"
    assert second["action"] == "unchanged"


def test_git_evidence_dry_run_does_not_write(tmp_path: Path) -> None:
    evidence = build_drift_evidence(
        ROOT,
        MODEL_CATALOG,
        archive_root=None,
        git_revision="HEAD",
        branch_label="test-current-head",
        history_window=5,
    )
    assert evidence["repository"]["branch"] == "test-current-head"
    assert evidence["repository"]["requested_revision"] == "HEAD"
    json_path = tmp_path / "evidence" / "drift.json"
    markdown_path = tmp_path / "evidence" / "drift.md"
    result = write_drift_evidence(
        evidence,
        json_path,
        markdown_path,
        dry_run=True,
    )
    assert {item["action"] for item in result["actions"]} == {
        "would_write"
    }
    assert not json_path.exists()
    assert not markdown_path.exists()


def test_sad_semantic_enrichment_is_current_without_writes() -> None:
    result = enrich_sads(CONFIG, ROOT, dry_run=True)
    assert {item["action"] for item in result["actions"]} == {"unchanged"}
    assert result["sections"] == [3, 5, 6, 7, 8, 9, 11]


def test_archaeology_snapshot_contains_no_external_absolute_dependency() -> None:
    evidence = json.loads(
        (
            ROOT
            / "docs"
            / "architecture"
            / "evidence"
            / "architecture-drift-baseline.json"
        ).read_text(encoding="utf-8-sig")
    )
    encoded = json.dumps(evidence, ensure_ascii=False)
    assert evidence["architecture_archaeology"]["available"] is True
    assert evidence["architecture_archaeology"]["root_label"] == "New folder"
    assert "E:\\New folder" not in encoded
