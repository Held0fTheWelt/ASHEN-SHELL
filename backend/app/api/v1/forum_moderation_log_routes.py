"""Forum moderation activity log routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin, _require_moderator_or_admin

@api_v1_bp.route("/forum/moderation/log", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderation_log():
    """
    Moderator/admin-visible moderation log for forum actions.
    Thin wrapper around activity logs filtered by category=forum.

    Query: q, status, date_from, date_to, page, limit.
    """
    user = get_current_user()
    if not user or not current_user_is_moderator_or_admin():
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_medium, min_val=1, max_val=route_pagination_config.page_size_large)
    q = request.args.get("q", "").strip() or None
    status = request.args.get("status", "").strip() or None
    date_from = request.args.get("date_from", "").strip() or None
    date_to = request.args.get("date_to", "").strip() or None

    items, total = list_activity_logs(
        page=page,
        limit=limit,
        q=q,
        category="forum",
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    return jsonify(
        {
            "items": [e.to_dict() for e in items],
            "total": total,
            "page": page,
            "limit": limit,
        }
    ), route_status_codes.ok
