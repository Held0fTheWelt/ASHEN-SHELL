"""Forum tag administration routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin, _require_moderator_or_admin

@api_v1_bp.route("/forum/tags", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_tags_list():
    """
    List all tags (moderator/admin only). Paginated with optional search.
    Query: q, page, limit.
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_medium, min_val=1, max_val=route_pagination_config.page_size_large)
    q = (request.args.get("q") or "").strip() or None
    tags, total = list_all_tags(page=page, per_page=limit, q=q)
    counts = batch_tag_thread_counts([t.id for t in tags])
    items = []
    for t in tags:
        items.append({
            "id": t.id,
            "slug": t.slug,
            "label": t.label,
            "thread_count": counts.get(t.id, 0),
            "created_at": t.created_at.isoformat() if t.created_at else None,
        })
    return jsonify({"items": items, "total": total, "page": page, "per_page": limit}), route_status_codes.ok


@api_v1_bp.route("/forum/tags/<int:tag_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_tag_delete(tag_id: int):
    """
    Delete a tag if unused (admin only). Returns 409 if tag has thread associations.
    """
    user, err_resp = _require_admin()
    if err_resp:
        return err_resp
    tag = ForumTag.query.get(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), route_status_codes.not_found
    err = delete_tag(tag)
    if err:
        return jsonify({"error": err}), route_status_codes.conflict
    log_activity(
        actor=user,
        category="forum",
        action="tag_deleted",
        status="success",
        message=f"Forum tag deleted: {tag.slug}",
        route=request.path,
        method=request.method,
        target_type="forum_tag",
        target_id=str(tag_id),
    )
    return jsonify({"message": "Deleted"}), route_status_codes.ok
