"""Login request parsing and account-state gates (policy-ish; no SQL)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional, Union


@dataclass
class LoginParseError:
    """Return this from phase helpers; handler maps to HTTP."""

    body: dict
    status: int


@dataclass
class ParsedLoginRequest:
    username: str
    password: str


def parse_login_request(data: dict | None) -> Union[ParsedLoginRequest, LoginParseError]:
    if data is None:
        return LoginParseError({"error": "Invalid or missing JSON body"}, 400)
    username = (data.get("username") or "").strip()
    password = data.get("password")
    if not username or password is None:
        return LoginParseError({"error": "Username and password are required"}, 400)
    return ParsedLoginRequest(username=username, password=password)


def locked_account_error_if_active(user: Any, *, now_utc: datetime) -> Optional[LoginParseError]:
    if not user or not user.locked_until:
        return None
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    if locked_until > now_utc:
        return LoginParseError(
            {"error": "Account temporarily locked. Try again in 15 minutes."},
            429,
        )
    return None


def banned_user_error(user: Any) -> Optional[LoginParseError]:
    if getattr(user, "is_banned", False):
        return LoginParseError({"error": "Account is restricted."}, 403)
    return None


def unverified_email_error(
    user: Any,
    *,
    require_email_verification_for_login: bool,
) -> Optional[LoginParseError]:
    if (
        require_email_verification_for_login
        and user.email
        and user.email_verified_at is None
    ):
        return LoginParseError(
            {
                "error": "Please verify your email before logging in",
                "code": "EMAIL_NOT_VERIFIED",
            },
            403,
        )
    return None
