from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wos_mvp.app import app, settings


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_session_and_execute_turn_flow() -> None:
    created = client.post("/api/v1/sessions", json={"module_id": "god_of_carnage"})
    assert created.status_code == 200
    payload = created.json()
    session_id = payload["session_id"]
    assert payload["turn_zero_required"] is True
    assert payload["player_payload"]["path_class"] == "authoritative_player"

    fetched = client.get(f"/api/v1/sessions/{session_id}")
    assert fetched.status_code == 200
    assert fetched.json()["player_view"]["turn_number"] == 0

    turned = client.post(
        f"/api/v1/sessions/{session_id}/turns",
        json={"player_input": "I want to follow the money."},
    )
    assert turned.status_code == 200
    turn_payload = turned.json()
    assert turn_payload["turn_result"]["turn_number"] == 1
    assert turn_payload["player_payload"]["truth_status"] == "committed"


def test_internal_routes_require_key() -> None:
    created = client.post("/api/v1/sessions", json={"module_id": "god_of_carnage"}).json()
    session_id = created["session_id"]

    denied = client.get(f"/api/v1/sessions/{session_id}/state")
    assert denied.status_code == 403

    allowed = client.get(
        f"/api/v1/sessions/{session_id}/state",
        headers={"X-Internal-API-Key": settings.internal_api_key},
    )
    assert allowed.status_code == 200
    assert allowed.json()["current_turn"] == 0
