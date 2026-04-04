# H1 gate report — harden embedding backend and cache behavior

## Verdict: **Pass**

## Scope completed

- Clarified embedding dependency stance: **optional for sparse-only RAG**; **strongly recommended for full BC-next / C1-next hybrid verification** when installs include `fastembed` and a usable model cache.
- Added **explicit backend probe** (`embedding_backend_probe` / `EmbeddingBackendReport`) with stable reason codes (`embeddings_disabled_by_env`, `fastembed_import_failed`, `embedding_encode_failed`).
- Added **`WOS_RAG_EMBEDDING_CACHE_DIR`**, forwarded to `fastembed.TextEmbedding(cache_dir=...)` for deterministic, test-friendly cache roots (CI can set this to a temp or pre-seeded directory).
- Introduced a **per-process lazy singleton** for `TextEmbedding` (keyed by model id + resolved cache dir) to avoid repeated model construction and make runtime behavior stable within a worker.
- Added **`clear_embedding_model_singleton()`** for tests and config reload scenarios when the cache directory or model choice must be reapplied.
- Centralized **`requires_embeddings`** pytest skip logic in `wos_ai_stack/tests/embedding_markers.py` (single definition of “backend ready”, aligned with the probe).
- Updated architecture doc **`rag_in_world_of_shadows.md`** to describe hybrid + sparse, env vars, and remaining environment risk honestly.

## Files changed

| Area | Files |
|------|--------|
| Embedding backend | `wos_ai_stack/semantic_embedding.py` |
| Tests | `wos_ai_stack/tests/test_rag.py`, `wos_ai_stack/tests/test_semantic_embedding.py` (new), `wos_ai_stack/tests/embedding_markers.py` (new), `wos_ai_stack/tests/__init__.py` (new) |
| Docs | `docs/architecture/rag_in_world_of_shadows.md`, `docs/reports/ai_stack_gates/C1_NEXT_GATE_REPORT.md` (cross-reference only) |
| Gate | `docs/reports/ai_stack_gates/H1_EMBEDDING_HARDENING_GATE_REPORT.md` (this file) |

## What was hardened vs what already existed

| Topic | Before | After |
|-------|--------|--------|
| Dependency clarity | `fastembed` in requirements; sparse fallback documented in code comments and C1 report | Same stack; **documented** optional vs verification-recommended in `rag_in_world_of_shadows.md` and module docstring |
| Cache path | Implicit fastembed / HF hub default only | **`WOS_RAG_EMBEDDING_CACHE_DIR`** explicitly passed into `TextEmbedding` |
| Backend visibility | Infer from `retrieval_route` / skip reasons | **`embedding_backend_probe()`** returns structured availability and reason codes |
| In-process model loading | New `TextEmbedding` on every `encode_texts` call | **Lazy singleton** per `(model_id, cache_dir)` |
| Tests | Skipif via ad-hoc `encode_texts(["ping"])` | Shared **`embedding_markers.requires_embeddings`** + **smoke tests** for disabled env, simulated import failure, cache-dir wiring, singleton reuse |

RAG ranking logic, corpus formats, and hybrid vs sparse scoring in `wos_ai_stack/rag.py` were **not** redesigned.

## How dependency expectations are defined

- **Runtime without hybrid:** valid — omit `fastembed` or set `WOS_RAG_DISABLE_EMBEDDINGS=1`; retrieval uses sparse-only with explicit `retrieval_route=sparse_fallback`.
- **Verification with hybrid:** install `fastembed` (and `numpy`) per `world-engine/requirements.txt` / `backend/requirements.txt`; ensure the ONNX model can be loaded (network once or primed cache); optionally set `WOS_RAG_EMBEDDING_CACHE_DIR` for a fixed root.
- **Introspection:** `embedding_backend_probe()` is the supported check for “can this process run a sample encode?” without mutating `.wos/rag/` artifacts.

## How cache behavior is controlled

- **`WOS_RAG_EMBEDDING_CACHE_DIR`:** if non-empty after strip, used as `cache_dir` for `TextEmbedding`. If unset, `None` is passed and fastembed / hub defaults apply.
- **Standard HF / hub env vars** may still affect layout; they are not overridden by this milestone.
- **Corpus sidecars** (`runtime_embeddings.npz` / `.meta.json`) remain colocated with `runtime_corpus.json` under `.wos/rag/`; behavior unchanged except that encoding now reuses one model instance per process.

## How backend available / unavailable is exposed

- **Code:** `EmbeddingBackendReport` fields and `messages` tuple (reason codes).
- **Retrieval:** existing `retrieval_route`, `embedding_model_id`, and ranking notes (unchanged contract).
- **Tests:** always-on probe tests for disabled env and import failure; gated hybrid tests use `requires_embeddings` with an explicit skip reason string.

## What remains environment-sensitive

- **First-time model download** still depends on network (or a pre-populated cache) unless artifacts already exist under the configured cache dir.
- **ONNX runtime / OS differences** (performance, occasional execution quirks) are outside this repo’s control.
- **Windows + Hugging Face hub:** symlink limitations can trigger hub warnings and slightly different on-disk cache behavior; retrieval still works but disk layout may vary.
- **Hybrid tests** remain `skipif` when `embedding_backend_probe()` is not `available` — that is intentional so the suite does not pretend hybrid passed on machines without a working backend.

## Tests added or updated

- **New:** `wos_ai_stack/tests/test_semantic_embedding.py` — disabled-by-env probe, simulated `fastembed` import failure, `embedding_cache_dir_from_env`, cache_dir passed to constructor (gated), singleton reuse (gated), probe available when backend works (gated).
- **Updated:** `wos_ai_stack/tests/test_rag.py` — imports `requires_embeddings` from `embedding_markers` (same skip semantics, single source of truth).

## Exact test commands run

Host: Windows, Python 3.13.12. All commands executed from repository root `C:\Users\YvesT\PycharmProjects\WorldOfShadows`.

```powershell
Set-Location "C:\Users\YvesT\PycharmProjects\WorldOfShadows"
python -m pytest wos_ai_stack/tests/test_semantic_embedding.py wos_ai_stack/tests/test_rag.py -v --tb=short
```

Result: **26 passed** (including all embedding-gated hybrid tests on this host).

```powershell
Set-Location "C:\Users\YvesT\PycharmProjects\WorldOfShadows"
python -m pytest world-engine/tests/test_story_runtime_rag_runtime.py -v --tb=short
```

Result: **8 passed** (runtime path still exercises RAG assembly with `ContextRetriever` / corpus build as before).

## Reason for verdict

- Embedding behavior is **materially clearer** (probe + docs + env vars).
- Cache roots are **more deterministic** via `WOS_RAG_EMBEDDING_CACHE_DIR` and test coverage of constructor wiring.
- Absence / presence of the backend is **explicit** in code, tests, and docs; no silent change from hybrid to sparse beyond the existing, documented fallback semantics.
- BC-next verification risk is **reduced** by pin-able cache dirs and a single, honest definition of “backend ready” for pytest.
- Remaining sensitivity is **stated above**, not hidden.

## Remaining risk (summary)

Same as “What remains environment-sensitive”: network/model cache, ONNX/OS variance, Windows hub symlink behavior, and skipped hybrid tests when the probe reports unavailable.
