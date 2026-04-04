# RAG in World of Shadows

Status: C1 repaired baseline (semantic + persistent operational retrieval).

## Purpose

Provide retrieval support for authoritative runtime, Writers-Room review workflows, and improvement/evaluation workflows while keeping narrative authority in World-Engine and governance in backend/admin layers.

## Storage approach

- Runtime retriever persistence is active by default through `.wos/rag/runtime_corpus.json`.
- Startup retrieval now attempts cache load first and rebuilds only when the source fingerprint changes.
- Source fingerprinting is based on selected source file path + size + mtime metadata.
- Persisted corpus carries:
  - `index_version`
  - `corpus_fingerprint`
  - per-chunk `source_version` and `source_hash`
  - retrieval profile version markers

This is a local persistent store, not a distributed vector database.

## Ingestion and metadata/versioning

Ingestion reads project-owned sources:

- `content/**/*` authored materials (`.md`, `.json`, `.yml`, `.yaml`)
- `docs/architecture/**/*.md` policy and architecture guidance
- `docs/reports/**/*.md` review and evaluation artifacts
- `world-engine/app/var/runs/**/*.json` runtime transcript-like artifacts

Chunk metadata includes:

- `source_path`, `source_name`, `content_class`
- `source_version` (`sha256:<prefix>`) and `source_hash`
- `canonical_priority` (authored/canonical material receives higher priority)
- semantic sparse-vector terms and norm

When source content changes, chunk source versions change accordingly.

## Embedding/retrieval approach

- Retrieval uses a local sparse semantic representation with:
  - canonicalized token normalization
  - concept expansion terms
  - weighted sparse vectors with IDF weighting
  - cosine similarity ranking
- Retrieval remains deterministic and does not require external embedding services.
- Profile and context boosts are applied on top of semantic similarity:
  - content-class boosts by profile
  - canonical priority boost
  - module match boost
  - scene hint boost

This is materially semantic compared to prior lexical overlap scoring, while remaining lightweight and local.

## Retrieval domains and active profiles

- `runtime` domain, profile `runtime_turn_support`
- `writers_room` domain, profile `writers_review`
- `improvement` domain, profile `improvement_eval`

Domain content access gates remain enforced before ranking.

## Canonical authored/published prioritization

Canonical authored material is treated as a first-class source through:

- explicit authored-module classification
- canonical-priority metadata at ingestion
- profile-level canonical boost during ranking

This keeps runtime retrieval biased toward canonical authored truth where relevant.

## Real wiring in active paths

- World-Engine runtime turn execution uses `build_runtime_retriever(...)` and therefore the persistent semantic corpus path.
- Writers-Room workflow uses the same retrieval core through capability invocation (`wos.context_pack.build`) with `writers_review` profile.

## Current limits

- Semantic retrieval is local sparse-vector semantics, not transformer embedding search.
- Persistence is single-node local JSON storage; no distributed index, sharding, or service-managed durability.
- There is no advanced profile auto-tuning or retrieval quality dashboard yet.
