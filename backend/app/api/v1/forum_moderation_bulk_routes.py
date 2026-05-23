"""Forum moderation bulk action routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin, _require_moderator_or_admin

@api_v1_bp.route("/forum/moderation/bulk-threads/status", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def forum_moderation_bulk_threads_status():
    """
    Bulk lock/unlock/archive/unarchive threads.
    Body: { "thread_ids": [int, ...], "lock": true/false (optional), "archive": true/false (optional) }.
    Only moderators/admins with rights on the category may modify a thread.
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    ids = data.get("thread_ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "thread_ids must be a non-empty list"}), route_status_codes.bad_request
    try:
        thread_ids = [int(x) for x in ids]
    except (TypeError, ValueError):
        return jsonify({"error": "thread_ids must contain integers"}), route_status_codes.bad_request
    lock = data.get("lock")
    archive = data.get("archive")
    if lock is None and archive is None:
        return jsonify({"error": "At least one of lock or archive must be provided"}), route_status_codes.bad_request

    before_states: dict[int, dict] = {}
    updated: list[int] = []
    for tid in thread_ids:
        thread = get_thread_by_id(tid)
        if not thread or not thread.category:
            continue
        # Ensure user can moderate this category
        if not user_can_moderate_category(user, thread.category):
            continue
        before_states[thread.id] = {"is_locked": thread.is_locked, "status": thread.status}
        if lock is not None:
            thread = set_thread_lock(thread, bool(lock))
        if archive is not None:
            if archive:
                thread = set_thread_archived(thread)
            else:
                thread = set_thread_unarchived(thread)
        updated.append(thread.id)

    if updated:
        actions = []
        after_state = {}
        if lock is not None:
            actions.append(f"lock={bool(lock)}")
            after_state["is_locked"] = bool(lock)
        if archive is not None:
            actions.append(f"archive={bool(archive)}")
            after_state["status"] = "archived" if archive else "open"
        log_activity(
            actor=user,
            category="forum",
            action="threads_bulk_status_updated",
            status="success",
            message=f"Threads {updated} updated ({', '.join(actions)})",
            route=request.path,
            method=request.method,
            target_type="forum_thread",
            target_id=",".join(str(x) for x in updated),
            metadata={"before": {str(tid): before_states.get(tid, {}) for tid in updated}, "after": after_state},
        )
    return jsonify({"updated_ids": updated}), route_status_codes.ok


@api_v1_bp.route("/forum/moderation/bulk-posts/hide", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def forum_moderation_bulk_posts_hide():
    """
    Bulk hide/unhide posts.
    Body: { "post_ids": [int, ...], "hidden": true/false }.
    """
    user, err_resp = _require_moderator_or_admin()
    if err_resp:
        return err_resp
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    ids = data.get("post_ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "post_ids must be a non-empty list"}), route_status_codes.bad_request
    try:
        post_ids = [int(x) for x in ids]
    except (TypeError, ValueError):
        return jsonify({"error": "post_ids must contain integers"}), route_status_codes.bad_request
    hidden = data.get("hidden")
    if hidden is None:
        return jsonify({"error": "hidden must be provided"}), route_status_codes.bad_request

    before_states: dict[int, dict] = {}
    updated: list[int] = []
    for pid in post_ids:
        post = get_post_by_id(pid)
        if not post or not post.thread or not post.thread.category:
            continue
        if not user_can_moderate_category(user, post.thread.category):
            continue
        before_states[post.id] = {"status": post.status}
        if hidden:
            hide_post(post)
        else:
            unhide_post(post)
        updated.append(post.id)

    new_status = "hidden" if hidden else "visible"
    if updated:
        log_activity(
            actor=user,
            category="forum",
            action="posts_bulk_hidden" if hidden else "posts_bulk_unhidden",
            status="success",
            message=f"Posts {updated} {'hidden' if hidden else 'unhidden'}",
            route=request.path,
            method=request.method,
            target_type="forum_post",
            target_id=",".join(str(x) for x in updated),
            metadata={"before": {str(pid): before_states.get(pid, {}) for pid in updated}, "after": {"status": new_status}},
        )
    return jsonify({"updated_ids": updated, "hidden": bool(hidden)}), route_status_codes.ok
