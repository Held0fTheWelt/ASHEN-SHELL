"""Unit tests for login parse / gate helpers (DS-011)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.api.v1.auth_login_phases import (
    LoginParseError,
    locked_account_error_if_active,
    parse_login_request,
)


def test_parse_login_request_invalid_json():
    err = parse_login_request(None)
    assert isinstance(err, LoginParseError)
    assert err.status == 400


def test_parse_login_request_missing_fields():
    err = parse_login_request({"username": "  ", "password": "x"})
    assert isinstance(err, LoginParseError)
    err2 = parse_login_request({"username": "u"})
    assert isinstance(err2, LoginParseError)


def test_parse_login_request_ok():
    ok = parse_login_request({"username": "alice", "password": "secret"})
    assert ok.username == "alice"
    assert ok.password == "secret"


def test_locked_account_error_if_active():
    now = datetime.now(timezone.utc)
    locked = type("U", (), {})()
    locked.locked_until = now + timedelta(minutes=1)
    err = locked_account_error_if_active(locked, now_utc=now)
    assert err is not None and err.status == 429

    assert locked_account_error_if_active(None, now_utc=now) is None
