from __future__ import annotations

from fy_platform.ai.backup_manager import create_workspace_backup, rollback_workspace_backup
from fy_platform.ai.evidence_registry.registry import EvidenceRegistry


def test_create_and_rollback_workspace_backup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = EvidenceRegistry(tmp_path)
    manifest = create_workspace_backup(tmp_path, reason='test')
    assert manifest['backup_id'].startswith('backup-')
    db = tmp_path / '.fydata' / 'registry' / 'registry.db'
    original = db.read_bytes()
    db.write_bytes(b'corrupted')
    result = rollback_workspace_backup(tmp_path)
    assert result['ok'] is True
    assert db.read_bytes() == original
