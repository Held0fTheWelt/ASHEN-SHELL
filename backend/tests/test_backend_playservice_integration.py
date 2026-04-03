from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from app.services import game_service
from app.services.game_service import GameServiceError


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture
def play_service_endpoint() -> dict[str, str]:
    pytest.importorskip("uvicorn")
    repo_root = Path(__file__).resolve().parents[2]
    world_engine_dir = repo_root / "world-engine"
    port = _free_port()

    env = os.environ.copy()
    env["PLAY_SERVICE_INTERNAL_API_KEY"] = "ops-key"
    env["BACKEND_CONTENT_SYNC_ENABLED"] = "false"

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=str(world_engine_dir),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15.0
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        try:
            response = httpx.get(f"{base_url}/api/templates", timeout=1.0)
            if response.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError("world-engine test server did not become ready in time")

    if proc.poll() is not None:
        raise RuntimeError("world-engine test server exited before readiness")

    try:
        yield {
            "public_url": base_url,
            "internal_url": base_url,
            "internal_key": "ops-key",
        }
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def test_backend_to_playservice_happy_path(app, play_service_endpoint):
    with app.app_context():
        app.config["PLAY_SERVICE_PUBLIC_URL"] = play_service_endpoint["public_url"]
        app.config["PLAY_SERVICE_INTERNAL_URL"] = play_service_endpoint["internal_url"]
        app.config["PLAY_SERVICE_INTERNAL_API_KEY"] = play_service_endpoint["internal_key"]
        app.config["PLAY_SERVICE_SHARED_SECRET"] = "integration-shared-secret"
        app.config["PLAY_SERVICE_REQUEST_TIMEOUT"] = 10

        templates = game_service.list_templates()
        assert any(item.get("id") == "god_of_carnage_solo" for item in templates)

        created = game_service.create_run(
            template_id="god_of_carnage_solo",
            account_id="acct:integration",
            display_name="Integration User",
            character_id="char:integration",
        )
        run_id = created["run"]["id"]
        assert run_id

        join = game_service.resolve_join_context(
            run_id=run_id,
            account_id="acct:integration",
            display_name="Integration User",
            character_id="char:integration",
        )
        assert join.run_id == run_id
        assert join.participant_id
        assert join.role_id

        details = game_service.get_run_details(run_id)
        assert details["run"]["id"] == run_id
        assert details["lobby"] is None or isinstance(details["lobby"], dict)

        transcript = game_service.get_run_transcript(run_id)
        assert transcript["run_id"] == run_id
        assert isinstance(transcript["entries"], list)

        terminated = game_service.terminate_run(run_id, actor_display_name="integration_test", reason="e2e_gate")
        assert terminated["run_id"] == run_id
        assert terminated["terminated"] is True
        assert terminated["actor_display_name"] == "integration_test"
        assert terminated["reason"] == "e2e_gate"


def test_backend_contract_failure_on_missing_required_field_with_live_playservice(app, play_service_endpoint):
    with app.app_context():
        app.config["PLAY_SERVICE_PUBLIC_URL"] = play_service_endpoint["public_url"]
        app.config["PLAY_SERVICE_INTERNAL_URL"] = play_service_endpoint["internal_url"]
        app.config["PLAY_SERVICE_INTERNAL_API_KEY"] = play_service_endpoint["internal_key"]
        app.config["PLAY_SERVICE_SHARED_SECRET"] = "integration-shared-secret"
        app.config["PLAY_SERVICE_REQUEST_TIMEOUT"] = 10

        with pytest.raises(GameServiceError) as exc:
            game_service.create_run(
                template_id="",
                account_id="acct:integration",
                display_name="Integration User",
            )

        assert exc.value.status_code in {400, 404, 422}
