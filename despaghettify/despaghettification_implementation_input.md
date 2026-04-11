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
| **Open hotspots** | `backend/app/services/writers_room_pipeline.py:_execute_writers_room_workflow_package` (603L), `backend/app/runtime/turn_executor.py` ↔ `turn_executor_validated_pipeline.py` import cycle, and `ai_stack/rag.py` (2k+ LOC multi-domain orchestration) remain unresolved and should map to dedicated DS rows. |

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
| DS-001 | Runtime import cycles and local-import workaround drift | `backend/app/runtime/turn_executor.py`, `backend/app/runtime/turn_executor_validated_pipeline.py`, related runtime cycle SCCs | Track SCC count and largest SCC size from internal import graph; verify with `tools/ds005_runtime_import_check.py` | Introduce neutral execution-core interfaces (DTO/protocol module), invert dependencies, remove cycle-causing cross-imports | High: touches core turn path; do not run parallel edits on same runtime files |
| DS-002 | God-function / orchestration monolith | `backend/app/services/writers_room_pipeline.py:_execute_writers_room_workflow_package` | Function length, branch count, number of responsibilities in one function | Slice into bounded pipeline stages with typed input/output payloads and explicit stage contracts | High: large blast radius in one file; split by stage owners only with strict integration checkpoints |
| DS-003 | Multi-responsibility RAG monolith and mixed policy/scoring/persistence concerns | `ai_stack/rag.py` | File-level function/class density, import breadth, duplicate helper patterns | Split into `rag_policy`, `rag_scoring`, `rag_embeddings`, `rag_persistence`, `rag_pack_assembly` while preserving public facade | High: many call sites; coordinate adapter/facade changes first to avoid API breakage |
| DS-004 | Magic numbers and mutable module-level state | `backend/app/api/v1/*_routes.py`, `ai_stack/rag.py`, `backend/app/extensions.py`, runtime input interpreters | Count non-trivial numeric literals and mutable globals per file; track decreases wave by wave | Centralize thresholds in typed config objects and replace mutable globals with scoped state containers/factories | Medium: easy to create hidden behavior drift if constants move without tests |
| DS-005 | Confusing control flow (many branches/returns in handlers) | `backend/app/api/v1/user_routes_users_update.py`, `backend/app/services/user_service.py`, `backend/app/services/news_service.py` | Branch/return density and error-path fan-out | Extract guard-policy evaluators and dedicated error handlers; flatten nested/branchy flows | Medium: endpoint semantics can regress; requires strong request/response regression tests |

**New rows:** consecutive **DS-001**, **DS-002**, … (or your ID scheme); briefly justify why it is a structure/spaghetti topic. Per § *DS-ID → primary workstream* pick `artifacts/workstreams/<slug>/pre|post/` paths.

## Recommended implementation order

Prioritised **phases**, **order**, and **dependencies** — aligned with § **information input list** and [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md). After filling: optional subsections per phase, Mermaid `flowchart`, gates per wave, short priority list.

| Priority / phase | DS-ID(s) | short logic | workstream (primary) | note (dependencies, gates) |
|------------------|----------|-------------|----------------------|----------------------------|
| Phase 1: dependency untangle | DS-001 | Break runtime cycles before deeper refactors to stabilize module boundaries | `backend_runtime_services` | Must pass `tools/ds005_runtime_import_check.py` and runtime regression tests before next phase |
| Phase 2: monolith split (service layer) | DS-002 | Decompose biggest backend orchestration hotspot into composable steps | `backend_runtime_services` | Start only after DS-001 interfaces are in place; require pre/post complexity evidence |
| Phase 3: monolith split (AI stack) | DS-003 | Decompose `ai_stack/rag.py` by concern while preserving facade compatibility | `ai_stack` | Can overlap late DS-002 only if interfaces are frozen; strict API compatibility checks |
| Phase 4: state and constant hardening | DS-004 | Remove brittle magic values/global mutable state after architecture seams exist | `backend_runtime_services` | Prefer small waves by subsystem to reduce behavior drift |
| Phase 5: control-flow cleanup | DS-005 | Flatten high-risk handlers and service methods with policy/guard extraction | `backend_runtime_services` | End with focused endpoint regression suite and updated hotspots list |

**Fill in:** take rows from the input table; make hard chains explicit (e.g. interfaces before large moves). Coordination § *Maintaining this file*: when priority changes or new **DS-*** appear, update this section and Mermaid if used.

**Implementation** of phases until documented closure (completion gate, session by session): [spaghetti-solve-task.md](spaghetti-solve-task.md).

## Progress / work log (optional, in addition to mandatory maintenance above)

Implementers may **briefly** record visible progress (for reviewers and the next iteration). **Mandatory** for structural waves remains **updating the input table, § structure scan, and — if needed — this log** (see coordination § *Maintaining this file*). **Additionally**, new waves add **pre/post files** under `despaghettify/state/artifacts/…` (see `EXECUTION_GOVERNANCE.md`); older session artefacts may be missing if intentionally cleaned — proof then via Git/CI/PR. Not a substitute for issues/PRs.

| date | ID(s) | short description | pre artefacts (rel. to `despaghettify/state/`) | post artefacts (rel. to `despaghettify/state/`) | state doc(s) updated | PR / commit |
|------|-------|-------------------|----------------------------------------|----------------------------------------|----------------------|-------------|
| 2026-04-11 | — (spaghetti-check) | [spaghetti-check-task.md](spaghetti-check-task.md): `spaghetti_ast_scan.py` telemetry **N=4143**, **L₅₀=257**, **L₁₀₀=70**, **D₆=0**; 7-category score **M7≈61.9%** with critical C3/C4. Builtins grep **0**; `ds005_runtime_import_check.py` **exit 0**; runtime spot check as in scan table. | — | — | — | — |
| — | — | — | — | — | — | — |

**New rows:** chronologically (**newest first** recommended); **DS-ID(s)**, gates/tests run, pre/post paths as in [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md); for scan/docs-only updates note briefly. Longer history: Git, PRs, `WORKSTREAM_*_STATE.md`.

## Canonical technical reading paths (after refactor)

After structural changes to runtime/AI/RAG/MCP, align **active** technical docs (not the 2026 archive):

- Runtime / authority: [`docs/technical/runtime/runtime-authority-and-state-flow.md`](../docs/technical/runtime/runtime-authority-and-state-flow.md) — supervisor orchestration: `supervisor_orchestrate_execute.py` + `supervisor_orchestrate_execute_sections.py`; subagent invocation: `supervisor_invoke_agent.py` + `supervisor_invoke_agent_sections.py`
- Inspector projection (backend): `inspector_turn_projection_sections.py` orchestrates; pieces in `inspector_turn_projection_sections_{utils,constants,semantic,provenance}.py`
- Admin tool routes: `administration-tool/route_registration.py` + `route_registration_{proxy,pages,manage,security}.py`
- God-of-Carnage solo builtin (core): `story_runtime_core/goc_solo_builtin_template.py` + `goc_solo_builtin_catalog.py` + `goc_solo_builtin_roles_rooms.py`
- AI / RAG / LangGraph: [`docs/technical/ai/RAG.md`](../docs/technical/ai/RAG.md), [`docs/technical/integration/LangGraph.md`](../docs/technical/integration/LangGraph.md), [`docs/technical/integration/MCP.md`](../docs/technical/integration/MCP.md)
- Dev seam overview: [`docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md`](../docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md)

---

*Created as an operational bridge between structural code work, the state hub under [`despaghettify/state/`](state/README.md) (pre/post evidence), and the completed documentation archive of 2026.*
