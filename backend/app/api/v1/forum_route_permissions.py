"""Permission helpers for forum route modules."""

from app.api.v1.forum_route_context import *

def _require_moderator_for_category(cat: ForumCategory):
    user = get_current_user()
    if not user:
        return None, (jsonify({"error": "Authorization required"}), route_status_codes.unauthorized)
    if not user_can_moderate_category(user, cat):
        return None, (jsonify({"error": "Forbidden"}), route_status_codes.forbidden)
    return user, None


def _require_admin():
    user = get_current_user()
    if not user or not current_user_is_admin():
        return None, (jsonify({"error": "Forbidden"}), route_status_codes.forbidden)
    return user, None


def _require_moderator_or_admin():
    user = get_current_user()
    if not user or not current_user_is_moderator_or_admin():
        return None, (jsonify({"error": "Forbidden"}), route_status_codes.forbidden)
    return user, None
