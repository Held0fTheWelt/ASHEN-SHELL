from __future__ import annotations

from pathlib import Path

from fy_platform.ai.workspace import workspace_root


def resolve_repo_root(raw: str | None = None) -> Path:
    if raw:
        return workspace_root(Path(raw).resolve())
    return workspace_root(Path(__file__).resolve())


def suite_root(repo_root: Path) -> Path:
    return repo_root / 'mvpify'


def reports_root(repo_root: Path) -> Path:
    return suite_root(repo_root) / 'reports'


def state_root(repo_root: Path) -> Path:
    return suite_root(repo_root) / 'state'


def imports_root(repo_root: Path) -> Path:
    return suite_root(repo_root) / 'imports'


def docs_imports_root(repo_root: Path) -> Path:
    return repo_root / 'docs' / 'MVPs' / 'imports'
