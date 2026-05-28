"""Error handlers, HTTPS redirect, security headers, JWT API loaders (DS-042)."""

from __future__ import annotations

from http import HTTPStatus
from urllib.parse import urlparse

from flask import Flask, jsonify, redirect, request

from app.extensions import jwt

HTTP_MOVED_PERMANENTLY = int(HTTPStatus.MOVED_PERMANENTLY)
HTTP_UNAUTHORIZED = int(HTTPStatus.UNAUTHORIZED)
HTTP_NOT_FOUND = int(HTTPStatus.NOT_FOUND)
HTTP_TOO_MANY_REQUESTS = int(HTTPStatus.TOO_MANY_REQUESTS)
HTTP_INTERNAL_SERVER_ERROR = int(HTTPStatus.INTERNAL_SERVER_ERROR)
HSTS_HEADER_VALUE = "max-age=31536000; includeSubDomains"
CSP_CONNECT_INSERT_INDEX = 5
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}
CSP_DIRECTIVES = (
    "default-src 'self'",
    "script-src 'self' https://cdnjs.cloudflare.com",
    "style-src 'self' https://fonts.googleapis.com",
    "img-src 'self' data: https:",
    "font-src 'self' https://fonts.gstatic.com",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
)


def _wants_json() -> bool:
    return request.path.startswith("/api/")


def _https_enforced(app: Flask) -> bool:
    return bool(app.config.get("ENFORCE_HTTPS") and not app.config.get("TESTING"))


def _play_service_connect_sources(app: Flask) -> list[str]:
    connect_sources = ["'self'", "https:"]
    play_service_public_url = (app.config.get("PLAY_SERVICE_PUBLIC_URL") or "").strip()
    if not play_service_public_url:
        return connect_sources
    parsed = urlparse(play_service_public_url)
    if parsed.scheme and parsed.netloc:
        connect_sources.append(f"{parsed.scheme}://{parsed.netloc}")
        ws_scheme = "wss" if parsed.scheme == "https" else "ws"
        connect_sources.append(f"{ws_scheme}://{parsed.netloc}")
    return connect_sources


def _content_security_policy(app: Flask) -> str:
    connect = f"connect-src {' '.join(_play_service_connect_sources(app))}"
    return "; ".join(
        (
            *CSP_DIRECTIVES[:CSP_CONNECT_INSERT_INDEX],
            connect,
            *CSP_DIRECTIVES[CSP_CONNECT_INSERT_INDEX:],
        )
    )


def register_http_shell(app: Flask) -> None:
    @jwt.unauthorized_loader
    def unauthorized_callback(_):
        return jsonify({"error": "Authorization required. Missing or invalid token."}), HTTP_UNAUTHORIZED

    @jwt.invalid_token_loader
    def invalid_token_callback(_err):
        return jsonify({"error": "Invalid or expired token."}), HTTP_UNAUTHORIZED

    if _https_enforced(app):

        @app.before_request
        def enforce_https():
            if request.scheme == "http" and not app.debug:
                url = request.url.replace("http://", "https://", 1)
                return redirect(url, code=HTTP_MOVED_PERMANENTLY)

    @app.errorhandler(HTTP_NOT_FOUND)
    def not_found(_e):
        if _wants_json():
            return jsonify({"error": "Not found"}), HTTP_NOT_FOUND
        return "Not found", HTTP_NOT_FOUND

    @app.errorhandler(HTTP_TOO_MANY_REQUESTS)
    def ratelimit_handler(_request):
        return jsonify({"error": "Too many requests. Please try again later."}), HTTP_TOO_MANY_REQUESTS

    @app.errorhandler(HTTP_INTERNAL_SERVER_ERROR)
    def server_error(_e):
        if _wants_json():
            return jsonify({"error": "Internal server error"}), HTTP_INTERNAL_SERVER_ERROR
        return "Internal server error", HTTP_INTERNAL_SERVER_ERROR

    @app.after_request
    def add_security_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        response.headers["Content-Security-Policy"] = _content_security_policy(app)
        if _https_enforced(app):
            response.headers["Strict-Transport-Security"] = HSTS_HEADER_VALUE
        return response
