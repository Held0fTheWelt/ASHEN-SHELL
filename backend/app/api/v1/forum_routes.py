"""Forum API route registration facade."""

import sys
import types

from app.api.v1 import (
    forum_category_admin_routes as _category_admin_routes,
    forum_community_routes as _community_routes,
    forum_moderation_bulk_routes as _moderation_bulk_routes,
    forum_moderation_log_routes as _moderation_log_routes,
    forum_moderation_report_readout_routes as _moderation_report_readout_routes,
    forum_moderation_thread_readout_routes as _moderation_thread_readout_routes,
    forum_moderation_readout_routes as _readout_routes,
    forum_moderation_routes as _moderation_routes,
    forum_post_interaction_routes as _post_interaction_routes,
    forum_public_routes as _public_routes,
    forum_report_queue_routes as _report_queue_routes,
    forum_report_status_routes as _report_status_routes,
    forum_route_context as _route_context,
    forum_route_permissions as _route_permissions,
    forum_subscriber_readout_routes as _subscriber_readout_routes,
    forum_subscription_report_routes as _subscription_report_routes,
    forum_tag_admin_routes as _tag_admin_routes,
    forum_thread_authoring_routes as _thread_authoring_routes,
    forum_thread_state_moderation_routes as _thread_state_moderation_routes,
    forum_thread_structure_moderation_routes as _thread_structure_moderation_routes,
)
from app.api.v1.forum_routes_helpers import (
    _parse_int,
    _validate_category_title_length,
    _validate_content_length,
    _validate_title_length,
)
from app.api.v1.forum_moderation_report_readout_routes import _enrich_report_dict
from app.api.v1.forum_community_routes import *
from app.api.v1.forum_moderation_routes import *
from app.api.v1.forum_moderation_readout_routes import *
from app.api.v1.forum_route_permissions import (
    _require_admin,
    _require_moderator_for_category,
    _require_moderator_or_admin,
)

_SPLIT_ROUTE_MODULES = (
    _route_context,
    _route_permissions,
    _community_routes,
    _moderation_routes,
    _readout_routes,
    _public_routes,
    _thread_authoring_routes,
    _post_interaction_routes,
    _subscription_report_routes,
    _thread_state_moderation_routes,
    _thread_structure_moderation_routes,
    _report_status_routes,
    _report_queue_routes,
    _category_admin_routes,
    _tag_admin_routes,
    _subscriber_readout_routes,
    _moderation_report_readout_routes,
    _moderation_bulk_routes,
    _moderation_log_routes,
    _moderation_thread_readout_routes,
)


class _ForumRoutesFacade(types.ModuleType):
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        for module in _SPLIT_ROUTE_MODULES:
            if hasattr(module, name):
                setattr(module, name, value)


sys.modules[__name__].__class__ = _ForumRoutesFacade

__all__ = [name for name in globals() if not name.startswith("__")]
