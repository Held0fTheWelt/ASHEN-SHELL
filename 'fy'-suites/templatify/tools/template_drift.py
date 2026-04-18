from __future__ import annotations

from pathlib import Path
import re

from templatify.tools.template_registry import template_map

HEADER_RE = re.compile(r'templify:template_id=([^\s]+) template_hash=([0-9a-f]{64})')


def scan_generated_drift(workspace_root: Path, generated_dir: Path) -> dict:
    records = template_map(workspace_root)
    drifted = []
    scanned = 0
    if not generated_dir.exists():
        return {'ok': True, 'scanned_files': 0, 'drift_count': 0, 'drifted': []}
    for path in generated_dir.rglob('*.md'):
        scanned += 1
        first = path.read_text(encoding='utf-8', errors='replace').splitlines()[:1]
        if not first:
            continue
        match = HEADER_RE.search(first[0])
        if not match:
            continue
        template_id, used_hash = match.group(1), match.group(2)
        current = records.get(template_id)
        if current and current.sha256 != used_hash:
            drifted.append({'path': path.as_posix(), 'template_id': template_id, 'used_hash': used_hash, 'current_hash': current.sha256})
    return {'ok': True, 'scanned_files': scanned, 'drift_count': len(drifted), 'drifted': drifted}
