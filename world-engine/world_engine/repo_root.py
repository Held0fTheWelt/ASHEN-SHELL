"""Resolve World of Shadows repository root for RAG and packaged content paths.

The play-service Docker image uses ``WORKDIR /app`` with ``./app`` as the FastAPI package
(``/app/app/...``). Naive ``Path(__file__).parents[N]`` often lands on ``/``, producing
``/.wos`` and an empty retrieval corpus. Prefer ``WOS_REPO_ROOT``, then walk ancestors for
a full monorepo checkout (``backend/app``) or a world-engine container root (``app/main.py``
+ ``app/story_runtime`` under ``/app``).
"""

from __future__ import annotations

import os
from pathlib import Path


def _is_filesystem_root(p: Path) -> bool:
    r = p.resolve()
    return r.parent == r


def _is_full_monorepo_root(candidate: Path) -> bool:
    """True if ``candidate`` is the repo root containing ``backend/app``."""
    if not candidate.is_dir() or _is_filesystem_root(candidate):
        return False
    return (candidate / "backend" / "app").is_dir()


def _is_world_engine_container_root(candidate: Path) -> bool:
    """True for slim play-service image: ``<root>/app/main.py`` and ``app/story_runtime``."""
    if not candidate.is_dir() or _is_filesystem_root(candidate):
        return False
    if (candidate / "backend" / "app").is_dir():
        return False
    app_pkg = candidate / "app"
    if not (app_pkg / "main.py").is_file():
        return False
    return (app_pkg / "story_runtime").is_dir()


def resolve_wos_repo_root(*, start: Path | None = None) -> Path:
    """Resolve checkout or container root for RAG ``.wos`` and ``content/`` layout."""
    env = (os.environ.get("WOS_REPO_ROOT") or "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if _is_full_monorepo_root(p) or _is_world_engine_container_root(p):
            return p

    base = (start if start is not None else Path(__file__).resolve().parent).resolve()
    full_hit: Path | None = None
    slim_hit: Path | None = None
    cur = base
    for _ in range(32):
        if _is_filesystem_root(cur):
            break
        if _is_full_monorepo_root(cur):
            full_hit = cur
        if _is_world_engine_container_root(cur):
            slim_hit = cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent

    if full_hit is not None:
        return full_hit
    if slim_hit is not None:
        return slim_hit

    raise RuntimeError(
        "Cannot resolve WOS repository root for world-engine. Set WOS_REPO_ROOT to the checkout "
        "that contains backend/app/, or for the play-service container use WOS_REPO_ROOT=/app."
    )
