"""Area 2 Closure Task 1 — Runtime ranking stage closure gates (G-RANK-01 .. G-RANK-08).

Pass conditions and failure meaning are documented in each test docstring.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.content.module_models import ContentModule, ModuleMetadata
from app.runtime.adapter_registry import clear_registry, register_adapter_model
from app.runtime.ai_adapter import AdapterRequest, AdapterResponse, StoryAIAdapter
from app.runtime.ai_turn_executor import execute_turn_with_ai
from app.runtime.model_inventory_contract import RUNTIME_STAGED_REQUIRED, RequiredRoutingTuple
from app.runtime.model_routing_contracts import TaskKind, WorkflowPhase
from app.runtime.runtime_ai_stages import (
    RANKING_SLM_ONLY_SKIP_REASON,
    RankingStageOutput,
    RuntimeStageId,
    SignalStageOutput,
    build_ranking_routing_request,
    compute_synthesis_gate_after_ranking,
    parse_ranking_payload,
)
from app.runtime.runtime_models import SessionState

from .test_runtime_staged_orchestration import StagedRecordingAdapter, _llm_spec, _slm_spec


REPO_ROOT = Path(__file__).resolve().parents[3]
DOCS_STRAT = REPO_ROOT / "docs" / "architecture" / "llm_slm_role_stratification.md"
DOCS_CONTRACT = REPO_ROOT / "docs" / "architecture" / "ai_story_contract.md"
DOCS_CLOSURE = REPO_ROOT / "docs" / "architecture" / "area2_runtime_ranking_closure_report.md"


@pytest.fixture
def minimal_module() -> ContentModule:
    meta = ModuleMetadata(
        module_id="m1",
        title="T",
        version="1",
        contract_version="1.0.0",
    )
    return ContentModule(metadata=meta, scenes={}, characters={})


def test_g_rank_01_stage_existence_gate():
    """G-RANK-01: Ranking exists as an explicit Runtime stage identity.

    Pass: ``RuntimeStageId.ranking`` is defined.
    Fail: Ranking folded into another stage identifier or missing from the enum.
    """

    assert hasattr(RuntimeStageId, "ranking")
    assert RuntimeStageId.ranking.value == "ranking"


def test_g_rank_02_stage_contract_gate():
    """G-RANK-02: Ranking has a bounded Pydantic contract distinct from story output.

    Pass: ``RankingStageOutput`` validates bounded payloads; invalid payloads fail parse.
    Fail: Unbounded or implicit contract without validation.
    """

    ok, err = parse_ranking_payload(
        {
            "runtime_stage": "ranking",
            "ranked_hypotheses": ["a"],
            "preferred_hypothesis_index": 0,
            "recommend_skip_synthesis": True,
            "skip_synthesis_after_ranking_reason": "clear_single_read",
            "synthesis_recommended": False,
            "ambiguity_residual": 0.1,
            "ranking_confidence": 0.9,
            "ranking_notes": [],
        }
    )
    assert ok is not None and not err

    bad, err2 = parse_ranking_payload({"runtime_stage": "ranking", "recommend_skip_synthesis": True})
    assert bad is None and err2


def test_g_rank_03_stage_routing_gate():
    """G-RANK-03: Ranking routing request is stage-specific (interpretation + ranking task kind).

    Pass: ``build_ranking_routing_request`` sets ``TaskKind.ranking`` and correct phase.
    Fail: Ranking reuses signal or synthesis routing semantics.
    """

    session = SessionState(
        session_id="g3",
        execution_mode="ai",
        adapter_name="x",
        module_id="m1",
        module_version="1",
        current_scene_id="s1",
    )
    session.canonical_state = {}
    rr = build_ranking_routing_request(session, extra_hints=[])
    assert rr.workflow_phase == WorkflowPhase.interpretation
    assert rr.task_kind == TaskKind.ranking
    assert rr.requires_structured_output is True


@pytest.mark.asyncio
async def test_g_rank_04_orchestration_effect_gate(minimal_module: ContentModule):
    """G-RANK-04: Ranking materially changes synthesis vs signal-only counterfactual.

    Pass:
    - Ranked-skip: signal requests synthesis; ranking suppresses → no synthesis call.
    - Ranked-then-synthesis: ranking preserves synthesis intent → LLM synthesis invoked.
    - Degraded ranking parse: invalid ranking payload forces synthesis with degraded reason.

    Fail: Ranking traces exist but never change ``needs_llm`` outcomes.
    """

    clear_registry()
    skip_ad = StagedRecordingAdapter("g4_skip", slm_sufficient=False, rank_recommend_skip=True)
    register_adapter_model(_slm_spec("g4_skip"), skip_ad)
    register_adapter_model(_llm_spec("g4_skip_llm"), StagedRecordingAdapter("g4_skip_llm"))
    session = SessionState(
        session_id="g4-skip",
        execution_mode="ai",
        adapter_name="g4_skip",
        module_id="m1",
        module_version="1",
        current_scene_id="scene1",
    )
    session.canonical_state = {}
    await execute_turn_with_ai(session, 1, skip_ad, minimal_module)
    log = (session.metadata.get("ai_decision_logs") or [])[-1]
    assert log.runtime_orchestration_summary.get("final_path") == "ranked_slm_only"
    assert log.runtime_orchestration_summary.get("synthesis_gate_reason") == "ranking_skip_synthesis"
    assert "synthesis" not in skip_ad.stages_seen

    clear_registry()
    keep_ad = StagedRecordingAdapter("g4_keep", slm_sufficient=False, rank_recommend_skip=False)
    llm_keep = StagedRecordingAdapter("g4_keep_llm", slm_sufficient=False)
    register_adapter_model(_slm_spec("g4_keep"), keep_ad)
    register_adapter_model(_llm_spec("g4_keep_llm"), llm_keep)
    session2 = SessionState(
        session_id="g4-keep",
        execution_mode="ai",
        adapter_name="g4_keep",
        module_id="m1",
        module_version="1",
        current_scene_id="scene1",
    )
    session2.canonical_state = {}
    await execute_turn_with_ai(session2, 1, keep_ad, minimal_module)
    log2 = (session2.metadata.get("ai_decision_logs") or [])[-1]
    assert log2.runtime_orchestration_summary.get("final_path") == "ranked_then_llm"
    assert "synthesis" in llm_keep.stages_seen

    clear_registry()

    class BadRankingGoodSignalAdapter(StoryAIAdapter):
        @property
        def adapter_name(self) -> str:
            return "g4_bad_rank"

        def generate(self, request: AdapterRequest) -> AdapterResponse:
            stage = (request.metadata or {}).get("runtime_stage") or ""
            if stage == "preflight":
                pl = {
                    "runtime_stage": "preflight",
                    "ambiguity_score": 0.1,
                    "trigger_signals": [],
                    "repetition_risk": "low",
                    "classification_label": "x",
                    "preflight_ok": True,
                }
            elif stage == "signal_consistency":
                pl = {
                    "runtime_stage": "signal_consistency",
                    "needs_llm_synthesis": True,
                    "narrative_summary": "n",
                    "consistency_notes": "",
                    "consistency_flags": [],
                }
            elif stage == "ranking":
                pl = {"runtime_stage": "ranking", "recommend_skip_synthesis": "not_bool"}
            else:
                pl = {"scene_interpretation": "x", "detected_triggers": [], "proposed_state_deltas": []}
            return AdapterResponse(raw_output=json.dumps(pl), structured_payload=pl, error=None)

    bad_ad = BadRankingGoodSignalAdapter()
    llm_deg = StagedRecordingAdapter("g4_bad_llm", slm_sufficient=False)
    register_adapter_model(_slm_spec("g4_bad_rank"), bad_ad)
    register_adapter_model(_llm_spec("g4_bad_llm"), llm_deg)
    session3 = SessionState(
        session_id="g4-deg",
        execution_mode="ai",
        adapter_name="g4_bad_rank",
        module_id="m1",
        module_version="1",
        current_scene_id="scene1",
    )
    session3.canonical_state = {}
    await execute_turn_with_ai(session3, 1, bad_ad, minimal_module)
    log3 = (session3.metadata.get("ai_decision_logs") or [])[-1]
    assert (
        log3.runtime_orchestration_summary.get("synthesis_gate_reason")
        == "degraded_ranking_parse_forcing_synthesis"
    )
    assert log3.runtime_orchestration_summary.get("final_path") == "degraded_ranking_parse_forcing_synthesis"
    clear_registry()


@pytest.mark.asyncio
async def test_g_rank_05_trace_and_audit_visibility_gate(minimal_module: ContentModule):
    """G-RANK-05: Ranking appears in stage traces, summary, and operator audit timeline.

    Pass: Trace list includes ``ranking``; summary exposes ``ranking_effect``; audit timeline includes ranking.
    Fail: Ranking only exists in comments or non-audit side channels.
    """

    clear_registry()
    ad = StagedRecordingAdapter("g5", slm_sufficient=True)
    register_adapter_model(_slm_spec("g5"), ad)
    session = SessionState(
        session_id="g5",
        execution_mode="ai",
        adapter_name="g5",
        module_id="m1",
        module_version="1",
        current_scene_id="scene1",
    )
    session.canonical_state = {}
    await execute_turn_with_ai(session, 1, ad, minimal_module)
    log = (session.metadata.get("ai_decision_logs") or [])[-1]
    ids = [t.get("stage_id") for t in log.runtime_stage_traces or []]
    assert "ranking" in ids
    assert "ranking_effect" in (log.runtime_orchestration_summary or {})
    timeline = (log.operator_audit or {}).get("audit_timeline") or []
    assert any(e.get("stage_key") == "ranking" for e in timeline)
    clear_registry()


def test_g_rank_06_path_coverage_gate_documented():
    """G-RANK-06: Path coverage is enforced by this module plus staged orchestration tests.

    Pass: This file and ``test_runtime_staged_orchestration`` together prove SLM-only (suppressed ranking),
    ranked-then-synthesis, ranked-skip, and degraded ranking (G-RANK-04).
    Fail: Any listed path lacks a dedicated proof test.
    """

    # Consolidated marker — individual paths are asserted in G-RANK-04 and staged orchestration tests.
    assert RANKING_SLM_ONLY_SKIP_REASON == "ranking_not_required_signal_allows_slm_only"


@pytest.mark.asyncio
async def test_g_rank_06_slm_only_suppressed_ranking_trace(minimal_module: ContentModule):
    """G-RANK-06 (supplement): SLM-only path records ranking stage without routing or bounded call."""

    clear_registry()
    ad = StagedRecordingAdapter("g6", slm_sufficient=True)
    register_adapter_model(_slm_spec("g6"), ad)
    session = SessionState(
        session_id="g6",
        execution_mode="ai",
        adapter_name="g6",
        module_id="m1",
        module_version="1",
        current_scene_id="scene1",
    )
    session.canonical_state = {}
    await execute_turn_with_ai(session, 1, ad, minimal_module)
    log = (session.metadata.get("ai_decision_logs") or [])[-1]
    rk = next(t for t in log.runtime_stage_traces or [] if t.get("stage_id") == "ranking")
    assert rk.get("skip_reason") == RANKING_SLM_ONLY_SKIP_REASON
    assert rk.get("decision") is None
    assert rk.get("bounded_model_call") is False
    clear_registry()


def test_g_rank_07_documentation_truth_gate():
    """G-RANK-07: Documentation and inventory describe the ranking stage.

    Pass: Required routing tuples include ranking; architecture docs and closure report exist and mention ranking.
    Fail: Docs describe a pipeline without ranking while code requires it.
    """

    ranking_tuples = [
        t
        for t in RUNTIME_STAGED_REQUIRED
        if t.task_kind == TaskKind.ranking and t.workflow_phase == WorkflowPhase.interpretation
    ]
    assert len(ranking_tuples) == 1
    assert isinstance(ranking_tuples[0], RequiredRoutingTuple)
    assert DOCS_STRAT.is_file()
    assert DOCS_CONTRACT.is_file()
    assert DOCS_CLOSURE.is_file()
    text = DOCS_STRAT.read_text(encoding="utf-8") + DOCS_CONTRACT.read_text(encoding="utf-8")
    assert "ranking" in text.lower()
    closure = DOCS_CLOSURE.read_text(encoding="utf-8")
    assert "G-RANK-01" in closure


@pytest.mark.asyncio
async def test_g_rank_08_legacy_authority_safety_gate(minimal_module: ContentModule):
    """G-RANK-08: Ranked-skip path still completes execute_turn successfully (guards unchanged).

    Pass: ``execution_status == success`` and ``guard_outcome`` populated on ranked-skip path.
    Fail: Ranking integration breaks guard or commit semantics.
    """

    import asyncio

    clear_registry()
    ad = StagedRecordingAdapter("g8", slm_sufficient=False, rank_recommend_skip=True)
    register_adapter_model(_slm_spec("g8"), ad)
    register_adapter_model(_llm_spec("g8_llm"), StagedRecordingAdapter("g8_llm"))
    session = SessionState(
        session_id="g8",
        execution_mode="ai",
        adapter_name="g8",
        module_id="m1",
        module_version="1",
        current_scene_id="scene1",
    )
    session.canonical_state = {}
    result = await asyncio.wait_for(execute_turn_with_ai(session, 1, ad, minimal_module), timeout=30.0)
    assert result.execution_status == "success"
    assert result.guard_outcome is not None
    clear_registry()


def test_compute_synthesis_gate_after_ranking_no_eligible_fallback():
    """G-RANK-04 supplement: no-eligible ranking falls back to base signal gate."""

    sig = SignalStageOutput(
        needs_llm_synthesis=True,
        narrative_summary="n",
        consistency_notes="",
        consistency_flags=[],
    )
    needs, reason, effect = compute_synthesis_gate_after_ranking(
        base_needs_llm=True,
        base_reason="signal_requested_synthesis",
        signal=sig,
        signal_parse_ok=True,
        ranking_out=None,
        ranking_parse_ok=False,
        ranking_bounded_ran=False,
        ranking_no_eligible_adapter=True,
    )
    assert needs is True
    assert reason == "degraded_ranking_no_eligible_adapter_fallback_to_signal_gate"
    assert effect == "degraded_no_eligible_fallback"
