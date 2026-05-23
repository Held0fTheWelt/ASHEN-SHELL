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
| **DS-012** | `backend_runtime_services` | — | **CLOSED** 2026-05-22 |
| **DS-013** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-014** | `world_engine` | — | **CLOSED** 2026-05-22 |
| **DS-015** | `ai_stack` | `backend_runtime_services`, `administration_tool`, `story_runtime_core` | **CLOSED** 2026-05-22 |
| **DS-016** | `repo_governance_rollout` | `tools/mcp_server`, `administration_tool` | **CLOSED** 2026-05-23 |
| **DS-017** | `ai_stack` | — | **CLOSED** 2026-05-23 |
| **DS-018** | `world_engine` | `ai_stack` (runtime call surfaces only) | **CLOSED** 2026-05-23 |
| **DS-019** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-020** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-021** | `ai_stack` | — | **CLOSED** 2026-05-23 |
| **DS-022** | `world_engine` | — | **CLOSED** 2026-05-23 |
| **DS-023** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-024** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-025** | `world_engine` | — | **CLOSED** 2026-05-23 |
| **DS-026** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-027** | `ai_stack` | `story_runtime_core` | **CLOSED** 2026-05-23 |
| **DS-028** | `repo_governance_rollout` | `tools/mcp_server`, `ai_stack` | **CLOSED** 2026-05-23 |
| **DS-029** | `ai_stack` | `story_runtime_core` | **OPEN** 2026-05-23 |
| **DS-030** | `backend_runtime_services` | — | **OPEN** 2026-05-23 |
| **DS-031** | `world_engine` | — | **OPEN** 2026-05-23 |
| **DS-032** | `backend_runtime_services` | `ai_stack`, `world_engine`, `story_runtime_core`, `administration_tool` | **OPEN** 2026-05-23 |

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
| **As of (date & time)** | — | **2026-05-23 14:33:12 (UTC)** |
| Spaghetti scan command | — | `PYTHONPATH="'fy'-suites" python -m despaghettify.tools check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` |
| Measurement scope (ROOTS) | — | `backend/app`, `world-engine/app`, `ai_stack`, `story_runtime_core`, `tools/mcp_server`, `administration-tool` from `fy-manifest.yaml` |
| **M7** — gewichtete 7-Kategorien-Summe | **46.21** | **3.86** |
| C1: Circular dependencies | **9.45** | **0.74** |
| C2: Nesting depth | **0.00** | **1.39** |
| C3: Long functions + complexity | **98.70** | **1.25** |
| C4: Multi-responsibility modules | **72.88** | **7.25** |
| C5: Magic numbers + global state | **40.09** | **0.84** |
| C6: Missing abstractions / duplication | **39.47** | **13.75** |
| C7: Confusing control flow | **64.16** | **6.85** |
| **AST telemetry N / L₅₀ / L₁₀₀ / D₆** | — | **11076** / **803** / **139** / **0** |
| Extra check builtins | — | **0** matches for `def build_god_of_carnage_solo` in `**/builtins.py`; `story_runtime_core/goc_solo_builtin_template.py` still owns the definition |
| Extra check runtime | — | **`ds005_runtime_import_check.py`** exit **0**; imported **12** current runtime modules via `app.runtime.package_classification.runtime_module_import_path`. Grep `TYPE_CHECKING` / `avoid circular` / `circular dependency` under `backend/app/runtime`: **0** hits |
| **Open hotspots** | — | **Trigger policy fires:** `M7_anteil` **3.862** is below `M7_ref` **4.24**, but Anteil exceeds bars on **C4** (**7.25** > **5**), **C5** (**0.84** > **0**), **C6** (**13.75** > **0**), and **C7** (**6.85** > **3**). **C4/C7 anchors:** the current longest functions cluster around AI actor/NPC/narrative surfaces (`build_npc_agency_closure`, `extract_w5_snapshot_from_committed_event`, `classify_voice_semantic_lines`, `derive_narrative_momentum`, `build_post_cut_in_follow_up_event`, `assess_npc_agency_claim_readiness`, `hydrate_actor_lanes`), backend service snapshots (`build_world_engine_control_center_snapshot`, `get_runtime_dashboard`), and world-engine live envelope/narrator/opening surfaces (`_build_live_scene_turn_envelope`, `_realize_narrator_path_output`, `_build_opening_prompt`). **C5/C6 residual:** policy literals and duplicate-name proxies remain nonzero around prompt/store, HTTP shell, contract-policy normalization, pacing/context synthesis, and callback export surfaces. **C7 nesting tail:** depth-6 leaders are now closed; `D6` is **0**. **Metric scan gate:** DS-005 imports **12** current runtime modules with exit **0**. |

### Score *M7* — inputs, weights, and calculation

| Symbol | Meaning | **Trigger v2** (0–100) | **Anteil %** |
|--------|---------|------------------------|--------------|
| **M7** | Gewichtete Summe | **46.21** | **3.86** |
| **C1** | Circular dependencies | **9.45** | **0.74** |
| **C2** | Nesting depth | **0.00** | **1.39** |
| **C3** | Long functions + complexity | **98.70** | **1.25** |
| **C4** | Multi-responsibility modules | **72.88** | **7.25** |
| **C5** | Magic numbers + global state | **40.09** | **0.84** |
| **C6** | Missing abstractions / duplication | **39.47** | **13.75** |
| **C7** | Confusing control flow | **64.16** | **6.85** |
| **AST telemetry** | N / L₅₀ / L₁₀₀ / D₆ | — | **11076** / **803** / **139** / **0** |

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
| **DS-029** | **C4 · C6 · C7 ·** AI actor/NPC/narrative long-callable cluster | `ai_stack/story_runtime/npc_agency/npc_agency_realization.py`, `ai_stack/actor_tracking/extractor.py`, `ai_stack/story_runtime/npc_agency/character/character_voice_semantic_classifier.py`, `ai_stack/story_runtime/narrative/narrative_momentum_engine.py`, `ai_stack/story_runtime/session_loop/follow_up_event.py`, `ai_stack/story_runtime/npc_agency/npc_agency_claim_readiness.py`, `ai_stack/story_runtime/actor_lane_hydration.py` | Current scan anchors: `build_npc_agency_closure` **166L**, `extract_w5_snapshot_from_committed_event` **163L**, `classify_voice_semantic_lines` **159L**, `derive_narrative_momentum` **158L**, `build_post_cut_in_follow_up_event` **158L**, `assess_npc_agency_claim_readiness` **154L**, `hydrate_actor_lanes` **153L**. | Split closure, actor-tracking extraction, voice classification, momentum derivation, follow-up event, claim-readiness, and hydration phases behind stable public wrappers. | High semantic risk; preserve W5 actor-tracking authority, NPC agency contracts, Actor Lane, and committed-event/readiness semantics. |
| **DS-030** | **C4 · C6 · C7 ·** Backend service snapshot/dashboard leaders | `backend/app/services/story_runtime/world_engine_control_center_service.py`, `backend/app/services/ai_stack/ai_engineer_suite/runtime_dashboard.py` | Current scan anchors: `build_world_engine_control_center_snapshot` **164L**, `get_runtime_dashboard` **163L**. | Extract snapshot collectors, status derivation, dashboard-section builders, and serializers while keeping API response shapes stable. | Backend/admin blast radius; preserve control-center and AI-engineer-suite response contracts and route/service call sites. |
| **DS-031** | **C4 · C7 ·** World-engine live envelope, narrator output, and opening prompt leaders | `world-engine/app/story_runtime/manager/live_scene_turn_envelope.py`, `world-engine/app/story_runtime/manager/narrator_output_realization.py`, `world-engine/app/story_runtime/manager/opening_prompt_and_narrator_candidates.py` | Current scan anchors: `_build_live_scene_turn_envelope` **157L**, `_realize_narrator_path_output` **151L**, `_build_opening_prompt` **151L**. | Split live turn envelope assembly, narrator path output realization, and opening prompt/candidate construction into named manager phases. | Preserve visible output, diagnostics envelope, narrator projection, opening prompt, and session-manager behavior. |
| **DS-032** | **C5 · C6 ·** Policy literal and duplicate-name residual tail | `world-engine/app/main.py`, `backend/app/services/prompts/prompt_store_service.py`, `backend/app/factory_http_shell.py`, `backend/app/services/analytics/metrics_service.py`, `ai_stack/contracts/consequence_cascade_contracts.py`, `ai_stack/contracts/callback_web_contracts.py`, `story_runtime_core/callbacks/callback_web.py`, `ai_stack/story_runtime/narrative/context_synthesis_engine.py`, `ai_stack/story_runtime/narrative/pacing_rhythm_engine.py` | Current scan anchors: C5 remains **0.84%** and C6 remains **13.75%**; literal-heavy leaders include `register_world_engine_ui_routes`, `update_prompt_record`, `register_http_shell`, `_range_end_and_buckets`, `normalize_consequence_cascade_policy`, `normalize_callback_web_policy`, and `derive_pacing_rhythm`. | Promote HTTP/status/bucket/policy literals into named constants and narrow duplicate helper families without renaming intentional public protocol methods. | Broad cross-package tail; keep HTTP behavior, prompt-store validation, analytics buckets, contract normalization, and callback export shapes stable. |

### Closed (archived)

*None.* Closed **DS-*** detail lives in [despaghettification_completed_log.md](despaghettification_completed_log.md).

**New rows:** next **DS-033**+ when check fills the open table; on closure append [despaghettification_completed_log.md](despaghettification_completed_log.md) and remove from *Open* above.
## Recommended implementation order

Prioritised **phases** for **open** **DS-*** only — aligned with § *Open* in the information input list and [`EXECUTION_GOVERNANCE.md`](../state/EXECUTION_GOVERNANCE.md). **Mandatory** Mermaid `flowchart` **below** the table once open phase rows exist ([spaghetti-check-task.md](../spaghetti-check-task.md) §3).

### Open phases

| Priority / phase | DS-ID(s) | short logic | workstream (primary) | note (dependencies, gates) |
|------------------|----------|-------------|----------------------|----------------------------|
| **1a** | **DS-029** | Stabilise AI actor/NPC/narrative authority surfaces before more narrator/world-engine manager edits. | `ai_stack` | Parallel-eligible with **1b**; gates should include actor-tracking projection, NPC agency, narrator/momentum, session-loop, and Actor Lane hydration tests. |
| **1b** | **DS-030** | Shrink backend snapshot/dashboard service leaders independently of AI-stack runtime semantics. | `backend_runtime_services` | Parallel-eligible with **1a**; gates should include control-center/dashboard service tests and relevant backend route smoke tests. |
| **2** | **DS-031** | Split world-engine live envelope/narrator/opening prompt after AI actor/narrator surfaces are clearer. | `world_engine` | Soft dependency on **DS-029**; gates should include live turn envelope, narrator path output, opening prompt/session, and MVP03/MVP04 diagnostics gates. |
| **3** | **DS-032** | Clean policy-literal and duplicate-name residual tail after the largest semantic leaders stop moving. | `backend_runtime_services` | Broad tail; gates should include prompt store, HTTP shell, analytics, contract normalization, callback export, and `check --with-metrics`. |

```mermaid
flowchart TD
    P1A["1a · DS-029 · AI actor/NPC narrative"]
    P1B["1b · DS-030 · Backend snapshots"]
    P2["2 · DS-031 · World-engine envelope"]
    P3["3 · DS-032 · Policy literal tail"]
    P1A --> P2
    P1A --> P3
    P1B --> P3
    P2 --> P3
```

### Closed phases (archived)

*None.* See [despaghettification_completed_log.md](despaghettification_completed_log.md).

**Fill in:** one phase row per **open** **DS-*** when check repopulates the backlog. **Mermaid:** omit while the open table is only `—`.

**Implementation:** invoke [spaghetti-solve-task.md](../spaghetti-solve-task.md) with **one** **DS-ID** per run.
## Active progress (in-flight only)

**Completed waves** live in **[despaghettification_completed_log.md](despaghettification_completed_log.md)** — append there when a **DS-ID** is **CLOSED** or a check/reset pass is finished; do **not** grow this table with closed work.

Use this section only for:

- **Partial** solve runs (`k < N` sub-waves; resume anchor),
- **Open** DS waves before final closure,
- At most **3** rows — archive older **closed** rows to the completed log.

| date | ID(s) | short description | pre artefacts (rel. to `despaghettify/state/`) | post artefacts (rel. to `despaghettify/state/`) | state doc(s) updated | PR / commit |
|------|-------|-------------------|----------------------------------------|----------------------------------------|----------------------|-------------|
| — | — | — | — | — | — | — |

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
