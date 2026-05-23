"""Forum thread structure and post visibility moderation routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_moderator_for_category, _require_moderator_or_admin

@api_v1_bp.route("/forum/threads/<int:source_thread_id>/merge", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def forum_thread_merge(source_thread_id: int):
    """
    Merge a source thread into a target thread (moderator/admin only).

    Body: { "target_thread_id": <int> }
    """
    source = get_thread_by_id(source_thread_id)
    if not source or not source.category:
        return jsonify({"error": "Source thread not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(source.category)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    try:
        target_thread_id = int(data.get("target_thread_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "target_thread_id must be an integer"}), route_status_codes.bad_request

    target = get_thread_by_id(target_thread_id)
    if not target or not target.category:
        return jsonify({"error": "Target thread not found"}), route_status_codes.not_found

    # Ensure the user may moderate the target category as well.
    _, err_resp_target = _require_moderator_for_category(target.category)
    if err_resp_target:
        return err_resp_target

    err = merge_threads(source, target)
    if err:
        return jsonify({"error": err}), route_status_codes.bad_request

    log_activity(
        actor=user,
        category="forum",
        action="thread_merged",
        status="success",
        message=f"Thread {source.id} merged into {target.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(target.id),
    )
    data = target.to_dict()
    data["author_username"] = target.author.username if target.author else None
    if target.category:
        data["category"] = target.category.to_dict()
    return jsonify(data), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/split", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_split(thread_id: int):
    """
    Split a thread starting from a top-level post into a new thread (moderator/admin only).

    Safe, constrained behavior:
    - root_post_id must refer to a top-level post in the source thread (parent_post_id is null).
    - The root post and its direct replies (single-level replies) move into the new thread.
    - New thread title is required; category defaults to the source thread's category
      unless a target category_id is provided.
    """
    source_thread = get_thread_by_id(thread_id)
    if not source_thread or not source_thread.category:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found

    user, err_resp = _require_moderator_for_category(source_thread.category)
    if err_resp:
        return err_resp

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request

    try:
        root_post_id = int(data.get("root_post_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "root_post_id must be an integer"}), route_status_codes.bad_request

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), route_status_codes.bad_request

    category_id = data.get("category_id")
    target_category: Optional[ForumCategory] = None
    if category_id is not None:
        try:
            category_id_int = int(category_id)
        except (TypeError, ValueError):
            return jsonify({"error": "category_id must be an integer"}), route_status_codes.bad_request
        target_category = ForumCategory.query.get(category_id_int)
        if not target_category:
            return jsonify({"error": "Category not found"}), route_status_codes.not_found
        if not user_can_moderate_category(user, target_category):
            return jsonify({"error": "Forbidden"}), route_status_codes.forbidden

    root_post = get_post_by_id(root_post_id)
    if not root_post:
        return jsonify({"error": "Root post not found"}), route_status_codes.not_found

    new_thread, err = split_thread_from_post(
        source_thread=source_thread,
        root_post=root_post,
        new_title=title,
        new_category=target_category,
    )
    if err:
        return jsonify({"error": err}), route_status_codes.bad_request

    log_activity(
        actor=user,
        category="forum",
        action="thread_split",
        status="success",
        message=f"Thread {source_thread.id} split into new thread {new_thread.id} from post {root_post.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(new_thread.id),
    )
    resp_data = new_thread.to_dict()
    resp_data["author_username"] = new_thread.author.username if new_thread.author else None
    if new_thread.category:
        resp_data["category"] = new_thread.category.to_dict()
    return jsonify(resp_data), route_status_codes.created


@api_v1_bp.route("/forum/posts/<int:post_id>/hide", methods=["POST"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_post_hide(post_id: int):
    """Hide a post (moderator/admin only)."""
    post = get_post_by_id(post_id)
    if not post or not post.thread or not post.thread.category:
        return jsonify({"error": "Post not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(post.thread.category)
    if err_resp:
        return err_resp
    old_post_status = post.status
    post = hide_post(post)
    log_activity(
        actor=user,
        category="forum",
        action="post_hidden",
        status="success",
        message=f"Post hidden: {post.id}",
        route=request.path,
        method=request.method,
        target_type="forum_post",
        target_id=str(post.id),
        metadata={"before": {"status": old_post_status}, "after": {"status": "hidden"}},
    )
    return jsonify(post.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/posts/<int:post_id>/unhide", methods=["POST"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_post_unhide(post_id: int):
    """Unhide a post (moderator/admin only)."""
    post = get_post_by_id(post_id)
    if not post or not post.thread or not post.thread.category:
        return jsonify({"error": "Post not found"}), route_status_codes.not_found
    user, err_resp = _require_moderator_for_category(post.thread.category)
    if err_resp:
        return err_resp
    old_post_status = post.status
    post = unhide_post(post)
    log_activity(
        actor=user,
        category="forum",
        action="post_unhidden",
        status="success",
        message=f"Post unhidden: {post.id}",
        route=request.path,
        method=request.method,
        target_type="forum_post",
        target_id=str(post.id),
        metadata={"before": {"status": old_post_status}, "after": {"status": post.status}},
    )
    return jsonify(post.to_dict()), route_status_codes.ok
