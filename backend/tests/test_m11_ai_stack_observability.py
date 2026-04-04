"""Milestone 11: trace continuity, governance evidence API, and failure visibility tests."""

from __future__ import annotations

from app.observability.audit_log import log_world_engine_bridge, log_workflow_audit
from app.services.game_service import GameServiceError


def test_admin_session_evidence_returns_runtime_bundle(client, moderator_headers, monkeypatch):
    create_resp = client.post("/api/v1/sessions", json={"module_id": "god_of_carnage"})
    assert create_resp.status_code == 201
    session_id = create_resp.get_json()["session_id"]

    monkeypatch.setattr(
        "app.services.ai_stack_evidence_service.get_story_state",
        lambda *_a, **_k: {"session_id": "we-x", "turn_counter": 0},
    )
    monkeypatch.setattr(
        "app.services.ai_stack_evidence_service.get_story_diagnostics",
        lambda *_a, **_k: {"diagnostics": [{"graph": {"repro_metadata": {"module_id": "god_of_carnage"}}}]},
    )

    from app.runtime.session_store import get_session as get_runtime_session

    runtime_session = get_runtime_session(session_id)
    runtime_session.current_runtime_state.metadata["world_engine_story_session_id"] = "we-x"

    response = client.get(
        f"/api/v1/admin/ai-stack/session-evidence/{session_id}",
        headers=moderator_headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["backend_session_id"] == session_id
    assert data["module_id"] == "god_of_carnage"
    assert data["world_engine_story_session_id"] == "we-x"
    assert data["world_engine_state"]["session_id"] == "we-x"
    assert data.get("last_turn_repro_metadata", {}).get("module_id") == "god_of_carnage"
    assert "trace_id" in data


def test_admin_session_evidence_404_for_unknown_session(client, moderator_headers):
    response = client.get(
        "/api/v1/admin/ai-stack/session-evidence/nonexistent-session-id",
        headers=moderator_headers,
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data.get("error") == "backend_session_not_found"


def test_execute_turn_surfaces_world_engine_failure(client, monkeypatch):
    create_resp = client.post("/api/v1/sessions", json={"module_id": "god_of_carnage"})
    session_id = create_resp.get_json()["session_id"]

    def _boom(**_kwargs):
        raise GameServiceError("play down", status_code=503)

    monkeypatch.setattr("app.api.v1.session_routes.create_story_session", _boom)

    response = client.post(
        f"/api/v1/sessions/{session_id}/turns",
        json={"player_input": "look"},
    )
    assert response.status_code == 502
    body = response.get_json()
    assert body.get("failure_class") == "world_engine_unreachable"
    assert "trace_id" in body


def test_workflow_and_bridge_audit_emit_structured_dicts(monkeypatch):
    sent: list[dict] = []

    class _FakeLogger:
        def info(self, msg):
            sent.append(msg)

    monkeypatch.setattr("app.observability.audit_log.get_audit_logger", lambda: _FakeLogger())
    log_workflow_audit(
        "t-wf", workflow="writers_room_review", actor_id="1", outcome="ok", resource_id="god_of_carnage"
    )
    log_world_engine_bridge(
        "t-br",
        operation="execute_story_turn",
        backend_session_id="bs1",
        world_engine_story_session_id="we1",
        outcome="ok",
    )
    assert sent[0]["event"] == "workflow.run"
    assert sent[0]["trace_id"] == "t-wf"
    assert sent[1]["event"] == "world_engine.bridge"
    assert sent[1].get("failure_class") is None


def test_improvement_experiment_response_includes_trace(client, auth_headers):
    variant_resp = client.post(
        "/api/v1/improvement/variants",
        headers=auth_headers,
        json={"baseline_id": "god_of_carnage", "candidate_summary": "Test candidate for trace field."},
    )
    assert variant_resp.status_code == 201
    variant_id = variant_resp.get_json()["variant_id"]
    experiment_resp = client.post(
        "/api/v1/improvement/experiments/run",
        headers=auth_headers,
        json={"variant_id": variant_id},
    )
    assert experiment_resp.status_code == 200
    payload = experiment_resp.get_json()
    assert "trace_id" in payload
    assert "experiment" in payload
    assert "recommendation_package" in payload
