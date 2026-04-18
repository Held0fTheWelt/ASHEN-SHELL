from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get('WOS_USABILIFY_REPO_ROOT')
    if override:
        return Path(override).resolve()
    current = Path.cwd().resolve()
    markers = ['pyproject.toml', 'fy_platform', 'contractify', 'documentify', 'templatify', 'usabilify']
    for parent in [current, *current.parents]:
        if any((parent / marker).exists() for marker in markers):
            return parent
    current_file = Path(__file__).resolve()
    for parent in current_file.parents:
        if any((parent / marker).exists() for marker in markers):
            return parent
    raise RuntimeError('Could not determine repository root for usabilify')
