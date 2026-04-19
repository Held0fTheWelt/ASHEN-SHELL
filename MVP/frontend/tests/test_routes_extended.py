"""Extended route coverage for player/public frontend."""
from __future__ import annotations

from app.api_client import BackendApiError


class FakeResponse:
    def __init__(self, *, status_code=200, payload=None, content=None, headers=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.ok = 200 <= status_code < 300
        self.content = content if content is not None else b"{}"
        self.headers = headers or {"Content-Type": "application/json"}

    def json(self):
        return self._payload


def test_login_get_redirects_when_already_logged_in(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.get("/login", follow_redirects=False)
    assert r.status_code == 302
    assert "/dashboard" in r.headers["Location"]


def test_login_get_shows_form(client):
    r = client.get("/login")
    assert r.status_code == 200


def test_login_post_empty_fields(client):
    r = client.post("/login", data={"username": "", "password": ""})
    assert r.status_code == 400


def test_login_post_backend_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=401, payload={"error": "bad creds"}),
    )
    r = client.post("/login", data={"username": "a", "password": "b"})
    assert r.status_code == 401


def test_logout_post_with_token_calls_backend(client, monkeypatch):
    calls = []

    def rec(method, path, **kwargs):
        calls.append((method, path))
        return FakeResponse()

    monkeypatch.setattr("app.routes.request_backend", rec)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.post("/logout", follow_redirects=False)
    assert r.status_code == 302
    assert ("POST", "/api/v1/auth/logout") in calls


def test_logout_post_without_token(client, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("should not call backend")

    monkeypatch.setattr("app.routes.request_backend", boom)
    r = client.post("/logout", follow_redirects=False)
    assert r.status_code == 302


def test_register_get(client):
    r = client.get("/register")
    assert r.status_code == 200


def test_register_post_validation(client):
    r = client.post("/register", data={"username": "", "password": ""})
    assert r.status_code == 400


def test_register_post_password_mismatch(client):
    r = client.post(
        "/register",
        data={"username": "u", "email": "u@e.com", "password": "a", "password_confirm": "b"},
    )
    assert r.status_code == 400


def test_register_post_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={}),
    )
    r = client.post(
        "/register",
        data={
            "username": "nu",
            "email": "nu@e.com",
            "password": "secret",
            "password_confirm": "secret",
        },
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert "/register/pending" in r.headers["Location"]


def test_register_post_api_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=409, payload={"error": "taken"}),
    )
    r = client.post(
        "/register",
        data={
            "username": "nu",
            "email": "nu@e.com",
            "password": "secret",
            "password_confirm": "secret",
        },
    )
    assert r.status_code == 409


def test_register_pending_get(client):
    r = client.get("/register/pending")
    assert r.status_code == 200


def test_resend_verification_get(client):
    r = client.get("/resend-verification")
    assert r.status_code == 200


def test_resend_verification_post_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"message": "sent"}),
    )
    r = client.post("/resend-verification", data={"email": "a@b.com"}, follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_resend_verification_post_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=400, payload={"error": "no"}),
    )
    r = client.post("/resend-verification", data={"email": "a@b.com"})
    assert r.status_code == 400


def test_forgot_password_get(client):
    r = client.get("/forgot-password")
    assert r.status_code == 200


def test_forgot_password_post_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"message": "check mail"}),
    )
    r = client.post("/forgot-password", data={"email": "a@b.com"}, follow_redirects=False)
    assert r.status_code == 302


def test_forgot_password_post_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=503, payload={"error": "fail"}),
    )
    r = client.post("/forgot-password", data={"email": "a@b.com"})
    assert r.status_code == 503


def test_reset_password_get(client):
    r = client.get("/reset-password/tok123")
    assert r.status_code == 200


def test_reset_password_post_mismatch(client):
    r = client.post(
        "/reset-password/tok123",
        data={"password": "a", "password_confirm": "b"},
    )
    assert r.status_code == 400


def test_reset_password_post_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"message": "ok"}),
    )
    r = client.post(
        "/reset-password/tok123",
        data={"password": "secret", "password_confirm": "secret"},
        follow_redirects=False,
    )
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_reset_password_post_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=400, payload={"error": "bad token"}),
    )
    r = client.post(
        "/reset-password/tok123",
        data={"password": "secret", "password_confirm": "secret"},
    )
    assert r.status_code == 400


def test_dashboard_unauthorized_clears_session(client, monkeypatch):
    def fail(*a, **k):
        raise BackendApiError("nope", status_code=401)

    monkeypatch.setattr("app.routes.request_backend", fail)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"id": 1}
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("access_token") is None


def test_dashboard_backend_error_non_401_shows_flash_and_fallback_user(client, monkeypatch):
    def fail(*a, **k):
        raise BackendApiError("offline", status_code=503)

    monkeypatch.setattr("app.routes.request_backend", fail)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "bob"}
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert b"bob" in r.data


def test_news_ok_and_empty(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"items": [{"title": "N1"}]}),
    )
    r = client.get("/news")
    assert r.status_code == 200
    assert b"N1" in r.data

    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=500, payload={}),
    )
    r2 = client.get("/news")
    assert r2.status_code == 200


def test_wiki_index_and_slug_and_status_codes(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda m, p, **k: FakeResponse(payload={"title": "Idx"}) if p.endswith("index") else FakeResponse(),
    )
    r = client.get("/wiki")
    assert r.status_code == 200

    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda m, p, **k: FakeResponse(status_code=404, payload={}),
    )
    r404 = client.get("/wiki/missing")
    assert r404.status_code == 404

    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda m, p, **k: FakeResponse(status_code=502, payload={}),
    )
    r502 = client.get("/wiki/broken")
    assert r502.status_code == 200


def test_community_ok_and_fail(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"items": [{"title": "Cat", "description": "d"}]}),
    )
    r = client.get("/community")
    assert b"Cat" in r.data

    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=503),
    )
    r2 = client.get("/community")
    assert r2.status_code == 200


def test_game_menu_requires_login(client):
    r = client.get("/game-menu", follow_redirects=False)
    assert r.status_code == 302


def test_game_menu_renders(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "pam"}
    r = client.get("/game-menu")
    assert r.status_code == 200
    assert b"Game Menu" in r.data
    assert b"Open play launcher" in r.data


def test_play_create_missing_template(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.post("/play/start", data={}, follow_redirects=False)
    assert r.status_code == 302
    assert "/play" in r.headers["Location"]


def test_play_create_api_error(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=400, payload={"error": "no"}),
    )
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.post("/play/start", data={"template_id": "t1"}, follow_redirects=False)
    assert r.status_code == 302
    assert "/play" in r.headers["Location"]


def test_play_create_no_run_id(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"run": {}}),
    )
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.post("/play/start", data={"template_id": "t1"}, follow_redirects=False)
    assert r.status_code == 302
    assert "/play" in r.headers["Location"]


def test_play_create_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(payload={"run": {"id": "run-99"}}),
    )
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.post("/play/start", data={"template_id": "t1"}, follow_redirects=False)
    assert r.status_code == 302
    assert "/play/run-99" in r.headers["Location"]
    with client.session_transaction() as sess:
        assert sess.get("play_shell_run_modules", {}).get("run-99") == "t1"


def test_play_shell_ticket_ok_and_error(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc", "participant_id": "p1", "role_id": "host", "ws_base_url": "wss://play.example.com"})
        if path == "/api/v1/game/runs/s1":
            return FakeResponse(payload={"run": {"id": "s1"}, "template_source": "backend_published", "template": {"title": "God of Carnage"}, "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s1/transcript":
            return FakeResponse(payload={"run_id": "s1", "entries": [{"text": "A sharp opening line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-1"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s1": "god_of_carnage"}
    r = client.get("/play/s1")
    assert r.status_code == 200
    assert b"Natural language is the primary input path" in r.data
    assert b"name=\"player_input\"" in r.data
    with client.session_transaction() as sess:
        assert sess.get("play_shell_backend_sessions", {}).get("s1") == "backend-session-1"

    monkeypatch.setattr(
        "app.routes.request_backend",
        lambda *a, **k: FakeResponse(status_code=400, payload={"error": "nope"}),
    )
    r2 = client.get("/play/s2")
    assert r2.status_code == 200


def test_play_execute_empty_and_runtime_dispatch(client, monkeypatch):
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        if path == "/api/v1/sessions/backend-session-1/turns":
            return FakeResponse(
                payload={
                    "turn": {
                        "turn_number": 1,
                        "raw_input": kwargs["json_data"]["player_input"],
                        "interpreted_input": {"kind": "speech"},
                    }
                }
            )
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(payload={"run": {"id": "sid", "status": "active"}, "template_source": "backend_published", "template": {"title": "God of Carnage"}, "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(payload={"run_id": "sid", "entries": [{"text": "A sharp reply."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.post("/play/sid/execute", data={"player_input": ""}, follow_redirects=False)
    assert r.status_code == 302

    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"sid": "backend-session-1"}
    client.post("/play/sid/execute", data={"player_input": "I look around and wait."}, follow_redirects=False)
    assert calls
    turn_calls = [call for call in calls if call[1] == "/api/v1/sessions/backend-session-1/turns"]
    assert turn_calls
    assert turn_calls[0][2]["json_data"]["player_input"] == "I look around and wait."
    assert any(path == "/api/v1/game/runs/sid" for _, path, _ in calls)
    assert any(path == "/api/v1/game/runs/sid/transcript" for _, path, _ in calls)
    with client.session_transaction() as sess:
        observation = sess.get("play_shell_authoritative_observations", {}).get("sid")
        assert observation["latest_entry_text"] == "A sharp reply."
        assert observation["transcript_entry_count"] == 1
        assert "shell_state_view" in observation
        assert observation["shell_state_view"]["authoritative_status_summary"].startswith("Run status: active")


def test_play_execute_rejects_missing_backend_session_binding(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(status_code=503, payload={"error": "detail down"})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(status_code=503, payload={"error": "transcript down"})
        if path == "/api/v1/sessions":
            raise AssertionError("runtime recovery should not attempt session creation without recoverable binding")
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    response = client.post("/play/sid/execute", data={"player_input": "I stay silent."}, follow_redirects=False)
    assert response.status_code == 302
    with client.session_transaction() as sess:
        flashes = sess.get("_flashes", [])
    assert any("Runtime session recovery is not possible from current shell state." in message for _, message in flashes)


def test_api_proxy_get_and_post(client, monkeypatch):
    class Resp:
        status_code = 201
        content = b'{"ok":true}'
        headers = {"Content-Type": "application/json"}

    def fake_request(method, url, **kwargs):
        assert "query" in kwargs.get("params", {}) or method == "POST"
        return Resp()

    monkeypatch.setattr("app.api_client.requests.request", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    r = client.get("/api/v1/news/items?query=x")
    assert r.status_code == 201
    assert r.get_json() == {"ok": True}

    r2 = client.post(
        "/api/v1/game/runs",
        json={"template_id": "x"},
        headers={"Content-Type": "application/json"},
    )
    assert r2.status_code == 201




def test_play_shell_gracefully_handles_missing_run_detail_and_transcript(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s3":
            return FakeResponse(status_code=404, payload={"error": "missing detail"})
        if path == "/api/v1/game/runs/s3/transcript":
            return FakeResponse(status_code=404, payload={"error": "missing transcript"})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-3"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s3": "god_of_carnage"}
    r = client.get("/play/s3")
    assert r.status_code == 200
    assert b"Run details are currently unavailable." in r.data
    assert b"No transcript entries available yet." in r.data


def test_play_execute_warns_when_authoritative_refresh_fails(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/sessions/backend-session-1/turns":
            return FakeResponse(payload={"turn": {"interpreted_input": {"kind": "speech"}}})
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(status_code=503, payload={"error": "run detail down"})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(status_code=503, payload={"error": "run transcript down"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"sid": "backend-session-1"}
    response = client.post("/play/sid/execute", data={"player_input": "I hesitate."}, follow_redirects=False)
    assert response.status_code == 302


def test_play_shell_renders_cached_authoritative_observation_as_fallback(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s4":
            return FakeResponse(status_code=404, payload={"error": "missing detail"})
        if path == "/api/v1/game/runs/s4/transcript":
            return FakeResponse(status_code=404, payload={"error": "missing transcript"})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-4"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s4": "god_of_carnage"}
        sess["play_shell_authoritative_observations"] = {
            "s4": {
                "template_title": "God of Carnage",
                "template_source": "backend_published",
                "lobby_status": "active",
                "transcript_entry_count": 2,
                "latest_entry_text": "Cached authoritative line.",
                "run_detail": {"run": {"id": "s4"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}},
                "transcript": {"entries": [{"text": "Cached authoritative line."}]},
            }
        }
    r = client.get("/play/s4")
    assert r.status_code == 200
    assert b"Latest authoritative observation" in r.data
    assert b"Cached authoritative line." in r.data


def test_play_execute_json_returns_authoritative_shell_state_bundle(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/sessions/backend-session-1/turns":
            return FakeResponse(payload={"turn": {"interpreted_input": {"kind": "speech"}}})
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(payload={"run": {"id": "sid", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(payload={"run_id": "sid", "entries": [{"text": "A sharp reply."}, {"text": "Another line."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"sid": "backend-session-1"}
    response = client.post("/play/sid/execute", json={"player_input": "I look around and wait."}, headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["interpreted_input_kind"] == "speech"
    assert data["shell_state_view"]["run_title"] == "God of Carnage"
    assert data["shell_state_view"]["transcript_entry_count"] == 2
    assert data["shell_state_view"]["latest_entry_text"] == "Another line."
    assert data["shell_state_view"]["transcript_preview"] == ["A sharp reply.", "Another line."]
    assert data["shell_state_view"]["authoritative_status_summary"] == "Run status: active · Lobby: active · Transcript entries: 2 · Latest line: Another line."
    assert "Run status: active" in data["message"]


def test_play_execute_json_returns_error_for_missing_backend_session_binding(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(status_code=503, payload={"error": "detail down"})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(status_code=503, payload={"error": "transcript down"})
        if path == "/api/v1/sessions":
            raise AssertionError("runtime recovery should not attempt session creation without recoverable binding")
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    response = client.post("/play/sid/execute", json={"player_input": "I stay silent."}, headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 409
    data = response.get_json()
    assert data["runtime_recovery_status"] == "not_ready"
    assert data["error"].startswith("Runtime session recovery is not possible from current shell state.")


def test_play_shell_renders_no_reload_coherence_hooks(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s5":
            return FakeResponse(payload={"run": {"id": "s5", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s5/transcript":
            return FakeResponse(payload={"run_id": "s5", "entries": [{"text": "Observed line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-5"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

        
    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s5": "god_of_carnage"}
    r = client.get("/play/s5")
    assert r.status_code == 200
    assert b'id="execute-form"' in r.data
    assert b'id="shell-execute-status"' in r.data
    assert b'id="transcript-preview-list"' in r.data


def test_play_shell_prefers_fresh_authoritative_bundle_over_stale_cached_observation(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s6":
            return FakeResponse(payload={"run": {"id": "s6", "status": "paused", "template_title": "Fresh Title"}, "template": {"title": "Fresh Title"}, "template_source": "backend_published", "lobby": {"status": "paused"}})
        if path == "/api/v1/game/runs/s6/transcript":
            return FakeResponse(payload={"run_id": "s6", "entries": [{"text": "Fresh authoritative line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-6"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s6": "god_of_carnage"}
        sess["play_shell_authoritative_observations"] = {
            "s6": {
                "template_title": "Stale Title",
                "template_source": "stale_source",
                "lobby_status": "active",
                "transcript_entry_count": 9,
                "latest_entry_text": "Stale line.",
                "shell_state_view": {"run_title": "Stale Title", "authoritative_status_summary": "stale"},
                "run_detail": {"run": {"id": "s6", "status": "active"}},
                "transcript": {"entries": [{"text": "Stale line."}]},
            }
        }
    r = client.get("/play/s6")
    assert r.status_code == 200
    assert b"Fresh Title" in r.data
    assert b"Fresh authoritative line." in r.data
    assert b"Run status: paused" in r.data
    with client.session_transaction() as sess:
        observation = sess.get("play_shell_authoritative_observations", {}).get("s6")
        assert observation["template_title"] == "Fresh Title"
        assert observation["latest_entry_text"] == "Fresh authoritative line."


def test_play_shell_renders_authoritative_status_summary(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s7":
            return FakeResponse(payload={"run": {"id": "s7", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s7/transcript":
            return FakeResponse(payload={"run_id": "s7", "entries": [{"text": "Observed line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-7"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s7": "god_of_carnage"}
    r = client.get("/play/s7")
    assert r.status_code == 200
    assert b"Run status: active" in r.data
    assert b"Transcript entries: 1" in r.data


def test_play_observe_returns_authoritative_shell_state_bundle(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/s8":
            return FakeResponse(payload={"run": {"id": "s8", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s8/transcript":
            return FakeResponse(payload={"run_id": "s8", "entries": [{"text": "Observed line."}, {"text": "Newest observed line."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    response = client.get("/play/s8/observe", headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["shell_state_view"]["run_status"] == "active"
    assert data["shell_state_view"]["latest_entry_text"] == "Newest observed line."


def test_play_shell_renders_refresh_observation_button(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s9":
            return FakeResponse(payload={"run": {"id": "s9", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s9/transcript":
            return FakeResponse(payload={"run_id": "s9", "entries": [{"text": "Observed line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-9"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s9": "god_of_carnage"}
    r = client.get("/play/s9")
    assert r.status_code == 200
    assert b'id="refresh-observation-btn"' in r.data
    assert b'/play/s9/observe' in r.data


def test_play_execute_json_and_followup_observe_share_coherent_bundle_shape(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/sessions/backend-session-1/turns":
            return FakeResponse(payload={"turn": {"interpreted_input": {"kind": "speech"}}})
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(payload={"run": {"id": "sid", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(payload={"run_id": "sid", "entries": [{"text": "A sharp reply."}, {"text": "Another line."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"sid": "backend-session-1"}

    execute_response = client.post("/play/sid/execute", json={"player_input": "I look around and wait."}, headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    observe_response = client.get("/play/sid/observe", headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    execute_data = execute_response.get_json()
    observe_data = observe_response.get_json()
    assert execute_response.status_code == 200
    assert observe_response.status_code == 200
    assert execute_data["shell_state_view"]["authoritative_status_summary"] == observe_data["shell_state_view"]["authoritative_status_summary"]
    assert execute_data["shell_state_view"]["latest_entry_text"] == observe_data["shell_state_view"]["latest_entry_text"]



def test_play_shell_renders_observation_source_and_runtime_session_ready(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s10":
            return FakeResponse(payload={"run": {"id": "s10", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s10/transcript":
            return FakeResponse(payload={"run_id": "s10", "entries": [{"text": "Observed line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-10"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s10": "god_of_carnage"}
    r = client.get("/play/s10")
    assert r.status_code == 200
    assert b'Observation source:' in r.data
    assert b'>fresh<' in r.data
    assert b'Runtime session ready:' in r.data
    assert b'>yes<' in r.data


def test_play_shell_uses_cached_fallback_source_when_authoritative_fetch_fails(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s11":
            return FakeResponse(status_code=503, payload={"error": "detail down"})
        if path == "/api/v1/game/runs/s11/transcript":
            return FakeResponse(status_code=503, payload={"error": "transcript down"})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-11"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s11": "god_of_carnage"}
        sess["play_shell_authoritative_observations"] = {
            "s11": {
                "run_detail": {"run": {"id": "s11", "status": "paused"}, "template": {"title": "Cached Title"}, "template_source": "backend_published", "lobby": {"status": "paused"}},
                "transcript": {"entries": [{"text": "Cached line."}]},
                "shell_state_view": {"run_title": "Cached Title", "run_status": "paused", "transcript_entry_count": 1, "latest_entry_text": "Cached line.", "transcript_preview": ["Cached line."], "authoritative_status_summary": "Run status: paused · Lobby: paused · Transcript entries: 1 · Latest line: Cached line."},
                "template_title": "Cached Title",
                "template_source": "backend_published",
                "lobby_status": "paused",
                "transcript_entry_count": 1,
                "latest_entry_text": "Cached line.",
            }
        }
    r = client.get("/play/s11")
    assert r.status_code == 200
    assert b'>cached_fallback<' in r.data
    assert b'detail down' in r.data or b'transcript down' in r.data


def test_play_observe_returns_observation_source_and_runtime_session_flags(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/s12":
            return FakeResponse(payload={"run": {"id": "s12", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s12/transcript":
            return FakeResponse(payload={"run_id": "s12", "entries": [{"text": "Observed line."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"s12": "backend-session-12"}
    response = client.get("/play/s12/observe", headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["observation_source"] == "fresh"
    assert data["runtime_session_ready"] is True
    assert data["backend_session_id"] == "backend-session-12"
    assert data["can_refresh"] is True


def test_play_execute_json_returns_runtime_ready_and_observation_source(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/sessions/backend-session-1/turns":
            return FakeResponse(payload={"turn": {"interpreted_input": {"kind": "speech"}}})
        if path == "/api/v1/game/runs/sid":
            return FakeResponse(payload={"run": {"id": "sid", "status": "active", "template_title": "God of Carnage"}, "template": {"title": "God of Carnage"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/sid/transcript":
            return FakeResponse(payload={"run_id": "sid", "entries": [{"text": "A sharp reply."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"sid": "backend-session-1"}
    response = client.post("/play/sid/execute", json={"player_input": "I wait."}, headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["runtime_session_ready"] is True
    assert data["can_execute"] is True
    assert data["observation_source"] == "fresh"



def test_play_shell_embeds_initial_authoritative_shell_state_json(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/s7":
            return FakeResponse(payload={"run": {"id": "s7", "status": "active", "template_title": "GoC"}, "template": {"title": "GoC"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s7/transcript":
            return FakeResponse(payload={"run_id": "s7", "entries": [{"text": "Fresh line."}]})
        if path == "/api/v1/sessions":
            return FakeResponse(payload={"session_id": "backend-session-7"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
        sess["play_shell_run_modules"] = {"s7": "god_of_carnage"}
    r = client.get("/play/s7")
    assert r.status_code == 200
    assert b'id="initial-shell-state"' in r.data
    assert b'"observation_meta": {"error": null, "is_cached_fallback": false, "is_fresh": true, "is_unavailable": false, "source": "fresh"}' in r.data


def test_play_observe_returns_observation_meta(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/s8":
            return FakeResponse(payload={"run": {"id": "s8", "status": "active", "template_title": "GoC"}, "template": {"title": "GoC"}, "template_source": "backend_published", "lobby": {"status": "active"}})
        if path == "/api/v1/game/runs/s8/transcript":
            return FakeResponse(payload={"run_id": "s8", "entries": [{"text": "Observe line."}]})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"s8": "backend-session-8"}
    r = client.get("/play/s8/observe", headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["observation_meta"]["is_fresh"] is True
    assert data["runtime_session_ready"] is True
    assert data["shell_state_view"]["run_status"] == "active"


def test_play_observe_falls_back_to_cached_authoritative_observation(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/s9":
            return FakeResponse(status_code=503, payload={"error": "detail down"})
        if path == "/api/v1/game/runs/s9/transcript":
            return FakeResponse(status_code=503, payload={"error": "transcript down"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_backend_sessions"] = {"s9": "backend-session-9"}
        sess["play_shell_authoritative_observations"] = {"s9": {"run_id": "s9", "run_detail": {"run": {"id": "s9", "status": "paused", "template_title": "Cached GoC"}, "template": {"title": "Cached GoC"}, "template_source": "backend_published", "lobby": {"status": "paused"}}, "transcript": {"entries": [{"text": "Cached line."}]}, "transcript_entry_count": 1, "latest_entry_text": "Cached line.", "template_title": "Cached GoC", "template_source": "backend_published", "lobby_status": "paused", "run_status": "paused", "shell_state_view": {"run_title": "Cached GoC", "template_source": "backend_published", "lobby_status": "paused", "run_status": "paused", "transcript_entry_count": 1, "latest_entry_text": "Cached line.", "transcript_preview": ["Cached line."], "authoritative_status_summary": "Run status: paused · Lobby: paused · Transcript entries: 1 · Latest line: Cached line."}}}
    r = client.get("/play/s9/observe", headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["observation_meta"]["is_cached_fallback"] is True
    assert data["shell_state_view"]["latest_entry_text"] == "Cached line."


def test_play_shell_recovers_backend_session_from_authoritative_run_detail_when_mapping_missing(client, monkeypatch):
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs.get("json_data")))
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/recover-shell":
            return FakeResponse(payload={
                "run": {"id": "recover-shell", "status": "active", "template_title": "Recovered GoC"},
                "template_source": "backend_published",
                "template": {"id": "god_of_carnage_solo", "title": "Recovered GoC", "kind": "solo_story", "join_policy": "solo", "min_humans_to_start": 1},
                "lobby": {"status": "active"},
            })
        if path == "/api/v1/game/runs/recover-shell/transcript":
            return FakeResponse(payload={"run_id": "recover-shell", "entries": [{"text": "Recovered observation line."}]})
        if path == "/api/v1/sessions":
            assert kwargs.get("json_data") == {"module_id": "god_of_carnage_solo"}
            return FakeResponse(payload={"session_id": "backend-session-recover-shell"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
    response = client.get("/play/recover-shell")
    assert response.status_code == 200
    assert b'id="runtime-session-id">backend-session-recover-shell<' in response.data
    assert b'id="runtime-recovery-status">recovered<' in response.data
    with client.session_transaction() as sess:
        assert sess.get("play_shell_backend_sessions", {}).get("recover-shell") == "backend-session-recover-shell"
        assert sess.get("play_shell_run_modules", {}).get("recover-shell") == "god_of_carnage_solo"
    assert ("POST", "/api/v1/sessions", {"module_id": "god_of_carnage_solo"}) in calls



def test_play_observe_recovers_backend_session_from_cached_authoritative_observation(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/runs/recover-cache":
            return FakeResponse(status_code=503, payload={"error": "detail down"})
        if path == "/api/v1/game/runs/recover-cache/transcript":
            return FakeResponse(status_code=503, payload={"error": "transcript down"})
        if path == "/api/v1/sessions":
            assert kwargs.get("json_data") == {"module_id": "god_of_carnage_solo"}
            return FakeResponse(payload={"session_id": "backend-session-recover-cache"})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["play_shell_authoritative_observations"] = {
            "recover-cache": {
                "run_id": "recover-cache",
                "run_detail": {
                    "run": {"id": "recover-cache", "status": "paused", "template_title": "Cached GoC"},
                    "template": {"id": "god_of_carnage_solo", "title": "Cached GoC", "kind": "solo_story", "join_policy": "solo", "min_humans_to_start": 1},
                    "template_source": "backend_published",
                    "lobby": {"status": "paused"},
                },
                "transcript": {"entries": [{"text": "Cached line."}]},
                "shell_state_view": {"run_title": "Cached GoC", "template_source": "backend_published", "lobby_status": "paused", "run_status": "paused", "transcript_entry_count": 1, "latest_entry_text": "Cached line.", "transcript_preview": ["Cached line."], "authoritative_status_summary": "Run status: paused · Lobby: paused · Transcript entries: 1 · Latest line: Cached line."},
                "template_title": "Cached GoC",
                "template_source": "backend_published",
                "lobby_status": "paused",
                "run_status": "paused",
                "transcript_entry_count": 1,
                "latest_entry_text": "Cached line.",
            }
        }
    response = client.get("/play/recover-cache/observe", headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["observation_source"] == "cached_fallback"
    assert data["runtime_session_ready"] is True
    assert data["backend_session_id"] == "backend-session-recover-cache"
    assert data["runtime_recovery_status"] == "recovered"
    assert data["runtime_recovery"]["module_binding_source"] == "cached_authoritative_observation"
    with client.session_transaction() as sess:
        assert sess.get("play_shell_backend_sessions", {}).get("recover-cache") == "backend-session-recover-cache"
        assert sess.get("play_shell_run_modules", {}).get("recover-cache") == "god_of_carnage_solo"



def test_play_execute_json_recovers_backend_session_before_turn_dispatch(client, monkeypatch):
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs.get("json_data")))
        if path == "/api/v1/game/runs/recover-execute":
            return FakeResponse(payload={
                "run": {"id": "recover-execute", "status": "active", "template_title": "Recovered GoC"},
                "template_source": "backend_published",
                "template": {"id": "god_of_carnage_solo", "title": "Recovered GoC", "kind": "solo_story", "join_policy": "solo", "min_humans_to_start": 1},
                "lobby": {"status": "active"},
            })
        if path == "/api/v1/game/runs/recover-execute/transcript":
            return FakeResponse(payload={"run_id": "recover-execute", "entries": [{"text": "Fresh line after recovery."}]})
        if path == "/api/v1/sessions":
            assert kwargs.get("json_data") == {"module_id": "god_of_carnage_solo"}
            return FakeResponse(payload={"session_id": "backend-session-recover-execute"})
        if path == "/api/v1/sessions/backend-session-recover-execute/turns":
            return FakeResponse(payload={"turn": {"interpreted_input": {"kind": "speech"}}})
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
    response = client.post(
        "/play/recover-execute/execute",
        json={"player_input": "I recover and continue."},
        headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["runtime_session_ready"] is True
    assert data["backend_session_id"] == "backend-session-recover-execute"
    assert any(path == "/api/v1/sessions" for _, path, _ in calls)
    assert any(path == "/api/v1/sessions/backend-session-recover-execute/turns" for _, path, _ in calls)
    with client.session_transaction() as sess:
        assert sess.get("play_shell_backend_sessions", {}).get("recover-execute") == "backend-session-recover-execute"
        assert sess.get("play_shell_run_modules", {}).get("recover-execute") == "god_of_carnage_solo"



def test_play_shell_renders_explicit_bounded_failure_when_runtime_recovery_is_impossible(client, monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/api/v1/game/tickets":
            return FakeResponse(payload={"ticket": "abc"})
        if path == "/api/v1/game/runs/unrecoverable":
            return FakeResponse(status_code=503, payload={"error": "detail down"})
        if path == "/api/v1/game/runs/unrecoverable/transcript":
            return FakeResponse(status_code=503, payload={"error": "transcript down"})
        if path == "/api/v1/sessions":
            raise AssertionError("runtime recovery should not attempt session creation without recoverable binding")
        raise AssertionError(f"unexpected backend call: {method} {path}")

    monkeypatch.setattr("app.routes.request_backend", fake_request)
    with client.session_transaction() as sess:
        sess["access_token"] = "t"
        sess["current_user"] = {"username": "u1"}
    response = client.get("/play/unrecoverable")
    assert response.status_code == 200
    assert b'id="runtime-session-ready">no<' in response.data
    assert b'id="runtime-recovery-status">not_ready<' in response.data
    assert b'Runtime session recovery is not possible from current shell state.' in response.data
