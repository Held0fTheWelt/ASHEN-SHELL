"""Forum moderation report readout routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin, _require_moderator_or_admin

@api_v1_bp.route("/forum/moderation/metrics", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_metrics():
    """
    Get lightweight moderation metrics (moderator/admin only).
    Returns: open_reports count, hidden_posts count, locked_threads count.
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    open_reports = ForumReport.query.filter_by(status="open").count()
    hidden_posts = ForumPost.query.filter_by(status="hidden").count()
    locked_threads = ForumThread.query.filter_by(is_locked=True).count()
    pinned_threads = ForumThread.query.filter_by(is_pinned=True).filter(ForumThread.status != "deleted").count()

    return jsonify({
        "open_reports": open_reports,
        "hidden_posts": hidden_posts,
        "locked_threads": locked_threads,
        "pinned_threads": pinned_threads,
    }), route_status_codes.ok


def _enrich_report_dict(r):
    """Add thread_slug and target_title for dashboard linking."""
    d = r.to_dict()
    if r.target_type == "thread":
        t = get_thread_by_id(r.target_id)
        d["thread_slug"] = t.slug if t and t.deleted_at is None else None
        d["target_title"] = t.title if t else None
    elif r.target_type == "post":
        p = get_post_by_id(r.target_id)
        if p and p.thread:
            d["thread_slug"] = p.thread.slug if p.thread.deleted_at is None else None
            d["target_title"] = (p.content or "")[:80] + ("..." if len(p.content or "") > 80 else "")
        else:
            d["thread_slug"] = None
            d["target_title"] = None
    else:
        d["thread_slug"] = None
        d["target_title"] = None
    return d


@api_v1_bp.route("/forum/moderation/recent-reports", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_recent_reports():
    """
    Get recent open reports for moderator action (moderator/admin only).
    Query: limit (default 10, max 50).
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_small, min_val=1, max_val=50)

    reports = ForumReport.query.filter_by(status="open").order_by(ForumReport.created_at.desc()).limit(limit).all()
    items = [_enrich_report_dict(r) for r in reports]
    return jsonify({"items": items, "total": len(items)}), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/recently-handled", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_recently_handled():
    """
    Get recently handled reports (moderator/admin only).
    Query: limit (default 10, max 50). Returns reports with status reviewed/resolved/dismissed, ordered by handled_at desc.
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_small, min_val=1, max_val=50)
    reports = (
        ForumReport.query.filter(ForumReport.status.in_(["reviewed", "escalated", "resolved", "dismissed"]))
        .filter(ForumReport.handled_at.isnot(None))
        .order_by(ForumReport.handled_at.desc())
        .limit(limit)
        .all()
    )
    items = [_enrich_report_dict(r) for r in reports]
    return jsonify({"items": items, "total": len(items)}), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/locked-threads", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_locked_threads():
    """List locked threads for dashboard (moderator/admin only). Query: limit (default 20, max 100)."""
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)
    threads = (
        ForumThread.query.filter_by(is_locked=True)
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
