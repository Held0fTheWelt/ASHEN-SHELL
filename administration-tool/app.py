"""Lightweight Flask public frontend for World of Shadows.
Serves HTML and static assets only; consumes backend API for data. No database."""
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlparse

from flask import Flask, request, session, render_template, Response
import secrets  # Import the secrets module

# Load environment from .env (local dev convenience)
try:
    from dotenv import load_dotenv

    load_dotenv()
    _here = Path(__file__).resolve().parent
    load_dotenv(_here / ".env")
    # Also load repo-root .env so one file can be shared with backend
    _repo_root = _here.parent
    load_dotenv(_repo_root / ".env")
except ImportError:
    pass

# Backend API base URL (no trailing slash). Used for login link and for frontend JS.
# IMPORTANT: Defaults to production URL (held0fthewelt.pythonanywhere.com) for live testing.
# For local development: set BACKEND_API_URL=http://127.0.0.1:5000 or uncomment the localhost line below.
# BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://127.0.0.1:5000").rstrip("/") # LOCALHOST
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "https://held0fthewelt.pythonanywhere.com").rstrip("/")
SUPPORTED_LANGUAGES = ["de", "en"]
DEFAULT_LANGUAGE = "de"

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)
app.config["BACKEND_API_URL"] = BACKEND_API_URL

# CRITICAL SECURITY: Session secret must be explicitly configured via environment variable.
# Never use hardcoded defaults; always require explicit configuration.
_secret = os.environ.get("SECRET_KEY", "").strip()
if not _secret:
    # Generate a secure random key if SECRET_KEY is not set
    _secret = secrets.token_urlsafe(32)
    print("Warning: SECRET_KEY not found in environment. Generated a new one.")
app.secret_key = _secret


def _load_translations(lang: str) -> dict:
    """Load translation dict for lang from translations/<lang>.json. Fallback to default keys."""
    base = Path(app.root_path) / "translations"
    path = base / f"{lang}.json"
    if not path.is_file():
        path = base / f"{DEFAULT_LANGUAGE}.json"
    if not path.is_file():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _resolve_language():
    """Resolve UI language: query lang -> session -> Accept-Language -> default."""
    lang = (request.args.get("lang") or "").strip().lower()
    if lang in SUPPORTED_LANGUAGES:
        session["lang"] = lang
        return lang
    if session.get("lang") in SUPPORTED_LANGUAGES:
        return session["lang"]
    accept = request.headers.get("Accept-Language", "")
    for part in accept.replace(" ", "").split(","):
        code = part.split(";")[0].split("-")[0].lower()
        if code in SUPPORTED_LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


@app.context_processor
def inject_config():
    """Expose backend URL, frontend config, current language, and UI translations to all templates."""
    current_lang = _resolve_language()
    t = _load_translations(current_lang)
    return {
        "backend_api_url": app.config["BACKEND_API_URL"],
        "frontend_config": {
            "backendApiUrl": app.config["BACKEND_API_URL"],
            # Use same-origin proxy endpoints to avoid browser CORS issues when the backend is on a different origin.
            "apiProxyBase": "/_proxy",
            "supportedLanguages": SUPPORTED_LANGUAGES,
            "defaultLanguage": DEFAULT_LANGUAGE,
            "currentLanguage": current_lang,
        },
        "current_lang": current_lang,
        "supported_languages": SUPPORTED_LANGUAGES,
        "t": t,
    }


@app.route("/_proxy/<path:subpath>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def proxy_api(subpath: str):
    """Proxy API requests to the backend to avoid browser CORS limitations.

    Client calls: /_proxy/api/v1/...
    Server forwards to: {BACKEND_API_URL}/api/v1/...
    """
    # Allow preflight to succeed quickly (browser shouldn't need it for same-origin, but harmless).
    if request.method == "OPTIONS":
        return Response(status=204)

    base = (app.config.get("BACKEND_API_URL") or "").rstrip("/")
    if not base:
        return Response("Backend API URL not configured", status=500, mimetype="text/plain")

    # Preserve query string
    path = "/" + subpath.lstrip("/")
    target = base + path
    if request.query_string:
        target = target + "?" + request.query_string.decode("utf-8", errors="ignore")

    body = request.get_data() if request.method in ("POST", "PUT", "PATCH") else None

    headers = {}
    # Forward only relevant headers
    if request.headers.get("Authorization"):
        headers["Authorization"] = request.headers["Authorization"]
    if request.headers.get("Content-Type"):
        headers["Content-Type"] = request.headers["Content-Type"]
    headers["Accept"] = request.headers.get("Accept", "application/json")

    req = Request(target, data=body, method=request.method, headers=headers)
    try:
        with urlopen(req, timeout=20) as resp:
            resp_body = resp.read()
            content_type = resp.headers.get("Content-Type", "application/json")
            return Response(resp_body, status=resp.status, content_type=content_type)
    except HTTPError as e:
        err_body = e.read() if hasattr(e, "read") else b""
        content_type = getattr(e, "headers", {}).get("Content-Type", "application/json")
        return Response(err_body, status=int(getattr(e, "code", 502)), content_type=content_type)
    except URLError:
        return Response("Upstream network error", status=502, mimetype="text/plain")


@app.route("/")
def index():
    """Public home page."""
    return render_template("index.html")


@app.route("/news")
def news_list():
    """Public news list page. Data loaded by JS from backend API."""
    return render_template("news.html")


@app.route("/news/<int:news_id>")
def news_detail(news_id):
    """Public news detail page. Data loaded by JS from backend API."""
    return render_template("news_detail.html", news_id=news_id)


@app.route("/wiki")
@app.route("/wiki/<path:slug>")
def wiki_index(slug=None):
    """Public wiki page. Default slug 'wiki' for main page. Data loaded by JS from backend API."""
    return render_template