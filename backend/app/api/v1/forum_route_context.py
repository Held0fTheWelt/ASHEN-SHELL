"""Shared imports and dependencies for forum route modules."""
from datetime import datetime
from typing import Optional

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.v1 import api_v1_bp
from app.api.v1.forum_routes_helpers import (
    _current_user_optional,
    _parse_int,
    _require_user,
    _validate_category_title_length,
    _validate_content_length,
    _validate_title_length,
)
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
    ForumTag,
)
from app.services import log_activity
from app.services.activity.activity_log_service import list_activity_logs
from app.services.content.forum_service import (
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
    bookmark_thread,
    unbookmark_thread,
    list_bookmarked_threads,
    set_thread_tags,
    list_tags_for_thread,
)
from app.config.route_constants import route_status_codes, route_pagination_config

__all__ = [name for name in globals() if not name.startswith("__")]
