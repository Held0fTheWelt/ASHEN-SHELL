from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fy_platform.ai.policy.indexing_policy import DEFAULT_EXCLUDED_DIRS, DEFAULT_EXCLUDED_FILES
from fy_platform.ai.workspace import read_text_safe, workspace_root

SECRET_FILE_NAMES = {'.env', '.env.local', '.env.production', '.env.development', 'secrets.yml', 'secrets.yaml', 'id_rsa', 'id_ed25519'}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET_ACCESS_KEY|SECRET_KEY)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
]
TEXT_SUFFIXES = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.rst'}


def scan_workspace_security(root: Path | None = None) -> dict[str, Any]:
    workspace = workspace_root(root)
    risky_files: list[str] = []
    secret_hits: list[dict[str, str]] = []
    for path in workspace.rglob('*'):
        if any(part in DEFAULT_EXCLUDED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.name in SECRET_FILE_NAMES:
            risky_files.append(path.relative_to(workspace).as_posix())
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel_parts = {part.lower() for part in path.relative_to(workspace).parts}
        if 'tests' in rel_parts or 'fixtures' in rel_parts:
            continue
        try:
            text = read_text_safe(path)
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                secret_hits.append({'path': path.relative_to(workspace).as_posix(), 'pattern': pattern.pattern[:48]})
                break
    indexing_policy_ok = '.env' in DEFAULT_EXCLUDED_FILES and '.fydata' in DEFAULT_EXCLUDED_DIRS
    return {
        'schema_version': 'fy.security-review.v1',
        'workspace_root': str(workspace),
        'indexing_policy_ok': indexing_policy_ok,
        'risky_file_count': len(risky_files),
        'secret_hit_count': len(secret_hits),
        'risky_files': risky_files[:20],
        'secret_hits': secret_hits[:20],
        'ok': indexing_policy_ok and not risky_files and not secret_hits,
    }
