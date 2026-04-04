# C1 REFOCUS Gate Report — Deepen RAG Into a More Trustworthy Operational Layer

**Date:** 2026-04-04  
**Verdict:** **PASS**

## Scope completed

- Documented the **lightweight local retrieval** contract at module top of `wos_ai_stack/rag.py` (sparse TF-IDF-style terms + curated semantic expansion; not embeddings; JSON snapshot persistence limits).
- **Traceability:** `RetrievalResult` and `ContextPack` now carry `index_version`, `corpus_fingerprint`, and `storage_path` (when known). Per-hit `ContextPack.sources` includes `chunk_id` and `score`. Capability and LangGraph retrieval payloads expose the same corpus fields.
- **Index invalidation:** Bumped `INDEX_VERSION` to `c1_semantic_v2` so stale JSON caches rebuild cleanly.
- **Canonical truth:** `content/published/<module>/` authored chunks receive higher `canonical_priority` than `content/modules/<module>/`; runtime retrieval prefers published when semantic overlap is otherwise similar.
- **Module identity:** Replaced the `god_of_carnage`-only heuristic with path-based inference: `content/modules/<id>/`, `content/published/<id>/`, and flat `content/<stem>.md`.
- **Bounded paraphrase:** Added `tension` / `strained` → `conflict` in `SEMANTIC_CANON` with a focused test.
- **Persistence:** `PersistentRagStore.save` writes via a temp file in the target directory and `os.replace` for safer atomic update on Windows.
- **LangChain bridge:** `Document.metadata` now includes `chunk_id`, `source_version`, `index_version`, and `corpus_fingerprint`.

## Files changed

- `wos_ai_stack/rag.py`
- `wos_ai_stack/capabilities.py` (retrieval payload enrichment)
- `wos_ai_stack/langgraph_runtime.py` (fallback retrieval dict parity)
- `wos_ai_stack/langchain_integration/bridges.py`
- `wos_ai_stack/tests/test_rag.py`
- `wos_ai_stack/tests/test_langchain_integration.py`

## Deepened vs already present

| Already present | Deepened in this pass |
|-----------------|------------------------|
| Domain/profile separation, semantic expansion, JSON corpus cache | Explicit limits doc + atomic save + `INDEX_VERSION` bump |
| `RetrievalHit` with `chunk_id` | Trace fields on results/packs + `chunk_id` in `sources` and LangChain metadata |
| Heuristic `canonical_priority` | Published tree tier + path-based `module_id` |
| Hand-tuned `SEMANTIC_CANON` | Small additions (`tension`, `strained`) with test proof |

## Where the improved layer is used

- **Runtime-adjacent:** `StoryRuntimeManager` → `RuntimeTurnGraphExecutor` → `wos.context_pack.build` (capability path); LangGraph fallback dict includes trace fields.
- **Writers-room:** `writers_room_service` → `wos.context_pack.build` (response `retrieval` now includes trace fields from capability handler).
- **Improvement:** `improvement_routes` → `wos.context_pack.build` (same retrieval payload shape).

## What remains intentionally lightweight

- No embedding model or vector database; scoring remains sparse cosine over normalized terms.
- Source selection is glob-capped (`max_sources`); not a full repository crawl.
- JSON snapshot is suitable for single-host/dev workflows, not a durability or scale story.

## Tests added or updated

- Extended `test_context_pack_exposes_attribution_and_selection_notes` for `chunk_id`, `score`, and corpus trace on the pack.
- `test_retrieval_gracefully_handles_sparse_or_absent_corpus` asserts trace fields on empty-corpus results.
- **New:** `test_published_tree_outranks_module_tree_when_content_overlaps`
- **New:** `test_module_id_inferred_from_modules_path_not_collapsed`
- **New:** `test_semantic_canon_maps_tension_to_conflict`
- **New:** `test_improvement_profile_surfaces_evaluation_artifact`
- **New:** `test_persistent_rag_store_roundtrip_preserves_chunks`
- **Updated:** `test_langchain_retriever_bridge_returns_documents` metadata assertions.

## Exact test commands run

```text
python -m pytest wos_ai_stack/tests/test_rag.py wos_ai_stack/tests/test_langchain_integration.py -v --tb=short
# 19 passed

python -m pytest wos_ai_stack/tests/test_langgraph_runtime.py -v --tb=short
# 6 passed

cd world-engine && python -m pytest tests/test_story_runtime_rag_runtime.py -v --tb=short
# 8 passed

cd backend && python -m pytest tests/test_writers_room_routes.py -v --tb=short
# 4 passed
```

## Reason for verdict

Retrieval is **materially more traceable** (corpus fingerprint, index version, chunk IDs in evidence surfaces), **canonical published paths are prioritized** with an automated test, **module scoping is path-derived** instead of a single hard-coded module, persistence is **safer on crash**, and **operational tests** cover runtime-adjacent, writers-room, and improvement-domain behavior.

## Remaining risk

- Semantic quality still depends on small hand-maintained synonym maps; edge paraphrases may miss without further curation.
- Published vs draft conventions assume `content/published/<module>/` layout; repos that omit it only get module-tree priority.
