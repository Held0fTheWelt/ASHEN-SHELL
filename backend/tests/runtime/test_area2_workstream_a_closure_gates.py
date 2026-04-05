"""Area 2 Workstream A — practical convergence closure (G-A-01 .. G-A-07)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.runtime.area2_operator_truth import build_area2_operator_truth
from app.runtime.area2_routing_authority import (
    AUTHORITY_SOURCE_IMPROVEMENT,
    AUTHORITY_SOURCE_RUNTIME,
    AUTHORITY_SOURCE_WRITERS_ROOM,
    AREA2_AUTHORITY_REGISTRY,
    AuthorityLayer,
    CanonicalSurface,
    assert_langgraph_not_canonical_for_task2a,
    assert_routing_policy_entry_is_unique_authoritative_policy,
    authority_entries_for_surface,
)
from app.services.writers_room_model_routing import build_writers_room_model_route_specs

from . import test_area2_convergence_gates as _conv
from . import test_area2_final_closure_gates as _final
from . import test_cross_surface_operator_audit_contract as _xs

REPO_ROOT = Path(__file__).resolve().parents[3]


def _assert_primary_authority_sources_per_surface() -> None:
    """Each canonical surface lists registry entries; spec source strings are non-empty."""
    for surf in CanonicalSurface:
        assert authority_entries_for_surface(surf), f"no authority entries for {surf.value}"
    assert AUTHORITY_SOURCE_RUNTIME.strip()
    assert AUTHORITY_SOURCE_WRITERS_ROOM.strip()
    assert AUTHORITY_SOURCE_IMPROVEMENT == AUTHORITY_SOURCE_WRITERS_ROOM


def test_g_a_01_primary_authority_convergence_gate() -> None:
    """G-A-01: one primary Task 2A policy; registry entries per surface; spec authority strings."""
    _conv.test_g_conv_01_single_authority_gate()
    _final.test_g_final_03_practical_authority_convergence_gate()
    _assert_primary_authority_sources_per_surface()


def test_g_a_02_non_competing_auxiliary_layer_gate() -> None:
    """G-A-02: auxiliary layers explicit, bounded, and non-competing with route_model."""
    assert_routing_policy_entry_is_unique_authoritative_policy()
    authoritative_policy_ids = {
        e.component_id for e in AREA2_AUTHORITY_REGISTRY if e.layer == AuthorityLayer.authoritative
    }
    assert authoritative_policy_ids == {
        "task2a_route_model",
        "task2a_adapter_registry",
        "task2a_contracts",
    }, "authoritative registry must contain only route_model, adapter_registry, and contracts"
    for e in AREA2_AUTHORITY_REGISTRY:
        assert e.module_path.strip(), f"{e.component_id} missing module_path"
        assert e.description.strip(), f"{e.component_id} missing description"
        if e.layer == AuthorityLayer.compatibility_layer:
            assert e.canonical_for_task2a_paths == frozenset(), (
                f"{e.component_id}: compatibility layer must not claim canonical Task 2A surfaces"
            )
        if e.layer == AuthorityLayer.translation_layer:
            assert e.canonical_for_task2a_paths, (
                f"{e.component_id}: translation layer must declare bounded canonical surfaces"
            )


def test_g_a_03_canonical_path_coherence_gate() -> None:
    """G-A-03: no practical split-brain — LangGraph not canonical; summary states compatibility-only."""
    assert_langgraph_not_canonical_for_task2a()
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
    assert "LangGraph" in summary or "compatibility" in summary, (
        "canonical_authority_summary must name LangGraph / compatibility-only posture explicitly"
    )


@pytest.mark.asyncio
async def test_g_a_04_healthy_canonical_path_confidence_gate() -> None:
    """G-A-04: Runtime, Writers-Room, and Improvement healthy paths under testing_bootstrap_on."""
    _conv.test_g_conv_02_healthy_bootstrap_gate_runtime_specs()
    await _conv.test_g_conv_02_healthy_bootstrap_no_routine_no_eligible_on_execute_turn()
    await _final.test_g_final_02_healthy_canonical_paths_runtime_bootstrap_on()


def test_g_a_04_healthy_canonical_path_confidence_gate_bounded_http(
    client_bootstrap_on,
    auth_headers_bootstrap_on,
) -> None:
    """G-A-04 (HTTP): Writers-Room and Improvement bounded paths coherent when bootstrap on."""
    _conv.test_bounded_specs_cover_writers_room_and_improvement_surfaces()
    _final.test_g_final_02_healthy_canonical_paths_writers_room_bootstrap_on(
        client_bootstrap_on, auth_headers_bootstrap_on
    )
    _final.test_g_final_02_healthy_canonical_paths_improvement_bootstrap_on(
        client_bootstrap_on, auth_headers_bootstrap_on
    )


def test_g_a_05_no_eligible_non_normalization_gate() -> None:
    """G-A-05: no_eligible discipline; not normalized as healthy canonical success."""
    _conv.test_g_conv_04_no_eligible_discipline_gate()
    _final.test_g_final_04_no_eligible_non_normalization_gate()


def test_g_a_06_operator_grade_convergence_readability_gate(client, auth_headers) -> None:
    """G-A-06: legibility + bounded HTTP operator truth readable (derived facts only)."""
    _final.test_g_final_05_operator_legibility_gate()
    _xs.test_writers_room_operator_audit_and_routing_evidence_contract(client, auth_headers)


def test_g_a_07_documentation_truth_for_convergence_gate() -> None:
    """G-A-07: architecture docs list every G-A id and reference area2_routing_authority."""
    doc_names = (
        "area2_workstream_a_gates.md",
        "area2_practical_convergence_closure_report.md",
        "area2_dual_workstream_closure_report.md",
        "llm_slm_role_stratification.md",
        "ai_story_contract.md",
    )
    for name in doc_names:
        path = REPO_ROOT / "docs" / "architecture" / name
        assert path.is_file(), f"missing architecture doc {name}"
        text = path.read_text(encoding="utf-8")
        for n in range(1, 8):
            assert f"G-A-{n:02d}" in text, f"{name} missing G-A-{n:02d}"
        assert "area2_routing_authority" in text, f"{name} must reference area2_routing_authority"
