from __future__ import annotations

import json
import sqlite3
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from fy_platform.ai.persistence_state import ensure_schema_state
from fy_platform.ai.policy.review_policy import validate_transition
from fy_platform.ai.schemas.common import (
    ArtifactRecord,
    CompareRunsDelta,
    EvidenceRecord,
    SuiteRunRecord,
    to_jsonable,
)
from fy_platform.ai.workspace import ensure_workspace_layout, utc_now, workspace_root


class EvidenceRegistry:
    def __init__(self, root: Path | None = None) -> None:
        self.root = workspace_root(root)
        ensure_workspace_layout(self.root)
        self.db_path = self.root / '.fydata' / 'registry' / 'registry.db'
        self._init_db()
        ensure_schema_state(self.root)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS suite_runs (
                    run_id TEXT PRIMARY KEY,
                    suite TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    workspace_root TEXT NOT NULL,
                    target_repo_root TEXT,
                    target_repo_id TEXT,
                    status TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    suite TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    format TEXT NOT NULL,
                    role TEXT NOT NULL,
                    path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT,
                    FOREIGN KEY(run_id) REFERENCES suite_runs(run_id)
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    suite TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    source_uri TEXT NOT NULL,
                    ownership_zone TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    deterministic INTEGER NOT NULL,
                    review_state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    excerpt TEXT DEFAULT '',
                    FOREIGN KEY(run_id) REFERENCES suite_runs(run_id)
                );
                CREATE TABLE IF NOT EXISTS links (
                    src_id TEXT NOT NULL,
                    dst_id TEXT NOT NULL,
                    relation TEXT NOT NULL
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def start_run(self, *, suite: str, mode: str, target_repo_root: str | None, target_repo_id: str | None) -> SuiteRunRecord:
        record = SuiteRunRecord(
            run_id=f'{suite}-{uuid.uuid4().hex[:12]}',
            suite=suite,
            mode=mode,
            started_at=utc_now(),
            ended_at=None,
            workspace_root=str(self.root),
            target_repo_root=target_repo_root,
            target_repo_id=target_repo_id,
            status='running',
        )
        conn = self._connect()
        try:
            conn.execute(
                'INSERT INTO suite_runs(run_id, suite, mode, started_at, ended_at, workspace_root, target_repo_root, target_repo_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (record.run_id, record.suite, record.mode, record.started_at, record.ended_at, record.workspace_root, record.target_repo_root, record.target_repo_id, record.status),
            )
            conn.commit()
        finally:
            conn.close()
        return record

    def finish_run(self, run_id: str, *, status: str = 'ok') -> None:
        conn = self._connect()
        try:
            conn.execute('UPDATE suite_runs SET ended_at = ?, status = ? WHERE run_id = ?', (utc_now(), status, run_id))
            conn.commit()
        finally:
            conn.close()

    def record_artifact(self, *, suite: str, run_id: str, format: str, role: str, path: str, payload: Any | None = None) -> ArtifactRecord:
        rec = ArtifactRecord(artifact_id=uuid.uuid4().hex, suite=suite, run_id=run_id, format=format, role=role, path=path, created_at=utc_now())
        conn = self._connect()
        try:
            conn.execute(
                'INSERT INTO artifacts(artifact_id, suite, run_id, format, role, path, created_at, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (rec.artifact_id, rec.suite, rec.run_id, rec.format, rec.role, rec.path, rec.created_at, json.dumps(to_jsonable(payload)) if payload is not None else None),
            )
            conn.commit()
        finally:
            conn.close()
        return rec

    def record_evidence(self, *, suite: str, run_id: str, kind: str, source_uri: str, ownership_zone: str, content_hash: str, mime_type: str, deterministic: bool, review_state: str = 'raw', excerpt: str = '') -> EvidenceRecord:
        rec = EvidenceRecord(
            evidence_id=uuid.uuid4().hex,
            suite=suite,
            run_id=run_id,
            kind=kind,
            source_uri=source_uri,
            ownership_zone=ownership_zone,
            content_hash=content_hash,
            mime_type=mime_type,
            deterministic=deterministic,
            review_state=review_state,
            created_at=utc_now(),
        )
        conn = self._connect()
        try:
            conn.execute(
                'INSERT INTO evidence(evidence_id, suite, run_id, kind, source_uri, ownership_zone, content_hash, mime_type, deterministic, review_state, created_at, excerpt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (rec.evidence_id, rec.suite, rec.run_id, rec.kind, rec.source_uri, rec.ownership_zone, rec.content_hash, rec.mime_type, int(rec.deterministic), rec.review_state, rec.created_at, excerpt),
            )
            conn.commit()
        finally:
            conn.close()
        return rec

    def update_evidence_review_state(self, evidence_id: str, new_state: str) -> dict[str, Any]:
        conn = self._connect()
        try:
            row = conn.execute('SELECT review_state FROM evidence WHERE evidence_id = ?', (evidence_id,)).fetchone()
            if not row:
                return {'ok': False, 'reason': 'evidence_not_found', 'evidence_id': evidence_id}
            current = row['review_state']
            result = validate_transition(current, new_state)
            if not result.ok:
                return {'ok': False, 'reason': result.reason, 'evidence_id': evidence_id, 'current_state': current, 'new_state': new_state}
            conn.execute('UPDATE evidence SET review_state = ? WHERE evidence_id = ?', (new_state, evidence_id))
            conn.commit()
            return {'ok': True, 'evidence_id': evidence_id, 'current_state': current, 'new_state': new_state}
        finally:
            conn.close()

    def list_evidence(self, suite: str | None = None, review_state: str | None = None) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            query = 'SELECT * FROM evidence WHERE 1=1'
            params: list[Any] = []
            if suite:
                query += ' AND suite = ?'
                params.append(suite)
            if review_state:
                query += ' AND review_state = ?'
                params.append(review_state)
            query += ' ORDER BY created_at DESC'
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def evidence_for_run(self, run_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute('SELECT * FROM evidence WHERE run_id = ? ORDER BY created_at ASC', (run_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def link(self, src_id: str, dst_id: str, relation: str) -> None:
        conn = self._connect()
        try:
            conn.execute('INSERT INTO links(src_id, dst_id, relation) VALUES (?, ?, ?)', (src_id, dst_id, relation))
            conn.commit()
        finally:
            conn.close()

    def latest_run(self, suite: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute('SELECT * FROM suite_runs WHERE suite = ? ORDER BY started_at DESC LIMIT 1', (suite,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute('SELECT * FROM suite_runs WHERE run_id = ?', (run_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_runs(self, suite: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute('SELECT * FROM suite_runs WHERE suite = ? ORDER BY started_at DESC', (suite,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def artifacts_for_run(self, run_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute('SELECT * FROM artifacts WHERE run_id = ? ORDER BY created_at ASC', (run_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def artifact_payload(self, artifact_id: str) -> Any | None:
        conn = self._connect()
        try:
            row = conn.execute('SELECT payload_json FROM artifacts WHERE artifact_id = ?', (artifact_id,)).fetchone()
            if not row or not row['payload_json']:
                return None
            return json.loads(row['payload_json'])
        finally:
            conn.close()

    def compare_runs(self, left_run_id: str, right_run_id: str) -> CompareRunsDelta | None:
        from fy_platform.ai.run_journal.journal import RunJournal

        left = self.get_run(left_run_id)
        right = self.get_run(right_run_id)
        if not left or not right:
            return None
        left_art = self.artifacts_for_run(left_run_id)
        right_art = self.artifacts_for_run(right_run_id)
        left_ev = self.evidence_for_run(left_run_id)
        right_ev = self.evidence_for_run(right_run_id)
        left_roles = {item['role'] for item in left_art}
        right_roles = {item['role'] for item in right_art}
        left_formats = {item['format'] for item in left_art}
        right_formats = {item['format'] for item in right_art}
        left_review_counts = dict(sorted(Counter(item['review_state'] for item in left_ev).items()))
        right_review_counts = dict(sorted(Counter(item['review_state'] for item in right_ev).items()))
        journal = RunJournal(self.root)
        left_summary = journal.summarize(left['suite'], left_run_id)
        right_summary = journal.summarize(right['suite'], right_run_id)
        return CompareRunsDelta(
            left_run_id=left_run_id,
            right_run_id=right_run_id,
            left_status=left['status'],
            right_status=right['status'],
            artifact_delta=len(right_art) - len(left_art),
            added_roles=sorted(right_roles - left_roles),
            removed_roles=sorted(left_roles - right_roles),
            left_artifact_count=len(left_art),
            right_artifact_count=len(right_art),
            left_evidence_count=len(left_ev),
            right_evidence_count=len(right_ev),
            left_review_state_counts=left_review_counts,
            right_review_state_counts=right_review_counts,
            left_journal_event_count=left_summary['event_count'],
            right_journal_event_count=right_summary['event_count'],
            left_duration_seconds=_duration_seconds(left['started_at'], left['ended_at']),
            right_duration_seconds=_duration_seconds(right['started_at'], right['ended_at']),
            mode_changed=left['mode'] != right['mode'],
            target_repo_changed=left['target_repo_root'] != right['target_repo_root'],
            target_repo_id_changed=left['target_repo_id'] != right['target_repo_id'],
            added_formats=sorted(right_formats - left_formats),
            removed_formats=sorted(left_formats - right_formats),
        )


def _duration_seconds(started_at: str | None, ended_at: str | None) -> float | None:
    if not started_at or not ended_at:
        return None
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(ended_at)
    except ValueError:
        return None
    return round((end - start).total_seconds(), 6)
