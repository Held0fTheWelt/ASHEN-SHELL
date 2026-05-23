"""Community forum route registration facade."""

from app.api.v1.forum_public_routes import *
from app.api.v1.forum_thread_authoring_routes import *
from app.api.v1.forum_post_interaction_routes import *
from app.api.v1.forum_subscription_report_routes import *

__all__ = [name for name in globals() if not name.startswith("__")]
