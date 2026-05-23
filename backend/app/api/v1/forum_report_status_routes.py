"""Forum report status moderation routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_moderator_or_admin

@api_v1_bp.route("/forum/reports", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_reports_list():
    """
    List forum reports (moderator/admin only).
    Query: status, target_type, page, limit.
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    status = (request.args.get("status") or "").strip() or None
    target_type = (request.args.get("target_type") or "").strip() or None
    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)
    items, total = list_reports(status=status, target_type=target_type, page=page, limit=limit)
    return jsonify({"items": [r.to_dict() for r in items], "total": total, "page": page, "limit": limit}), route_status_codes.ok


@api_v1_bp.route("/forum/reports/<int:report_id>", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_report_get(report_id: int):
    """Get single report (moderator/admin only)."""
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    report = get_report_by_id(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), route_status_codes.not_found
    return jsonify(report.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/reports/<int:report_id>", methods=["PUT"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_report_update(report_id: int):
    """
    Update report status and metadata (moderator/admin only).
    Body: {
        "status": "open|reviewed|escalated|resolved|dismissed",
        "priority": "low|normal|high|critical" (optional),
        "escalation_reason": "str" (optional, for escalations),
        "resolution_note": "str" (optional)
    }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    report = get_report_by_id(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), route_status_codes.not_found
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    status = (data.get("status") or "").strip()
    old_status = report.status
    old_priority = report.priority

    priority = data.get("priority")
    if priority and priority not in ("low", "normal", "high", "critical"):
        return jsonify({"error": "Invalid priority"}), route_status_codes.bad_request

    escalation_reason = data.get("escalation_reason")
    if escalation_reason is not None:
        escalation_reason = str(escalation_reason).strip() or None

    resolution_note = data.get("resolution_note")
    if resolution_note is not None:
        resolution_note = str(resolution_note).strip() or None

    try:
        report = update_report_status(
            report,
            status=status,
            handled_by=user.id,
            resolution_note=resolution_note,
            priority=priority,
            escalation_reason=escalation_reason,
        )
    except ValueError as e:
        log_full_error(e, "Report status update validation failed", user_id=user.id, route=request.path, method=request.method)
        return jsonify({"error": ERROR_MESSAGES["validation_error"]}), route_status_codes.bad_request
    log_activity(
        actor=user,
        category="forum",
        action="report_status_updated",
        status="success",
        message=f"Report {report.id} status -> {report.status}",
        route=request.path,
        method=request.method,
        target_type="forum_report",
        target_id=str(report.id),
        metadata={
            "before": {"status": old_status, "priority": old_priority},
            "after": {"status": report.status, "priority": report.priority},
        },
    )
    return jsonify(report.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/reports/bulk-status", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def forum_reports_bulk_status():
    """
    Bulk update report status with per-item feedback (moderator/admin only).
    Body: {
        "report_ids": [int, ...],
        "status": "reviewed|escalated|resolved|dismissed",
        "priority": "low|normal|high|critical" (optional),
        "resolution_note": "str" (optional)
    }
    Response: { "updated_ids": [...], "failed_items": [{"id": int, "reason": str}, ...] }
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    ids = data.get("report_ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "report_ids must be a non-empty list"}), route_status_codes.bad_request
    try:
        id_list = [int(x) for x in ids]
    except (TypeError, ValueError):
        return jsonify({"error": "report_ids must contain integers"}), route_status_codes.bad_request
    status = (data.get("status") or "").strip()
    if status not in ("reviewed", "escalated", "resolved", "dismissed"):
        return jsonify({"error": "Invalid status for bulk update"}), route_status_codes.bad_request

    priority = data.get("priority")
    if priority and priority not in ("low", "normal", "high", "critical"):
        return jsonify({"error": "Invalid priority"}), route_status_codes.bad_request

    resolution_note = data.get("resolution_note")
    if resolution_note is not None:
        resolution_note = str(resolution_note).strip() or None

    # Use service function for bulk update with per-item feedback
    success_ids, failed_items = bulk_update_report_status(
        id_list,
        status=status,
        handled_by=user.id,
        resolution_note=resolution_note,
        priority=priority,
    )

    if success_ids:
        log_activity(
            actor=user,
            category="forum",
            action="reports_bulk_status_updated",
            status="success",
            message=f"Reports {success_ids} status -> {status}",
            route=request.path,
            method=request.method,
            target_type="forum_report",
            target_id=",".join(str(x) for x in success_ids),
            metadata={
                "before": {"status": "mixed"},
                "after": {"status": status, "count": len(success_ids)},
            },
        )
    return jsonify({"updated_ids": success_ids, "failed_items": failed_items}), route_status_codes.ok
