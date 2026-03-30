"""Test W3.1 Session API endpoints scope boundaries.

These endpoints are deferred to W3.2 (persistence layer not yet implemented).
Tests verify they return 501 Not Implemented as per W3.1 contract.
"""

import pytest
import json
from app.services.session_service import create_session


def test_get_session_returns_501_not_implemented(client, test_user):
    """GET /api/v1/sessions/<id> deferred to W3.2."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    response = client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 501
    data = json.loads(response.data)
    assert "error" in data
    assert "W3.2" in data["error"] or "persistence" in data["error"]


def test_post_execute_turn_returns_501_not_implemented(client, test_user):
    """POST /api/v1/sessions/<id>/turns deferred to W3.2."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    response = client.post(
        f"/api/v1/sessions/{session_id}/turns",
        json={"operator_input": "test action", "turn_number": 1},
        content_type="application/json"
    )

    assert response.status_code == 501
    data = json.loads(response.data)
    assert "error" in data


def test_get_logs_returns_501_not_implemented(client, test_user):
    """GET /api/v1/sessions/<id>/logs deferred to W3.2."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    response = client.get(f"/api/v1/sessions/{session_id}/logs")

    assert response.status_code == 501
    data = json.loads(response.data)
    assert "error" in data


def test_get_state_returns_501_not_implemented(client, test_user):
    """GET /api/v1/sessions/<id>/state deferred to W3.2."""
    session = create_session("god_of_carnage")
    session_id = session.session_id

    response = client.get(f"/api/v1/sessions/{session_id}/state")

    assert response.status_code == 501
    data = json.loads(response.data)
    assert "error" in data


def test_create_session_still_works(client, test_user):
    """POST /api/v1/sessions (create) is fully implemented in W3.1."""
    response = client.post(
        "/api/v1/sessions",
        json={"module_id": "god_of_carnage"},
        content_type="application/json"
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "session_id" in data
    assert data["module_id"] == "god_of_carnage"
