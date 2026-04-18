"""Resolve monorepo root and Docify hub directory paths."""
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
    """Return project root via shared resolver with manifest-friendly fallback."""
    return resolve_project_root(start=start, marker_text=None)




def docify_hub_dir(repo: Path | None = None) -> Path:
    r = repo or repo_root()
    return _current_or_legacy_suite_dir(r, 'docify')


def docify_hub_rel_posix(repo: Path | None = None) -> str:
    """Hub directory as a repo-relative POSIX path for messages."""
    r = repo or repo_root()
    return docify_hub_dir(r).relative_to(r).as_posix()
