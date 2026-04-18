from __future__ import annotations

import os
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
    env = os.environ.get('DOCUMENTIFY_REPO_ROOT', '').strip()
    if env:
        forced = Path(env).expanduser().resolve()
        if forced.is_dir():
            return forced
    return resolve_project_root(start=start, marker_text=None)


def documentify_hub_dir(repo: Path | None = None) -> Path:
    r = repo or repo_root()
    return r / FY_SUITES_DIRNAME / 'documentify'
