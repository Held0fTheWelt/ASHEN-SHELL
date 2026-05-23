"""Authenticated forum thread authoring routes."""

from app.api.v1.forum_route_context import *

# --- Authenticated community actions (threads, posts, likes, reports) ---------


@api_v1_bp.route("/forum/categories/<slug>/threads", methods=["POST"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_create(slug):
    """
    Create a new thread in a category.
    Body: title, content.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    cat = ForumCategory.query.filter_by(slug=slug).first()
    if not cat:
        return jsonify({"error": "Category not found"}), route_status_codes.not_found
    if not user_can_create_thread(user, cat):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request

    # Type check before stripping
    title_raw = data.get("title")
    content_raw = data.get("content")
    if title_raw is not None and not isinstance(title_raw, str):
        return jsonify({"error": "Title must be a string"}), route_status_codes.bad_request
    if content_raw is not None and not isinstance(content_raw, str):
        return jsonify({"error": "Content must be a string"}), route_status_codes.bad_request

    title = (title_raw or "").strip()
    content = (content_raw or "").strip()
    if not title or not content:
        return jsonify({"error": "title and content are required"}), route_status_codes.bad_request

    # Validate title length (5-500 characters)
    is_valid, error_msg = _validate_title_length(title, min_len=5, max_len=500)
    if not is_valid:
        return jsonify({"error": error_msg}), route_status_codes.bad_request

    # Validate content length (10-50000 characters)
    is_valid, error_msg = _validate_content_length(content, min_len=10, max_len=50000)
    if not is_valid:
        return jsonify({"error": error_msg}), route_status_codes.bad_request

    thread, post, err = create_thread(
        category=cat,
        author_id=user.id,
        title=title,
        content=content,
    )
    if err:
        return jsonify({"error": err}), route_status_codes.bad_request
    log_activity(
        actor=user,
        category="forum",
        action="thread_created",
        status="success",
        message=f"Thread created in category {cat.slug}: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
    )
    data = thread.to_dict()
    data["author_username"] = thread.author.username if thread.author else None
    if thread.category:
        data["category"] = thread.category.to_dict()
    return jsonify(data), route_status_codes.created


@api_v1_bp.route("/forum/threads/<int:thread_id>", methods=["PUT"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_update(thread_id: int):
    """
    Update thread title. Author or category moderators/admins only.
    Moderators can only update threads in their assigned categories.
    Body: title (optional).
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    if not thread.category:
        return jsonify({"error": "Thread has no category"}), route_status_codes.bad_request
    # Author can update their own thread
    if thread.author_id == user.id:
        pass
    # Moderators/admins must be assigned to the category
    elif not user_can_moderate_category(user, thread.category):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    title = data.get("title")
    if title is not None:
        # Type check before attempting to strip
        if not isinstance(title, str):
            return jsonify({"error": "Title must be a string"}), route_status_codes.bad_request
        title = title.strip()
        # Validate title length (5-500 characters)
        is_valid, error_msg = _validate_title_length(title, min_len=5, max_len=500)
        if not is_valid:
            return jsonify({"error": error_msg}), route_status_codes.bad_request
    thread = update_thread(thread, title=title)
    log_activity(
        actor=user,
        category="forum",
        action="thread_updated",
        status="success",
        message=f"Thread updated: {thread.id}",
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


@api_v1_bp.route("/forum/threads/<int:thread_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_delete(thread_id: int):
    """
    Soft-delete a thread. Author or category moderators/admins only.
    Moderators can only delete threads in their assigned categories.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    if not thread.category:
        return jsonify({"error": "Thread has no category"}), route_status_codes.bad_request
    # Author can delete their own thread
    if thread.author_id == user.id:
        pass
    # Moderators/admins must be assigned to the category
    elif not user_can_moderate_category(user, thread.category):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    thread = soft_delete_thread(thread)
    log_activity(
        actor=user,
        category="forum",
        action="thread_deleted",
        status="success",
        message=f"Thread soft-deleted: {thread.id}",
        route=request.path,
        method=request.method,
        target_type="forum_thread",
        target_id=str(thread.id),
    )
    return jsonify({"message": "Deleted"}), route_status_codes.ok
