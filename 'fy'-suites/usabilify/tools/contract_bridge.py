from __future__ import annotations

import re
from pathlib import Path
from typing import Any

UI_DOC_PATTERNS = [
    'docs/dev/play_shell_ux.md',
    'docs/dev/world_engine_console_a11y.md',
    'docs/dev/world_engine_console_wireframes.md',
    'docs/ADR/adr-0020-debug-panel-ui.md',
    'docs/ADR/adr-0016-frontend-backend-restructure.md',
    'docs/technical/runtime/player_input_interpretation_contract.md',
    'docs/technical/architecture/session_runtime_contract.md',
    'docs/technical/content/writers-room-and-publishing-flow.md',
    'docs/technical/architecture/backend-runtime-classification.md',
]
REQ_RE = re.compile(r'^(?:-|\*|\d+\.)\s+(.*(?:must|should|keyboard|accessible|error|feedback|status|player|console|form|navigation).*)$', re.I)
HEADING_RE = re.compile(r'^#\s+(.*)$', re.M)


def _classify_area(path: str, title: str, text: str) -> list[str]:
    source = ' '.join([path.lower(), title.lower(), text.lower()])
    tags: list[str] = []
    if 'frontend' in source or 'play shell' in source or 'player' in source:
        tags.append('frontend')
    if 'world engine console' in source or 'manage' in source or 'debug panel' in source:
        tags.append('administration_manage')
        tags.append('administration_tool')
    if 'writers-room' in source or 'publishing' in source:
        tags.append('writers_room')
    if 'backend' in source or 'api' in source:
        tags.append('backend_info')
    if not tags:
        tags.extend(['frontend', 'administration_tool'])
    return sorted(set(tags))


def scan_contracts(repo_root: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {'suite': 'usabilify', 'contracts': []}
    for rel_path in UI_DOC_PATTERNS:
        path = repo_root / rel_path
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        title_match = HEADING_RE.search(text)
        title = title_match.group(1).strip() if title_match else path.stem
        reqs = [match.group(1).strip() for match in REQ_RE.finditer(text)]
        payload['contracts'].append(
            {
                'path': rel_path,
                'title': title,
                'area_tags': _classify_area(rel_path, title, text),
                'requirements': reqs[:20],
                'requirement_count': len(reqs),
            }
        )
    return payload
