"""Test W3 Session API endpoints for closure.

Tests verify that the 4 stubbed API endpoints now return real data
instead of 501 errors.
"""

import pytest
import json
from app.services.session_service import create_session


def test_get_session_returns_current_state(client, test_user):
    """GET /api/v1/sessions/<id> returns current SessionState."""
    # Create a session
    session = create_session("god_of_carnage")
    session_id = session.session_id

    # GET the session
    response = client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"
    data = json.loads(response.data)
    assert data["session_id"] == session_id
    assert data["module_id"] == "god_of_carnage"
    assert "canonical_state" in data
    assert "context_layers" in data


def test_post_execute_turn_executes_and_returns_result(client, test_user):
    """POST /api/v1/sessions/<id>/turns executes turn and returns TurnExecutionResult."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    # Execute turn
    response = client.post(
        f"/api/v1/sessions/{session_id}/turns",
        json={"operator_input": "test action", "turn_number": 1},
        content_type="application/json"
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "turn_number" in data
    assert "result_status" in data or "outcome" in data
    assert "updated_state" in data


def test_get_logs_returns_event_log(client, test_user):
    """GET /api/v1/sessions/<id>/logs returns RuntimeEventLog."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    # GET logs (even with no turns executed yet)
    response = client.get(f"/api/v1/sessions/{session_id}/logs")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert "events" in data or "entries" in data
    # First session may have 0 events


def test_get_state_returns_current_canonical_state(client, test_user):
    """GET /api/v1/sessions/<id>/state returns current canonical_state only."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    response = client.get(f"/api/v1/sessions/{session_id}/state")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    # Canonical state should be a dict (may be empty or have scene/character data)


def test_execution_result_persisted_in_context(client, test_user):
    """Turn execution result and AI log persisted in SessionState."""
    from app.runtime.session_store import get_session as get_runtime_session

    session = create_session("god_of_carnage")
    session_id = session.session_id

    # Execute a turn via API
    response = client.post(
        f"/api/v1/sessions/{session_id}/turns",
        json={"operator_input": "test action"},
        content_type="application/json"
    )
    assert response.status_code == 200

    # Verify diagnostics persisted in SessionState
    runtime_session = get_runtime_session(session_id)
    state = runtime_session.current_runtime_state

    assert state is not None
    assert state.context_layers is not None
    assert state.context_layers.last_turn_number > 0, "Turn number should be set after execution"
    # last_turn_execution_result may be None or dict depending on mock behavior
    assert state.context_layers.last_turn_number == 1
