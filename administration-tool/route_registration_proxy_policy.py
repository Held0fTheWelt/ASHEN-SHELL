"""Proxy policy and response helpers for the administration tool."""

from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request

from flask import Response

PROXY_ALLOWLIST_PREFIXES = [
    "api/",  # /_proxy/api/* -> allowed (REST API endpoints)
]

PROXY_DENYLIST_PREFIXES = [
    "admin",  # /_proxy/admin/* -> 403 Forbidden (internal admin only)
]

PROXY_DANGEROUS_HEADERS = {
    "Cookie",
    "Set-Cookie",
    "Host",
    "X-Forwarded-For",
    "X-Real-IP",
}

PROXY_ALLOWED_HEADERS = {
    "Authorization",
    "Content-Type",
    "Accept",
    "Accept-Language",
    "User-Agent",
}

PROXY_BACKEND_TIMEOUT_SECONDS = 20
PROXY_STATUS_NO_CONTENT = 204
PROXY_STATUS_FORBIDDEN = 403
PROXY_STATUS_BACKEND_NOT_CONFIGURED = 500
PROXY_STATUS_UPSTREAM_NETWORK_ERROR = 502
PROXY_FORBIDDEN_BODY = "Forbidden"
PROXY_BACKEND_NOT_CONFIGURED_BODY = "Backend API URL not configured"
PROXY_UPSTREAM_NETWORK_ERROR_BODY = "Upstream network error"


def proxy_subpath_allowed(subpath: str) -> bool:
    is_allowed = any(subpath.startswith(prefix) for prefix in PROXY_ALLOWLIST_PREFIXES)
    is_denied = any(subpath.startswith(prefix) for prefix in PROXY_DENYLIST_PREFIXES)
    return is_allowed and not is_denied


def build_proxy_target(base_url: str, subpath: str, query_string: bytes) -> str:
    target = base_url.rstrip("/") + "/" + subpath.lstrip("/")
    if query_string:
        target = target + "?" + query_string.decode("utf-8", errors="ignore")
    return target


def proxy_request_body(method: str, body: bytes) -> bytes | None:
    return body if method in {"POST", "PUT", "PATCH"} else None


def forwarded_proxy_headers(request_headers: Any) -> dict[str, str]:
    headers: dict[str, str] = {}
    for header_name in PROXY_ALLOWED_HEADERS:
        header_value = request_headers.get(header_name)
        if header_value:
            headers[header_name] = header_value
    for header_name in PROXY_DANGEROUS_HEADERS:
        headers.pop(header_name, None)
    return headers


def redacted_proxy_headers(headers: dict[str, str]) -> dict[str, str]:
    out = dict(headers)
    auth = out.get("Authorization")
    if auth and isinstance(auth, str) and auth.startswith("Bearer "):
        out["Authorization"] = "Bearer ***redacted***"
    return out


def log_proxy_request(*, method: str, subpath: str, target: str, headers: dict[str, str], body: bytes | None) -> None:
    print(f"\n[PROXY DEBUG] {method} /_proxy/{subpath}")
    print(f"[PROXY DEBUG] Target: {target}")
    print(f"[PROXY DEBUG] Headers: {redacted_proxy_headers(headers)}")
    print(f"[PROXY DEBUG] Body length: {len(body) if body else 0}")
    if body:
        try:
            print(f"[PROXY DEBUG] Body: {body.decode('utf-8')}")
        except Exception:
            print(f"[PROXY DEBUG] Body (raw): {body}")


def build_upstream_proxy_request(*, target: str, body: bytes | None, method: str, headers: dict[str, str]) -> Request:
    return Request(target, data=body, method=method, headers=headers)


def response_from_upstream(resp: Any) -> Response:
    resp_body = resp.read()
    content_type = resp.headers.get("Content-Type", "application/json")
    print(f"[PROXY DEBUG] Response: {resp.status}")
    return Response(resp_body, status=resp.status, content_type=content_type)


def response_from_http_error(error: HTTPError) -> Response:
    err_body = error.read() if hasattr(error, "read") else b""
    print(f"[PROXY DEBUG] HTTPError: {error.code}")
    print(f"[PROXY DEBUG] Error body: {err_body[:200]}")
    content_type = getattr(error, "headers", {}).get("Content-Type", "application/json")
    return Response(err_body, status=int(getattr(error, "code", 502)), content_type=content_type)


def response_from_url_error(error: URLError) -> Response:
    print(f"[PROXY DEBUG] URLError: {error}")
    return Response(
        PROXY_UPSTREAM_NETWORK_ERROR_BODY,
        status=PROXY_STATUS_UPSTREAM_NETWORK_ERROR,
        mimetype="text/plain",
    )


__all__ = [
    "PROXY_ALLOWED_HEADERS",
    "PROXY_ALLOWLIST_PREFIXES",
    "PROXY_BACKEND_NOT_CONFIGURED_BODY",
    "PROXY_BACKEND_TIMEOUT_SECONDS",
    "PROXY_DANGEROUS_HEADERS",
    "PROXY_DENYLIST_PREFIXES",
    "PROXY_FORBIDDEN_BODY",
    "PROXY_STATUS_BACKEND_NOT_CONFIGURED",
    "PROXY_STATUS_FORBIDDEN",
    "PROXY_STATUS_NO_CONTENT",
    "build_proxy_target",
    "build_upstream_proxy_request",
    "forwarded_proxy_headers",
    "log_proxy_request",
    "proxy_request_body",
    "proxy_subpath_allowed",
    "response_from_http_error",
    "response_from_upstream",
    "response_from_url_error",
]
