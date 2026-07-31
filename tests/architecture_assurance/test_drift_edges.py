from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from tools.architecture_assurance.audit import build_report
from tools.architecture_assurance.drift_claims import load_claim_catalog
from tools.architecture_assurance.drift_edges import (
    load_drift_edge_catalog,
    render_drift_edge_markdown,
    render_drift_edge_puml,
    validate_authoritative_write_surfaces,
    validate_drift_edge_catalog,
)
from tools.architecture_assurance.semantic_models import load_model_catalog


ROOT = Path(__file__).resolve().parents[2]
EDGE_CATALOG = (
    ROOT / "tools" / "architecture_assurance" / "drift_edge_catalog.json"
)
MODEL_CATALOG = (
    ROOT / "tools" / "architecture_assurance" / "model_catalog.json"
)
CLAIM_CATALOG = (
    ROOT / "tools" / "architecture_assurance" / "drift_claim_catalog.json"
)
CONFIG = ROOT / "tools" / "architecture_assurance" / "config.json"


def _findings(catalog: dict) -> list[dict]:
    return validate_drift_edge_catalog(
        catalog,
        model_catalog=load_model_catalog(MODEL_CATALOG),
        claim_catalog=load_claim_catalog(CLAIM_CATALOG),
        repo_root=ROOT,
        catalog_path=EDGE_CATALOG.relative_to(ROOT).as_posix(),
    )


def test_drift_edges_resolve_to_individual_models_and_cover_active_claims() -> None:
    catalog = load_drift_edge_catalog(EDGE_CATALOG)
    assert _findings(catalog) == []
    active_claims = {
        claim["id"]
        for claim in load_claim_catalog(CLAIM_CATALOG)["claims"]
        if claim["status"] in {"conflicting", "open_target"}
    }
    covered_claims = {
        claim_id
        for edge in catalog["edges"]
        for claim_id in edge["claim_ids"]
    }
    assert active_claims <= covered_claims
    assert {
        edge["from"].split(":", 1)[0] for edge in catalog["edges"]
    } >= {
        "ai-stack",
        "content-authority",
        "observability-traceability",
        "quality-gates",
        "world-engine",
    }


def test_competing_authoritative_write_path_is_ci_failure() -> None:
    catalog = deepcopy(load_drift_edge_catalog(EDGE_CATALOG))
    second_writer = deepcopy(
        next(
            edge
            for edge in catalog["edges"]
            if edge["effect"] == "authoritative_write"
        )
    )
    second_writer.update(
        {
            "id": "legacy-runtime-authoritative-write",
            "from": "world-engine:runtime",
            "anchor": "world-engine/world_engine/runtime/manager.py",
        }
    )
    catalog["edges"].append(second_writer)
    findings = _findings(catalog)
    assert any(
        finding["rule_id"] == "BT-AUTHORITY-WRITE-CONFLICT"
        and "competing write paths" in finding["message"]
        for finding in findings
    )


def test_undeclared_source_sink_callsite_is_ci_failure(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    (source_root / "allowed.py").write_text(
        "class Manager:\n"
        "    def _persist_session(self, session):\n"
        "        self._session_store.save(session.id, {})\n",
        encoding="utf-8",
    )
    (source_root / "bypass.py").write_text(
        "class Bypass:\n"
        "    def commit_directly(self, session):\n"
        "        self._session_store.save(session.id, {})\n",
        encoding="utf-8",
    )
    catalog = {
        "authority_invariants": [
            {"resource": "live_story_session"}
        ],
        "write_surfaces": [
            {
                "id": "session-save",
                "resource": "live_story_session",
                "call": "self._session_store.save",
                "scan_roots": ["src"],
                "allowed_callsites": [
                    {
                        "path": "src/allowed.py",
                        "symbol": "_persist_session",
                    }
                ],
                "minimum_calls": 1,
                "maximum_calls": 1,
            }
        ],
    }
    findings = validate_authoritative_write_surfaces(
        catalog,
        repo_root=tmp_path,
        catalog_path="drift_edge_catalog.json",
    )
    assert any(
        finding["rule_id"] == "BT-AUTHORITY-WRITE-CONFLICT"
        for finding in findings
    )
    assert any(
        finding["rule_id"] == "BT-AUTHORITY-WRITE-CALLSITE"
        and finding["path"] == "src/bypass.py"
        for finding in findings
    )


def test_lost_envelope_field_is_ci_failure_at_exact_edge() -> None:
    catalog = deepcopy(load_drift_edge_catalog(EDGE_CATALOG))
    edge = next(
        item
        for item in catalog["edges"]
        if item["id"] == "runtime-proposal-to-world-bridge"
    )
    edge["carries"].remove("primary_responder_id")
    findings = _findings(catalog)
    assert {
        (
            finding["rule_id"],
            finding["unit"],
            finding["message"],
        )
        for finding in findings
    } >= {
        (
            "BT-ENVELOPE-FIELD-LOSS",
            "dramatic-turn-envelope-v1:primary_responder_id",
            "runtime-proposal-to-world-bridge drops required field "
            "'primary_responder_id'",
        )
    }


def test_competing_writer_reaches_top_level_ci_gate(
    tmp_path: Path,
) -> None:
    catalog = deepcopy(load_drift_edge_catalog(EDGE_CATALOG))
    second_writer = deepcopy(
        next(
            edge
            for edge in catalog["edges"]
            if edge["effect"] == "authoritative_write"
        )
    )
    second_writer.update(
        {
            "id": "ai-executor-authoritative-write",
            "from": "ai-stack:executor",
            "anchor": "ai_stack/langgraph/langgraph_runtime_executor.py",
        }
    )
    catalog["edges"].append(second_writer)
    mutant_path = tmp_path / "drift_edge_catalog.json"
    mutant_path.write_text(
        json.dumps(catalog, indent=2),
        encoding="utf-8",
    )
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    config["drift_edge_catalog"] = str(mutant_path)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    report = build_report(config_path, ROOT)

    assert report["drift_edges"]["status"] == "FAIL"
    assert report["gate"]["status"] == "FAIL"
    assert any(
        finding["rule_id"] == "BT-AUTHORITY-WRITE-CONFLICT"
        for finding in report["gate"]["failures"]
    )


def test_drift_projection_is_deterministic_and_source_bound() -> None:
    catalog = load_drift_edge_catalog(EDGE_CATALOG)
    models = load_model_catalog(MODEL_CATALOG)
    first_puml = render_drift_edge_puml(catalog, models)
    second_puml = render_drift_edge_puml(
        json.loads(json.dumps(catalog)),
        json.loads(json.dumps(models)),
    )
    assert first_puml == second_puml
    assert "authoritative_write" in first_puml
    assert "world-validation-authoritative-write" in first_puml
    markdown = render_drift_edge_markdown(catalog)
    assert "dramatic-turn-envelope-v1" in markdown
    assert "DRIFT-001" in markdown
