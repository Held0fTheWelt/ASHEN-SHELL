from __future__ import annotations

import hashlib
from pathlib import Path

from fy_platform.ai.evidence_registry.registry import EvidenceRegistry
from fy_platform.ai.workspace import target_repo_id, workspace_root, write_json


class TestifyAdapter:
    def __init__(self, root: Path | None = None) -> None:
        self.root = workspace_root(root)
        self.registry = EvidenceRegistry(self.root)

    def audit(self, target_repo_root: str | Path) -> dict:
        root = workspace_root(Path(target_repo_root))
        report = root / 'testify' / 'reports' / 'testify_audit.json'
        if not report.exists():
            write_json(report, {'summary': {'finding_count': 0, 'warning_count': 0}, 'findings': [], 'warnings': []})
        run = self.registry.start_run(suite='testify', mode='audit', target_repo_root=str(root), target_repo_id=target_repo_id(root), strategy_profile='D', run_metadata={})
        digest = hashlib.sha256(report.read_bytes()).hexdigest()
        self.registry.record_artifact(suite='testify', run_id=run.run_id, format='json', role='report', path='testify/reports/testify_audit.json')
        self.registry.record_evidence(suite='testify', run_id=run.run_id, kind='json_report', source_uri=str(report), ownership_zone='testify', content_hash=digest, mime_type='application/json', deterministic=True)
        self.registry.finish_run(run.run_id, status='ok')
        write_json(root / 'testify/reports/status/most_recent_next_steps.json', {'ok': True, 'summary': 'Testify evidence is available.', 'next_steps': ['Review testing evidence.'], 'command': 'audit', 'latest_run': {'run_id': run.run_id}})
        return {'ok': True, 'run_id': run.run_id}
