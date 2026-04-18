from __future__ import annotations

from pathlib import Path

from templatify.tools.template_registry import discover_templates


def resolve_template_path(workspace_root: Path, family: str, name: str) -> Path:
    base = workspace_root / 'templatify' / 'templates'
    candidates = [base / family / f'{name}.md.tmpl', base / family / f'{name}.tmpl']
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    available = ', '.join(sorted(item.template_id for item in discover_templates(workspace_root) if item.family == family))
    raise FileNotFoundError(f'No template for family={family!r} name={name!r}. Available: {available}')
