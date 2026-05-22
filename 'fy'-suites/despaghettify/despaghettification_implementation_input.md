# Despaghettification — information input list for implementers

*Path:* `despaghettify/despaghettification_implementation_input.md` — Overview: [README.md](../README.md).

This document is **not** part of the frozen consolidation archive under [`docs/archive/documentation-consolidation-2026/`](../../docs/archive/documentation-consolidation-2026/). That archive holds **completed** findings and migration evidence (ledgers, topic map, validation reports) — **do not overwrite or “continue writing” those files**.

Here you find the **living working basis**: structural and spaghetti topics in **code**, prioritised input rows for task implementers, coordination rules, and **in-flight** progress (closed history: [despaghettification_completed_log.md](despaghettification_completed_log.md)). Like documentation consolidation 2026: **one canonical truth per topic** — applied here to **code structure** (fewer duplicates, clearer boundaries, smaller coherent modules).

**This file is part of wave discipline:** Whoever implements a **despaghettification wave** in code (new helper modules, noticeable AST/structure change) **updates this Markdown in the same wave** — not only the code. Details: § **“Maintaining this file during structural waves”** under coordination. This does **not** replace pre/post artefacts under `despaghettify/state/artifacts/…` (they remain mandatory per [`EXECUTION_GOVERNANCE.md`](../state/EXECUTION_GOVERNANCE.md)); it complements them as the **functional** entry and priority track.

**Language:** [Repository language](../docs/dev/contributing.md#repository-language) — English for every editor-maintained field here (DS rows, structure scan prose, Open hotspots, coordination, active progress). **Closed** wave history: [despaghettification_completed_log.md](despaghettification_completed_log.md).

## Link to `despaghettify/state/` (execution governance, pre/post)

This document is **not** a replacement for [`state/EXECUTION_GOVERNANCE.md`](../state/EXECUTION_GOVERNANCE.md); it is the **functional input side** for structural refactors that should use the **same** evidence and restart rules.

| Governance building block | Role for despaghettification |
|---------------------------|------------------------------|
| [`EXECUTION_GOVERNANCE.md`](../state/EXECUTION_GOVERNANCE.md) | Mandatory: read state document, **pre** and **post** artefacts per wave, compare pre→post, update state from evidence (**completion gate**). |
| [`WORKSTREAM_INDEX.md`](../state/WORKSTREAM_INDEX.md) | Maps **workstream** → `artifacts/workstreams/<slug>/pre|post/`. |
| [`state/README.md`](../state/README.md) | Entry to the state hub. |
| `despaghettify/state/artifacts/repo_governance_rollout/pre|post/` | Optional for **repo-wide** waves (e.g. large diff across packages); useful when a structural wave needs the same repo commands as the rollout. |

**Artefact paths (canonical, relative to `despaghettify/state/`):**

- Per affected workstream: `artifacts/workstreams/<workstream>/pre/` and `…/post/`.
- Slugs as in the index: `backend_runtime_services`, `ai_stack`, `administration_tool`, `world_engine` (documentation only if MkDocs/nav is in scope).

**Naming convention for structural waves (DS-*):**

- Session/wave prefix as today: `session_YYYYMMDD_…`.
- **DS-ID in the filename**, e.g. `session_YYYYMMDD_DS-001_scope_snapshot.txt`, `session_YYYYMMDD_DS-001_pytest_collect.exit.txt`, `session_YYYYMMDD_DS-001_pre_post_comparison.json` (the latter typically under **`post/`**).
- At least **one** human-readable artefact (`.txt`/`.md`) and **preferably** one machine-readable (`.json`) — as governance requires.

**DS-ID → primary workstream (where to place pre/post):**

| ID | Primary workstream (`artifacts/workstreams/…`) | Also involved | Status |
|----|--------------------------------------------------|---------------|--------|
| **DS-001** | `backend_runtime_services` | — | **CLOSED** 2026-05-20 |
| **DS-002** | `backend_runtime_services` | `ai_stack` (call sites) | **CLOSED** 2026-05-20 |
| **DS-003** | `ai_stack` | — | **CLOSED** 2026-05-20 |
| **DS-004** | `backend_runtime_services` | `administration_tool` (if admin surfaces share constants) | **CLOSED** 2026-05-20 |
| **DS-005** | `backend_runtime_services` | `world_engine`, `ai_stack` | **CLOSED** 2026-05-20 |
| **DS-006** | `repo_governance_rollout` | `world_engine` scan tree, despaghettify config | **CLOSED** 2026-05-20 |
| **DS-007** | `backend_runtime_services` | — | **CLOSED** 2026-05-20 |
| **DS-008** | `ai_stack` | — | **CLOSED** 2026-05-20 |
| **DS-009** | `world_engine` | — | **CLOSED** 2026-05-20 |
| **DS-010** | `ai_stack` | `backend_runtime_services` | **CLOSED** 2026-05-22 |
| **DS-011** | `ai_stack` | `story_runtime_core`, `backend_runtime_services` | **CLOSED** 2026-05-22 |
| **DS-012** | `backend_runtime_services` | — | **OPEN** |
| **DS-013** | `ai_stack` | `story_runtime_core` | **OPEN** |
| **DS-014** | `world_engine` | — | **OPEN** |
| **DS-015** | `ai_stack` | `backend_runtime_services`, `administration_tool`, `story_runtime_core` | **OPEN** |
| **DS-016** | `repo_governance_rollout` | `tools/mcp_server`, `administration_tool` | **OPEN** |

**Fill in:** For each active **DS-*** one row (or a group sharing the same primary workstream); slugs as in [`WORKSTREAM_INDEX.md`](../state/WORKSTREAM_INDEX.md): `backend_runtime_services`, `ai_stack`, `administration_tool`, `world_engine`, `documentation`. Repo-wide cross-check without product code: optional `artifacts/repo_governance_rollout/pre|post/` (e.g. **DS-REPLAY-G**).

Implementers: tick the **completion gate** from `EXECUTION_GOVERNANCE.md`; record the wave and new artefact paths in the matching `WORKSTREAM_*_STATE.md`. Avoid crossings: one clear wave owner per **DS-ID**; multiple workstreams only with agreed **separate** artefact sets.

## Link to documentation-consolidation-2026

| Archive artefact | Link to code despaghettification |
|------------------|----------------------------------|
| [`TOPIC_CONSOLIDATION_MAP.md`](../../docs/archive/documentation-consolidation-2026/TOPIC_CONSOLIDATION_MAP.md) | Topics map to **one** active doc per topic; code refactors should not reopen the same functional edge across two parallel implementations (e.g. RAG, MCP, runtime). |
| [`DURABLE_TRUTH_MIGRATION_LEDGER.md`](../../docs/archive/documentation-consolidation-2026/DURABLE_TRUTH_MIGRATION_LEDGER.md) | Model for **traceable** moves instead of silent drift; despaghettification: **one source** for shared building blocks (e.g. builtins). |
| [`FINAL_DOCUMENTATION_VALIDATION_REPORT.md`](../../docs/archive/documentation-consolidation-2026/FINAL_DOCUMENTATION_VALIDATION_REPORT.md) | Closure criteria for a **documentation** strand; for code: tests/CI green, behaviour unchanged, interfaces explicit. |

## Coordination — extend work without colliding

1. **Claims:** Before larger refactors, name the **ID(s)** in team/issue/PR (all **`DS-*** you are taking from this information input list). Preferably **one** clear owner per ID.
2. **No double track:** Two implementers do **not** work the same ID in parallel; if split: separate sub-tasks explicitly (e.g. DS-003a backend wiring only, DS-003b world-engine import only).
3. **Leave archive alone:** Do not mirror code findings into `documentation-consolidation-2026/*.md`; use CHANGELOG, PR description, **`despaghettify/state/` artefacts**, **this input list** (§ *Latest structure scan*, open DS rows only), **[despaghettification_completed_log.md](despaghettification_completed_log.md)** for closed waves, and matching **`WORKSTREAM_*_STATE.md`**.
4. **Interfaces first:** For cycles (runtime cluster) small **DTO / protocol modules** before big moves; avoids PRs that touch half of `app.runtime` at once.
5. **Measurement optional:** AST/review-based lengths are **guidance**; success is **understandable** boundaries + green suites, not a percentage score.

### Maintaining this file during structural waves (move with the code)

For every relevant **DS-*** / despaghettification **wave**, update this file in the **same PR/commit logic** (not “code only”):

| What | Content |
|------|---------|
| **Information input list** | **Open** rows only; **pattern** starts with **C1..C7** per [spaghetti-check-task.md](../spaghetti-check-task.md) §2. On closure: strikethrough here **or** remove row and record in [despaghettification_completed_log.md](despaghettification_completed_log.md) (preferred when batch is done). |
| **§ Latest structure scan** | After measurable change: **main table** — **Trigger v2** + **Anteil %** for **M7** / **C1..C7** from **`metrics_bundle.score`** via `check --with-metrics` ([spaghetti-check-task.md](../spaghetti-check-task.md) §1); telemetry **N / L₅₀ / L₁₀₀ / D₆** from `spaghetti_ast_scan`; § *Score M7* **same** dual columns + **AST telemetry** row **under C7**; optional **extra checks**; **open hotspots** (**prune** solved items). For runtime edges `despaghettify/tools/ds005_runtime_import_check.py`. Rankings: script output only. |
| **§ Recommended implementation order** | Update when priority, dependency, or phase changes; **mandatory** Mermaid `flowchart` below the phase table on every [spaghetti-check-task.md](../spaghetti-check-task.md) pass that fills phases (see that doc §3). |
| **§ Active progress** | **In-flight only** (partial sub-waves, open DS): at most **3** rows; see [despaghettification_completed_log.md](despaghettification_completed_log.md) when a **DS-ID** is **CLOSED** or a pass is done. |
| **DS-ID → workstream table** | Place new or moved **DS-*** here; note co-involved workstreams. |

**Governance:** `despaghettify/state/artifacts/workstreams/<slug>/pre|post/` and `WORKSTREAM_*_STATE.md` remain **formal** evidence; this file is the **compact** working and review map.

## Latest structure scan (orientation, no warranty)

**Purpose:** A **fillable** overview after measurable runs — update **date and time**, **`metrics_bundle.score`** (**Trigger v2** + **Anteil %**), **AST telemetry**, optional **extra checks**, and **open hotspots** per [spaghetti-check-task.md](../spaghetti-check-task.md). **Numeric** thresholds (**bars**, **weights**, **`M7_ref`**) are canonical in [spaghetti-setup.md](../spaghetti-setup.md). The spaghetti check maintains the **information input list** and **recommended implementation order** when the **trigger policy** in § *Trigger policy for check task updates* fires (per **setup**); otherwise this scan section (including M7 and category breakdown) is enough. **Rankings:** `python "./'fy'-suites/despaghettify/tools/spaghetti_ast_scan.py"` only (repo root). **Open hotspots:** [spaghetti-solve-task.md](../spaghetti-solve-task.md) clears or narrows items when waves resolve them; on every spaghetti-check run, **prune** so solved items are not listed.

| Field | **Trigger v2** (0–100; advisory) | **Anteil %** (vs. bars / `M7_ref`; **M7** row = `m7_anteil_pct_gewichtet`) |
|-------|-------------------------------------|-------------------------------------|
| **As of (date & time)** | — | **2026-05-22 17:00:29 (UTC)** |
| Spaghetti scan command | — | `PYTHONPATH="'fy'-suites" python -m despaghettify.tools check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` |
| Measurement scope (ROOTS) | — | `backend/app`, `world-engine/app`, `ai_stack`, `story_runtime_core`, `tools/mcp_server`, `administration-tool` from `fy-manifest.yaml` |
| **M7** — gewichtete 7-Kategorien-Summe | **52.98** | **4.25** |
| C1: Circular dependencies | **11.18** | **0.78** |
| C2: Nesting depth | **55.07** | **1.71** |
| C3: Long functions + complexity | **99.76** | **1.81** |
| C4: Multi-responsibility modules | **73.90** | **7.46** |
| C5: Magic numbers + global state | **40.64** | **0.97** |
| C6: Missing abstractions / duplication | **51.59** | **15.15** |
| C7: Confusing control flow | **64.84** | **7.26** |
| **AST telemetry N / L₅₀ / L₁₀₀ / D₆** | — | **10641** / **794** / **193** / **20** |
| Extra check builtins | — | **0** matches for `def build_god_of_carnage_solo` in `**/builtins.py`; `story_runtime_core/goc_solo_builtin_template.py` still owns the definition |
| Extra check runtime | — | **`ds005_runtime_import_check.py`** exit **0**; imported **12** current runtime modules via `app.runtime.package_classification.runtime_module_import_path`. Grep `TYPE_CHECKING` / `avoid circular` / `circular dependency` under `backend/app/runtime`: **0** hits |
| **Open hotspots** | — | **Trigger policy fires:** `M7_anteil` **4.2456** ≥ `M7_ref` **4.24**; Anteil exceeds bars on **C4** (**7.46** > **5**), **C5** (**0.97** > **0**), **C6** (**15.15** > **0**), and **C7** (**7.26** > **3**). **C4/C7 anchors:** `backend/app/api/v1/forum_routes.py` **2240** lines, `backend/app/content/module_loader.py:load_all_module_files` **310L**, `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py:run_visible_render` **340L**, `ai_stack/story_runtime/player_action_resolution.py:resolve_player_action` **314L**, `world-engine/app/story_runtime/manager/story_window_entries.py:_story_window_entries_for_session` depth **6** / **237L**, and `story_runtime_core/branching/branch_timeline.py:build_branch_timeline_snapshot` depth **8**. **C5 anchor:** magic-int proxy remains concentrated in prompt/proxy/narrative policy builders such as `prompt_store_service.update_prompt_record`, `symbolic_object_resonance_engine.derive_symbolic_object_resonance`, and administration proxy tests. **C6 anchor:** DS-015 w01 now classifies public protocol duplicates (`to_dict`, `to_runtime_dict`, `generate`) separately from actionable helper families (`_text`, `_clean_str_list`, `_bounded_int`, `_do`, `_as_list`); helper centralization remains open for w02/w03. **Metric scan gate repaired:** DS-005 imports **12** current runtime modules with exit **0**. |

### Score *M7* — inputs, weights, and calculation

| Symbol | Meaning | **Trigger v2** (0–100) | **Anteil %** |
|--------|---------|------------------------|--------------|
| **M7** | Gewichtete Summe | **52.98** | **4.25** |
| **C1** | Circular dependencies | **11.18** | **0.78** |
| **C2** | Nesting depth | **55.07** | **1.71** |
| **C3** | Long functions + complexity | **99.76** | **1.81** |
| **C4** | Multi-responsibility modules | **73.90** | **7.46** |
| **C5** | Magic numbers + global state | **40.64** | **0.97** |
| **C6** | Missing abstractions / duplication | **51.59** | **15.15** |
| **C7** | Confusing control flow | **64.84** | **7.26** |
| **AST telemetry** | N / L₅₀ / L₁₀₀ / D₆ | — | **10641** / **794** / **193** / **20** |

**Formeln:** **Trigger:** `M7_trigger = Σ weight_i × trigger_v2(Ci)` aus **`metrics_bundle.m7`** / **`score`**. **Anteil:** `M7_anteil = Σ weight_i × anteil_pct(Ci)` aus **`score.m7_anteil_pct_gewichtet`**. **Weights:** [spaghetti-setup.md](../spaghetti-setup.md) § *M7 category weights*.

**Evaluation:** From **`check --with-metrics`**: fill **`metrics_bundle.score`** (both columns); **AST** from **`spaghetti_ast_scan`**. **Bars** apply to **Anteil %** / **`metric_a.m7`** only (see [spaghetti-check-task.md](../spaghetti-check-task.md) §1).

**Trigger policy for check task updates:**

Update § *Information input list*, § *Recommended implementation order*, and § *DS-ID → primary workstream* when **`metrics_bundle.trigger_policy_fires`** is true — i.e. **Anteil(C*n*) > bar*n*** or **`M7_anteil ≥ M7_ref`** per [spaghetti-setup.md](../spaghetti-setup.md).

| Condition | Rule |
|-----------|------|
| **Per-category** | **Anteil(C*n*)** **>** **bar*n*** per [spaghetti-setup.md](../spaghetti-setup.md) § *Per-category trigger bars*. |
| **Composite** | **`M7_anteil` ≥ `M7_ref`** (`metric_a.m7`). |

**Otherwise** (no per-category exceedance **and** **`M7_anteil` < `M7_ref`**): update **only** § *Latest structure scan*.

*Note:* **`trigger_policy_basis`:** `anteil_pct`. **Trigger v2** is advisory. No hand edits.

## Information input list (extensible)

Each **open** row: **ID**, **pattern** (lead with **C1..C7** from [spaghetti-setup.md](../spaghetti-setup.md) § *Per-category trigger bars*, e.g. **`C3 ·`** …), **location**, **hint / measurement idea**, **direction**, **collision hint**.

### Open

| ID | pattern | location (typical) | hint / measurement idea | direction (solution sketch) | collision hint |
|----|---------|--------------------|-------------------------|----------------------------|----------------|
| **DS-012** | **C4 · C5 · C7 ·** Backend route/content runtime hotspots | `backend/app/api/v1/forum_routes.py`, `backend/app/content/module_loader.py`, `backend/app/services/ai_stack/ai_engineer_suite/orchestration_status.py`, `backend/app/services/governance/narrative_governance_service.py` | `forum_routes.py` is **2240** lines; `load_all_module_files` is **310L** depth **4**; `get_orchestration_status` is **161L** depth **7**; `_is_condition_match` reaches depth **8**. | Split route/content orchestration into coherent submodules, flatten governance predicates, and keep external route contracts stable. | High collision with backend API/service edits; run backend route/runtime tests and `ds005_runtime_import_check.py`. |
| **DS-013** | **C4 · C5 · C7 ·** AI-stack story-runtime long-callable pass | `ai_stack/story_runtime/turn/god_of_carnage_turn_seams.py`, `ai_stack/story_runtime/player_action_resolution.py`, `ai_stack/story_runtime/semantic_planner/semantic_scene_plan/enrichment.py`, `ai_stack/story_runtime/narrative/*`, `story_runtime_core/branching/branch_timeline.py` | Top offenders include `run_visible_render` **340L**, `resolve_player_action` **314L**, `build_semantic_scene_plan_enrichment` **297L**, `derive_symbolic_object_resonance` **270L**, and `build_branch_timeline_snapshot` depth **8**. | Extract render/action/enrichment and branching decision phases behind stable wrappers; move constants out of narrative policy bodies where behavior is stable. | Avoid overlap with W5/narrator behavior changes; run focused `ai_stack` story-runtime and `story_runtime_core` branching suites. |
| **DS-014** | **C4 · C7 ·** World-engine manager readout/session hotspots | `world-engine/app/story_runtime/manager/player_visible_persistence.py`, `session/session_state_api.py`, `story_window_entries.py`, `committed_dramatic_context.py`, `world-engine/app/story_runtime/governed_runtime.py` | Current scan lists `_persist_player_visible_turn_event` **255L**, `get_state` **250L**, `_story_window_entries_for_session` **237L** depth **6**, `_build_committed_dramatic_context_summary` **235L**, and `build_governed_model_adapters` depth **7**. | Split persistence, state readout, story-window entry assembly, and adapter governance into testable manager helpers without changing committed output. | Coordinate with active narrator-strict worktree changes; run world-engine manager/runtime diagnostics tests. |
| **DS-015** | **C6 · C5 ·** Remaining duplicate-name proxy triage | `ai_stack/contracts/*`, `ai_stack/story_runtime/narrative/*`, `backend/app/api/v1/operational_governance/*`, `administration-tool/tests/*`, `story_runtime_core/*` | C6 Anteil remains **15.149** after DS-011; intentional protocol names (`to_dict`, `to_runtime_dict`, `generate`) coexist with actionable helper families (`_text`, `_clean_str_list`, `_bounded_int`, `_do`, `_as_list`) and repeated magic-literal policy builders. | Classify intentional protocol duplicates, centralize only true helper duplication per package, and add scan guards so proxy cleanup does not rename public contracts blindly. | Cross-package blast radius; do not rename public dataclass/protocol methods without call-site audit. |
| **DS-016** | **C4 · C5 · C7 ·** Tooling/test fixture hotspot cleanup | `tools/mcp_server/tests/test_langfuse_verify_tools.py`, `administration-tool/route_registration_proxy.py`, `administration-tool/tests/*` | Largest callable is `test_summarize_runtime_aspect_matrix_reads_ledger_from_path_summary` at **558L**; administration proxy tests and routes carry repeated status-code and policy literals. | Split large verification tests into fixtures/assertion helpers and extract proxy status/policy constants while preserving test intent. | Keep production MCP handler behavior untouched; run MCP server tests and administration-tool proxy tests. |

### Closed (archived)

*None.* Closed **DS-*** detail lives in [despaghettification_completed_log.md](despaghettification_completed_log.md).

**New rows:** next **DS-006**+ when check fills the open table; on closure append [despaghettification_completed_log.md](despaghettification_completed_log.md) and remove from *Open* above.
## Recommended implementation order

Prioritised **phases** for **open** **DS-*** only — aligned with § *Open* in the information input list and [`EXECUTION_GOVERNANCE.md`](../state/EXECUTION_GOVERNANCE.md). **Mandatory** Mermaid `flowchart` **below** the table once open phase rows exist ([spaghetti-check-task.md](../spaghetti-check-task.md) §3).

### Open phases

| Priority / phase | DS-ID(s) | short logic | workstream (primary) | note (dependencies, gates) |
|------------------|----------|-------------|----------------------|----------------------------|
| **1** | **DS-015** | Separate intentional protocol duplicates from real helper duplication before broader module movement. | `ai_stack` | Gates: duplicate-helper grep, focused contract/narrative tests, backend operational-governance smoke if `_do` helpers move. |
| **2a** | **DS-012** | Shrink backend route/content/governance hotspots behind stable route contracts. | `backend_runtime_services` | Parallel with **DS-014** / **DS-016** after DS-015 classification; gates: backend route/service tests plus `ds005_runtime_import_check.py`. |
| **2b** | **DS-014** | Split world-engine manager state/readout surfaces into granular manager helpers. | `world_engine` | Parallel with **DS-012** / **DS-016**; avoid narrator-strict behavior changes; gates: world-engine manager diagnostics/runtime tests. |
| **2c** | **DS-016** | Clean tool/test fixture hotspots without touching production MCP handler behavior. | `repo_governance_rollout` | Parallel with **DS-012** / **DS-014**; gates: MCP server tests and administration-tool proxy tests. |
| **3** | **DS-013** | Refactor AI-stack story-runtime long-callable surfaces after duplicate-helper vocabulary is settled. | `ai_stack` | Depends softly on **DS-015**; gates: focused `ai_stack` story-runtime suites and `story_runtime_core` branching tests. |

```mermaid
flowchart TD
P1["1 · DS-015 · Duplicate proxy triage"]
P2A["2a · DS-012 · Backend route/content hotspots"]
P2B["2b · DS-014 · World-engine manager readouts"]
P2C["2c · DS-016 · Tool/test fixture cleanup"]
P3["3 · DS-013 · AI-stack story-runtime split"]
P1 --> P2A
P1 --> P2B
P1 --> P2C
P1 --> P3
```

### Closed phases (archived)

See [despaghettification_completed_log.md](despaghettification_completed_log.md).

**Current order:** classify duplicate proxies first, then run backend/world-engine/tooling cleanup in parallel where owners do not share hot files; AI-stack story-runtime split follows after DS-015 settles helper vocabulary.

**Implementation:** invoke [spaghetti-solve-task.md](../spaghetti-solve-task.md) with **one** **DS-ID** per run.

## Active progress (in-flight only)

**Completed waves** live in **[despaghettification_completed_log.md](despaghettification_completed_log.md)** — append there when a **DS-ID** is **CLOSED** or a check/reset pass is finished; do **not** grow this table with closed work.

Use this section only for:

- **Partial** solve runs (`k < N` sub-waves; resume anchor),
- **Open** DS waves before final closure,
- At most **3** rows — archive older **closed** rows to the completed log.

| date | ID(s) | short description | pre artefacts (rel. to `despaghettify/state/`) | post artefacts (rel. to `despaghettify/state/`) | state doc(s) updated | PR / commit |
|------|-------|-------------------|----------------------------------------|----------------------------------------|----------------------|-------------|
| 2026-05-22 | **DS-015** | `w01`/3 completed: duplicate-name proxy classification guard added; next `w02` centralizes AI-stack helper families. | `artifacts/workstreams/ai_stack/pre/session_20260522_DS-015_wave_plan.*`; `artifacts/workstreams/ai_stack/pre/session_20260522_DS-015_w01_duplicate_proxy_classification_snapshot.*` | `artifacts/workstreams/ai_stack/post/session_20260522_DS-015_w01_duplicate_proxy_classification_comparison.*` | `WORKSTREAM_AI_STACK_STATE.md` | working tree |

**Rules:** [`despaghettification_completed_log.md`](despaghettification_completed_log.md) § *When to append here*; formal evidence still under `despaghettify/state/artifacts/…` per [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md).

## Canonical technical reading paths (after refactor)

After structural changes to runtime/AI/RAG/MCP, align **active** technical docs (not the 2026 archive):

- Runtime / authority: [`docs/technical/runtime/runtime-authority-and-state-flow.md`](../../docs/technical/runtime/runtime-authority-and-state-flow.md) — supervisor orchestration: `supervisor_orchestrate_execute.py` + `supervisor_orchestrate_execute_sections.py`; subagent invocation: `supervisor_invoke_agent.py` + `supervisor_invoke_agent_sections.py`
- Inspector projection (backend): `inspector_turn_projection_sections.py` orchestrates; pieces in `inspector_turn_projection_sections_{utils,constants,semantic,provenance}.py`
- Admin tool routes: `administration-tool/route_registration.py` + `route_registration_{proxy,pages,manage,security}.py`
- God-of-Carnage solo builtin (core): `story_runtime_core/goc_solo_builtin_template.py` + `goc_solo_builtin_catalog.py` + `goc_solo_builtin_roles_rooms.py`
- AI / RAG / LangGraph: [`docs/technical/ai/RAG.md`](../../docs/technical/ai/RAG.md), [`docs/technical/integration/LangGraph.md`](../../docs/technical/integration/LangGraph.md), [`docs/technical/integration/MCP.md`](../../docs/technical/integration/MCP.md)
- Dev seam overview: [`docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md`](../../docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md)

---

*Created as an operational bridge between structural code work, the state hub under [`despaghettify/state/`](../state/README.md) (pre/post evidence), and the completed documentation archive of 2026.*
