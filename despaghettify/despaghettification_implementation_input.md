# Despaghettification — information input list for implementers

*Path:* `despaghettify/despaghettification_implementation_input.md` — Overview: [README.md](README.md).

This document is **not** part of the frozen consolidation archive under [`docs/archive/documentation-consolidation-2026/`](../docs/archive/documentation-consolidation-2026/). That archive holds **completed** findings and migration evidence (ledgers, topic map, validation reports) — **do not overwrite or “continue writing” those files**.

Here you find the **living working basis**: structural and spaghetti topics in **code**, prioritised input rows for task implementers, coordination rules, and an **optional** progress note. Like documentation consolidation 2026: **one canonical truth per topic** — applied here to **code structure** (fewer duplicates, clearer boundaries, smaller coherent modules).

**This file is part of wave discipline:** Whoever implements a **despaghettification wave** in code (new helper modules, noticeable AST/structure change) **updates this Markdown in the same wave** — not only the code. Details: § **“Maintaining this file during structural waves”** under coordination. This does **not** replace pre/post artefacts under `despaghettify/state/artifacts/…` (they remain mandatory per [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md)); it complements them as the **functional** entry and priority track.

## Link to `despaghettify/state/` (execution governance, pre/post)

This document is **not** a replacement for [`state/EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md); it is the **functional input side** for structural refactors that should use the **same** evidence and restart rules.

| Governance building block | Role for despaghettification |
|---------------------------|------------------------------|
| [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md) | Mandatory: read state document, **pre** and **post** artefacts per wave, compare pre→post, update state from evidence (**completion gate**). |
| [`WORKSTREAM_INDEX.md`](state/WORKSTREAM_INDEX.md) | Maps **workstream** → `artifacts/workstreams/<slug>/pre|post/`. |
| [`state/README.md`](state/README.md) | Entry to the state hub. |
| `despaghettify/state/artifacts/repo_governance_rollout/pre|post/` | Optional for **repo-wide** waves (e.g. large diff across packages); useful when a structural wave needs the same repo commands as the rollout. |

**Artefact paths (canonical, relative to `despaghettify/state/`):**

- Per affected workstream: `artifacts/workstreams/<workstream>/pre/` and `…/post/`.
- Slugs as in the index: `backend_runtime_services`, `ai_stack`, `administration_tool`, `world_engine` (documentation only if MkDocs/nav is in scope).

**Naming convention for structural waves (DS-*):**

- Session/wave prefix as today: `session_YYYYMMDD_…`.
- **DS-ID in the filename**, e.g. `session_YYYYMMDD_DS-001_scope_snapshot.txt`, `session_YYYYMMDD_DS-001_pytest_collect.exit.txt`, `session_YYYYMMDD_DS-001_pre_post_comparison.json` (the latter typically under **`post/`**).
- At least **one** human-readable artefact (`.txt`/`.md`) and **preferably** one machine-readable (`.json`) — as governance requires.

**DS-ID → primary workstream (where to place pre/post):**

| ID | Primary workstream (`artifacts/workstreams/…`) | Also involved (own pre/post only for real scope) |
|----|--------------------------------------------------|-----------------------------------------------------|
| DS-001 (runtime cycle break) | `backend_runtime_services` | `ai_stack` (if turn-execution interfaces need AI-stack adapters) |
| DS-002 (writers room pipeline split) | `backend_runtime_services` | `ai_stack` |
| DS-003 (RAG module decomposition) | `ai_stack` | `backend_runtime_services` |
| DS-004 (global state + constants hardening) | `backend_runtime_services` | `ai_stack`, `world_engine` |
| DS-005 (control-flow simplification in API/service handlers) | `backend_runtime_services` | `administration_tool` (if shared handler patterns are extracted) |

**Fill in:** For each active **DS-*** one row (or a group sharing the same primary workstream); slugs as in [`WORKSTREAM_INDEX.md`](state/WORKSTREAM_INDEX.md): `backend_runtime_services`, `ai_stack`, `administration_tool`, `world_engine`, `documentation`. Repo-wide cross-check without product code: optional `artifacts/repo_governance_rollout/pre|post/` (e.g. **DS-REPLAY-G**).

Implementers: tick the **completion gate** from `EXECUTION_GOVERNANCE.md`; record the wave and new artefact paths in the matching `WORKSTREAM_*_STATE.md`. Avoid crossings: one clear wave owner per **DS-ID**; multiple workstreams only with agreed **separate** artefact sets.

## Link to documentation-consolidation-2026

| Archive artefact | Link to code despaghettification |
|------------------|----------------------------------|
| [`TOPIC_CONSOLIDATION_MAP.md`](../docs/archive/documentation-consolidation-2026/TOPIC_CONSOLIDATION_MAP.md) | Topics map to **one** active doc per topic; code refactors should not reopen the same functional edge across two parallel implementations (e.g. RAG, MCP, runtime). |
| [`DURABLE_TRUTH_MIGRATION_LEDGER.md`](../docs/archive/documentation-consolidation-2026/DURABLE_TRUTH_MIGRATION_LEDGER.md) | Model for **traceable** moves instead of silent drift; despaghettification: **one source** for shared building blocks (e.g. builtins). |
| [`FINAL_DOCUMENTATION_VALIDATION_REPORT.md`](../docs/archive/documentation-consolidation-2026/FINAL_DOCUMENTATION_VALIDATION_REPORT.md) | Closure criteria for a **documentation** strand; for code: tests/CI green, behaviour unchanged, interfaces explicit. |

## Coordination — extend work without colliding

1. **Claims:** Before larger refactors, name the **ID(s)** in team/issue/PR (all **`DS-*** you are taking from this information input list). Preferably **one** clear owner per ID.
2. **No double track:** Two implementers do **not** work the same ID in parallel; if split: separate sub-tasks explicitly (e.g. DS-003a backend wiring only, DS-003b world-engine import only).
3. **Leave archive alone:** Do not mirror code findings into `documentation-consolidation-2026/*.md`; use CHANGELOG, PR description, **`despaghettify/state/` artefacts**, **this input list** (§ *Latest structure scan*, filled DS rows, optional § *progress*) and matching **`WORKSTREAM_*_STATE.md`**.
4. **Interfaces first:** For cycles (runtime cluster) small **DTO / protocol modules** before big moves; avoids PRs that touch half of `app.runtime` at once.
5. **Measurement optional:** AST/review-based lengths are **guidance**; success is **understandable** boundaries + green suites, not a percentage score.

### Maintaining this file during structural waves (move with the code)

For every relevant **DS-*** / despaghettification **wave**, update this file in the **same PR/commit logic** (not “code only”):

| What | Content |
|------|---------|
| **Information input list** | Per **DS-***: maintain columns (*hint / measurement idea*, *direction*, *collision hint*); mark completed waves briefly. |
| **§ Latest structure scan** | After measurable change: **main table** (as-of date, **M7** overall, 7 category scores, and AST telemetry **N / L₅₀ / L₁₀₀ / D₆**); subsection **M7 calculation and thresholds**; optional **extra checks**; **open hotspots** on **every** [spaghetti-check-task.md](spaghetti-check-task.md) run (**prune** solved items — never list resolved problems); [spaghetti-solve-task.md](spaghetti-solve-task.md) when a wave **resolves** listed hotspots (clear, shorten, or rewrite remaining risk). For runtime edges `tools/ds005_runtime_import_check.py`. Rankings: script output only. |
| **§ Recommended implementation order** | Update when priority, dependency, or phase changes; optional Mermaid. |
| **§ Progress / work log** | Optional **one** new row: DS-ID(s), short summary, gates/tests, pre/post paths (or “see PR”). |
| **DS-ID → workstream table** | Place new or moved **DS-*** here; note co-involved workstreams. |

**Governance:** `despaghettify/state/artifacts/workstreams/<slug>/pre|post/` and `WORKSTREAM_*_STATE.md` remain **formal** evidence; this file is the **compact** working and review map.

## Latest structure scan (orientation, no warranty)

**Purpose:** A **fillable** overview after measurable runs — after larger refactors update **date**, **M7 inputs**, and optional **extra checks** / **open hotspots**. Measurement flow, builtins grep, runtime spot check: [spaghetti-check-task.md](spaghetti-check-task.md). The spaghetti check maintains the **information input list** and **recommended implementation order** when **M7 is elevated** (`M7 >= 40%`) **or** at least one category score is **critical** (`>= 70%`); otherwise this scan section (including M7 and category breakdown) is enough. **Rankings** and longest functions: output of `python tools/spaghetti_ast_scan.py` only (repo root). **Open hotspots** (known structural callouts in the table row below): [spaghetti-solve-task.md](spaghetti-solve-task.md) **independently** clears or narrows items when a wave resolves them — same PR as the code, even when thresholds are below trigger so the check task does not edit other cells. On every [spaghetti-check-task.md](spaghetti-check-task.md) run, **prune** **Open hotspots** so it never lists **already solved** problems (only current unresolved callouts).

| Field | Value (adjust when updating scan) |
|-------|-------------------------------------|
| **As of (date)** | **2026-04-11** (spaghetti-check-task + 7-category review) |
| Spaghetti scan command | `python tools/spaghetti_ast_scan.py` (ROOTS = *measurement scope* column) |
| Measurement scope (ROOTS) | `backend/app`, `world-engine/app`, `ai_stack`, `story_runtime_core`, `tools/mcp_server`, `administration-tool` |
| **M7** — weighted 7-category spaghetti score | **≈ 61.9%** (elevated: update DS list and implementation order) |
| C1: Circular dependencies | **48%** |
| C2: Nesting depth | **30%** |
| C3: Long functions + complexity | **78%** |
| C4: Multi-responsibility modules | **72%** |
| C5: Magic numbers + global state | **66%** |
| C6: Missing abstractions / duplication | **62%** |
| C7: Confusing control flow | **69%** |
| **AST telemetry N / L₅₀ / L₁₀₀ / D₆** | **4143 / 257 / 70 / 0** |
| Extra check builtins | Grep `def build_god_of_carnage_solo` in `**/builtins.py`: **0** hits (**2026-04-11**) |
| Extra check runtime | `python tools/ds005_runtime_import_check.py` **exit 0**; no `TYPE_CHECKING` under `backend/app/runtime/**/*.py`; comments / local imports for cycle avoidance e.g. `turn_executor`, `ai_decision`, `role_structured_decision`, `ai_failure_recovery` (**2026-04-11** spot check) |
| **Open hotspots** | **DS-001, DS-002, DS-004:** **closed 2026-04-11**. **DS-003:** `ai_stack/rag.py` **~88** LOC + split modules (stages 1–11, through 2026-04-11). `ds005` **exit 0**. |

### Score *M7* — inputs, weights, and calculation

| Symbol | Meaning | Value |
|--------|---------|-------|
| **C1** | Circular dependencies | **48** |
| **C2** | Nesting depth | **30** |
| **C3** | Long functions + complexity | **78** |
| **C4** | Multi-responsibility modules | **72** |
| **C5** | Magic numbers + global state | **66** |
| **C6** | Missing abstractions / duplication | **62** |
| **C7** | Confusing control flow | **69** |

**Formula:** `M7 = 0.20*C1 + 0.10*C2 + 0.20*C3 + 0.15*C4 + 0.10*C5 + 0.15*C6 + 0.10*C7`

**Evaluation:** `0.20*48 + 0.10*30 + 0.20*78 + 0.15*72 + 0.10*66 + 0.15*62 + 0.10*69 = 61.9` → one decimal **≈ 61.9%** (copy **M7** into the main table).

**Trigger policy for check task updates:**

- If **M7 >= 40%** or **any category >= 70%**: update § *Information input list* and § *Recommended implementation order*.
- If **M7 < 40%** and no category is critical: update only § *Latest structure scan*.

*Note:* M7 is still heuristic; AST telemetry (`N/L₅₀/L₁₀₀/D₆`) remains mandatory context for trend comparability.

## Information input list (extensible)

Each row: **ID**, **pattern**, **location**, **hint / measurement idea**, **direction**, **collision hint** (what is risky in parallel).

| ID | pattern | location (typical) | hint / measurement idea | direction (solution sketch) | collision hint |
|----|---------|--------------------|-------------------------|----------------------------|----------------|
| DS-001 | Runtime import cycles and local-import workaround drift — **closed 2026-04-11** | `turn_executor.py`, `turn_executor_validated_pipeline.py`, `turn_executor_decision_delta.py`, `validators.py` | `ds005` + import graph; validated pipeline must not depend on `turn_executor` | Neutral delta module + `validators.validate_decision` in validated path; `turn_executor` lazy-imports pipeline only | High: touches core turn path; do not run parallel edits on same runtime files |
| DS-002 | God-function / orchestration monolith — **closed 2026-04-11** | `writers_room_pipeline.py` (**82** AST lines on `_execute_writers_room_workflow_package`); `writers_room_pipeline_{manifest,context_preview,retrieval_stage,generation_stage,packaging_stage,finalize_stage}.py` | Function length, branch count, number of responsibilities in one function | **Closed:** stage modules + thin orchestrator; closure artefact `post/session_20260411_DS-002_closure_notes.md` | High: large blast radius in one file; split by stage owners only with strict integration checkpoints |
| DS-003 | Multi-responsibility RAG monolith and mixed policy/scoring/persistence concerns | `ai_stack/rag.py` (**~88** LOC, 2026-04-11) + split modules (DTOs, corpus, ingestion, runtime bootstrap, context retriever/pack/store, retrieval support/policy/lexical, embedding, governance, types/constants) | File-level function/class density, import breadth, duplicate helper patterns | **Stages 1–11 + optional pass:** retrieval DTOs in `rag_retrieval_dtos.py`; `rag` remains compatibility facade. **Next:** close DS-003 when satisfied; optional call-site migration off `ai_stack.rag` only where worth it | High: many call sites; coordinate adapter/facade changes first to avoid API breakage |
| DS-004 (**closed 2026-04-11**) | Magic numbers and mutable module-level state | `backend/app/api/v1/*_routes.py` (24 files), `backend/app/extensions.py` | **CLOSED:** 2 config modules (route_constants.py, limiter_config.py); 24 routes refactored (672 refs updated); extensions hardened. Pre: `session_20260411_DS-004_scope_snapshot.md` + `.json`; Post: `session_20260411_DS-004_post.md` + `.json`. 31 new tests, 241 backend tests passing (zero regressions). | Centralized thresholds in frozen dataclasses; replaced mutable globals with factory functions; all constants immutable. | Medium (MITIGATED): tests verify immutability, config drift is now compile-time checkable. |
| DS-005 | Confusing control flow (many branches/returns in handlers) | `user_routes_users_update.py` (wave 1); `user_service` / `news_service` (waves 2–4: create/update/translation-upsert guards, `user_service_account_guards.py`) | Branch/return density and error-path fan-out | **Stages 1–4 done:** PUT; account + `create_news`; `update_news`; `upsert_article_translation`. **Next:** optional further routes or close this slice | Medium: endpoint semantics can regress; requires strong request/response regression tests |

**New rows:** consecutive **DS-001**, **DS-002**, … (or your ID scheme); briefly justify why it is a structure/spaghetti topic. Per § *DS-ID → primary workstream* pick `artifacts/workstreams/<slug>/pre|post/` paths.

## Recommended implementation order

Prioritised **phases**, **order**, and **dependencies** — aligned with § **information input list** and [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md). After filling: optional subsections per phase, Mermaid `flowchart`, gates per wave, short priority list.

| Priority / phase | DS-ID(s) | short logic | workstream (primary) | note (dependencies, gates) |
|------------------|----------|-------------|----------------------|----------------------------|
| Phase 1: dependency untangle | DS-001 | Break runtime cycles before deeper refactors to stabilize module boundaries | `backend_runtime_services` | **Done 2026-04-11** — `ds005` + `pytest …/test_turn_executor.py`; see work log. |
| Phase 2: monolith split (service layer) | DS-002 | Decompose biggest backend orchestration hotspot into composable steps | `backend_runtime_services` | **Done 2026-04-11** — Writers Room stage modules + closure `post/session_20260411_DS-002_closure_notes.md`; `pytest tests/writers_room/` 64 passed. Next primary structural hotspot: **DS-003**. |
| Phase 3: monolith split (AI stack) | DS-003 | Decompose `ai_stack/rag.py` by concern while preserving facade compatibility | `ai_stack` | DS-002 closed; strict API compatibility checks on facade |
| Phase 4: state and constant hardening | DS-004 (**closed 2026-04-11**) | Removed hardcoded values from 24 routes and extensions.py; centralized in frozen config. | `backend_runtime_services` | Completed in single wave; zero behavior drift (identical tests pre/post). |
| Phase 5: control-flow cleanup | DS-005 | Flatten high-risk handlers and service methods with policy/guard extraction | `backend_runtime_services` | End with focused endpoint regression suite and updated hotspots list |

**Fill in:** take rows from the input table; make hard chains explicit (e.g. interfaces before large moves). Coordination § *Maintaining this file*: when priority changes or new **DS-*** appear, update this section and Mermaid if used.

**Implementation** of phases until documented closure (completion gate, session by session): [spaghetti-solve-task.md](spaghetti-solve-task.md).

## Progress / work log (optional, in addition to mandatory maintenance above)

Implementers may **briefly** record visible progress (for reviewers and the next iteration). **Mandatory** for structural waves remains **updating the input table, § structure scan, and — if needed — this log** (see coordination § *Maintaining this file*). **Additionally**, new waves add **pre/post files** under `despaghettify/state/artifacts/…` (see `EXECUTION_GOVERNANCE.md`); older session artefacts may be missing if intentionally cleaned — proof then via Git/CI/PR. Not a substitute for issues/PRs.

| date | ID(s) | short description | pre artefacts (rel. to `despaghettify/state/`) | post artefacts (rel. to `despaghettify/state/`) | state doc(s) updated | PR / commit |
|------|-------|-------------------|----------------------------------------|----------------------------------------|----------------------|-------------|
| 2026-04-11 | **DS-004** (closure) | Magic numbers + mutable state hardening. Config modules: route_constants.py (frozen dataclasses for auth, session, site, user, pagination, HTTP codes), limiter_config.py (period mappings, defaults). Refactored: 24 route files (672 references). Hardened: extensions.py (no embedded constants). Tests: 31 new, 241 backend suite all passing. Pre: `session_20260411_DS-004_scope_snapshot.md` + `.json`. Post: `session_20260411_DS-004_post.md` + `.json`. | — | `artifacts/workstreams/backend_runtime_services/post/session_20260411_DS-004_post.md` + `session_20260411_DS-004_pre_post_comparison.json` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-10 | **DS-005** (stage 4) | `news_service_translation_upsert_guards` for `upsert_article_translation` (update + create paths). `pytest` `test_news_service.py` **48 passed**. | — | `artifacts/workstreams/backend_runtime_services/post/session_20260410_DS-005_stage4_translation_upsert_guards_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-005** (stage 3) | `news_service_update_guards.validate_news_update_patch` + `normalize_news_slug` export; `update_news` applies validated patch. `pytest` `test_news_service.py` **48 passed**. | — | `artifacts/workstreams/backend_runtime_services/post/session_20260411_DS-005_stage3_update_news_guards_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-005** (stage 2) | `news_service_create_guards` + `user_service_account_guards`; `create_news`, `create_user`, `change_password` delegate validation. `pytest` `test_news_service` + `test_user_service` + `test_service_layer` **125 passed**. | — | `artifacts/workstreams/backend_runtime_services/post/session_20260411_DS-005_stage2_news_user_create_guards_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-005** (stage 1) | PUT `/users/<id>`: `user_routes_users_update_guards.py` + slim `user_routes_users_update.py`. `pytest` `test_user_routes -k users_update` **55**; `test_users_api -k users_update` **4 passed**. | — | `artifacts/workstreams/backend_runtime_services/post/session_20260411_DS-005_stage1_user_put_guards_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-001/002/003** (follow-up) | **DS-001:** `ds005` adds `app.runtime.validators`. **DS-002:** `writers_room_store.py`. **DS-003:** tests import `INDEX_VERSION` / `ContextRetriever` from canonical modules. `pytest` ai_stack RAG trio **73**; `backend` writers_room + improvement_routes **88 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_followup_001_002_003_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-001/002/003** (optional pass) | **DS-003:** `rag_retrieval_dtos.py` + direct imports in support/rerank/langgraph; `rag.py` **~88** LOC. **DS-001:** `ds005` + `post/DS-001_runtime_import_policy_note.md`. **DS-002:** `writers_room_pipeline_workflow.py`. `pytest` ai_stack RAG trio **73**; `backend/tests/writers_room` **64 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_optional_combined_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 11) | `rag_runtime_bootstrap.py` — `build_runtime_retriever`; `rag.py` lazy delegate **~163** LOC. `pytest` ai_stack **73 passed**; `backend/tests/writers_room` + `improvement` subset **41 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage11_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-10 | **DS-003** (stage 10) | `rag_corpus.py` — `CorpusChunk`, `InMemoryRetrievalCorpus`, `_ScoredCandidate`; breaks `rag` ↔ `rag_ingestion` cycle; `rag.py` **~175** LOC. `pytest` `test_rag.py` + `test_retrieval_governance_summary.py` + `test_langgraph_runtime.py` **73 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260410_DS-003_stage10_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 9) | `rag_ingestion.py` — `RagIngestionPipeline`, path/content helpers; `rag.py` **~314** LOC. `pytest` `test_rag.py` + `test_retrieval_governance_summary.py` + `test_langgraph_runtime.py` **73 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage9_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 8) | `rag_context_retriever.py` — `ContextRetriever` + `_run_retrieval_encode_score_pool_phase`; `rag.py` **~470** LOC. `pytest` `test_rag.py` + `test_retrieval_governance_summary.py` **63 passed**; `test_langgraph_runtime.py` **10 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage8_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 7) | `rag_context_pack_assembler.py` + `rag_persistent_store.py`; `rag.py` **~797** LOC. `pytest` `test_rag.py` **56 passed**, `test_retrieval_governance_summary.py` **7 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage7_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 6) | `rag_retrieval_support.py` — query profile, prefix/quality notes, rerank merge (lazy `compute_rerank_adjustments`), `RetrievalResult` builders (lazy types), pool sort, `_RetrievalEncodeScorePoolPhase`; `rag.py` **~1000** LOC. `pytest` `test_rag.py` **56 passed**, `test_retrieval_governance_summary.py` **7 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage6_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 5) | `rag_retrieval_policy_pool.py` — pool sizing, hard/soft policy, pack roles/notes, dedup, pack sort; `rag.py` **~1286** LOC. `pytest` `test_rag.py` **56 passed**, `test_retrieval_governance_summary.py` **7 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage5_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 4) | `rag_retrieval_lexical.py` — semantic/profile maps + sparse/hybrid helpers; `rag.py` **~1515** LOC. `pytest` `test_rag.py` **56 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage4_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 3) | `rag_embedding_index.py` — dense index load/save/ensure; `rag.py` **~1706** LOC. `pytest` `ai_stack/tests/test_rag.py` **56 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage3_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 2) | `rag_governance.py` — `governance_view_for_chunk`; `rag.py` **~1915** LOC. `pytest` `test_rag.py` **56 passed**, `test_retrieval_governance_summary.py` **7 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage2_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-003** (stage 1) | `rag_types.py` + `rag_constants.py` split from `rag.py` (~1973 LOC left); `pytest` `ai_stack/tests/test_rag.py` **56 passed**, `test_retrieval_governance_summary.py` **7 passed**. | — | `artifacts/workstreams/ai_stack/post/session_20260411_DS-003_stage1_post.md` | [WORKSTREAM_AI_STACK_STATE.md](state/WORKSTREAM_AI_STACK_STATE.md) | — |
| 2026-04-11 | **DS-002** (stage 4) | `writers_room_pipeline_packaging_stage.py` — issues, recommendations, review bundle, proposal package, aggregates; main workflow **185** AST lines. `pytest tests/writers_room/` **64 passed**. | (stage 1 pre) | `post/session_20260411_DS-002_stage4_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-002** (stage 3) | `writers_room_pipeline_generation_stage.py` — preflight + synthesis routing + LangChain + mock fallback; main workflow **449** AST lines. `pytest tests/writers_room/` **64 passed**. Re-export `_norm_wr_adapter` from orchestrator for tests. | (stage 1 pre) | `post/session_20260411_DS-002_stage3_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-002** (stage 2) | Extracted `run_writers_room_retrieval_stage` → `writers_room_pipeline_retrieval_stage.py`; `_execute_writers_room_workflow_package` **585** AST lines (was 603). `pytest tests/writers_room/` **64 passed**. | (same baseline as stage 1) | `post/session_20260411_DS-002_stage2_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-002** (stage 1) | Removed duplicate helper defs in `writers_room_pipeline.py` (manifest + context preview live only in split modules). `_execute_writers_room_workflow_package` still **603** AST lines. `pytest tests/writers_room/` **64 passed**. | `pre/session_20260411_DS-002_stage1_baseline.md` | `post/session_20260411_DS-002_stage1_post.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-001** (closure) | **Full DS-001:** `turn_executor_validated_pipeline` imports `validate_decision` from `app.runtime.validators` (no `turn_executor`); `turn_executor` drops unused `validate_decision` re-export. System-error test patches `turn_executor_validated_pipeline.validate_decision`. `ds005` **exit 0**; `pytest backend/tests/runtime/test_turn_executor.py` **31 passed**. Post addendum: `…/post/session_20260411_DS-001_closure_notes.md`. | (same pre as partial wave) | `post/session_20260411_DS-001_closure_notes.md` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | **DS-001** (partial wave) | Structural: `turn_executor_decision_delta.py` extracted; validated pipeline uses it for construct/apply/guard; `ds005` **exit 0**; `pytest backend/tests/runtime/test_turn_executor.py` **31 passed**. Pre/post: `artifacts/workstreams/backend_runtime_services/pre/session_20260411_DS-001_coupling_baseline.md`, `…/post/session_20260411_DS-001_coupling_post.md`, `…/post/session_20260411_DS-001_pre_post_comparison.json`. | `pre/session_20260411_DS-001_coupling_baseline.md` | `post/session_20260411_DS-001_*` | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | — (spaghetti-solve Phase 1) | [spaghetti-solve-task.md](spaghetti-solve-task.md) **Phase 1** — review § *Information input list* / § *Recommended implementation order*: rows **DS-001..DS-005** match phase table; no contradiction stop. **Open hotspots** reconciled with repo: `_execute_writers_room_workflow_package` **603** AST lines; `turn_executor` ↔ `turn_executor_validated_pipeline` bidirectional **lazy** imports (`ds005` **exit 0**); `rag.py` **~1890** lines. **Next (Phase 2):** claim **DS-001**, then pre/post under `artifacts/workstreams/backend_runtime_services/` per [EXECUTION_GOVERNANCE.md](state/EXECUTION_GOVERNANCE.md). | — | — | [WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md](state/WORKSTREAM_BACKEND_RUNTIME_AND_SERVICES_STATE.md) | — |
| 2026-04-11 | — (spaghetti-check) | [spaghetti-check-task.md](spaghetti-check-task.md): `spaghetti_ast_scan.py` telemetry **N=4143**, **L₅₀=257**, **L₁₀₀=70**, **D₆=0**; 7-category score **M7≈61.9%** with critical C3/C4. Builtins grep **0**; `ds005_runtime_import_check.py` **exit 0**; runtime spot check as in scan table. | — | — | — | — |
| — | — | — | — | — | — | — |

**New rows:** chronologically (**newest first** recommended); **DS-ID(s)**, gates/tests run, pre/post paths as in [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md); for scan/docs-only updates note briefly. Longer history: Git, PRs, `WORKSTREAM_*_STATE.md`.

## Canonical technical reading paths (after refactor)

After structural changes to runtime/AI/RAG/MCP, align **active** technical docs (not the 2026 archive):

- Runtime / authority: [`docs/technical/runtime/runtime-authority-and-state-flow.md`](../docs/technical/runtime/runtime-authority-and-state-flow.md) — supervisor orchestration: `supervisor_orchestrate_execute.py` + `supervisor_orchestrate_execute_sections.py`; subagent invocation: `supervisor_invoke_agent.py` + `supervisor_invoke_agent_sections.py`
- Mock turn path: `turn_executor.py` orchestrates; validated branch in `turn_executor_validated_pipeline.py` (`validators.validate_decision` + `turn_executor_decision_delta`); **DS-001** closed (2026-04-11).
- Writers Room pipeline: `writers_room_pipeline.py` orchestrates workflow package; manifest / preview / retrieval / generation / packaging / finalize stages in `writers_room_pipeline_{manifest,context_preview,retrieval_stage,generation_stage,packaging_stage,finalize_stage}.py` — **DS-002** closed (2026-04-11); closure `post/session_20260411_DS-002_closure_notes.md`.
- Inspector projection (backend): `inspector_turn_projection_sections.py` orchestrates; pieces in `inspector_turn_projection_sections_{utils,constants,semantic,provenance}.py`
- Admin tool routes: `administration-tool/route_registration.py` + `route_registration_{proxy,pages,manage,security}.py`
- God-of-Carnage solo builtin (core): `story_runtime_core/goc_solo_builtin_template.py` + `goc_solo_builtin_catalog.py` + `goc_solo_builtin_roles_rooms.py`
- AI / RAG / LangGraph: [`docs/technical/ai/RAG.md`](../docs/technical/ai/RAG.md), [`docs/technical/integration/LangGraph.md`](../docs/technical/integration/LangGraph.md), [`docs/technical/integration/MCP.md`](../docs/technical/integration/MCP.md) — RAG facade `ai_stack/rag.py`; types/constants; governance; dense index; lexical/hybrid helpers (`rag_retrieval_lexical`) (**DS-003** stages 1–4, 2026-04-11).
- Dev seam overview: [`docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md`](../docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md)

---

*Created as an operational bridge between structural code work, the state hub under [`despaghettify/state/`](state/README.md) (pre/post evidence), and the completed documentation archive of 2026.*
