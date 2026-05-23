"""Forum moderation queue routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_moderator_or_admin

@api_v1_bp.route("/forum/moderation/escalation-queue", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_escalation_queue():
    """
    Get escalated reports in priority order (moderator/admin only).
    Query params: page (default 1), limit (default 50, max 100), priority (filter: critical|high|normal|low)
    Response: { items: [ForumReport], total }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_medium, min_val=1, max_val=route_pagination_config.page_size_large)
    priority_filter = request.args.get("priority", "").strip() or None

    items, total = list_escalation_queue(
        page=page,
        per_page=limit,
        priority_filter=priority_filter,
    )

    return jsonify({
        "items": [r.to_dict() for r in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/review-queue", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_review_queue():
    """
    Get open and reviewed reports pending action (moderator/admin only).
    Query params: page (default 1), limit (default 50, max 100)
    Response: { items: [ForumReport], total }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_medium, min_val=1, max_val=route_pagination_config.page_size_large)

    items, total = list_review_queue(page=page, per_page=limit)

    return jsonify({
        "items": [r.to_dict() for r in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/moderator-assigned", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_moderator_assigned():
    """
    Get reports assigned to the current moderator (moderator/admin only).
    Query params: page (default 1), limit (default 50, max 100)
    Response: { items: [ForumReport], total }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_medium, min_val=1, max_val=route_pagination_config.page_size_large)

    items, total = list_moderator_assigned_reports(user.id, page=page, per_page=limit)

    return jsonify({
        "items": [r.to_dict() for r in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/handled-reports", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_handled_reports():
    """
    Get resolved or dismissed reports (moderator/admin only).
    Query params: page (default 1), limit (default 50, max 100), status (filter: resolved|dismissed)
    Response: { items: [ForumReport], total }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), route_pagination_config.page_size_medium, min_val=1, max_val=route_pagination_config.page_size_large)
    status_filter = request.args.get("status", "").strip() or None

    items, total = list_handled_reports(page=page, per_page=limit, status_filter=status_filter)

    return jsonify({
        "items": [r.to_dict() for r in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/reports/<int:report_id>/assign", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_report_assign(report_id: int):
    """
    Assign a report to a moderator (moderator/admin only).
    Body: { "moderator_id": int } or { "assign_to_me": true }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp

    report = get_report_by_id(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), route_status_codes.not_found

    data = request.get_json(silent=True) or {}
    assign_to_me = data.get("assign_to_me", False)

    if assign_to_me:
        moderator_id = user.id
    else:
        moderator_id = data.get("moderator_id")
        if not moderator_id:
            return jsonify({"error": "moderator_id or assign_to_me required"}), route_status_codes.bad_request
        try:
            moderator_id = int(moderator_id)
        except (TypeError, ValueError):
            return jsonify({"error": "moderator_id must be integer"}), route_status_codes.bad_request

    before_assigned = report.assigned_to
    report = assign_report_to_moderator(report, moderator_id)

    log_activity(
        actor=user,
        category="forum",
        action="report_assigned",
        status="success",
        message=f"Report {report_id} assigned to moderator {moderator_id}",
        route=request.path,
        method=request.method,
        target_type="forum_report",
        target_id=str(report_id),
        metadata={"before": {"assigned_to": before_assigned}, "after": {"assigned_to": moderator_id}},
    )

    return jsonify({"id": report.id, "assigned_to": report.assigned_to}), route_status_codes.ok
