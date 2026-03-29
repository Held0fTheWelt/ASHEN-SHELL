"""Integration tests for W3.3 session UI.

Tests verify:
- GET /play/<session_id> displays scene from canonical state
- POST /play/<session_id>/execute calls dispatch_turn with operator_input
- Result feedback is presenter-mapped correctly
- Session isolation between concurrent sessions
- CSRF protection on form submission

Note: Full integration tests deferred until W3.2 session creation flow is stable.
These tests verify route structure and imports.
"""

import pytest
from flask import session as flask_session


class TestSessionUIRoutes:
    """Tests for W3.3 UI routes."""

    def test_session_execute_route_requires_login(self, client):
        """POST /play/<session_id>/execute requires authentication."""
        response = client.post("/play/test-session/execute", data={}, follow_redirects=False)
        assert response.status_code == 302

    def test_session_start_returns_module_list(self, client, test_user):
        """GET /play shows available modules."""
        user, password = test_user
        client.post("/login", data={"username": user.username, "password": password}, follow_redirects=False)
        response = client.get("/play")
        assert response.status_code == 200
        assert b"god_of_carnage" in response.data
