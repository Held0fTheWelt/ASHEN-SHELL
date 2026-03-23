"""Public read-only news API. Only published news is exposed.

List:  GET /api/v1/news?q=&sort=published_at&direction=desc&page=1&limit=20&category=
  Response: { "items": [ { "id", "title", "slug", "summary", "content", "author_id", "author_name",
    "is_published", "published_at", "created_at", "updated_at", "cover_image", "category" } ], "total", "page", "per_page" }

Detail: GET /api/v1/news/<id>
  Response: single object same shape as list item, or { "error": "Not found" } 404.

Write (all require Authorization: Bearer <JWT> and moderator/admin role; 401 if missing/invalid token, 403 if forbidden):
  POST   /api/v1/news             -> create (body: title, slug, content; optional summary, is_published, cover_image, category)
  PUT    /api/v1/news/<id>        -> update (body: optional title, slug, summary, content, cover_image, category)
  DELETE /api/v1/news/<id>        -> delete
  POST   /api/v1/news/<id>/publish   -> set published
  POST   /api/v1/news/<id>/unpublish -> set unpublished
"""
from datetime import datetime, timezone

from flask import g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request

from app.api.v1 import api_v1_bp
from app.auth import current_user_can_write_news
from app.auth.permissions import get_current_user, require_editor_or_n8n_service, require_jwt_moderator_or_admin
from app.extensions import limiter, db
from app.services import log_activity
from app.i18n import normalize_language, validate_language_code
from app.models import NewsArticle, ForumThread
from app.services.news_service import (
    SORT_FIELDS,
    SORT_ORDERS,
    approve_article_translation,
    create_news,
    delete_news,
    get_article_translation,
    get_news_by_id,
    get_news_by_slug,
    get_news_article_by_id,
    get_suggested_threads_for_article,
    list_article_translations,
    list_news,
    publish_article_translation,
    publish_news,
    submit_review_article_translation,
    unpublish_news,
    update_news,
    upsert_article_translation,
    _translation_to_dict,
    list_related_threads_for_article,
)


def _parse_int(value, default, min_val=None, max_val=None):
    """Parse query param as int; return default if missing/invalid."""
    if value is None:
        return default
    try:
        n = int(value)
        if min_val is not None and n < min_val:
            return default
        if max_val is not None and n > max_val:
            return max_val
        return n
    except (TypeError, ValueError):
        return default


def _request_wants_include_drafts():
    """True if request has valid JWT with moderator/admin and query published_only=0 or include_drafts=1."""
    try:
        verify_jwt_in_request()
        raw = get_jwt_identity()
        if raw is None:
            return False
    except Exception:
        return False
    if not current_user_can_write_news():
        return False
    p = request.args.get("published_only", "").strip().lower()
    if p in ("0", "false", "no"):
        return True
    d = request.args.get("include_drafts", "").strip().lower()
    if d in ("1", "true", "yes"):
        return True
    return False


@api_v1_bp.route("/news", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def news_list():
    """
    List news. By default only published. With JWT (moderator/admin) and published_only=0 or include_drafts=1, includes drafts.
    Query params: q (search), sort, direction, page, limit, category, lang, published_only (0 to include drafts).
    Response: { "items": [...], "total": N, "page": P, "per_page": L }.
    """
    q = request.args.get("q", "").strip() or None
    sort = request.args.get("sort", "published_at").strip() or "published_at"
    if sort not in SORT_FIELDS:
        sort = "published_at"
    direction = request.args.get("direction", "desc").strip().lower() or "desc"
    if direction not in SORT_ORDERS:
        direction = "desc"
    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=100)
    category = request.args.get("category", "").strip() or None
    lang = request.args.get("lang", "").strip() or None
    published_only = not _request_wants_include_drafts()

    items, total = list_news(
        published_only=published_only,
        search=q,
        sort=sort,
        order=direction,
        page=page,
        per_page=limit,
        category=category,
        lang=lang,
    )
    return jsonify({
        "items": items,
        "total": total,
        "page": page,
        "per_page": limit,
    }), 200


@api_v1_bp.route("/news/<id_or_slug>", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def news_detail(id_or_slug):
    """
    Get a single news article by id (integer) or slug (string). Public: only published; 404 for draft.
    With JWT (moderator/admin): returns article even if draft. Query: lang for language.
    Response: single news object (id, title, slug, summary, content, author_id, author_name, language_code, ...).
    """
    lang = request.args.get("lang", "").strip() or None
    news = None
    if id_or_slug.isdigit():
        news = get_news_by_id(int(id_or_slug), lang=lang)
    else:
        news = get_news_by_slug(id_or_slug, lang=lang)
    if not news:
        return jsonify({"error": "Not found"}), 404
    if not news.get("is_published"):
        try:
            verify_jwt_in_request()
            if get_jwt_identity() is not None and current_user_can_write_news():
                return jsonify(news), 200
        except Exception:
            pass
        return jsonify({"error": "Not found"}), 404
    now = datetime.now(timezone.utc)
    pub_at = news.get("published_at")
    if pub_at:
        try:
            dt = datetime.fromisoformat(pub_at.replace("Z", "+00:00")) if isinstance(pub_at, str) else pub_at
            if hasattr(dt, "tzinfo") and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt > now:
