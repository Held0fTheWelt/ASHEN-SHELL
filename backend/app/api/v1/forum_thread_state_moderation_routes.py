"""Forum thread state moderation routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_moderator_for_category, _require_moderator_or_admin

@api_v1_bp.route("/forum/threads/<int:thread_id>/lock", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_lock(thread_id: int):
    """Lock a thread (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_locked = thread.is_locked
    old_status = thread.status
    thread = set_thread_lock(thread, True)
    log_activity(
        actor=user,
        category="forum",
        action="thread_locked",
        status="success",
        message=f"Thread locked: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"is_locked": old_locked, "status": old_status}, "after": {"is_locked": True, "status": thread.status}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/unlock", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_unlock(thread_id: int):
    """Unlock a thread (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_locked = thread.is_locked
    old_status = thread.status
    thread = set_thread_lock(thread, False)
    log_activity(
        actor=user,
        category="forum",
        action="thread_unlocked",
        status="success",
        message=f"Thread unlocked: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"is_locked": old_locked, "status": old_status}, "after": {"is_locked": False, "status": thread.status}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/pin", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_pin(thread_id: int):
    """Pin a thread in its category (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_pinned = thread.is_pinned
    thread = set_thread_pinned(thread, True)
    log_activity(
        actor=user,
        category="forum",
        action="thread_pinned",
        status="success",
        message=f"Thread pinned: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"is_pinned": old_pinned}, "after": {"is_pinned": True}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/unpin", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_unpin(thread_id: int):
    """Unpin a thread in its category (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_pinned = thread.is_pinned
    thread = set_thread_pinned(thread, False)
    log_activity(
        actor=user,
        category="forum",
        action="thread_unpinned",
        status="success",
        message=f"Thread unpinned: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"is_pinned": old_pinned}, "after": {"is_pinned": False}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/feature", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_feature(thread_id: int):
    """Mark a thread as featured (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_featured = thread.is_featured
    thread = set_thread_featured(thread, True)
    log_activity(
        actor=user,
        category="forum",
        action="thread_featured",
        status="success",
        message=f"Thread featured: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"is_featured": old_featured}, "after": {"is_featured": True}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/unfeature", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_unfeature(thread_id: int):
    """Remove featured flag from a thread (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_featured = thread.is_featured
    thread = set_thread_featured(thread, False)
    log_activity(
        actor=user,
        category="forum",
        action="thread_unfeatured",
        status="success",
        message=f"Thread unfeatured: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"is_featured": old_featured}, "after": {"is_featured": False}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/move", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_move(thread_id: int):
    """Move a thread to another category (moderator/admin only). Body: category_id (int)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    try:
        category_id = int(data.get("category_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "category_id must be an integer"}), route_status_codes.bad_request
    new_cat = ForumCategory.query.get(category_id)
    if not new_cat:
        return jsonify({"error": "Category not found"}), route_status_codes.not_found
    if not user_can_moderate_category(user, new_cat):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    thread, err = move_thread(thread, new_cat)
    if err:
        return jsonify({"error": err}), route_status_codes.bad_request
    log_activity(
        actor=user,
        category="forum",
        action="thread_moved",
        status="success",
        message=f"Thread {thread.id} moved to category {new_cat.slug}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
    )
    data = thread.to_dict()
    data["author_username"] = thread.author.username if thread.author else None
    if thread.category:
        data["category"] = thread.category.to_dict()
    return jsonify(data), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/archive", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_archive(thread_id: int):
    """Archive a thread (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_status = thread.status
    thread = set_thread_archived(thread)
    log_activity(
        actor=user,
        category="forum",
        action="thread_archived",
        status="success",
        message=f"Thread archived: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"status": old_status}, "after": {"status": "archived"}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/unarchive", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_unarchive(thread_id: int):
    """Unarchive a thread (moderator/admin only)."""
    thread = get_thread_by_id(thread_id)
    if not thread or not thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(thread.category)
    if err_resp:
        return err_resp
    old_status = thread.status
    thread = set_thread_unarchived(thread)
    log_activity(
        actor=user,
        category="forum",
        action="thread_unarchived",
        status="success",
        message=f"Thread unarchived: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
        metadata={"before": {"status": old_status}, "after": {"status": thread.status}},
    )
    return jsonify(thread.to_dict()), route_status_codes.ok
