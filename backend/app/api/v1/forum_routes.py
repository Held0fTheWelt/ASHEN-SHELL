"""Forum API: categories, threads, posts, likes, reports.

Public/community endpoints are read-only and allow anonymous access where safe.
Authenticated endpoints require JWT; moderation/admin flows are role-restricted.
"""
from datetime import datetime
from typing import Optional
import re

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.v1 import api_v1_bp
from app.utils.error_handler import log_full_error, ERROR_MESSAGES
from app.auth.permissions import (
    current_user_is_admin,
    current_user_is_moderator,
    current_user_is_moderator_or_admin,
    get_current_user,
)
from app.extensions import limiter, db
from app.models import (
    ForumCategory,
    ForumPostLike,
    ForumThread,
    ForumPost,
    ForumReport,
    ForumThreadSubscription,
    Notification,
    ForumTag,
)
from app.services import log_activity
from app.services.activity_log_service import list_activity_logs
from app.services.search_utils import _escape_sql_like_wildcards
from app.services.forum_service import (
    assign_report_to_moderator,
    bulk_update_report_status,
    create_category,
    create_notifications_for_thread_reply,
    create_post,
    create_report,
    create_thread,
    delete_category,
    delete_tag,
    get_category_by_slug_for_user,
    get_post_by_id,
    get_report_by_id,
    get_thread_by_id,
    get_thread_by_slug,
    hide_post,
    hide_thread,
    increment_thread_view,
    like_post,
    list_all_tags,
    list_categories_for_user,
    list_escalation_queue,
    list_handled_reports,
    list_moderator_assigned_reports,
    list_posts_for_thread,
    list_reports,
    list_reports_for_target,
    list_review_queue,
    list_threads_for_category,
    list_tags_for_threads,
    bookmarked_thread_ids_for_user,
    merge_threads,
    move_thread,
    recalc_thread_counters,
    set_thread_archived,
    set_thread_featured,
    set_thread_lock,
    set_thread_pinned,
    set_thread_unarchived,
    soft_delete_post,
    soft_delete_thread,
    split_thread_from_post,
    subscribe_thread,
    batch_tag_thread_counts,
    unsubscribe_thread,
    unhide_post,
    unlike_post,
    update_category,
    update_post,
    update_report_status,
    update_thread,
    user_can_create_thread,
    user_can_edit_post,
    user_can_like_post,
    user_can_manage_categories,
    user_can_moderate_category,
    user_can_post_in_thread,
    user_can_soft_delete_post,
    user_can_view_post,
    user_can_view_thread,
    user_is_moderator,
    _utc_now,
    bookmark_thread,
    unbookmark_thread,
    list_bookmarked_threads,
    set_thread_tags,
    list_tags_for_thread,
)


def _parse_int(value, default, min_val=None, max_val=None):
    if value is None:
        return default
    try:
        n = int(value)
        if min_val is not None and n < min_val:
            return default
        if max_val is not None and n > max_val:
            return max_val
        return n
    except (TypeError, ValueError):
        return default


def _current_user_optional():
    """Return current user object or None (for optional JWT endpoints)."""
    try:
        return get_current_user()
    except Exception:
        return None


def _validate_content_length(content, min_len=10, max_len=50000):
    """
    Validate content length. Returns (is_valid, error_message).
    Enforces strict type checking to prevent bypass via non-string inputs.
    """
    # Type check first: must be a string
    if not isinstance(content, str):
        return False, "Content must be a string"

    # Strip and check length
    trimmed = content.strip()
    if len(trimmed) < min_len:
        return False, f"Content must be at least {min_len} characters"
    if len(trimmed) > max_len:
        return False, f"Content must not exceed {max_len} characters"
    return True, None


def _validate_title_length(title, min_len=5, max_len=500):
    """
    Validate title length. Returns (is_valid, error_message).
    Enforces strict type checking to prevent bypass via non-string inputs.
    """
    # Type check first: must be a string
    if not isinstance(title, str):
        return False, "Title must be a string"

    # Strip and check length
    trimmed = title.strip()
    if len(trimmed) < min_len:
        return False, f"Title must be at least {min_len} characters"
    if len(trimmed) > max_len:
        return False, f"Title must not exceed {max_len} characters"
    return True, None


def _validate_category_title_length(title, min_len=5, max_len=200):
    """
    Validate category title length. Returns (is_valid, error_message).
    Enforces strict type checking to prevent bypass via non-string inputs.
    """
    # Type check first: must be a string
    if not isinstance(title, str):
        return False, "Title must be a string"

    # Strip and check length
    trimmed = title.strip()
    if len(trimmed) < min_len:
        return False, f"Title must be at least {min_len} characters"
    if len(trimmed) > max_len:
        return False, f"Title must not exceed {max_len} characters"
    return True, None


def _sanitize_slug(slug):
    """Sanitize the slug to prevent path traversal."""
    # Allow only alphanumeric characters and hyphens
    if re.match(r'^[a-zA-Z0-9-]+$', slug):
        return slug
    return None


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
    return jsonify({"items": [c.to_dict() for c in cats], "total": len(cats)}), 200


@api_v1_bp.route("/forum/categories/<slug>", methods=["GET"])
@limiter.limit("60 per minute")
@jwt_required(optional=True)
def forum_category_detail(slug):
    """
    Get one category by slug if the current user may access it.
    Response: category.to_dict() plus basic thread counts.
    """
    sanitized_slug = _sanitize_slug(slug)
    if not sanitized_slug:
        return jsonify({"error": "Invalid category slug"}), 400

    user = _current_user_optional()
    cat = get_category_by_slug_for_user(user, sanitized_slug)
    if not cat:
        return jsonify({"error": "Category not found"}), 404
    # Basic stats: non-deleted threads count
    total_threads = (
        ForumThread.query.filter_by(category_id=