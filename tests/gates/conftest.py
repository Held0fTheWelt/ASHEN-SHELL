"""Gate test path configuration.

Adds world-engine to sys.path so gate tests can import from both backend (app.*)
and world-engine (app.runtime.*, app.story_runtime.*).

World-engine's app package and backend's app package are distinct; only one
can be on sys.path as 'app' at a time. Gate tests that need world-engine imports
must use the world-engine path explicitly or call through the LDSS module.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORLD_ENGINE_DIR = REPO_ROOT / "world-engine"

# Only add world-engine if it's not already on the path
_world_engine_str = str(WORLD_ENGINE_DIR)
if WORLD_ENGINE_DIR.exists() and _world_engine_str not in sys.path:
    sys.path.insert(1, _world_engine_str)
