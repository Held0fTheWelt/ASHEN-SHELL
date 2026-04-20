#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]

BACKEND_ALLOWED = {
    "flask",
    "flask-cors",
    "flask-sqlalchemy",
    "flask-jwt-extended",
    "flask-limiter",
    "flask-migrate",
    "flask-wtf",
    "flask-mail",
    "werkzeug",
    "alembic",
    "python-dotenv",
    "markdown",
    "bleach",
    "httpx",
    "email-validator",
    "pydantic",
    "fastapi",
    "requests",
    "pyyaml",
    "marshmallow",
    "cryptography",
    "pyopenssl",
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-timeout",
    "anyio",
    "exceptiongroup",
    "uvicorn",
}

WORLD_ENGINE_ALLOWED = {
    "fastapi",
    "httpx",
    "pydantic",
    "pyyaml",
    "pytest",
    "pytest-asyncio",
    "pytest-timeout",
    "uvicorn",
}

EXPLICIT_PACKAGES = ["uvicorn>=0.30,<1"]


def _normalize_requirement_name(requirement: str) -> str:
    name = requirement.strip()
    cut_points = [name.find(marker) for marker in (';', '[', '<', '>', '=', '!', '~', ' ')]
    cut_points = [index for index in cut_points if index != -1]
    if cut_points:
        name = name[:min(cut_points)]
    return name.strip().lower()


def _collect_requirements(pyproject_path: Path, allowed_names: set[str]) -> list[str]:
    data = tomllib.loads(pyproject_path.read_text(encoding='utf-8'))
    project = data.get('project', {})
    requirements: list[str] = []
    for requirement in project.get('dependencies', []):
        if _normalize_requirement_name(requirement) in allowed_names:
            requirements.append(requirement)
    optional = project.get('optional-dependencies', {})
    for requirement in optional.get('test', []):
        if _normalize_requirement_name(requirement) in allowed_names:
            requirements.append(requirement)
    seen: set[str] = set()
    deduped: list[str] = []
    for requirement in requirements:
        if requirement not in seen:
            deduped.append(requirement)
            seen.add(requirement)
    return deduped


def _run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    display_cwd = str(cwd or REPO_ROOT)
    print(f"\n[{display_cwd}]$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, cwd=str(cwd or REPO_ROOT), env=env, check=True)


def main() -> int:
    python = sys.executable
    backend_requirements = _collect_requirements(REPO_ROOT / 'backend' / 'pyproject.toml', BACKEND_ALLOWED)
    world_engine_requirements = _collect_requirements(REPO_ROOT / 'world-engine' / 'pyproject.toml', WORLD_ENGINE_ALLOWED)

    combined_requirements: list[str] = []
    seen: set[str] = set()
    for requirement in [*backend_requirements, *world_engine_requirements, *EXPLICIT_PACKAGES]:
        if requirement not in seen:
            combined_requirements.append(requirement)
            seen.add(requirement)

    pip_env = dict(os.environ)
    pip_env.setdefault('PIP_DISABLE_PIP_VERSION_CHECK', '1')
    _run([python, '-m', 'pip', 'install', *combined_requirements], env=pip_env)

    _run([python, '-m', 'pytest', '-q', 'tests/test_runtime_manager.py', '-q'], cwd=REPO_ROOT / 'world-engine')
    _run([python, '-m', 'pytest', '-q', 'tests/test_backend_playservice_integration.py', '-q'], cwd=REPO_ROOT / 'backend')

    print('\nLive activation proof validation completed successfully.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
