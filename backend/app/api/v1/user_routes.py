"""User CRUD API: list (admin), get (admin or self), update (admin or self), delete (admin)."""
import logging
import re
from datetime import datetime

from flask import jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.v1 import api_v1_bp
from app.auth.feature_registry import FEATURE_MANAGE_USERS, user_can_access_feature
from app.auth.permissions import (
    admin_may_assign_role_level,
    admin_may_edit_target,
    current_user_is_admin,
    current_user_is_super_admin,
    get_current_user,
    require_jwt_admin,
)
from app.auth.admin_security import admin_security, admin_security_sensitive
from app.extensions import limiter, db
from app.services import log_activity
from app.services.user_service import (
    assign_role as assign_role_service,
    ban_user as ban_user_service,
    change_password as change_password_service,
    get_user_by_id,
    list_users,
    unban_user as unban_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service,
    count_user_threads,
    count_user_posts,
    count_user_bookmarks,
    get_user_recent_threads,
    get_user_recent_posts,
    get_user_bookmarks,
    get_user_tags,
    validate_password_complexity,
    validate_email_format,
    USERNAME_MAX_LENGTH,
)

logger = logging.getLogger(__name__)

# Role level bounds (0-9999)
ROLE_LEVEL_MIN = 0
ROLE_LEVEL_MAX = 9999


def _validate_role_level_bounds(level: int) -> tuple[bool, str | None]:
    """
    Validate that role_level is within bounds [0, 9999].
    Returns (is_valid, error_message) tuple.
    """
    if level < ROLE_LEVEL_MIN or level > ROLE_LEVEL_MAX:
        return False, f"role_level must be between {ROLE_LEVEL_MIN} and {ROLE_LEVEL_MAX}"
    return True, None


def _log_privilege_change(admin_id: int, user_id: int, old_role: str, new_role: str, old_level: int = None, new_level: int = None, reason: str = None):
    """
    Log a privilege/role change with security alerts for SuperAdmin grants.
    Logs to both application logger and activity log.
    """
    from app.models.user import SUPERADMIN_THRESHOLD

    # Check if admin_id is valid and has necessary permissions
    current_admin = get_user_by_id(admin_id)
    if not current_admin or not current_user_is_admin(current_admin):
        raise PermissionError("Invalid or unauthorized admin_id")

    admin_name = f"{current_admin.username}(id={admin_id})"
    user_name = f"user_id={user_id}"
    target_user = get_user_by_id(user_id) if user_id else None
    if target_user:
        user_name = f"{target_user.username}(id={user_id})"

    # Build log message
    changes = []
    if old_role != new_role:
        changes.append(f"role {old_role} -> {new_role}")
    if old_level is not None and new_level is not None and old_level != new_level:
        changes.append(f"role_level {old_level} -> {new_level}")

    change_desc = ", ".join(changes) if changes else "privilege level"
    base_msg = f"Privilege change: {admin_name} modified {user_name}: {change_desc}"

    # Log to application logger with structured data
    current_app.logger.warning(
        base_msg,
        extra={
            "event_type": "privilege_change",
            "event": "privilege_change",
            "admin_id": admin_id,
            "admin_username": current_admin.username,
            "user_id": user_id,
            "user_username": target_user.username if target_user else None,
            "old_role": old_role,
            "new_role": new_role,
            "old_role_level": old_level,
            "new_role_level": new_level,
            "reason": reason,
        }
    )

    # Security alert: SuperAdmin grant
    if new_role == "admin" and new_level is not None and new_level >= SUPERADMIN_THRESHOLD:
        alert_msg = f"SECURITY ALERT: SuperAdmin privilege granted by {admin_name} to {user_name}"
        current_app.logger.critical(
            alert_msg,
            extra={
                "event_type": "superadmin_grant",
                "event": "superadmin_grant",
                "admin_id": admin_id,
                "admin_username": current_admin.username,
                "user_id": user_id,
                "user_username": target_user.username if target_user else None,
                "new_role": new_role,
                "new_role_level": new_level,
                "reason": reason,
            }
        )

    # Also log to activity log for admin dashboard
    metadata = {
        "old_role": old_role,
        "new_role": new_role,
    }
    if old_level is not None:
        metadata["old_role_level"] = old_level
    if new_level is not None:
        metadata["new_role_level"] = new_level
    if reason:
        metadata["reason"] = reason

    severity = "critical" if (new_role == "admin" and new_level is not None and new_level >= SUPERADMIN_THRESHOLD) else "warning"

    log_activity(
        actor=current_admin,
        category="privilege_change",
        action="role_level_modified",
        status=severity,
        message=base_msg,
        route=request.path if request else None,
        method=request.method if request else None,
        target_type="user",
        target_id=str(user_id),
        metadata=metadata,
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


def _validate_username(username: str) -> tuple[bool, str | None]:
    """
    Validate username field.
    - 3-32 characters (for user-facing display, stricter than internal 2-80)
    - alphanumeric, underscore, hyphen
    Returns (is_valid, error_message)
    """
    if not isinstance(username, str):
        return False, "Username must be a string"

    username = username.strip()
    if not username:
        return False, "Username cannot be empty"

    if len(username) < 3:
        return False, "Username must be at least 3 characters"

    if len(username) > 32:
        return False, "Username must be at most 32 characters"

    # Allow alphanumeric, underscore, hyphen
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"

    return True, None


def _validate_email(email: str) -> tuple[bool, str | None]:
    """
    Validate email field using RFC