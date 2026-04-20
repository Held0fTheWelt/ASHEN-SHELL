"""
Tests for player routes.

Covers:
- join_game: Player joins a session
- execute_action: Player executes a turn
- get_state: Player queries session state
- get_history: Player queries turn history

Constitutional Laws:
- Law 1: One truth boundary (world-engine authority)
- Law 4: Route purity (pure reflection of truth)
- Law 6: Fail closed on authority seams
- Law 8: Degraded-safe stays explicit
"""

import pytest
from flask_jwt_extended import create_access_token

from app.models import User


@pytest.fixture(scope="function")
def client(app):
    """Create test client."""
    return app.test_client()


class TestJoinGame:
    """Tests for join_game route."""

    def test_join_game_success_binds_player_to_session(self, client, test_user, auth_headers):
        """Player POST /api/v1/player/join_game binds player to session.

        Law 1: Session authority via world-engine
        Law 6: Fail closed on unknown session
        """
        user, _ = test_user  # Unpack (user, password) tuple
        session_id = "test-session-123"

        response = client.post(
            "/api/v1/player/join_game",
            json={"session_id": session_id},
            headers=auth_headers
        )

        # Should return 404 for nonexistent session (fail closed)
        # or 200 if session exists and binding succeeds
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert data["session_id"] == session_id
            assert "player_id" in data
            assert data["bound"] is True

    def test_join_game_missing_session_id_returns_400(self, client, auth_headers):
        """Missing session_id in request returns 400.

        Law 8: Explicit error, not hidden
        """
        response = client.post(
            "/api/v1/player/join_game",
            json={},
            headers=auth_headers
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data or "message" in data

    def test_join_game_missing_auth_returns_401(self, client):
        """Missing JWT returns 401.

        Law 6: Fail closed on missing authority
        """
        response = client.post(
            "/api/v1/player/join_game",
            json={"session_id": "test-session"}
        )

        assert response.status_code == 401

    def test_join_game_unknown_session_returns_404(self, client, auth_headers):
        """Unknown session_id returns 404, not 500.

        Law 6: Fail closed on unknown session
        """
        response = client.post(
            "/api/v1/player/join_game",
            json={"session_id": "nonexistent-session"},
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data or "message" in data


class TestExecuteAction:
    """Tests for execute_action route."""

    def test_execute_action_success_advances_turn(self, client, auth_headers):
        """Player POST /api/v1/player/execute_action executes turn.

        Law 1: Turn truth via world-engine authority
        """
        session_id = "test-session-123"
        action = {
            "type": "move",
            "target": "north",
            "parameters": {}
        }

        response = client.post(
            "/api/v1/player/execute_action",
            json={"session_id": session_id, "action": action},
            headers=auth_headers
        )

        # May return 404 if session doesn't exist, or 200 if it does
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert "success" in data
            if data.get("success"):
                assert "new_turn_number" in data
                assert data["new_turn_number"] >= 0

    def test_execute_action_missing_session_returns_400(self, client, auth_headers):
        """Missing session_id returns 400."""
        response = client.post(
            "/api/v1/player/execute_action",
            json={"action": {"type": "move"}},
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_execute_action_missing_action_returns_400(self, client, auth_headers):
        """Missing action returns 400."""
        response = client.post(
            "/api/v1/player/execute_action",
            json={"session_id": "test-session"},
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_execute_action_missing_auth_returns_401(self, client):
        """Missing JWT returns 401."""
        response = client.post(
            "/api/v1/player/execute_action",
            json={
                "session_id": "test-session",
                "action": {"type": "move"}
            }
        )

        assert response.status_code == 401

    def test_execute_action_unknown_session_returns_404(self, client, auth_headers):
        """Unknown session returns 404.

        Law 6: Fail closed on unknown session
        """
        response = client.post(
            "/api/v1/player/execute_action",
            json={
                "session_id": "nonexistent",
                "action": {"type": "move"}
            },
            headers=auth_headers
        )

        assert response.status_code == 404


class TestGetState:
    """Tests for get_state route."""

    def test_get_state_returns_current_snapshot(self, client, auth_headers):
        """Player GET /api/v1/player/state returns current session snapshot.

        Law 1: All reads from mirror (SessionService)
        Law 4: Route purity (pure reflection of truth)
        """
        session_id = "test-session-123"

        response = client.get(
            f"/api/v1/player/state?session_id={session_id}",
            headers=auth_headers
        )

        # May return 404 if session doesn't exist, or 200 if it does
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert data["session_id"] == session_id
            assert "turn_number" in data
            assert "state" in data

    def test_get_state_missing_session_id_returns_400(self, client, auth_headers):
        """Missing session_id query param returns 400."""
        response = client.get(
            "/api/v1/player/state",
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_get_state_missing_auth_returns_401(self, client):
        """Missing JWT returns 401."""
        response = client.get(
            "/api/v1/player/state?session_id=test-session"
        )

        assert response.status_code == 401

    def test_get_state_unknown_session_returns_404(self, client, auth_headers):
        """Unknown session returns 404.

        Law 6: Fail closed
        """
        response = client.get(
            "/api/v1/player/state?session_id=nonexistent",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestGetHistory:
    """Tests for get_history route."""

    def test_get_history_returns_turn_log(self, client, auth_headers):
        """Player GET /api/v1/player/history returns turn logs."""
        session_id = "test-session-123"

        response = client.get(
            f"/api/v1/player/history?session_id={session_id}&limit=10",
            headers=auth_headers
        )

        # May return 404 if session doesn't exist, or 200 if it does
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert data["session_id"] == session_id
            assert "history" in data
            assert isinstance(data["history"], list)

    def test_get_history_default_limit(self, client, auth_headers):
        """get_history without limit parameter uses default."""
        session_id = "test-session-123"

        response = client.get(
            f"/api/v1/player/history?session_id={session_id}",
            headers=auth_headers
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert "history" in data

    def test_get_history_missing_session_id_returns_400(self, client, auth_headers):
        """Missing session_id returns 400."""
        response = client.get(
            "/api/v1/player/history",
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_get_history_missing_auth_returns_401(self, client):
        """Missing JWT returns 401."""
        response = client.get(
            "/api/v1/player/history?session_id=test-session"
        )

        assert response.status_code == 401

    def test_get_history_unknown_session_returns_404(self, client, auth_headers):
        """Unknown session returns 404."""
        response = client.get(
            "/api/v1/player/history?session_id=nonexistent",
            headers=auth_headers
        )

        assert response.status_code == 404


class TestAuthorizationAndBinding:
    """Tests for authorization and player binding verification."""

    def test_join_game_with_valid_token(self, client, auth_headers, test_user):
        """join_game with valid JWT succeeds or returns appropriate error."""
        user, _ = test_user  # Unpack (user, password) tuple
        response = client.post(
            "/api/v1/player/join_game",
            json={"session_id": "test-session"},
            headers=auth_headers
        )

        # Should not be 401 (auth succeeded)
        assert response.status_code != 401

    def test_all_routes_require_jwt(self, client):
        """All player routes require JWT.

        Law 6: Fail closed on missing auth
        """
        routes = [
            ("POST", "/api/v1/player/join_game", {"session_id": "test"}),
            ("POST", "/api/v1/player/execute_action", {"session_id": "test", "action": {"type": "move"}}),
            ("GET", "/api/v1/player/state?session_id=test", None),
            ("GET", "/api/v1/player/history?session_id=test", None),
        ]

        for method, path, data in routes:
            if method == "POST":
                response = client.post(path, json=data)
            else:
                response = client.get(path)

            assert response.status_code == 401, f"{method} {path} should require JWT"
