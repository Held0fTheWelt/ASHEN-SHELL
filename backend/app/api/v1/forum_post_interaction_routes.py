"""Forum post, bookmark, tag, and like interaction routes."""

from app.api.v1.forum_route_context import *

@api_v1_bp.route("/forum/threads/<int:thread_id>/posts", methods=["POST"])
@limiter.limit("10 per minute")
@jwt_required()
def forum_post_create(thread_id: int):
    """
    Create a post in a thread.
    Body: content, optional parent_post_id.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    if not user_can_post_in_thread(user, thread):
        return jsonify({"error": "Forbidden. Thread is locked or not accessible."}), route_status_codes.forbidden

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request

    # Type check before stripping
    content_raw = data.get("content")
    if content_raw is not None and not isinstance(content_raw, str):
        return jsonify({"error": "Content must be a string"}), route_status_codes.bad_request

    content = (content_raw or "").strip()
    parent_post_id = data.get("parent_post_id")
    parent_id_int: Optional[int] = None
    if parent_post_id is not None:
        try:
            parent_id_int = int(parent_post_id)
        except (TypeError, ValueError):
            return jsonify({"error": "parent_post_id must be an integer"}), route_status_codes.bad_request

    # Validate content length (10-50000 characters)
    is_valid, error_msg = _validate_content_length(content, min_len=10, max_len=50000)
    if not is_valid:
        return jsonify({"error": error_msg}), route_status_codes.bad_request

    post, err = create_post(
        thread=thread,
        author_id=user.id,
        content=content,
        parent_post_id=parent_id_int,
    )
    if err:
        return jsonify({"error": err}), route_status_codes.bad_request
    create_notifications_for_thread_reply(thread, post, user.id)
    log_activity(
        actor=user,
        category="forum",
        action="post_created",
        status="success",
        message=f"Post created in thread {thread.id}: {post.id}",
        route=request.path,
        method=request.method,
        target_type="forum_post",
        target_id=str(post.id),
    )
    return jsonify(post.to_dict()), route_status_codes.created


@api_v1_bp.route("/forum/threads/<int:thread_id>/bookmark", methods=["POST"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_thread_bookmark(thread_id: int):
    """
    Bookmark a thread for the current user.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread or not user_can_view_thread(user, thread):
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    bookmark_thread(user, thread)
    return jsonify({"message": "Bookmarked"}), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/bookmark", methods=["DELETE"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_thread_unbookmark(thread_id: int):
    """
    Remove bookmark for a thread for the current user.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    unbookmark_thread(user, thread)
    return jsonify({"message": "Unbookmarked"}), route_status_codes.ok


@api_v1_bp.route("/forum/bookmarks", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_bookmarks_list():
    """
    List bookmarked threads for the current user.

    Query: page, limit.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)
    threads, total = list_bookmarked_threads(user, page=page, per_page=limit)
    items = []
    for t in threads:
        d = t.to_dict()
        d["author_username"] = t.author.username if t.author else None
        if t.category:
            d["category"] = t.category.to_dict()
        tags = list_tags_for_thread(t)
        if tags:
            d["tags"] = [{"slug": tag.slug, "label": tag.label} for tag in tags]
        items.append(d)
    return jsonify({"items": items, "total": total, "page": page, "per_page": limit}), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/tags", methods=["PUT"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_thread_set_tags(thread_id: int):
    """
    Set tags for a thread. Moderator/admin or thread author only.
    Body: { "tags": ["tag1", "tag2", ...] }
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    thread = get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    if not (thread.author_id == user.id or current_user_is_moderator() or current_user_is_admin()):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    raw_tags = data.get("tags") or []
    if not isinstance(raw_tags, list):
        return jsonify({"error": "tags must be a list of strings"}), route_status_codes.bad_request
    tags = [str(t) for t in raw_tags if isinstance(t, (str, bytes))]
    tag_rows = set_thread_tags(thread, tags=tags)
    out = [{"slug": t.slug, "label": t.label} for t in tag_rows]
    return jsonify({"tags": out}), route_status_codes.ok


@api_v1_bp.route("/forum/posts/<int:post_id>", methods=["PUT"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_post_update(post_id: int):
    """
    Update a post's content. Author or category moderators/admins only.
    Moderators can only edit posts in their assigned categories.
    Body: content.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    post = get_post_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), route_status_codes.not_found
    if not user_can_edit_post(user, post):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    content = data.get("content")
    if content is None:
        return jsonify({"error": "content is required"}), route_status_codes.bad_request

    # Type check before validation
    if not isinstance(content, str):
        return jsonify({"error": "Content must be a string"}), route_status_codes.bad_request

    # Validate content length (10-50000 characters)
    is_valid, error_msg = _validate_content_length(content, min_len=10, max_len=50000)
    if not is_valid:
        return jsonify({"error": error_msg}), route_status_codes.bad_request

    post = update_post(post, content=content, editor_id=user.id)
    log_activity(
        actor=user,
        category="forum",
        action="post_updated",
        status="success",
        message=f"Post updated: {post.id}",
        route=request.path,
        method=request.method,
        target_type="forum_post",
        target_id=str(post.id),
    )
    return jsonify(post.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/posts/<int:post_id>", methods=["DELETE"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_post_delete(post_id: int):
    """
    Soft-delete a post. Author or moderators/admins only.
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    post = get_post_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), route_status_codes.not_found
    if not user_can_soft_delete_post(user, post):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    post = soft_delete_post(post)
    log_activity(
        actor=user,
        category="forum",
        action="post_deleted",
        status="success",
        message=f"Post soft-deleted: {post.id}",
        route=request.path,
        method=request.method,
        target_type="forum_post",
        target_id=str(post.id),
    )
    return jsonify({"message": "Deleted"}), route_status_codes.ok


@api_v1_bp.route("/forum/posts/<int:post_id>/like", methods=["POST"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_post_like(post_id: int):
    """
    Like a post. Duplicate likes are ignored (idempotent - returns 200 for already-liked posts).
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    post = get_post_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), route_status_codes.not_found
    if not user_can_like_post(user, post):
        return jsonify({"error": "Forbidden"}), route_status_codes.forbidden
    like, err = like_post(user, post)
    if err:
        # Duplicate like - return 200 for idempotency (user already liked this post)
        return jsonify({"message": "Already liked", "like_count": post.like_count, "liked_by_me": True}), route_status_codes.ok
    return jsonify({"message": "Liked", "like_count": post.like_count, "liked_by_me": True}), route_status_codes.ok


@api_v1_bp.route("/forum/posts/<int:post_id>/like", methods=["DELETE"])
@limiter.limit("60 per minute")
@jwt_required()
def forum_post_unlike(post_id: int):
    """
    Remove like from a post (idempotent).
    """
    user, err_resp = _require_user()
    if err_resp:
        return err_resp
    post = get_post_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), route_status_codes.not_found
    unlike_post(user, post)
    return jsonify({"message": "Unliked", "like_count": post.like_count, "liked_by_me": False}), route_status_codes.ok
