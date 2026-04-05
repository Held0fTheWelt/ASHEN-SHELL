"""Area 2 final operational closure — G-FINAL-01 … G-FINAL-08 explicit gate tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from app import create_app
from app.config import Config, TestingConfig
from app.runtime.adapter_registry import clear_registry, iter_model_specs
from app.runtime.area2_operator_truth import build_area2_operator_truth
from app.runtime.area2_routing_authority import AREA2_AUTHORITY_REGISTRY, AuthorityLayer
from app.runtime.area2_startup_profiles import (
    Area2StartupProfile,
    expected_area2_operational_state_for_profile,
    facts_for_profile,
    resolve_startup_profile,
)
from app.runtime.area2_operational_state import (
    Area2OperationalState,
    NoEligibleDiscipline,
    classify_no_eligible_discipline,
)
from app.runtime.model_routing_contracts import RouteReasonCode
from app.services.writers_room_model_routing import build_writers_room_model_route_specs

from .test_area2_convergence_gates import assert_area2_truth_shape

REPO_ROOT = Path(__file__).resolve().parents[3]

G_FINAL_DOC_FILES = (
    "area2_final_closure_gates.md",
    "area2_final_operational_closure_report.md",
)

G_FINAL_ARCH_CROSSREF_FILES = (
    "llm_slm_role_stratification.md",
    "ai_story_contract.md",
)


def test_g_final_01_reproducible_bootstrap_gate():
    """G-FINAL-01: named profiles map deterministically to bootstrap and registry expectations."""
    assert facts_for_profile(Area2StartupProfile.production_default).routing_registry_bootstrap is True
    assert facts_for_profile(Area2StartupProfile.production_default).pytest_session is False
    assert (
        facts_for_profile(Area2StartupProfile.production_default).expect_global_model_specs_nonempty_after_create_app
        is True
    )

    assert facts_for_profile(Area2StartupProfile.testing_isolated).routing_registry_bootstrap is False
    assert facts_for_profile(Area2StartupProfile.testing_isolated).expect_global_model_specs_nonempty_after_create_app is False

    assert facts_for_profile(Area2StartupProfile.testing_bootstrap_on).routing_registry_bootstrap is True
    assert facts_for_profile(Area2StartupProfile.testing_bootstrap_on).pytest_session is True

    with patch("app.runtime.area2_startup_profiles.pytest_session_active", return_value=True):
        assert resolve_startup_profile(routing_registry_bootstrap=False) is Area2StartupProfile.testing_isolated
        assert resolve_startup_profile(routing_registry_bootstrap=True) is Area2StartupProfile.testing_bootstrap_on
    with patch("app.runtime.area2_startup_profiles.pytest_session_active", return_value=False):
        assert resolve_startup_profile(routing_registry_bootstrap=True) is Area2StartupProfile.production_default
        assert (
            resolve_startup_profile(routing_registry_bootstrap=False)
            is Area2StartupProfile.production_bootstrap_disabled
        )

    clear_registry()
    app_prod = create_app(Config)
    try:
        with app_prod.app_context():
            assert app_prod.config.get("ROUTING_REGISTRY_BOOTSTRAP", True) is True
            assert iter_model_specs(), "production_default profile must yield non-empty iter_model_specs after create_app"
    finally:
        clear_registry()

    class NoBoot(TestingConfig):
        ROUTING_REGISTRY_BOOTSTRAP = False

    clear_registry()
    app_test_off = create_app(NoBoot)
    try:
        with app_test_off.app_context():
            assert iter_model_specs() == []
    finally:
        clear_registry()


def test_g_final_01_expected_operational_state_matrix():
    """G-FINAL-01: profile-implied classification matches Area2OperationalState rules."""
    assert (
        expected_area2_operational_state_for_profile(
            Area2StartupProfile.testing_isolated,
            registry_model_spec_count=0,
            canonical_surfaces_all_satisfied=None,
        )
        == Area2OperationalState.test_isolated
    )
    with patch("app.runtime.area2_operational_state.pytest_session_active", return_value=False):
        assert (
            expected_area2_operational_state_for_profile(
                Area2StartupProfile.production_bootstrap_disabled,
                registry_model_spec_count=0,
                canonical_surfaces_all_satisfied=None,
            )
            == Area2OperationalState.intentionally_degraded
        )
    assert (
        expected_area2_operational_state_for_profile(
            Area2StartupProfile.testing_bootstrap_on,
            registry_model_spec_count=2,
            canonical_surfaces_all_satisfied=True,
        )
        == Area2OperationalState.healthy
    )


class _BootstrapEnabledTestingConfig(TestingConfig):
    ROUTING_REGISTRY_BOOTSTRAP = True


@pytest.mark.asyncio
async def test_g_final_02_healthy_canonical_paths_runtime_bootstrap_on():
    """G-FINAL-02: Runtime staged path remains eligible under testing_bootstrap_on create_app."""
    from app.content.module_models import ContentModule, ModuleMetadata
    from app.runtime.adapter_registry import get_adapter
    from app.runtime.ai_turn_executor import execute_turn_with_ai
    from app.runtime.runtime_models import SessionState

    clear_registry()
    app = create_app(_BootstrapEnabledTestingConfig)
    try:
        with app.app_context():
            assert get_adapter("mock") is not None
        meta = ModuleMetadata(
            module_id="m1",
            title="T",
            version="1",
            contract_version="1.0.0",
        )
        mod = ContentModule(metadata=meta, scenes={}, characters={})
        session = SessionState(
            session_id="gfinal02-rt",
            execution_mode="ai",
            adapter_name="mock",
            module_id="m1",
            module_version="1",
            current_scene_id="scene1",
        )
        session.canonical_state = {}
        mock_ad = get_adapter("mock")
        await execute_turn_with_ai(session, 1, mock_ad, mod)
        log = (session.metadata.get("ai_decision_logs") or [])[-1]
        for tr in log.runtime_stage_traces or []:
            if tr.get("stage_kind") != "routed_model_stage":
                continue
            dec = tr.get("decision")
            if isinstance(dec, dict):
                assert dec.get("route_reason_code") != RouteReasonCode.no_eligible_adapter.value, (
                    "healthy bootstrap-on runtime must not routine-hit no_eligible_adapter on routed stages"
                )
    finally:
        clear_registry()


def test_g_final_02_healthy_canonical_paths_writers_room_bootstrap_on(client_bootstrap_on, auth_headers_bootstrap_on):
    """G-FINAL-02: Writers-Room bounded stages route with eligible adapters under bootstrap-on app."""
    response = client_bootstrap_on.post(
        "/api/v1/writers-room/reviews",
        headers=auth_headers_bootstrap_on,
        json={"module_id": "god_of_carnage", "focus": "canon consistency"},
    )
    assert response.status_code == 200
    data = response.get_json()
    t2a = (data.get("model_generation") or {}).get("task_2a_routing") or {}
    for key in ("preflight", "synthesis"):
        st = t2a.get(key) or {}
        dec = st.get("decision") or {}
        assert dec.get("route_reason_code") != RouteReasonCode.no_eligible_adapter.value, (
            f"G-FINAL-02: {key} must not end in no_eligible_adapter on healthy canonical WR path"
        )
        assert dec.get("selected_adapter_name"), (
            f"G-FINAL-02: {key} must resolve a selected adapter name (routing succeeded)"
        )
    pre = t2a.get("preflight") or {}
    assert pre.get("bounded_model_call") is True, (
        "G-FINAL-02: preflight must perform bounded model call when adapter resolves"
    )
    audit = data.get("operator_audit") or {}
    assert_area2_truth_shape(audit.get("area2_operator_truth") or {})


def test_g_final_02_healthy_canonical_paths_improvement_bootstrap_on(client_bootstrap_on, auth_headers_bootstrap_on):
    """G-FINAL-02: Improvement bounded stages route with eligible adapters under bootstrap-on app."""
    variant_resp = client_bootstrap_on.post(
        "/api/v1/improvement/variants",
        headers=auth_headers_bootstrap_on,
        json={"baseline_id": "god_of_carnage", "candidate_summary": "G-FINAL-02 improvement variant."},
    )
    assert variant_resp.status_code == 201
    variant_id = variant_resp.get_json()["variant_id"]
    exp = client_bootstrap_on.post(
        "/api/v1/improvement/experiments/run",
        headers=auth_headers_bootstrap_on,
        json={
            "variant_id": variant_id,
            "test_inputs": ["a", "b", "c"],
        },
    )
    assert exp.status_code == 200
    rec = exp.get_json().get("recommendation_package") or {}
    t2a = rec.get("task_2a_routing") or {}
    for key in ("preflight", "synthesis"):
        st = t2a.get(key) or {}
        dec = st.get("decision") or {}
        assert dec.get("route_reason_code") != RouteReasonCode.no_eligible_adapter.value, (
            f"G-FINAL-02: improvement {key} must not end in no_eligible_adapter on healthy path"
        )
        assert dec.get("selected_adapter_name"), (
            f"G-FINAL-02: improvement {key} must resolve a selected adapter name"
        )
    assert (t2a.get("preflight") or {}).get("bounded_model_call") is True
    audit = rec.get("operator_audit") or {}
    assert_area2_truth_shape(audit.get("area2_operator_truth") or {})


def test_g_final_03_practical_authority_convergence_gate():
    """G-FINAL-03: registry lists operator truth + startup profiles; summary references route_model."""
    ids = {e.component_id for e in AREA2_AUTHORITY_REGISTRY}
    assert "area2_operator_truth" in ids
    assert "area2_startup_profiles" in ids
    assert "task2a_route_model" in ids
    policies = [e for e in AREA2_AUTHORITY_REGISTRY if e.layer == AuthorityLayer.authoritative]
    assert len(policies) >= 1
    specs = build_writers_room_model_route_specs()
    truth = build_area2_operator_truth(
        surface="writers_room",
        authority_source="build_writers_room_model_route_specs",
        bootstrap_enabled=True,
        registry_model_spec_count=len(specs),
        specs_for_coverage=list(specs),
        bounded_traces=[],
    )
    summary = truth.get("canonical_authority_summary") or ""
    assert "route_model" in summary
    assert "writers_room_model_routing" in summary or "adapter_registry" in summary


def test_g_final_04_no_eligible_non_normalization_gate():
    """G-FINAL-04: true no-eligible is classified distinctly; route_status does not read as plain healthy."""
    specs = build_writers_room_model_route_specs()
    trace_nea = [
        {
            "stage_id": "synthesis",
            "stage": "synthesis",
            "decision": {
                "route_reason_code": RouteReasonCode.no_eligible_adapter.value,
                "selected_adapter_name": None,
                "degradation_applied": False,
            },
            "routing_evidence": {"route_reason_code": RouteReasonCode.no_eligible_adapter.value},
        }
    ]
    truth = build_area2_operator_truth(
        surface="writers_room",
        authority_source="build_writers_room_model_route_specs",
        bootstrap_enabled=True,
        registry_model_spec_count=len(specs),
        specs_for_coverage=list(specs),
        bounded_traces=trace_nea,
    )
    assert truth["no_eligible_discipline"]["rollup_worst_case"] == NoEligibleDiscipline.true_no_eligible_adapter.value
    assert "not_normalized" in truth["legibility"]["route_status"]

    assert (
        classify_no_eligible_discipline(
            route_reason_code=RouteReasonCode.no_eligible_adapter.value,
            registry_spec_count=0,
            degradation_applied=False,
        )
        == NoEligibleDiscipline.test_isolated_empty_registry
    )
    assert (
        classify_no_eligible_discipline(
            route_reason_code=RouteReasonCode.no_eligible_adapter.value,
            registry_spec_count=3,
            degradation_applied=False,
        )
        == NoEligibleDiscipline.true_no_eligible_adapter
    )


def test_g_final_05_operator_legibility_gate():
    """G-FINAL-05: legibility block exposes direct readability fields (derived only)."""
    specs = build_writers_room_model_route_specs()
    truth = build_area2_operator_truth(
        surface="improvement",
        authority_source="build_writers_room_model_route_specs",
        bootstrap_enabled=False,
        registry_model_spec_count=len(specs),
        specs_for_coverage=list(specs),
        bounded_traces=[],
    )
    leg = truth["legibility"]
    assert leg["authority_source"] == "build_writers_room_model_route_specs"
    assert leg["operational_state"] == Area2OperationalState.test_isolated.value
    assert isinstance(leg["route_status"], str) and leg["route_status"]
    assert isinstance(leg["selected_vs_executed"], dict)
    assert ("primary_operational_concern" in leg) and (
        leg["primary_operational_concern"] is None or isinstance(leg["primary_operational_concern"], str)
    )
    assert leg["startup_profile"] == Area2StartupProfile.testing_isolated.value


@pytest.mark.asyncio
async def test_g_final_06_cross_surface_coherence_bootstrap_on(
    app_bootstrap_on,
    client_bootstrap_on,
    auth_headers_bootstrap_on,
):
    """G-FINAL-06: area2_operator_truth keys match across Runtime, WR, Improvement under same profile."""
    from app.content.module_models import ContentModule, ModuleMetadata
    from app.runtime.adapter_registry import register_adapter_model
    from app.runtime.ai_turn_executor import execute_turn_with_ai
    from app.runtime.routing_registry_bootstrap import bootstrap_routing_registry_from_config
    from app.runtime.runtime_models import SessionState

    from .test_runtime_staged_orchestration import StagedRecordingAdapter, _llm_spec, _slm_spec  # noqa: PLC2701

    clear_registry()
    bootstrap_routing_registry_from_config(app_bootstrap_on)
    try:
        with app_bootstrap_on.app_context():
            slm_ad = StagedRecordingAdapter("gfinal6_slm", slm_sufficient=True)
            llm_ad = StagedRecordingAdapter("gfinal6_llm", slm_sufficient=True)
            register_adapter_model(_slm_spec("gfinal6_slm"), slm_ad)
            register_adapter_model(_llm_spec("gfinal6_llm"), llm_ad)
            meta = ModuleMetadata(
                module_id="m1",
                title="T",
                version="1",
                contract_version="1.0.0",
            )
            mod = ContentModule(metadata=meta, scenes={}, characters={})
            session = SessionState(
                session_id="gfinal6-rt",
                execution_mode="ai",
                adapter_name="gfinal6_slm",
                module_id="m1",
                module_version="1",
                current_scene_id="scene1",
            )
            session.canonical_state = {}
            await execute_turn_with_ai(session, 1, slm_ad, mod)
            log = (session.metadata.get("ai_decision_logs") or [])[-1]
            rt_truth = (log.operator_audit or {}).get("area2_operator_truth") or {}
            assert_area2_truth_shape(rt_truth)
    finally:
        clear_registry()

    wr = client_bootstrap_on.post(
        "/api/v1/writers-room/reviews",
        headers=auth_headers_bootstrap_on,
        json={"module_id": "god_of_carnage", "focus": "G-FINAL-06 coherence"},
    )
    assert wr.status_code == 200
    wr_truth = (wr.get_json().get("operator_audit") or {}).get("area2_operator_truth") or {}
    assert_area2_truth_shape(wr_truth)

    variant_resp = client_bootstrap_on.post(
        "/api/v1/improvement/variants",
        headers=auth_headers_bootstrap_on,
        json={"baseline_id": "god_of_carnage", "candidate_summary": "G-FINAL-06 variant."},
    )
    assert variant_resp.status_code == 201
    variant_id = variant_resp.get_json()["variant_id"]
    exp = client_bootstrap_on.post(
        "/api/v1/improvement/experiments/run",
        headers=auth_headers_bootstrap_on,
        json={"variant_id": variant_id, "test_inputs": ["x"]},
    )
    assert exp.status_code == 200
    imp_truth = (exp.get_json().get("recommendation_package") or {}).get("operator_audit") or {}
    imp_truth = imp_truth.get("area2_operator_truth") or {}
    assert_area2_truth_shape(imp_truth)

    assert set(rt_truth.keys()) == set(wr_truth.keys()) == set(imp_truth.keys())


def test_g_final_07_legacy_compatibility_gate():
    """G-FINAL-07: TestingConfig default keeps bootstrap off and empty registry (isolated tests)."""
    clear_registry()

    class NoBootstrapConfig(TestingConfig):
        ROUTING_REGISTRY_BOOTSTRAP = False

    app = create_app(NoBootstrapConfig)
    try:
        with app.app_context():
            assert app.config["ROUTING_REGISTRY_BOOTSTRAP"] is False
            assert iter_model_specs() == []
    finally:
        clear_registry()


def test_g_final_08_documentation_and_closure_truth_gate():
    """G-FINAL-08: final gate docs and architecture cross-references list every G-FINAL id."""
    for name in G_FINAL_DOC_FILES + G_FINAL_ARCH_CROSSREF_FILES:
        path = REPO_ROOT / "docs" / "architecture" / name
        assert path.is_file(), f"missing architecture doc {name}"
        text = path.read_text(encoding="utf-8")
        for n in range(1, 9):
            assert f"G-FINAL-{n:02d}" in text, f"{name} missing G-FINAL-{n:02d}"
        assert "area2_routing_authority" in text
    gates_md = (REPO_ROOT / "docs" / "architecture" / "area2_final_closure_gates.md").read_text(encoding="utf-8")
    for n in range(1, 9):
        assert f"G-CONV-{n:02d}" in gates_md, "final gates doc must retain G-CONV cross-reference for continuity"
