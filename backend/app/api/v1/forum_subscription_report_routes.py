"""Forum subscription and report creation routes."""

from app.api.v1.forum_route_context import *

@api_v1_bp.route("/forum/threads/<int:thread_id>/subscribe", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_subscribe(thread_id: int):
    """
    Subscribe to a thread (for future notifications).
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread or not user_can_view_thread(user, thread):
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    sub = subscribe_thread(user, thread)
    return jsonify({"message": "Subscribed", "subscription_id": sub.id}), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/subscribe", methods=["DELETE"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_unsubscribe(thread_id: int):
    """
    Unsubscribe from a thread.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    unsubscribe_thread(user, thread)
    return jsonify({"message": "Unsubscribed"}), route_status_codes.ok


@api_v1_bp.route("/forum/reports", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def forum_report_create():
    """
    Create a report on a thread or post.
    Body: target_type ('thread' or 'post'), target_id, reason.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    target_type = (data.get("target_type") or "").strip()
    try:
        target_id = int(data.get("target_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "target_id must be an integer"}), route_status_codes.bad_request
    reason = data.get("reason")
    if target_type == "thread":
        target = get_thread_by_id(target_id)
        if not target or not user_can_view_thread(user, target):
            return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    elif target_type == "post":
        target = get_post_by_id(target_id)
        if not target or not user_can_view_post(user, target):
            return jsonify({"error": "Post not found"}), route_status_codes.not_found
    else:
        return jsonify({"error": "Invalid target_type"}), route_status_codes.bad_request

    report, err = create_report(
        target_type=target_type,
        target_id=target_id,
        reported_by=user.id,
        reason=reason,
    )
    if err:
        return jsonify({"error": err}), route_status_codes.bad_request
    log_activity(
        actor=user,
        category="forum",
        action="report_created",
        status="success",
        message=f"Report created: {report.id}",
        route=request.path,
        method=request.method,
        target_type="forum_report",
        target_id=str(report.id),
    )
    return jsonify(report.to_dict()), route_status_codes.created
