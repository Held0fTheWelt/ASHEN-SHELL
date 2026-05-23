"""Forum category administration routes."""

from app.api.v1.forum_route_context import *
from app.api.v1.forum_route_permissions import _require_admin

@api_v1_bp.route("/forum/admin/categories", methods=["POST"])
@limiter.limit("20 per minute")
@jwt_required()
def forum_admin_category_create():
    """
    Create a forum category (admin only).
    Body: slug, title, optional description, parent_id, sort_order, is_active, is_private, required_role.
    """
    user, err_resp = _require_admin()
    if err_resp:
        return err_resp
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request

    # Type check title before stripping
    title_raw = data.get("title")
    if title_raw is not None and not isinstance(title_raw, str):
        return jsonify({"error": "Title must be a string"}), route_status_codes.bad_request

    slug = (data.get("slug") or "").strip()
    title = (title_raw or "").strip()
    description = data.get("description")
    parent_id = data.get("parent_id")
    sort_order = data.get("sort_order", 0)
    is_active = bool(data.get("is_active", True))
    is_private = bool(data.get("is_private", False))
    required_role = data.get("required_role")
    parent_id_int: Optional[int] = None
    if parent_id is not None:
        try:
            parent_id_int = int(parent_id)
        except (TypeError, ValueError):
            return jsonify({"error": "parent_id must be an integer"}), route_status_codes.bad_request
    try:
        sort_order_int = int(sort_order)
    except (TypeError, ValueError):
        sort_order_int = 0

    # Validate category title length (5-200 characters)
    is_valid, error_msg = _validate_category_title_length(title, min_len=5, max_len=200)
    if not is_valid:
        return jsonify({"error": error_msg}), route_status_codes.bad_request

    cat, err = create_category(
        slug=slug,
        title=title,
        description=description,
        parent_id=parent_id_int,
        sort_order=sort_order_int,
        is_active=is_active,
        is_private=is_private,
        required_role=required_role,
    )
    if err:
        status = 409 if "already exists" in err.lower() else 400
        return jsonify({"error": err}), status
    log_activity(
        actor=user,
        category="forum",
        action="category_created",
        status="success",
        message=f"Forum category created: {cat.slug}",
        route=request.path,
        method=request.method,
        target_type="forum_category",
        target_id=str(cat.id),
    )
    return jsonify(cat.to_dict()), route_status_codes.created


@api_v1_bp.route("/forum/admin/categories/<int:category_id>", methods=["PUT"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_admin_category_update(category_id: int):
    """
    Update a forum category (admin only).
    Body: optional title, description, sort_order, is_active, is_private, required_role.
    """
    user, err_resp = _require_admin()
    if err_resp:
        return err_resp
    cat = ForumCategory.query.get(category_id)
    if not cat:
        return jsonify({"error": "Category not found"}), route_status_codes.not_found
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), route_status_codes.bad_request
    title = data.get("title")
    description = data.get("description")
    sort_order = data.get("sort_order")
    is_active = data.get("is_active")
    is_private = data.get("is_private")
    required_role = data.get("required_role")
    sort_order_int: Optional[int] = None
    if sort_order is not None:
        try:
            sort_order_int = int(sort_order)
        except (TypeError, ValueError):
            return jsonify({"error": "sort_order must be an integer"}), route_status_codes.bad_request

    # Validate category title length if provided (5-200 characters)
    if title is not None:
        # Type check first
        if not isinstance(title, str):
            return jsonify({"error": "Title must be a string"}), route_status_codes.bad_request
        title = title.strip()
        is_valid, error_msg = _validate_category_title_length(title, min_len=5, max_len=200)
        if not is_valid:
            return jsonify({"error": error_msg}), route_status_codes.bad_request

    cat = update_category(
        cat,
        title=title,
        description=description,
        sort_order=sort_order_int,
        is_active=bool(is_active) if is_active is not None else None,
        is_private=bool(is_private) if is_private is not None else None,
        required_role=required_role,
    )
    log_activity(
        actor=user,
        category="forum",
        action="category_updated",
        status="success",
        message=f"Forum category updated: {cat.slug}",
        route=request.path,
        method=request.method,
        target_type="forum_category",
        target_id=str(cat.id),
    )
    return jsonify(cat.to_dict()), route_status_codes.ok


@api_v1_bp.route("/forum/admin/categories/<int:category_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
@jwt_required()
def forum_admin_category_delete(category_id: int):
    """
    Delete a forum category (admin only). This will cascade to threads/posts per
    the database schema (ondelete rules).
    """
    user, err_resp = _require_admin()
    if err_resp:
        return err_resp
    cat = ForumCategory.query.get(category_id)
    if not cat:
        return jsonify({"error": "Category not found"}), route_status_codes.not_found
    delete_category(cat)
    log_activity(
        actor=user,
        category="forum",
        action="category_deleted",
        status="success",
        message=f"Forum category deleted: {cat.slug}",
        route=request.path,
        method=request.method,
        target_type="forum_category",
        target_id=str(category_id),
    )
    return jsonify({"message": "Deleted"}), route_status_codes.ok
