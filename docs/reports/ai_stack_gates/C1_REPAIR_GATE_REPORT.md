# C1 Repair Gate Report — RAG Semantic Persistence and Operational Wiring

Date: 2026-04-04

## 1. Scope completed

- Replaced lexical-only ranking with semantic sparse-vector retrieval in `wos_ai_stack/rag.py`.
- Added persistent corpus storage and cache reuse for the runtime retriever path (`.wos/rag/runtime_corpus.json`).
- Added per-chunk source metadata/versioning (`source_version`, `source_hash`, canonical priority).
- Added profile-aware ranking behavior (`runtime_turn_support`, `writers_review`, `improvement_eval`) with canonical source prioritization.
- Kept runtime and writers-room code paths on the same retrieval core, now backed by persistent semantic retrieval.
- Added C1 tests for persistence, semantic paraphrase retrieval, profile-based canonical prioritization, and version metadata behavior.

## 2. Files changed

- `.gitignore`
- `wos_ai_stack/rag.py`
- `wos_ai_stack/tests/test_rag.py`
- `docs/architecture/rag_in_world_of_shadows.md`
- `docs/reports/ai_stack_gates/C1_REPAIR_GATE_REPORT.md`

## 3. What is truly wired

- `build_runtime_retriever(...)` now loads from persistent corpus cache when source fingerprint is unchanged, and rebuilds/saves when changed.
- World-Engine runtime manager uses `build_runtime_retriever(...)`, so authoritative turn-time retrieval now uses the persistent semantic path.
- Writers-room service uses the same retrieval core via `wos.context_pack.build` with writers-room domain/profile; it now inherits semantic ranking and source-version metadata.
- Retrieval result sources now include version metadata (`source_version`) for traceability.

## 4. What remains incomplete

- Semantic retrieval is lightweight local sparse semantics; no transformer embedding model or external vector service is integrated.
- Persistence is local JSON storage only; no multi-node durability, lock coordination, or index compaction strategy exists.
- Improvement workflow uses retrieval primitives but does not yet include C1-specific improvement-only retrieval tuning beyond profile boosts.

## 5. Tests added/updated

- Updated `wos_ai_stack/tests/test_rag.py`:
  - semantic phrasing retrieval test (paraphrase-style query)
  - runtime profile canonical-priority retrieval test
  - persistent retriever cache reuse test
  - ingestion source-version change test
  - context pack source-version attribution assertion
- Existing runtime and writers-room tests were executed to verify wiring continuity:
  - `world-engine/tests/test_story_runtime_rag_runtime.py`
  - `backend/tests/test_writers_room_routes.py`

## 6. Exact test commands run

```powershell
python -m pytest "wos_ai_stack/tests/test_rag.py"
```

```powershell
python -m pytest "world-engine/tests/test_story_runtime_rag_runtime.py"
```

```powershell
python -m pytest "backend/tests/test_writers_room_routes.py"
```

## 7. Pass / Partial / Fail

Pass

## 8. Reason for the verdict

- Persistence is active on intended runtime path and verified by test.
- Retrieval is materially semantic (sparse semantic vector + cosine ranking + concept expansion), not lexical overlap only.
- Runtime-adjacent and writers-room paths are both wired to the repaired retrieval core.
- Tests now explicitly cover persistence behavior, semantic retrieval behavior, profile behavior, and metadata/version coherence.

## 9. Risks introduced or remaining

- Local JSON corpus can grow large and increase startup I/O for large repositories.
- Concept-expansion semantics are deterministic but heuristic and may require tuning for broader narrative domains.
- Source fingerprinting is file-metadata based; rare edge cases where content changes without mtime/size changes are unlikely but possible on unusual filesystems.
