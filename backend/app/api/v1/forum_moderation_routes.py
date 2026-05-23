"""Forum moderation route registration facade."""

from app.api.v1.forum_thread_state_moderation_routes import *
from app.api.v1.forum_thread_structure_moderation_routes import *
from app.api.v1.forum_report_status_routes import *
from app.api.v1.forum_report_queue_routes import *
from app.api.v1.forum_category_admin_routes import *

__all__ = [name for name in globals() if not name.startswith("__")]
