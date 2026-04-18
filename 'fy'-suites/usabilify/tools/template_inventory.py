from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXTENDS_RE = re.compile(r"{%\s*extends\s+['\"]([^'\"]+)['\"]\s*%}")
BLOCK_RE = re.compile(r"{%\s*block\s+([A-Za-z0-9_]+)\s*%}(.*?){%\s*endblock(?:\s+[A-Za-z0-9_]+)?\s*%}", re.S)
TAG_PATTERNS = {
    'forms': re.compile(r'<form\b', re.I),
    'inputs': re.compile(r'<input\b', re.I),
    'buttons': re.compile(r'<button\b', re.I),
    'links': re.compile(r'<a\b', re.I),
    'navs': re.compile(r'<nav\b', re.I),
    'mains': re.compile(r'<main\b', re.I),
    'headers': re.compile(r'<header\b', re.I),
    'footers': re.compile(r'<footer\b', re.I),
    'labels': re.compile(r'<label\b', re.I),
    'selects': re.compile(r'<select\b', re.I),
    'textareas': re.compile(r'<textarea\b', re.I),
    'tables': re.compile(r'<table\b', re.I),
    'dialogs': re.compile(r'<dialog\b', re.I),
    'sections': re.compile(r'<section\b', re.I),
    'asides': re.compile(r'<aside\b', re.I),
    'headings': re.compile(r'<h[1-4]\b', re.I),
}
SIGNAL_PATTERNS = {
    'aria_label': re.compile(r"aria-label\s*=\s*['\"]", re.I),
    'aria_labelledby': re.compile(r"aria-labelledby\s*=\s*['\"]", re.I),
    'aria_describedby': re.compile(r"aria-describedby\s*=\s*['\"]", re.I),
    'aria_live': re.compile(r"aria-live\s*=\s*['\"]", re.I),
    'role_alert': re.compile(r"role\s*=\s*['\"]alert['\"]", re.I),
    'role_status': re.compile(r"role\s*=\s*['\"]status['\"]", re.I),
    'tabindex': re.compile(r"tabindex\s*=\s*['\"]", re.I),
    'skip_link': re.compile(r'skip to content|skip-link', re.I),
    'flash_message': re.compile(r'flash|alert-|notification|toast', re.I),
}

AREA_DEFINITIONS: dict[str, dict[str, str]] = {
    'frontend': {'target_root': 'frontend/templates', 'base_template': 'base.html'},
    'administration_tool': {'target_root': 'administration-tool/templates', 'base_template': 'base.html'},
    'administration_manage': {'target_root': 'administration-tool/templates/manage', 'base_template': 'base.html'},
    'backend_info': {'target_root': 'backend/app/info/templates', 'base_template': 'base.html'},
    'writers_room': {'target_root': 'writers-room/app/templates', 'base_template': 'base.html'},
}


@dataclass
class TemplateRecord:
    area: str
    path: str
    extends: str | None
    blocks: list[str]
    element_counts: dict[str, int]
    signals: dict[str, bool]


def parse_template(text: str) -> dict[str, Any]:
    extends_match = EXTENDS_RE.search(text)
    extends = extends_match.group(1) if extends_match else None
    blocks = [match.group(1) for match in BLOCK_RE.finditer(text)]
    element_counts = {name: len(pattern.findall(text)) for name, pattern in TAG_PATTERNS.items()}
    signals = {name: bool(pattern.search(text)) for name, pattern in SIGNAL_PATTERNS.items()}
    return {'extends': extends, 'blocks': blocks, 'element_counts': element_counts, 'signals': signals}


def scan_area(area: str, root: Path) -> list[TemplateRecord]:
    records: list[TemplateRecord] = []
    if not root.is_dir():
        return records
    for path in sorted(root.rglob('*.html')):
        parsed = parse_template(path.read_text(encoding='utf-8', errors='ignore'))
        records.append(
            TemplateRecord(
                area=area,
                path=path.relative_to(root).as_posix(),
                extends=parsed['extends'],
                blocks=parsed['blocks'],
                element_counts=parsed['element_counts'],
                signals=parsed['signals'],
            )
        )
    return records


def inspect_areas(repo_root: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {'suite': 'usabilify', 'areas': {}, 'views': []}
    for area, info in AREA_DEFINITIONS.items():
        target = repo_root / info['target_root']
        records = scan_area(area, target)
        base_record = next((record for record in records if record.path == info['base_template']), None)
        payload['areas'][area] = {
            'target_root': info['target_root'],
            'base_template': info['base_template'],
            'exists': target.is_dir(),
            'template_count': len(records),
            'view_count': sum(1 for record in records if record.path != info['base_template']),
            'base_blocks': base_record.blocks if base_record else [],
            'base_signals': base_record.signals if base_record else {},
            'base_element_counts': base_record.element_counts if base_record else {},
        }
        payload['views'].extend(asdict(record) for record in records)
    return payload
