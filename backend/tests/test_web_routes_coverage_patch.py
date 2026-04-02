"""Targeted coverage for app.web.routes (FRONTEND_URL, logs export, play edge cases, execute paths)."""

from __future__ import annotations

import re
import pytest

from app.extensions import db
from app.models import User, Role
from app.runtime.session_store import clear_registry
from werkzeug.security import generate_password_hash


@pytest.fixture(autouse=True)
def _clear_runtime_registry(app):
    with app.app_context():
        clear_registry()
    yield
    clear_registry()


def _web_login(client, username: str, password: str):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=False)


def _admin_session(client, app):
    with app.app_context():
        role = Role.query.filter_by(name=Role.NAME_ADMIN).first()
        u = User(
            username="webcovadmin",
            password_hash=generate_password_hash("Webcovadmin1"),
            role_id=role.id,
            role_level=50,
        )
        db.session.add(u)
        db.session.commit()
        db.session.refresh(u)
    _web_login(client, "webcovadmin", "Webcovadmin1")
    return u


def _csrf_from_play(client):
    r = client.get("/play")
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', r.data.decode())
    return m.group(1) if m else ""


def test_home_redirects_when_frontend_url_set(client, app):
    app.config["FRONTEND_URL"] = "https://example.com"
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"].rstrip("/").endswith("example.com")

    app.config["FRONTEND_URL"] = "https://example.com/"
    resp2 = client.get("/", follow_redirects=False)
    assert resp2.status_code == 302
    assert "example.com" in resp2.headers["Location"]


def test_dashboard_logs_export_admin_returns_csv(client, app):
    _admin_session(client, app)
    resp = client.get("/dashboard/api/logs/export")
    assert resp.status_code == 200
    assert "text/csv" in (resp.content_type or "")
    text = resp.get_data(as_text=True)
    assert "id,created_at,actor_user_id" in text
    assert "attachment" in resp.headers.get("Content-Disposition", "")

    resp_cap = client.get("/dashboard/api/logs/export?limit=99999")
    assert resp_cap.status_code == 200


def test_play_start_without_module_id_redirects_with_flash(client, test_user):
    user, password = test_user
    _web_login(client, user.username, password)
    resp = client.post("/play/start", data={}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/play" in resp.headers.get("Location", "")


def test_play_start_session_start_error_redirects(client, test_user, monkeypatch):
    user, password = test_user
    _web_login(client, user.username, password)

    from app.runtime.session_start import SessionStartError

    def _boom(_module_id):
        raise SessionStartError("module_not_found", _module_id or "")

    monkeypatch.setattr("app.services.session_service.create_session", _boom)

    token = _csrf_from_play(client)
    resp = client.post(
        "/play/start",
        data={"module_id": "god_of_carnage", "csrf_token": token},
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_play_start_runtime_register_failure_still_redirects(client, test_user, monkeypatch):
    user, password = test_user
    _web_login(client, user.username, password)

    def _boom(**_kwargs):
        raise RuntimeError("registry down")

    monkeypatch.setattr("app.web.routes.create_runtime_session", _boom)

    token = _csrf_from_play(client)
    resp = client.post(
        "/play/start",
        data={"module_id": "god_of_carnage", "csrf_token": token},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/play/" in resp.headers.get("Location", "")


def test_session_execute_sets_trace_header_on_success(client, test_user):
    user, password = test_user
    _web_login(client, user.username, password)
    token = _csrf_from_play(client)
    start = client.post(
        "/play/start",
        data={"module_id": "god_of_carnage", "csrf_token": token},
        follow_redirects=False,
    )
    assert start.status_code == 302
    session_id = start.headers["Location"].split("/play/")[-1]

    page = client.get(f"/play/{session_id}")
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', page.data.decode())
    csrf = m.group(1) if m else ""

    resp = client.post(
        f"/play/{session_id}/execute",
        data={"operator_input": "look around", "csrf_token": csrf},
        follow_redirects=False,
        headers={"X-WoS-Trace-Id": "trace-integration-1"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("X-WoS-Trace-Id") == "trace-integration-1"


def test_session_execute_empty_operator_redirects(client, test_user):
    user, password = test_user
    _web_login(client, user.username, password)
    token = _csrf_from_play(client)
    start = client.post(
        "/play/start",
        data={"module_id": "god_of_carnage", "csrf_token": token},
        follow_redirects=False,
    )
    session_id = start.headers["Location"].split("/play/")[-1]
    page = client.get(f"/play/{session_id}")
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', page.data.decode())
    csrf = m.group(1) if m else ""

    resp = client.post(
        f"/play/{session_id}/execute",
        data={"operator_input": "   ", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_session_execute_mismatched_session_redirects(client, test_user):
    user, password = test_user
    _web_login(client, user.username, password)
    token = _csrf_from_play(client)
    start = client.post(
        "/play/start",
        data={"module_id": "god_of_carnage", "csrf_token": token},
        follow_redirects=False,
    )
    session_id = start.headers["Location"].split("/play/")[-1]
    page = client.get(f"/play/{session_id}")
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', page.data.decode())
    csrf = m.group(1) if m else ""

    resp = client.post(
        f"/play/wrong-{session_id}/execute",
        data={"operator_input": "x", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_session_execute_dispatch_failure_returns_400(client, test_user, monkeypatch):
    user, password = test_user
    _web_login(client, user.username, password)
    token = _csrf_from_play(client)
    start = client.post(
        "/play/start",
        data={"module_id": "god_of_carnage", "csrf_token": token},
        follow_redirects=False,
    )
    session_id = start.headers["Location"].split("/play/")[-1]
    page = client.get(f"/play/{session_id}")
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', page.data.decode())
    csrf = m.group(1) if m else ""

    async def _bad_dispatch(**_kwargs):
        raise ValueError("dispatch failed")

    monkeypatch.setattr("app.web.routes.dispatch_turn", _bad_dispatch)

    resp = client.post(
        f"/play/{session_id}/execute",
        data={"operator_input": "trigger error", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert resp.status_code == 400
    assert b"Turn execution failed" in resp.data or b"error" in resp.data.lower()
