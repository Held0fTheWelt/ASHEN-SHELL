"""Phase 3 service-level behavior tests for AI Engineer Suite."""

from __future__ import annotations

import app.services.ai_engineer_suite_service as suite_service


def test_effective_config_includes_comparison_and_boundedness(monkeypatch):
    monkeypatch.setattr(
        suite_service,
        "_read_suite_state",
        lambda: (
            "balanced",
            {
                "retrieval_top_k": 7,
                "runtime_diagnostics_verbosity": "debug",
            },
        ),
    )
    monkeypatch.setattr(
        suite_service,
        "_runtime_preset_map",
        lambda: {
            "balanced": {
                "display_name": "Balanced Runtime",
                "description": "Balanced profile",
                "stability": "recommended",
                "controlled_values": {
                    "retrieval_top_k": 5,
                    "runtime_diagnostics_verbosity": "operator",
                },
            }
        },
    )
    monkeypatch.setattr(
        suite_service,
        "_current_advanced_settings",
        lambda: {
            "retrieval_top_k": 6,
            "runtime_diagnostics_verbosity": "debug",
        },
    )
    monkeypatch.setattr(
        suite_service,
        "_guardrail_warnings",
        lambda effective: [{"severity": "warn", "message": "debug warning"}],
    )

    payload = suite_service.get_effective_runtime_config()

    assert payload["source_summary"]["override_count"] >= 1
    assert any(row["key"] == "retrieval_top_k" for row in payload["comparison_rows"])
    assert any(row["key"] == "runtime_diagnostics_verbosity" for row in payload["boundedness_notes"])
    assert payload["status_semantics"]["blocked"]


def test_runtime_dashboard_exposes_domain_status_and_warning_summary(app, monkeypatch):
    monkeypatch.setattr(
        suite_service,
        "evaluate_runtime_readiness",
        lambda: {
            "ai_only_valid": False,
            "readiness_severity": "blocked",
            "provider_summary": {"total": 2, "eligible_non_mock": 0},
            "route_summary": {"total": 3, "ai_ready": 0},
            "readiness_headline": "blocked by routes",
        },
    )
    monkeypatch.setattr(
        suite_service,
        "get_rag_operations_status",
        lambda: {
            "operational_state": "degraded",
            "degraded_reasons": ["embedding_backend_missing"],
            "guidance": [{"severity": "degraded", "message": "rag degraded"}],
            "corpus": {"chunk_count": 10},
            "embedding_backend": {"available": False},
            "dense_index": {"artifact_validity": "degraded"},
        },
    )
    monkeypatch.setattr(
        suite_service,
        "get_orchestration_status",
        lambda trace_id=None: {
            "overall_state": "blocked",
            "guidance": [{"severity": "degraded", "message": "parser issues"}],
            "langgraph": {"dependency_available": False, "fallback_posture": {"graph_error_count_recent": 2}},
            "langchain": {"bridge_available": True},
        },
    )
    monkeypatch.setattr(
        suite_service,
        "build_world_engine_control_center_snapshot",
        lambda app, trace_id=None: {
            "status": {"state": "blocked", "control_plane_ok": False, "warning_count": 1},
            "active_runtime": {"run_count": 0, "session_count": 0},
        },
    )
    monkeypatch.setattr(
        suite_service,
        "_effective_config_payload",
        lambda: {
            "active_preset_id": "balanced",
            "override_count": 2,
            "drift_keys": ["retrieval_top_k"],
            "guardrail_warnings": [{"severity": "warn", "message": "x"}],
        },
    )

    with app.app_context():
        payload = suite_service.get_runtime_dashboard()

    assert any(row["domain"] == "governance" and row["state"] == "blocked" for row in payload["domain_status"])
    assert any(row["domain"] == "rag" and row["state"] == "degraded" for row in payload["domain_status"])
    assert any(row["domain"] == "orchestration" and row["state"] == "blocked" for row in payload["domain_status"])
    assert payload["degraded_or_warning"]
    assert payload["status_semantics"]["healthy"]


def test_repo_root_resolves_to_repository_not_fs_root(app):
    """Regression: naive parents[3] can be ``/`` on shallow deploys, causing ``/.wos`` permission errors."""
    with app.app_context():
        root = suite_service._repo_root()
    assert root.resolve().parent != root.resolve()
    assert (root / "backend").is_dir()


def test_walk_best_rag_root_prefers_monorepo_over_slim(tmp_path):
    """When both layouts appear while walking up, full repo wins."""
    repo = tmp_path / "wos"
    (repo / "backend" / "app" / "services").mkdir(parents=True)
    (repo / "backend" / "app" / "__init__.py").write_text("#", encoding="utf-8")
    (repo / "backend" / "app" / "services" / ".keep").write_text("", encoding="utf-8")
    hit = suite_service._walk_best_rag_root(repo / "backend" / "app" / "services")
    assert hit == repo


def test_walk_best_rag_root_finds_slim_deploy(tmp_path):
    """PAAS-style tree: ``<deploy>/app/services`` without top-level ``backend``."""
    deploy = tmp_path / "srv"
    (deploy / "app" / "services").mkdir(parents=True)
    (deploy / "app" / "__init__.py").write_text("#", encoding="utf-8")
    (deploy / "app" / "services" / ".keep").write_text("", encoding="utf-8")
    hit = suite_service._walk_best_rag_root(deploy / "app" / "services")
    assert hit == deploy
