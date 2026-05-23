"""Forum moderation thread and post readout routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin, _require_moderator_or_admin

@api_v1_bp.route("/forum/moderation/pinned-threads", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_pinned_threads():
    """List pinned threads for dashboard (moderator/admin only). Query: limit (default 20, max 100)."""
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)
    threads = (
        ForumThread.query.filter_by(is_pinned=True)
        .filter(ForumThread.status != "deleted")
        .order_by(ForumThread.updated_at.desc().nullslast())
        .limit(limit)
        .all()
    )
    items = []
    for t in threads:
        items.append({
            "id": t.id,
            "slug": t.slug,
            "title": t.title,
            "category_slug": t.category.slug if t.category else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })
    return jsonify({"items": items, "total": len(items)}), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/hidden-posts", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_hidden_posts():
    """List hidden posts for dashboard (moderator/admin only). Query: limit (default 20, max 100)."""
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)
    posts = (
        ForumPost.query.filter_by(status="hidden")
        .order_by(ForumPost.updated_at.desc().nullslast())
        .limit(limit)
        .all()
    )
    items = []
    for p in posts:
        thread = p.thread
        items.append({
            "id": p.id,
            "thread_id": p.thread_id,
            "thread_slug": thread.slug if thread and thread.deleted_at is None else None,
            "thread_title": thread.title if thread else None,
            "content_snippet": (p.content or "")[:120] + ("..." if len(p.content or "") > 120 else ""),
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })
    return jsonify({"items": items, "total": len(items)}), route_status_codes.ok
