"""Forum moderation readout route registration facade."""

from app.api.v1.forum_tag_admin_routes import *
from app.api.v1.forum_subscriber_readout_routes import *
from app.api.v1.forum_moderation_report_readout_routes import *
from app.api.v1.forum_moderation_bulk_routes import *
from app.api.v1.forum_moderation_log_routes import *
from app.api.v1.forum_moderation_thread_readout_routes import *

__all__ = [name for name in globals() if not name.startswith("__")]
