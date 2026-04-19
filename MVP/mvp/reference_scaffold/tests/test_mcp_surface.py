from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wos_mvp.app import app, settings
from wos_mvp.mcp_surface import build_registry


class ClientTransport:
    def __init__(self, client: TestClient):
        self.client = client

    def get(self, path: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        parsed = urlparse(path)
        response = self.client.get(parsed.path + (f"?{parsed.query}" if parsed.query else ""), headers=headers)
        assert response.status_code < 400, response.text
        return response.json()

    def post(self, path: str, json_body: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        response = self.client.post(path, json=json_body, headers=headers)
        assert response.status_code < 400, response.text
        return response.json()


client = TestClient(app)
transport = ClientTransport(client)
registry = build_registry(transport, internal_api_key=settings.internal_api_key)


def test_registry_contains_runtime_safe_session_surfaces() -> None:
    names = {tool["name"] for tool in registry.list_tools()}
    assert "wos.session.get" in names
    assert "wos.session.logs" in names
    assert "wos.session.state" in names
    assert "wos.session.diag" in names
    assert "wos.session.execute_turn" in names


def test_handlers_roundtrip_through_api() -> None:
    create = registry.get("wos.session.create")
    assert create is not None
    created = create.handler({"module_id": "god_of_carnage"})
    session_id = created["session_id"]

    fetched = registry.get("wos.session.get")
    assert fetched is not None
    session_snapshot = fetched.handler({"session_id": session_id})
    assert session_snapshot["session_id"] == session_id

    turned = registry.get("wos.session.execute_turn")
    assert turned is not None
    result = turned.handler({"session_id": session_id, "player_input": "I question Marcus."})
    assert result["turn_result"]["turn_number"] == 1

    diag = registry.get("wos.session.diag")
    assert diag is not None
    diagnostics = diag.handler({"session_id": session_id})
    assert diagnostics["operator_bundle"]["audience"] == "operator"
