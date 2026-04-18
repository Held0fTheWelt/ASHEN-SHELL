from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import re

PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

@dataclass
class TemplateRecord:
    template_id: str
    family: str
    name: str
    path: str
    placeholders: list[str]
    sha256: str


def discover_templates(workspace_root: Path) -> list[TemplateRecord]:
    base = workspace_root / 'templatify' / 'templates'
    records: list[TemplateRecord] = []
    if not base.is_dir():
        return records
    for path in sorted(base.rglob('*.tmpl')):
        text = path.read_text(encoding='utf-8', errors='replace')
        family = path.relative_to(base).parts[0]
        rel = path.relative_to(base).as_posix()
        name = path.stem.replace('.md', '')
        placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
        records.append(TemplateRecord(
            template_id=f'{family}:{name}',
            family=family,
            name=name,
            path=rel,
            placeholders=placeholders,
            sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),
        ))
    return records


def template_map(workspace_root: Path) -> dict[str, TemplateRecord]:
    return {item.template_id: item for item in discover_templates(workspace_root)}
