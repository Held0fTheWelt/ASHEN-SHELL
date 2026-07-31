"""Game API routes — stable public namespace for Flask registration and test patches.

Wave 5: implementation lives in ``game_routes_impl.py``. This module identity is
bound to the impl so monkeypatches on ``app.api.v1.game_routes.*`` affect the
same globals the route functions close over (replacing the former exec-into-
namespace loader).
"""

from __future__ import annotations

import sys as _sys

from app.api.v1 import game_routes_impl as _impl

_sys.modules[__name__] = _impl
