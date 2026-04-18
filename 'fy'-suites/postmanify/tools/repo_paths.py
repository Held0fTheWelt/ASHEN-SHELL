"""Resolve monorepo root and Postmanify hub directory."""
from __future__ import annotations

from pathlib import Path

from fy_platform.core.project_resolver import resolve_project_root

FY_SUITES_DIRNAME = "'fy'-suites"


def _current_or_legacy_suite_dir(repo: Path, suite: str) -> Path:
    direct = repo / suite
    if direct.is_dir() or (repo / 'fy_platform').is_dir():
        return direct
    nested = repo / FY_SUITES_DIRNAME / suite
    return nested


def repo_root(*, start: Path | None = None) -> Path:
    """Resolve the current workspace root with shared project resolution."""
    return resolve_project_root(start=start, marker_text=None)


def postmanify_hub_dir(repo: Path | None = None) -> Path:
    """Return the current Postmanify hub, with legacy nested fallback."""
    r = repo or repo_root()
    return _current_or_legacy_suite_dir(r, 'postmanify')
