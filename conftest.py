"""Repository-root pytest path hygiene for monorepo test execution."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

# world-engine ``app.config`` fails fast when ``PLAY_SERVICE_SECRET`` is unset unless
# ``FLASK_ENV`` is exactly ``test``. Suites such as ``ai_stack/tests`` import
# ``app.story_runtime`` without loading ``world-engine/tests/conftest.py``; align env here
# so those imports work in CI and ``python -m pytest`` from the repo root.
_flask_env = (os.getenv("FLASK_ENV") or "").strip().lower()
_play_secret = (
    os.getenv("PLAY_SERVICE_SECRET") or os.getenv("PLAY_SERVICE_SHARED_SECRET") or ""
).strip()
if _flask_env not in {"production", "staging"} and not _play_secret:
    os.environ["FLASK_ENV"] = "test"
    os.environ.setdefault("PLAY_SERVICE_SECRET", "test-secret-key-for-unit-tests")

REPO_ROOT = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, REPO_ROOT / "backend", REPO_ROOT / "'fy'-suites"):
    text = str(candidate)
    if candidate.exists() and text not in sys.path:
        sys.path.insert(0, text)


def _available(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


_BACKEND_RUNTIME_READY = _available("flask") and _available("sqlalchemy")
pytest_plugins = ["backend.tests.conftest"] if _BACKEND_RUNTIME_READY else []
