"""API-Proxy-Routen (DS-015)."""

from __future__ import annotations

from types import ModuleType

from flask import Flask, request, Response
from urllib.error import HTTPError, URLError
from urllib.request import urlopen as _stdlib_urlopen

from route_registration_proxy_policy import (
    PROXY_ALLOWED_HEADERS,
    PROXY_ALLOWLIST_PREFIXES,
    PROXY_BACKEND_NOT_CONFIGURED_BODY,
    PROXY_BACKEND_TIMEOUT_SECONDS,
    PROXY_DANGEROUS_HEADERS,
    PROXY_DENYLIST_PREFIXES,
    PROXY_FORBIDDEN_BODY,
    PROXY_STATUS_BACKEND_NOT_CONFIGURED,
    PROXY_STATUS_FORBIDDEN,
    PROXY_STATUS_NO_CONTENT,
    build_proxy_target,
    build_upstream_proxy_request,
    forwarded_proxy_headers,
    log_proxy_request,
    proxy_request_body,
    proxy_subpath_allowed,
    response_from_http_error,
    response_from_upstream,
    response_from_url_error,
)


def register_proxy_routes(app: Flask, app_module: ModuleType) -> None:
    @app.route("/_proxy/<path:subpath>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    def proxy_api(subpath: str):
        """Proxy API requests to the backend to avoid browser CORS limitations."""
        try:
            if request.method == "OPTIONS":
                return Response(status=PROXY_STATUS_NO_CONTENT)

            if not proxy_subpath_allowed(subpath):
                return Response(
                    PROXY_FORBIDDEN_BODY,
                    status=PROXY_STATUS_FORBIDDEN,
                    mimetype="text/plain",
                )

            base = (app.config.get("BACKEND_API_URL") or "").rstrip("/")
            if not base:
                return Response(
                    PROXY_BACKEND_NOT_CONFIGURED_BODY,
                    status=PROXY_STATUS_BACKEND_NOT_CONFIGURED,
                    mimetype="text/plain",
                )

            target = build_proxy_target(base, subpath, request.query_string)
            body = proxy_request_body(request.method, request.get_data())
            headers = forwarded_proxy_headers(request.headers)
            log_proxy_request(
                method=request.method,
                subpath=subpath,
                target=target,
                headers=headers,
                body=body,
            )
            req = build_upstream_proxy_request(
                target=target,
                body=body,
                method=request.method,
                headers=headers,
            )
            urlopen_fn = getattr(app_module, "urlopen", _stdlib_urlopen)
            with urlopen_fn(req, timeout=PROXY_BACKEND_TIMEOUT_SECONDS) as resp:
                return response_from_upstream(resp)
        except HTTPError as e:
            return response_from_http_error(e)
        except URLError as e:
            return response_from_url_error(e)
        except Exception as e:
            print(f"\n{'!'*60}")
            print("[PROXY DEBUG] UNEXPECTED ERROR")
            print(f"Error: {e}")
            import traceback

            print(traceback.format_exc())
            print(f"{'!'*60}\n")
            raise
