"""Test that WebSocket timeouts work correctly."""
import socket
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from conftest import build_test_app, receive_until_snapshot


@pytest.mark.websocket
def test_websocket_receives_snapshot_with_timeout(tmp_path: Path):
    """Test that WebSocket receives snapshot even with socket timeout set."""
    app = build_test_app(tmp_path)
    client = TestClient(app)

    # Create run and ticket
    run_response = client.post(
        '/api/runs',
        json={'template_id': 'apartment_confrontation_group', 'account_id': '7', 'display_name': 'Host'},
    )
    run_id = run_response.json()['run']['id']

    ticket_response = client.post(
        '/api/tickets',
        json={'run_id': run_id, 'account_id': '7', 'display_name': 'Host'},
    )
    ticket = ticket_response.json()['ticket']

    # Connect and verify snapshot received with timeout
    with client.websocket_connect(f'/ws?ticket={ticket}') as ws:
        # Set socket timeout before receiving
        if hasattr(ws, 'sock') and ws.sock:
            ws.sock.settimeout(5.0)
        
        # Should receive snapshot without timeout
        msg = ws.receive_json()
        assert msg.get("type") == "snapshot"
        assert msg["data"]["viewer_role_id"] == "mediator"


@pytest.mark.websocket
def test_receive_until_snapshot_with_timeout(tmp_path: Path):
    """Test receive_until_snapshot helper with timeout."""
    app = build_test_app(tmp_path)
    client = TestClient(app)

    # Create run and ticket
    run_response = client.post(
        '/api/runs',
        json={'template_id': 'apartment_confrontation_group', 'account_id': '7', 'display_name': 'Host'},
    )
    run_id = run_response.json()['run']['id']

    ticket_response = client.post(
        '/api/tickets',
        json={'run_id': run_id, 'account_id': '7', 'display_name': 'Host'},
    )
    ticket = ticket_response.json()['ticket']

    # Test the helper function
    with client.websocket_connect(f'/ws?ticket={ticket}') as ws:
        snapshot = receive_until_snapshot(ws, lambda data: data["viewer_role_id"] == "mediator")
        assert snapshot["data"]["viewer_role_id"] == "mediator"
