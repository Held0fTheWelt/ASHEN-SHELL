"""MVP4 DiagnosticsEnvelope Manager Integration Tests.

Proves that _finalize_committed_turn produces diagnostics_envelope for GoC
solo sessions, and get_narrative_gov_summary returns operator health evidence.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock

from story_runtime_core.model_registry import ModelRegistry
from app.story_runtime.manager import StoryRuntimeManager


def _mock_graph_state():
    return {
        "validation_outcome": {
            "status": "approved",
            "reason": "mock_approved",
            "actor_lane_validation": {"status": "approved", "reason": ""},
        },
        "generation": {
            "success": True,
            "content": "Mock narration.",
            "metadata": {"adapter": "mock", "model": "mock-model"},
            "structured_output": {"mock": True},
        },
        "routing": {
            "selected_provider": "mock",
            "selected_model": "mock-model",
            "fallback_stage_reached": "primary_only",
        },
        "graph_diagnostics": {"errors": []},
        "visible_output_bundle": {"gm_narration": ["Mock."]},
        "committed_result": {"commit_applied": True},
        "quality_class": "canonical",
        "degradation_signals": [],
        "actor_survival_telemetry": {},
        "interpreted_input": {"input_kind": "dialogue"},
    }


def _goc_projection(human: str = "annette"):
    npc_map = {"annette": ["alain", "veronique", "michel"], "alain": ["annette", "veronique", "michel"]}
    npcs = npc_map.get(human, ["alain", "veronique", "michel"])
    return {
        "module_id": "god_of_carnage",
        "start_scene_id": "phase_1",
        "selected_player_role": human,
        "human_actor_id": human,
        "npc_actor_ids": npcs,
        "actor_lanes": {human: "human", **{n: "npc" for n in npcs}},
        "runtime_profile_id": "god_of_carnage_solo",
        "runtime_module_id": "solo_story_runtime",
        "content_module_id": "god_of_carnage",
    }


def _make_manager(human: str = "annette"):
    mgr = StoryRuntimeManager(registry=ModelRegistry(), adapters={})
    session = mgr.create_session(
        module_id="god_of_carnage",
        runtime_projection=_goc_projection(human),
    )
    mock_tg = MagicMock()
    mock_tg.run.return_value = _mock_graph_state()
    mgr.turn_graph = mock_tg
    return mgr, session


@pytest.mark.mvp4
def test_execute_turn_produces_diagnostics_envelope_annette():
    """execute_turn for Annette session includes diagnostics_envelope."""
    mgr, session = _make_manager("annette")
    result = mgr.execute_turn(
        session_id=session.session_id,
        player_input="What are we doing here?",
    )
    assert "diagnostics_envelope" in result
    env = result["diagnostics_envelope"]
    assert env["contract"] == "diagnostics_envelope.v1"
    assert env["human_actor_id"] == "annette"
    assert env["response_packaged_from_committed_state"] is True
    assert "visitor" not in json.dumps(env)


@pytest.mark.mvp4
def test_execute_turn_produces_diagnostics_envelope_alain():
    """execute_turn for Alain session includes diagnostics_envelope."""
    mgr, session = _make_manager("alain")
    result = mgr.execute_turn(
        session_id=session.session_id,
        player_input="I disagree with that.",
    )
    assert "diagnostics_envelope" in result
    env = result["diagnostics_envelope"]
    assert env["human_actor_id"] == "alain"
    assert "annette" in env["npc_actor_ids"]


@pytest.mark.mvp4
def test_diagnostics_envelope_actor_ownership():
    """Envelope includes actor ownership fields correctly."""
    mgr, session = _make_manager("annette")
    result = mgr.execute_turn(session_id=session.session_id, player_input="test")
    env = result["diagnostics_envelope"]
    assert env["human_actor_id"] == "annette"
    assert "alain" in env["ai_allowed_actor_ids"]
    assert "annette" in env["ai_forbidden_actor_ids"]
    assert "visitor" not in env["ai_allowed_actor_ids"]


@pytest.mark.mvp4
def test_diagnostics_envelope_langfuse_status():
    """langfuse_status reflects LANGFUSE_ENABLED env var (enabled/disabled)."""
    import os
    mgr, session = _make_manager("annette")
    result = mgr.execute_turn(session_id=session.session_id, player_input="test")
    env = result["diagnostics_envelope"]
    # Status should reflect LANGFUSE_ENABLED env var
    # (enabled_no_trace if enabled but no credentials, disabled if not enabled)
    is_enabled = os.getenv("LANGFUSE_ENABLED", "").lower() == "true"
    if is_enabled:
        # When enabled, status is "enabled_no_trace" (no credentials provided in test)
        assert env["langfuse_status"] in ("enabled_no_trace", "enabled")
    else:
        assert env["langfuse_status"] == "disabled"
    assert env["langfuse_trace_id"] == ""


@pytest.mark.mvp4
def test_diagnostics_traceable_decisions_present():
    """Envelope includes traceable decisions for responder, actor-lane, drama, commit."""
    mgr, session = _make_manager("annette")
    result = mgr.execute_turn(session_id=session.session_id, player_input="test")
    env = result["diagnostics_envelope"]
    decisions = env.get("traceable_decisions") or []
    assert len(decisions) >= 2
    types = {d["decision_type"] for d in decisions}
    assert "actor_lane_validation" in types
    assert "engine_commit" in types


@pytest.mark.mvp4
def test_get_last_diagnostics_envelope_method():
    """get_last_diagnostics_envelope returns envelope after turn."""
    mgr, session = _make_manager("annette")
    mgr.execute_turn(session_id=session.session_id, player_input="test")
    envelope = mgr.get_last_diagnostics_envelope(session.session_id)
    assert envelope is not None
    assert envelope["contract"] == "diagnostics_envelope.v1"


@pytest.mark.mvp4
def test_narrative_gov_summary_after_turn():
    """get_narrative_gov_summary returns real operator health after turn."""
    mgr, session = _make_manager("annette")
    mgr.execute_turn(session_id=session.session_id, player_input="test")
    summary = mgr.get_narrative_gov_summary()
    assert summary["contract"] == "narrative_gov_summary.v1"
    assert summary["last_story_session_id"] == session.session_id
    assert summary["last_turn_number"] == 1
    assert summary["ldss_health"]["status"] == "evidenced_live_path"
    assert summary["actor_lane_health"]["visitor_present"] is False


@pytest.mark.mvp4
def test_non_goc_session_no_diagnostics_envelope():
    """Non-GoC sessions do not produce diagnostics_envelope."""
    mgr = StoryRuntimeManager(registry=ModelRegistry(), adapters={})
    session = mgr.create_session(
        module_id="test_module",
        runtime_projection={"module_id": "test_module", "start_scene_id": "start"},
    )
    mock_tg = MagicMock()
    mock_tg.run.return_value = _mock_graph_state()
    mgr.turn_graph = mock_tg
    result = mgr.execute_turn(session_id=session.session_id, player_input="test")
    assert "diagnostics_envelope" not in result
