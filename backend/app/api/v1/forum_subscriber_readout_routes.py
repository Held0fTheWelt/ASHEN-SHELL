"""Forum subscriber readout routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin, _require_moderator_or_admin

@api_v1_bp.route("/forum/threads/<int:thread_id>/subscribers", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_thread_subscribers(thread_id: int):
    """
    List subscribers for a thread (moderator/admin only).
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found

    subs = ForumThreadSubscription.query.filter_by(thread_id=thread_id).all()
    items = []
    for sub in subs:
        items.append({
            "id": sub.id,
            "thread_id": sub.thread_id,
            "user_id": sub.user_id,
            "username": sub.user.username if hasattr(sub, 'user') and sub.user else None,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
        })
    return jsonify({"items": items, "total": len(items)}), route_status_codes.ok
