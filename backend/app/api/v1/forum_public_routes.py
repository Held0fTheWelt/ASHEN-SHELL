"""Public forum browsing and search routes."""

from app.api.v1.forum_route_context import *

# --- Public / community -------------------------------------------------------


@api_v1_bp.route("/forum/categories", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def forum_categories_list():
    """
    List visible forum categories for the current user (or anonymous).
    Response: { items: [ForumCategory], total } with to_dict() payloads.
    """
    user = _current_user_optional()
    cats = list_categories_for_user(user)
    return jsonify({"items": [c.to_dict() for c in cats], "total": len(cats)}), route_status_codes.ok


@api_v1_bp.route("/forum/categories/<slug>", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def forum_category_detail(slug):
    """
    Get one category by slug if the current user may access it.
    Response: category.to_dict() plus basic thread counts.
    """
    user = _current_user_optional()
    cat = get_category_by_slug_for_user(user, slug)
    if not cat:
        return jsonify({"error": "Category not found"}), route_status_codes.not_found
    # Basic stats: non-deleted threads count
    total_threads = (
        ForumThread.query.filter_by(category_id=cat.id)
        .filter(ForumThread.status != "deleted")
        .count()
    )
    data = cat.to_dict()
    data["thread_count"] = total_threads
    return jsonify(data), route_status_codes.ok


@api_v1_bp.route("/forum/categories/<slug>/threads", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def forum_category_threads(slug):
    """
    List threads in a category (paginated). Anonymous users only see public
    categories; private/staff categories require appropriate role.

    Query: page, limit.
    """
    user = _current_user_optional()
    cat = get_category_by_slug_for_user(user, slug)
    if not cat:
        return jsonify({"error": "Category not found"}), route_status_codes.not_found

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)

    # Moderators/admins see all statuses (hidden, archived); others get SQL-level filter.
    is_mod = user is not None and (current_user_is_moderator() or current_user_is_admin())
    page_items, total = list_threads_for_category(
        cat, page=page, per_page=limit, include_hidden=is_mod,
    )

    # Batch-load tags and bookmarks for the page items
    thread_ids = [t.id for t in page_items]
    tags_map = list_tags_for_threads(thread_ids)
    user_id = user.id if user else None
    bookmarked_ids = bookmarked_thread_ids_for_user(user_id, thread_ids)

    items_data = []
    for t in page_items:
        d = t.to_dict()
        d["author_username"] = t.author.username if t.author else None
        d["bookmarked_by_me"] = t.id in bookmarked_ids
        d["tags"] = tags_map.get(t.id, [])
        items_data.append(d)
    return jsonify(
        {
            "items": items_data,
            "total": total,
            "page": page,
            "per_page": limit,
        }
    ), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<slug>", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def forum_thread_detail(slug):
    """
    Get one thread by slug if visible to current user.
    Response: thread.to_dict() plus category basic info.
    """
    user = _current_user_optional()
    thread = get_thread_by_slug(slug)
    if not thread or not user_can_view_thread(user, thread):
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found
    user_id = user.id if user else None
    increment_thread_view(thread, user_id=user_id)
    data = thread.to_dict()
    data["author_username"] = thread.author.username if thread.author else None
    if thread.category:
        data["category"] = thread.category.to_dict()
    sub = None
    if user and user.id:
        sub = ForumThreadSubscription.query.filter_by(thread_id=thread.id, user_id=user.id).first()
        data["subscribed_by_me"] = sub is not None
    else:
        data["subscribed_by_me"] = False
    # Attach tags for community comfort layer
    tags = list_tags_for_thread(thread)
    if tags:
        data["tags"] = [{"slug": t.slug, "label": t.label} for t in tags]
    return jsonify(data), route_status_codes.ok


@api_v1_bp.route("/forum/threads/<int:thread_id>/posts", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def forum_thread_posts(thread_id: int):
    """
    List posts in a thread (paginated).
    Anonymous users see only visible posts in visible threads.
    Moderators/admins may include hidden/deleted via query flags.

    Query: page, limit, include_hidden (moderator+), include_deleted (moderator+).
    """
    user = _current_user_optional()
    thread = get_thread_by_id(thread_id)
    if not thread or not user_can_view_thread(user, thread):
        return jsonify({"error": "Thread not found"}), route_status_codes.not_found

    page = _parse_int(request.args.get("page"), 1, min_val=1)
    limit = _parse_int(request.args.get("limit"), 20, min_val=1, max_val=route_pagination_config.page_size_large)
    include_hidden = False
    include_deleted = False
    if user and (current_user_is_moderator() or current_user_is_admin()):
        include_hidden = (request.args.get("include_hidden", "").lower() in ("1", "true", "yes"))
        include_deleted = (request.args.get("include_deleted", "").lower() in ("1", "true", "yes"))
    items, total = list_posts_for_thread(
        thread,
        page=page,
        per_page=limit,
        include_hidden=include_hidden,
        include_deleted=include_deleted,
    )
    current_user_id = user.id if user else None
    post_list = []
    for p in items:
        d = p.to_dict()
        d["author_username"] = p.author.username if p.author else None
        d["liked_by_me"] = (
            bool(ForumPostLike.query.filter_by(post_id=p.id, user_id=current_user_id).first())
            if current_user_id else False
        )
        post_list.append(d)
    return jsonify(
        {
            "items": post_list,
            "total": total,
            "page": page,
            "per_page": limit,
        }
    ), route_status_codes.ok


@api_v1_bp.route("/forum/search", methods=["GET"])
@limiter.limit("30 per minute")
@jwt_required(optional=True)
def forum_search():
    """
    Search over thread titles and optionally post content with filters.

    Query parameters:
      - q: search query string (0-500 chars). Will be normalized and escaped.
      - page: page number (default 1, min 1, max 10000)
      - limit: results per page (default 20, min 1, max 100)
      - category: filter by category slug
      - status: filter by status (open, locked, archived, hidden)
      - tag: filter by tag slug
      - include_content: if 1/true/yes and q is 3+ chars, search post content too

    Validation:
      - Empty queries with no other filters return empty array (no unbounded scans)
      - Very short queries (1-2 chars) are rejected
      - Queries are truncated to 500 chars max
      - SQL LIKE wildcards are escaped for safety
      - Filter values are validated against known enums

    Ordering: pinned first, then by last_post_at desc, then by id asc

    Response: {items: [], total: int, page: int, per_page: int}
    """
    from app.api.v1.forum_thread_search_handler import run_forum_thread_search

    return run_forum_thread_search()
