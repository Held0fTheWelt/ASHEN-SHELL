from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def test_session_routes_declares_non_authority_warnings_and_world_engine_bridge() -> None:
    text = _read("backend/app/api/v1/session_routes.py")
    assert "Live play runs in the World Engine" in text
    assert "volatile in-memory ``SessionState``" in text
    assert "backend_in_process_session_not_authoritative_live_runtime" in text
    assert "authoritative_runs_execute_in_world_engine_play_service" in text
    assert "world_engine_story_runtime_authoritative_snapshot" in text
    assert "execute_story_turn_in_engine" in text
    assert "get_story_state" in text
    assert "get_story_diagnostics" in text



def test_session_store_declares_volatile_local_bounded_non_authoritative_role() -> None:
    text = _read("backend/app/runtime/session_store.py")
    assert "volatile in-memory registry" in text
    assert "authoritative for live play" in text
    assert "durable or" in text
    assert "data is lost on restart" in text
    assert "_runtime_sessions" in text



def test_session_service_stays_bootstrap_only_with_deferred_methods_unimplemented() -> None:
    text = _read("backend/app/services/session_service.py")
    assert "not" in text.lower() and "live narrative runtime" in text
    assert "create_session: start a **local** session" in text
    assert "register in ``session_store``" in text
    assert text.count("NotImplementedError") >= 4
    assert 'raise NotImplementedError("get_session requires W3.2 session persistence")' in text
    assert 'raise NotImplementedError("execute_turn requires W3.2 turn execution and persistence")' in text



def test_world_engine_console_routes_are_admin_capability_gated_bridge_only() -> None:
    text = _read("backend/app/api/v1/world_engine_console_routes.py")
    assert "Admin API: proxy read/write World Engine play service" in text
    assert "require_jwt_moderator_or_admin" in text
    assert "require_world_engine_capability" in text
    assert "/admin/world-engine/" in text
    assert "get_play_service_ready" in text
    assert "get_story_state" in text
    assert "get_story_diagnostics" in text
    assert "execute_story_turn" in text
    assert "session_store" not in text
    assert '"/api/v1/sessions"' not in text


def test_marker_backend_local_compatibility_state_minimized_after_authoritative_binding_present() -> None:
    text = _read("backend/app/api/v1/session_routes.py") + _read("backend/app/services/ai_stack_evidence_service.py")
    assert "backend_local_compatibility_state_minimized_after_authoritative_binding" in text


def test_marker_authoritative_story_session_id_or_explicit_local_fallback_required_present() -> None:
    text = _read("backend/app/api/v1/session_routes.py") + _read("backend/app/services/ai_stack_evidence_service.py")
    assert "AUTHORITATIVE_STORY_SESSION_ID_OR_EXPLICIT_LOCAL_FALLBACK_REQUIRED" in text


def test_marker_backend_local_fallback_can_only_be_used_as_explicit_compatibility_residue_present() -> None:
    text = _read("backend/app/api/v1/session_routes.py") + _read("backend/app/services/ai_stack_evidence_service.py")
    assert "backend_local_fallback_can_only_be_used_as_explicit_compatibility_residue" in text


def test_session_service_exposes_local_bootstrap_helper() -> None:
    text = _read("backend/app/services/session_service.py")
    assert "create_local_bootstrap_session" in text
