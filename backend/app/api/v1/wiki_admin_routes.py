"""Wiki admin API: pages CRUD and translations (submit-review, approve, publish, auto-translate)."""
from flask import g, jsonify, request

from app.api.v1 import api_v1_bp
from app.auth.permissions import get_current_user, require_editor_or_n8n_service, require_jwt_moderator_or_admin
from app.extensions import limiter, db
from app.i18n import normalize_language, validate_language_code
from app.services import log_activity
from app.models import WikiPage, ForumThread
from app.services.wiki_service import (
    approve_wiki_translation,
    create_wiki_page,
    get_wiki_page_by_id,
    list_wiki_page_translations,
    list_wiki_pages,
    get_wiki_page_translation,
    publish_wiki_translation,
    submit_review_wiki_translation,
    update_wiki_page,
    upsert_wiki_page_translation,
    list_related_threads_for_page,
)


def _page_to_dict(page):
    out = {
        "id": page.id,
        "key": page.key,
        "parent_id": page.parent_id,
        "sort_order": page.sort_order,
        "is_published": page.is_published,
        "created_at": page.created_at.isoformat() if page.created_at else None,
        "updated_at": page.updated_at.isoformat() if page.updated_at else None,
        "discussion_thread_id": page.discussion_thread_id,
    }
    if page.discussion_thread_id is not None:
        thread = db.session.get(ForumThread, page.discussion_thread_id)
        out["discussion_thread_slug"] = thread.slug if thread and thread.deleted_at is None else None
    else:
        out["discussion_thread_slug"] = None
    return out


def _translation_to_dict(t):
    return {
        "id": t.id,
        "page_id": t.page_id,
        "language_code": t.language_code,
        "title": t.title,
        "slug": t.slug,
        "content_markdown": t.content_markdown,
        "translation_status": t.translation_status,
        "source_language": t.source_language,
        "reviewed_by": t.reviewed_by,
        "reviewed_at": t.reviewed_at.isoformat() if t.reviewed_at else None,
    }


@api_v1_bp.route("/wiki-admin/pages", methods=["GET"])
@limiter.limit("60 per minute")
@require_jwt_moderator_or_admin
def wiki_admin_pages_list():
    """List all wiki pages. Requires moderator/admin."""
    pages = list_wiki_pages()
    return jsonify({"items": [_page_to_dict(p) for p in pages]}), 200


@api_v1_bp.route("/wiki-admin/pages", methods=["POST"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def wiki_admin_pages_create():
    """Create a wiki page. Body: key, parent_id?, sort_order?, is_published?. Requires moderator/admin."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    key = (data.get("key") or "").strip()
    parent_id = data.get("parent_id")
    sort_order = int(data.get("sort_order", 0))
    is_published = bool(data.get("is_published", True))
    page, err = create_wiki_page(key=key, parent_id=parent_id, sort_order=sort_order, is_published=is_published)
    if err:
        return jsonify({"error": err}), 400 if err != "Key already in use" else 409
    return jsonify(_page_to_dict(page)), 201


@api_v1_bp.route("/wiki-admin/pages/<int:page_id>", methods=["PUT"])
@limiter.limit("30 per minute")
@require_jwt_moderator_or_admin
def wiki_admin_pages_update(page_id):
    """Update wiki page. Body: key?, sort_order?, is_published?. Requires moderator/admin."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    kwargs = {}
    if "key" in data:
        kwargs["key"] = data.get("key")
    if "sort_order" in data:
        kwargs["sort_order"] = int(data.get("sort_order", 0))
    if "is_published" in data:
        kwargs["is_published"] = bool(data.get("is_published"))
    page, err = update_wiki_page(page_id, **kwargs)
    if err:
        return jsonify({"error": err}), 404 if err == "Page not found" else 400
    return jsonify(_page_to_dict(page)), 200


@api_v1_bp.route("/wiki-admin/pages/<int:page_id>/translations", methods=["GET"])
@limiter.limit("60 per minute")
@require_jwt_moderator_or_admin
def wiki_admin_translations_list(page_id):
    """List translation status per language for page. Requires moderator/admin."""
    items, err = list_wiki_page_translations(page_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({"items": items}), 200


@api_v1_bp.route("/wiki-admin/pages/<int:page_id>/translations/<lang>", methods=["GET"])
@limiter.limit("50 per minute", key_func=lambda: f"{request.remote_addr}:{request.headers.get('X-Service-Key', '')}")
@require_editor_or_n8n_service
def wiki_admin_translation_get(page_id, lang):
    """Get one wiki translation. Requires moderator/admin or n8n X-Service-Key."""
    validated_lang, err = validate_language_code(lang)
    if err:
        return jsonify({"error": err}), 400
    trans = get_wiki_page_translation(page_id, validated_lang)
    if not trans:
        return jsonify({"error": "Translation not found"}), 404
    return jsonify(_translation_to_dict(trans)), 200


@api_v1_bp.route("/wiki-admin/pages/<int:page_id>/translations/<lang>", methods=["PUT"])
@limiter.limit("50 per minute", key_func=lambda: f"{request.remote_addr}:{request.headers.get('X-Service-Key', '')}")
@require_editor_or_n8n_service
def wiki_admin_translation_put(page_id, lang):
    """Create or update wiki page translation. Body: title, slug, content_markdown, translation_status?. Requires moderator/admin or n8n X-Service-Key (machine_draft only)."""
    validated_lang, err = validate_language_code(lang)
    if err:
        return jsonify({"error": err}), 400
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    translation_status = data.get("translation_status")
    if getattr(g, "is_n8n_service", False):
        translation_status = "machine_draft"
    trans, err = upsert_wiki_page_translation(
        page_id,
        validated_lang,
        title=data.get("title"),
        slug=data.get("slug"),
        content_markdown=data.get("content_markdown"),
        translation_status