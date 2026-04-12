"""Low-level helpers for admin security (rate limit, IP, 2FA) — HTTP-free except Flask config."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask import current_app, request

logger = logging.getLogger(__name__)

_rate_limit_cache: dict[str, list[float]] = {}


def _check_rate_limit(key: str, limit_string: str) -> bool:
    """Return True if request is allowed; False if rate limit exceeded."""
    if current_app.config.get("TESTING"):
        return True

    try:
        parts = limit_string.split("/")
        if len(parts) != 2:
            return True

        limit_count = int(parts[0])
        time_unit = parts[1].lower()

        if "second" in time_unit:
            window = 1
        elif "minute" in time_unit:
            window = 60
        elif "hour" in time_unit:
            window = 3600
        elif "day" in time_unit:
            window = 86400
        else:
            return True

        now = datetime.now(timezone.utc).timestamp()

        if key not in _rate_limit_cache:
            _rate_limit_cache[key] = []

        _rate_limit_cache[key] = [t for t in _rate_limit_cache[key] if now - t < window]

        if len(_rate_limit_cache[key]) >= limit_count:
            return False

        _rate_limit_cache[key].append(now)
        return True

    except Exception as e:
        logger.error("Error checking rate limit: %s", e)
        return True


def _get_client_ip() -> str:
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "unknown"


def _is_ip_whitelisted(client_ip: str) -> bool:
    whitelist = current_app.config.get("ADMIN_IP_WHITELIST", [])
    if not whitelist:
        return True
    return client_ip in whitelist


def _verify_2fa(user) -> bool:
    if not hasattr(user, "two_factor_enabled"):
        return True

    if not user.two_factor_enabled:
        return True

    if not hasattr(user, "two_factor_verified_at") or user.two_factor_verified_at is None:
        return False

    verified_at = user.two_factor_verified_at
    if verified_at.tzinfo is None:
        verified_at = verified_at.replace(tzinfo=timezone.utc)

    time_since_verification = datetime.now(timezone.utc) - verified_at
    return time_since_verification < timedelta(hours=1)
