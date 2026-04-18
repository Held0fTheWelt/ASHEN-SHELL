from __future__ import annotations

import math
import re
import sqlite3
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from fy_platform.ai.persistence_state import ensure_schema_state
from fy_platform.ai.policy.indexing_policy import MAX_TEXT_BYTES, is_indexable_path, should_exclude_dir, should_exclude_file
from fy_platform.ai.schemas.common import ContextPack, RetrievalHit
from fy_platform.ai.workspace import read_text_safe, utc_now, workspace_root

TOKEN_RE = re.compile(r"[A-Za-z0-9_\-/]{2,}")


class SemanticIndex:
    def __init__(self, root: Path | None = None) -> None:
        self.root = workspace_root(root)
        self.db_path = self.root / '.fydata' / 'index' / 'semantic_index.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
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
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    suite TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    token_count INTEGER NOT NULL,
                    run_id TEXT,
                    target_repo_id TEXT,
                    scope TEXT NOT NULL,
                    created_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_chunks_suite ON chunks(suite);
                CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_path);
                CREATE INDEX IF NOT EXISTS idx_chunks_scope ON chunks(scope);
                """
            )
            cols = {row['name'] for row in conn.execute('PRAGMA table_info(chunks)').fetchall()}
            if 'created_at' not in cols:
                conn.execute('ALTER TABLE chunks ADD COLUMN created_at TEXT')
            conn.commit()
        finally:
            conn.close()

    def clear_scope(self, suite: str, scope: str, target_repo_id: str | None = None) -> None:
        conn = self._connect()
        try:
            if target_repo_id:
                conn.execute('DELETE FROM chunks WHERE suite = ? AND scope = ? AND target_repo_id = ?', (suite, scope, target_repo_id))
            else:
                conn.execute('DELETE FROM chunks WHERE suite = ? AND scope = ?', (suite, scope))
            conn.commit()
        finally:
            conn.close()

    def add_chunk(self, *, suite: str, source_path: str, chunk_type: str, text: str, scope: str, run_id: str | None = None, target_repo_id: str | None = None) -> str:
        chunk_id = uuid.uuid4().hex
        conn = self._connect()
        try:
            conn.execute(
                'INSERT INTO chunks(chunk_id, suite, source_path, chunk_type, text, token_count, run_id, target_repo_id, scope, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (chunk_id, suite, source_path, chunk_type, text, len(self._tokens(text)), run_id, target_repo_id, scope, utc_now()),
            )
            conn.commit()
        finally:
            conn.close()
        return chunk_id

    def index_texts(self, *, suite: str, items: Iterable[tuple[str, str]], scope: str, run_id: str | None = None, target_repo_id: str | None = None) -> int:
        count = 0
        for source_path, text in items:
            for i, chunk in enumerate(self._chunk_text(text)):
                self.add_chunk(suite=suite, source_path=f'{source_path}#chunk-{i+1}', chunk_type='text', text=chunk, scope=scope, run_id=run_id, target_repo_id=target_repo_id)
                count += 1
        return count

    def index_directory(self, *, suite: str, directory: Path, scope: str, run_id: str | None = None, target_repo_id: str | None = None) -> int:
        items = []
        for path in directory.rglob('*'):
            if path.is_dir() and should_exclude_dir(path.name):
                continue
            if not path.is_file() or should_exclude_file(path.name) or not is_indexable_path(path):
                continue
            try:
                if path.stat().st_size > MAX_TEXT_BYTES:
                    continue
            except OSError:
                continue
            rel = path.relative_to(directory).as_posix()
            items.append((rel, read_text_safe(path)))
        return self.index_texts(suite=suite, items=items, scope=scope, run_id=run_id, target_repo_id=target_repo_id)

    def _chunk_text(self, text: str, max_chars: int = 1200) -> list[str]:
        text = text.strip()
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]
        chunks = []
        current = []
        current_len = 0
        for para in text.split('\n\n'):
            para = para.strip()
            if not para:
                continue
            if current_len + len(para) + 2 > max_chars and current:
                chunks.append('\n\n'.join(current))
                current = [para]
                current_len = len(para)
            else:
                current.append(para)
                current_len += len(para) + 2
        if current:
            chunks.append('\n\n'.join(current))
        return chunks

    def _tokens(self, text: str) -> list[str]:
        return [t.lower() for t in TOKEN_RE.findall(text)]

    def search(self, query: str, *, suite_scope: list[str] | None = None, limit: int = 8) -> list[RetrievalHit]:
        query_tokens = self._tokens(query)
        q_counter = Counter(query_tokens)
        conn = self._connect()
        try:
            rows = conn.execute('SELECT rowid, * FROM chunks').fetchall()
        finally:
            conn.close()
        if not rows:
            return []
        newest_rowid = max(int(row['rowid']) for row in rows)
        hits = []
        emitted_by_source: dict[str, int] = {}
        for row in rows:
            if suite_scope and row['suite'] not in suite_scope:
                continue
            text = row['text']
            tokens = self._tokens(text)
            if not tokens:
                continue
            lexical = self._lexical_score(query_tokens, tokens)
            semantic = self._semantic_score(q_counter, Counter(tokens))
            matched_terms = sorted({token for token in query_tokens if token in tokens})[:8]
            recency = self._recency_score(int(row['rowid']), newest_rowid)
            scope_score = self._scope_score(row['scope'])
            suite_affinity = self._suite_affinity_score(query_tokens, row['suite'], row['source_path'])
            hybrid = 0.45 * lexical + 0.25 * semantic + 0.15 * recency + 0.10 * scope_score + 0.05 * suite_affinity
            if not self._passes_noise_gate(lexical, semantic, matched_terms):
                continue
            source_key = row['source_path'].split('#chunk-')[0]
            if emitted_by_source.get(source_key, 0) >= 2:
                continue
            emitted_by_source[source_key] = emitted_by_source.get(source_key, 0) + 1
            confidence = self._confidence(lexical, semantic, hybrid, matched_terms)
            excerpt = text[:280].replace('\n', ' ')
            rationale = self._rationale(matched_terms, recency, suite_affinity, scope_score)
            hits.append(RetrievalHit(
                chunk_id=row['chunk_id'],
                suite=row['suite'],
                score_lexical=round(lexical, 4),
                score_semantic=round(semantic, 4),
                score_hybrid=round(hybrid, 4),
                source_path=row['source_path'],
                excerpt=excerpt,
                scope=row['scope'],
                target_repo_id=row['target_repo_id'],
                score_recency=round(recency, 4),
                score_scope=round(scope_score, 4),
                score_suite_affinity=round(suite_affinity, 4),
                matched_terms=matched_terms,
                confidence=confidence,
                rationale=rationale,
            ))
        hits.sort(key=lambda h: (h.score_hybrid, h.score_lexical, h.score_semantic), reverse=True)
        return hits[:limit]

    def build_context_pack(self, query: str, *, suite_scope: list[str] | None = None, audience: str = 'developer', limit: int = 8) -> ContextPack:
        hits = self.search(query, suite_scope=suite_scope, limit=limit)
        summary = self._summarize_hits(query, hits, audience=audience)
        artifact_paths = sorted({hit.source_path for hit in hits})
        related_suites = sorted({hit.suite for hit in hits if hit.suite not in (suite_scope or [])})
        evidence_confidence = self._pack_confidence(hits)
        priorities = self._priorities(query, hits)
        next_steps = self._next_steps(hits, audience)
        uncertainty = self._pack_uncertainty(hits)
        return ContextPack(
            pack_id=uuid.uuid4().hex,
            query=query,
            suite_scope=suite_scope or [],
            audience=audience,
            hits=hits,
            summary=summary,
            artifact_paths=artifact_paths,
            related_suites=related_suites,
            evidence_confidence=evidence_confidence,
            priorities=priorities,
            next_steps=next_steps,
            uncertainty=uncertainty,
        )

    def _lexical_score(self, query_tokens: list[str], doc_tokens: list[str]) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        q = Counter(query_tokens)
        d = Counter(doc_tokens)
        inter = sum(min(q[t], d.get(t, 0)) for t in q)
        return inter / max(len(query_tokens), 1)

    def _semantic_score(self, q: Counter, d: Counter) -> float:
        if not q or not d:
            return 0.0
        dot = sum(q[k] * d.get(k, 0) for k in q)
        nq = math.sqrt(sum(v * v for v in q.values()))
        nd = math.sqrt(sum(v * v for v in d.values()))
        if nq == 0 or nd == 0:
            return 0.0
        return dot / (nq * nd)

    def _scope_score(self, scope: str) -> float:
        order = {'target': 1.0, 'suite': 0.8, 'workspace': 0.7}
        return order.get(scope or '', 0.5)

    def _suite_affinity_score(self, query_tokens: list[str], suite: str, source_path: str) -> float:
        tokens = set(query_tokens)
        score = 0.0
        if suite.lower() in tokens:
            score += 1.0
        path_bits = {part.lower() for part in re.split(r'[^A-Za-z0-9]+', source_path) if part}
        overlap = tokens & path_bits
        if overlap:
            score += min(0.8, 0.2 * len(overlap))
        return min(score, 1.0)

    def _recency_score(self, rowid: int, newest_rowid: int) -> float:
        if newest_rowid <= 0:
            return 0.0
        return max(0.1, rowid / newest_rowid)

    def _passes_noise_gate(self, lexical: float, semantic: float, matched_terms: list[str]) -> bool:
        if matched_terms and (lexical >= 0.15 or semantic >= 0.12):
            return True
        if lexical >= 0.3:
            return True
        if semantic >= 0.22:
            return True
        return False

    def _confidence(self, lexical: float, semantic: float, hybrid: float, matched_terms: list[str]) -> str:
        if hybrid >= 0.55 and lexical >= 0.25 and matched_terms:
            return 'high'
        if hybrid >= 0.3 and (matched_terms or semantic >= 0.2):
            return 'medium'
        return 'low'

    def _rationale(self, matched_terms: list[str], recency: float, suite_affinity: float, scope_score: float) -> str:
        parts = []
        if matched_terms:
            parts.append(f'matched terms: {", ".join(matched_terms)}')
        if recency >= 0.8:
            parts.append('recently indexed evidence')
        if suite_affinity >= 0.5:
            parts.append('strong suite/path affinity')
        if scope_score >= 0.9:
            parts.append('target-repo evidence')
        return '; '.join(parts) or 'weak indirect signal'

    def _pack_confidence(self, hits: list[RetrievalHit]) -> str:
        if not hits:
            return 'low'
        levels = [hit.confidence for hit in hits[:3]]
        if levels.count('high') >= 2:
            return 'high'
        if 'medium' in levels or 'high' in levels:
            return 'medium'
        return 'low'

    def _priorities(self, query: str, hits: list[RetrievalHit]) -> list[str]:
        if not hits:
            return [f'Collect more evidence for query "{query}" before acting.']
        priorities = [f'Start with {hits[0].source_path} because it currently has the strongest combined signal.']
        if len(hits) > 1:
            priorities.append(f'Compare it with {hits[1].source_path} before deciding on outward action.')
        suites = sorted({hit.suite for hit in hits})
        if len(suites) > 1:
            priorities.append(f'Use the cross-suite overlap across {", ".join(suites)} to avoid isolated decisions.')
        return priorities[:4]

    def _next_steps(self, hits: list[RetrievalHit], audience: str) -> list[str]:
        if not hits:
            return ['Re-run the relevant suite or index more evidence before building a context pack.']
        steps = [f'Open {hits[0].source_path} first.']
        if audience == 'manager':
            steps.append('Read the plain summary first and only open deep artifacts where the summary is still unclear.')
        elif audience == 'operator':
            steps.append('Check the top evidence and then verify the latest run status before outward application.')
        else:
            steps.append('Use the top two hits to validate the next code or governance action.')
        if any(hit.confidence == 'low' for hit in hits[:2]):
            steps.append('Treat the weaker hits as hints, not proof.')
        return steps[:4]

    def _pack_uncertainty(self, hits: list[RetrievalHit]) -> list[str]:
        if not hits:
            return ['no_hits']
        flags: list[str] = []
        if hits[0].confidence == 'low':
            flags.append('top_hit_low_confidence')
        if len(hits) > 1 and abs(hits[0].score_hybrid - hits[1].score_hybrid) < 0.05:
            flags.append('top_hits_close_together')
        if any(not hit.matched_terms for hit in hits[:3]):
            flags.append('weak_term_overlap_present')
        return flags

    def _summarize_hits(self, query: str, hits: list[RetrievalHit], *, audience: str = 'developer') -> str:
        if not hits:
            return f'No indexed evidence matched query: {query}. The safe next step is to collect more evidence first.'
        top = hits[0]
        suites = sorted({hit.suite for hit in hits})
        if audience == 'manager':
            return f'Found {len(hits)} useful evidence hits for "{query}". The clearest starting point is {top.source_path}. Review that first, then only open more detail where needed.'
        if audience == 'operator':
            return f'Found {len(hits)} evidence hits for "{query}" across suites {suites}. Start with {top.source_path}, then confirm the latest suite run before applying anything outward.'
        return f'Found {len(hits)} indexed evidence hits for query "{query}" across suites {suites}. Strongest source: {top.source_path}. Use the top-ranked items first and treat lower-confidence hits as hints.'
