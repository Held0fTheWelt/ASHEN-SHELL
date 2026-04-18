from __future__ import annotations

from pathlib import Path


def load_observifyfy_signal(repo_root: Path) -> dict:
    for report in [
        repo_root / 'observifyfy' / 'reports' / 'observifyfy_next_steps.json',
        repo_root / 'docs' / 'platform' / 'observifyfy_next_steps.json',
    ]:
        if report.exists():
            try:
                import json
                return {'present': True, 'payload': json.loads(report.read_text(encoding='utf-8')), 'path': str(report.relative_to(repo_root))}
            except Exception as exc:
                return {'present': True, 'error': str(exc), 'path': str(report.relative_to(repo_root))}
    return {'present': False}
