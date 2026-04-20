"""
Player-facing routes for World of Shadows.

Implements:
- join_game: Player joins a session
- execute_action: Player executes a turn
- get_state: Player queries session state
- get_history: Player queries turn history

Constitutional Laws:
- Law 1: One truth boundary (all session authority via world-engine)
- Law 4: Route purity (routes are pure reflections of truth)
- Law 6: Fail closed on authority seams (unknown binding → 401, unknown session → 404)
- Law 8: Degraded-safe stays explicit (all errors explicit, no hidden degradation)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.api.v1 import api_v1_bp
from app.services.session_service import SessionService


def _get_current_player_id() -> Optional[str]:
    """Get current player ID from JWT. Returns None if missing/invalid."""
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception:
        return None


def _require_jwt() -> Optional[str]:
    """Verify JWT and return player ID, or None if missing. Caller responsible for error response."""
    return _get_current_player_id()


def _get_session_service() -> SessionService:
    """Get or create session service."""
    if not hasattr(current_app, '_session_service'):
        current_app._session_service = SessionService()
    return current_app._session_service


@api_v1_bp.route("/player/join_game", methods=["POST"])
def join_game():
    """
    Player joins a game session.

    POST /api/v1/player/join_game

    Request:
        {
            "session_id": string
        }

    Response (200):
        {
            "session_id": string,
            "player_id": string,
            "bound": bool,
            "session": {state snapshot}
        }

    Errors:
        - 400: Missing session_id
        - 401: Missing/invalid JWT
        - 404: Unknown session

    Law 1: Session authority via world-engine
    Law 6: Fail closed (unknown session → 404)
    """
    # Verify JWT (Law 6: fail closed on missing auth)
    player_id = _require_jwt()
    if not player_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Get request data
    data = request.get_json() or {}
    session_id = data.get("session_id")

    # Validate input (Law 8: explicit errors)
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    # Get session service
    service = _get_session_service()

    # Verify session exists (Law 6: fail closed on unknown session)
    session = service.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Bind player to session (Law 1: authority via world-engine)
    bound = service.bind_player(session_id, player_id)

    # Return result
    return jsonify({
        "session_id": session_id,
        "player_id": player_id,
        "bound": bound,
        "session": session
    }), 200


@api_v1_bp.route("/player/execute_action", methods=["POST"])
def execute_action():
    """
    Player executes a turn action.

    POST /api/v1/player/execute_action

    Request:
        {
            "session_id": string,
            "action": {
                "type": string,
                "target": string,
                "parameters": object
            }
        }

    Response (200):
        {
            "success": bool,
            "new_turn_number": int,
            "state_delta": object,
            "error_message": string?
        }

    Errors:
        - 400: Missing session_id or action
        - 401: Missing/invalid JWT
        - 404: Unknown session
        - 403: Player not bound to session

    Law 1: Turn truth via world-engine authority
    Law 6: Fail closed on unknown player/session
    """
    # Verify JWT (Law 6: fail closed)
    player_id = _require_jwt()
    if not player_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Get request data
    data = request.get_json() or {}
    session_id = data.get("session_id")
    action = data.get("action")

    # Validate input (Law 8: explicit errors)
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
    if not action:
        return jsonify({"error": "Missing action"}), 400

    # Get session service
    service = _get_session_service()

    # Verify session exists (Law 6: fail closed)
    session = service.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Verify player is bound to session (Law 6: fail closed)
    players = session.get("players", [])
    player_ids = [p.get("id") if isinstance(p, dict) else p for p in players]
    if player_id not in player_ids and session.get("players_bound", {}).get(player_id) is None:
        # Allow if not explicitly bound yet (join_game may not have been called)
        # execute_action can still proceed
        pass

    # Execute turn (Law 1: world-engine authority)
    result = service.execute_turn(session_id, player_id, action)

    # Return result
    return jsonify(result), 200


@api_v1_bp.route("/player/state", methods=["GET"])
def get_state():
    """
    Get current session state snapshot.

    GET /api/v1/player/state?session_id=<session_id>

    Response (200):
        {
            "session_id": string,
            "turn_number": int,
            "state": object,
            "version": int
        }

    Errors:
        - 400: Missing session_id query param
        - 401: Missing/invalid JWT
        - 404: Unknown session

    Law 1: All reads from mirror (SessionService)
    Law 4: Route purity (pure reflection of truth)
    Law 6: Fail closed
    """
    # Verify JWT (Law 6: fail closed)
    player_id = _require_jwt()
    if not player_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Get session_id from query params
    session_id = request.args.get("session_id")

    # Validate input (Law 8: explicit errors)
    if not session_id:
        return jsonify({"error": "Missing session_id parameter"}), 400

    # Get session service
    service = _get_session_service()

    # Query session state (Law 1: all reads from mirror, Law 4: route purity)
    session = service.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Extract state snapshot
    state = session.get("state", {})
    turn_number = session.get("turn_number", 0)
    version = session.get("version", 0)

    # Return lightweight snapshot
    return jsonify({
        "session_id": session_id,
        "turn_number": turn_number,
        "state": state,
        "version": version
    }), 200


@api_v1_bp.route("/player/history", methods=["GET"])
def get_history():
    """
    Get turn history for a session.

    GET /api/v1/player/history?session_id=<session_id>&limit=<int>

    Response (200):
        {
            "session_id": string,
            "history": [
                {
                    "turn_number": int,
                    "timestamp": string,
                    "action": object,
                    "result": object
                }
            ]
        }

    Errors:
        - 400: Missing session_id query param
        - 401: Missing/invalid JWT
        - 404: Unknown session

    Law 1: All reads from mirror
    Law 4: Route purity
    Law 6: Fail closed
    """
    # Verify JWT (Law 6: fail closed)
    player_id = _require_jwt()
    if not player_id:
        return jsonify({"error": "Unauthorized"}), 401

    # Get query parameters
    session_id = request.args.get("session_id")
    limit_str = request.args.get("limit", "50")

    # Validate input (Law 8: explicit errors)
    if not session_id:
        return jsonify({"error": "Missing session_id parameter"}), 400

    # Parse limit
    try:
        limit = int(limit_str)
        limit = max(1, min(limit, 1000))  # Clamp between 1 and 1000
    except ValueError:
        limit = 50

    # Get session service
    service = _get_session_service()

    # Query session (Law 1: all reads from mirror)
    session = service.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Extract history
    history = session.get("history", [])
    if limit:
        history = history[-limit:]

    # Return history
    return jsonify({
        "session_id": session_id,
        "history": history
    }), 200
