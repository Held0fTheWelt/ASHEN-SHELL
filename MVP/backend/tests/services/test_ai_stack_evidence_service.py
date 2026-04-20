from app.services.ai_stack_evidence_service import build_session_evidence_bundle
from app.services.session_service import create_session


def test_build_session_evidence_bundle_requires_authoritative_id_when_unbound_fallback_not_allowed():
    session = create_session("god_of_carnage")
    data = build_session_evidence_bundle(session_id=session.session_id, trace_id="trace-unbound", allow_backend_local_fallback=False)
    assert data["error"] == "authoritative_world_engine_story_session_id_required"
    assert data["backend_session_id"] == session.session_id

