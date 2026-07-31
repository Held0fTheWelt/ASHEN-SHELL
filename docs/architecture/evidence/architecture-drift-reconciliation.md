# Better Tomorrow architecture drift reconciliation

Historical MVPs and work orders are classified against current source and Git evidence. The target column states the currently most coherent implementable direction; open or conflicting entries still require behavioral closure.

## Status summary

| Status | Claims | Meaning |
| --- | ---: | --- |
| Confirmed current | 2 | Current code and accepted architecture agree. |
| Superseded | 2 | Historical evidence remains useful but has no current authority. |
| Conflicting | 2 | Concurrent structures or semantics need an explicit decision. |
| Open target | 6 | Repair evidence exists, but production-path proof is incomplete. |

## Reconciliation map

| ID | Concern | Status | Diagnosis | Target direction |
| --- | --- | --- | --- | --- |
| `DRIFT-001` | Competing live-runtime structures | `confirmed_current` | Live story session and live run instance are separate persistence resources (Wave 2). Remaining risk is incomplete retirement of overlapping runtime generations. | Keep live_story_session and live_run_instance as distinct resources with one sink each; retire overlapping commit authority from app/runtime into named adapters only. |
| `DRIFT-002` | Proposal finalization is named and shaped like a second commit | `conflicting` | AI validation/finalization still uses commit terminology while world-engine is the declared commit authority. Even when behavior is proposal-only, naming and payload semantics invite authority drift. | Define an explicit ProposalDecision/ValidatedProposal contract. Rename AI-internal commit concepts to proposal finalization; reserve CommitDecision and committed state for world-engine. |
| `DRIFT-003` | Dramatic planner state survival through authoritative commit | `open_target` | Current source explicitly projects planner truth, beat progression and responder context after commit, which is evidence of repair. Source presence alone does not prove every selected dramatic dimension survives the production turn. | Use one versioned turn envelope from planner selection through proposal, validation, CommitDecision, committed dramatic context and player projection. Every narrowing step must be explicit and tested. |
| `DRIFT-004` | Authored content truth has several executable projections | `conflicting` | The intended YAML authority is surrounded by backend, world-engine and AI-specific projections. The projection contracts are real, but duplicated vocabularies and God-of-Carnage-specific Python remain a high-risk second-truth surface. | Keep YAML modules as authored truth, generate or validate a versioned compiled content contract once, and make world-engine/AI consumers read that contract through anti-corruption adapters. |
| `DRIFT-005` | Beat and canonical-path authority in the live turn | `open_target` | Current code reads a prior beat, projects beat progression into committed context and renders narration-beat metadata. The exact authoritative beat state and how canonical constraints avoid scripting the player remain architectural decisions requiring behavioral proof. | Model authored canonical constraints separately from live beat state. World-engine owns live progression; AI may propose beat effects; frontend displays only committed player-safe projections. |
| `DRIFT-006` | Manager decomposition contains generated-looking and legacy shards | `open_target` | World-engine manager SOURCE/exec shards are removed (Wave 1). Remaining dynamic SOURCE assembly lives in ai_stack/backend/tools (Waves 5/9). | Replace dynamic legacy assembly with explicit cohesive modules organized by session lifecycle, turn execution, commit, projection and observability. Preserve behavior through characterization tests before each deletion. |
| `DRIFT-007` | Player surface can flatten upstream runtime intelligence | `open_target` | Current renderer supports speaker labels and narration beats, and world-engine has explicit player-visible records. The modeled contract still needs proof that responder, action, narration and revision survive every delivery mode. | Adopt one player-visible block schema versioned at the world-engine delivery boundary. Frontend rendering is exhaustive over block variants and may not infer missing authority fields. |
| `DRIFT-008` | Observability contracts are fragmented across services | `open_target` | Four trace implementations are legitimate local adapters but lack one modeled cross-system envelope and completeness rule. A rich operator screen can therefore hide a missing production span. | Define a minimal TurnTrace contract with propagated identity, owned spans, explicit gaps and redaction. Each service adapts locally but must satisfy the shared trace tree. |
| `DRIFT-009` | Test presence and archived green runs can overstate proof | `open_target` | A central runner, changed-test selector and CI matrix now exist. Completeness still depends on proving that every declared test root is discoverable and that integration labels represent disposable real boundaries. | Generate the CI/test matrix from one suite catalog. Gate orphan test files, hidden skips, mock-only integration labels and profile/CI divergence. |
| `DRIFT-010` | Historical snapshots contain paths that no longer map to current architecture | `superseded` | The read-only April snapshot and current repository have large historical-only and current-only path sets. Snapshot structure is useful chronology but cannot be imported as present topology. | Retain hashes, claim headings and path-diff evidence. Port only a claim or behavior after current-source reconciliation; never copy a full old package over HEAD. |
| `DRIFT-011` | MVP completion labels are not architecture authority | `superseded` | Artifact names demonstrate iterative intent and local closure, not current production-path completion. Later audits explicitly contradicted some earlier closure claims. | Use capability lifecycle states proposed, implemented, integrated, proven and regressed. Only production-path evidence advances a capability to proven. |
| `DRIFT-012` | Architecture coverage metrics can hide shallow semantics | `confirmed_current` | The former fixed four-view generator has been replaced by individualized semantic views whose elements expose responsibility, contract and source anchor and whose edges state interaction contracts. | Keep model selection concern-driven and source-bound. Coverage remains supporting evidence; semantic analyzability, drill-down and correspondence determine acceptance. |

## Claim details

### DRIFT-001 - Competing live-runtime structures

**Status:** `confirmed_current`

**Historical assertions**

- The canonical player path and the explicit runtime/beat path were not the same path.
- Runtime tests expected story truth in a runtime profile.

**Current evidence**

- [`world-engine/world_engine/story_runtime/manager/runtime_manager.py`](../../../world-engine/world_engine/story_runtime/manager/runtime_manager.py)
- [`world-engine/world_engine/runtime/manager.py`](../../../world-engine/world_engine/runtime/manager.py)
- [`world-engine/world_engine/story_runtime/manager/commit_finalization.py`](../../../world-engine/world_engine/story_runtime/manager/commit_finalization.py)

**Best target direction**

Keep live_story_session and live_run_instance as distinct resources with one sink each; retire overlapping commit authority from app/runtime into named adapters only.

**Acceptance evidence**

- A dependency gate rejects app/story_runtime imports of overlapping app/runtime behavior.
- Every player turn enters one manager and one authoritative commit path.
- Compatibility calls are inventoried, named and covered by retirement tests.

### DRIFT-002 - Proposal finalization is named and shaped like a second commit

**Status:** `conflicting`

**Historical assertions**

- Graph commit and authoritative session commit were separate seams.
- Validation knew more than the authoritative commit.

**Current evidence**

- [`ai_stack/langgraph/runtime_executor/executor_validation_commit.py`](../../../ai_stack/langgraph/runtime_executor/executor_validation_commit.py)
- [`world-engine/world_engine/story_runtime/narrative_commit_resolution.py`](../../../world-engine/world_engine/story_runtime/narrative_commit_resolution.py)
- [`world-engine/world_engine/story_runtime/canonical_turn_lifecycle.py`](../../../world-engine/world_engine/story_runtime/canonical_turn_lifecycle.py)

**Best target direction**

Define an explicit ProposalDecision/ValidatedProposal contract. Rename AI-internal commit concepts to proposal finalization; reserve CommitDecision and committed state for world-engine.

**Acceptance evidence**

- Static architecture checks reject AI writes to live session stores.
- The cross-system sequence contains one authoritative committed transition.
- Contract tests prove rejected proposals leave the world revision unchanged.

### DRIFT-003 - Dramatic planner state survival through authoritative commit

**Status:** `open_target`

**Historical assertions**

- Planner state was computed after prompt assembly.
- Authoritative session commit ignored most dramatic planner state.
- Validation-to-commit asymmetry suppressed richer behavior.

**Current evidence**

- [`world-engine/world_engine/story_runtime/manager/turn_execution.py`](../../../world-engine/world_engine/story_runtime/manager/turn_execution.py)
- [`world-engine/world_engine/story_runtime/manager/committed_dramatic_context.py`](../../../world-engine/world_engine/story_runtime/manager/committed_dramatic_context.py)
- [`world-engine/world_engine/story_runtime/manager/committed_dramatic_context_parts.py`](../../../world-engine/world_engine/story_runtime/manager/committed_dramatic_context_parts.py)
- [`tests/test_pr_b_live_effect_propagation.py`](../../../tests/test_pr_b_live_effect_propagation.py)

**Best target direction**

Use one versioned turn envelope from planner selection through proposal, validation, CommitDecision, committed dramatic context and player projection. Every narrowing step must be explicit and tested.

**Acceptance evidence**

- A production-path test seeds distinctive planner values and observes them after commit.
- A correspondence table maps every envelope field to validator, commit and renderer handling.
- SARIF reports any modeled field that loses all downstream consumers.

### DRIFT-004 - Authored content truth has several executable projections

**Status:** `conflicting`

**Historical assertions**

- Canonical YAML resolution and the active path were only partially aligned.
- Tests expected story truth in god_of_carnage_solo runtime code.

**Current evidence**

- [`content/modules/god_of_carnage/module.yaml`](../../../content/modules/god_of_carnage/module.yaml)
- [`backend/app/content/module_loader.py`](../../../backend/app/content/module_loader.py)
- [`world-engine/world_engine/content/backend_loader.py`](../../../world-engine/world_engine/content/backend_loader.py)
- [`ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py`](../../../ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py)

**Best target direction**

Keep YAML modules as authored truth, generate or validate a versioned compiled content contract once, and make world-engine/AI consumers read that contract through anti-corruption adapters.

**Acceptance evidence**

- A content provenance test traces each runtime fact to module path and version.
- No product-specific Python constant can override a supplied authored fact.
- Compilation is deterministic and identical across repeated exports.

### DRIFT-005 - Beat and canonical-path authority in the live turn

**Status:** `open_target`

**Historical assertions**

- The beat system existed, but the canonical player path did not carry explicit beat state.
- Beat influence partly survived while commitment and rendering lost parts.

**Current evidence**

- [`content/modules/god_of_carnage/canonical_path/_schema.yaml`](../../../content/modules/god_of_carnage/canonical_path/_schema.yaml)
- [`world-engine/world_engine/story_runtime/manager/turn_execution.py`](../../../world-engine/world_engine/story_runtime/manager/turn_execution.py)
- [`world-engine/world_engine/story_runtime/manager/committed_dramatic_context.py`](../../../world-engine/world_engine/story_runtime/manager/committed_dramatic_context.py)
- [`frontend/static/play_block_renderer.js`](../../../frontend/static/play_block_renderer.js)

**Best target direction**

Model authored canonical constraints separately from live beat state. World-engine owns live progression; AI may propose beat effects; frontend displays only committed player-safe projections.

**Acceptance evidence**

- A state-machine test proves legal, rejected and deferred beat transitions.
- Free player actions remain valid when they do not match a canonical example.
- The rendered beat marker matches the committed revision and speaker.

### DRIFT-006 - Manager decomposition contains generated-looking and legacy shards

**Status:** `open_target`

**Historical assertions**

- Whole-system repair waves repeatedly split and reconciled the runtime manager.

**Current evidence**

- [`world-engine/world_engine/story_runtime/manager/commit_finalization.py`](../../../world-engine/world_engine/story_runtime/manager/commit_finalization.py)
- [`world-engine/world_engine/story_runtime/manager/runtime_manager.py`](../../../world-engine/world_engine/story_runtime/manager/runtime_manager.py)
- [`world-engine/world_engine/story_runtime/manager/turn_execution.py`](../../../world-engine/world_engine/story_runtime/manager/turn_execution.py)
- [`ai_stack/langgraph/runtime_executor/executor_model_routing_invocation.py`](../../../ai_stack/langgraph/runtime_executor/executor_model_routing_invocation.py)

**Best target direction**

Replace dynamic legacy assembly with explicit cohesive modules organized by session lifecycle, turn execution, commit, projection and observability. Preserve behavior through characterization tests before each deletion.

**Acceptance evidence**

- No SOURCE/SOURCE_LINES or exec(compile under world-engine/world_engine (gate test green).
- No SOURCE modules remain under ai_stack, backend/app, or tools production roots.
- Primary and degraded turn traces remain behaviorally equivalent.

### DRIFT-007 - Player surface can flatten upstream runtime intelligence

**Status:** `open_target`

**Historical assertions**

- The player shell underrepresented runtime intelligence.
- Story-window entries lost responder identity and dramatic context.

**Current evidence**

- [`world-engine/world_engine/story_runtime/manager/story_window_entries.py`](../../../world-engine/world_engine/story_runtime/manager/story_window_entries.py)
- [`world-engine/world_engine/story_runtime/manager/player_visible_canonical_record.py`](../../../world-engine/world_engine/story_runtime/manager/player_visible_canonical_record.py)
- [`frontend/static/play_block_renderer.js`](../../../frontend/static/play_block_renderer.js)
- [`frontend/static/play_narrative_stream.js`](../../../frontend/static/play_narrative_stream.js)

**Best target direction**

Adopt one player-visible block schema versioned at the world-engine delivery boundary. Frontend rendering is exhaustive over block variants and may not infer missing authority fields.

**Acceptance evidence**

- Contract tests cover every block variant and unknown-version behavior.
- Reconnect tests prove no duplicate or reordered visible blocks.
- Two role-sensitive E2E scenarios preserve speaker and dramatic metadata.

### DRIFT-008 - Observability contracts are fragmented across services

**Status:** `open_target`

**Historical assertions**

- Operator diagnostics were more coherent than the actual player runtime path.
- Langfuse evidence needed end-to-end traceable decisions.

**Current evidence**

- [`backend/app/api/v1/game/player_turn_trace_start.py`](../../../backend/app/api/v1/game/player_turn_trace_start.py)
- [`world-engine/world_engine/observability/trace.py`](../../../world-engine/world_engine/observability/trace.py)
- [`ai_stack/langfuse/langfuse_evidence.py`](../../../ai_stack/langfuse/langfuse_evidence.py)
- [`tools/mcp_server/langfuse_tracing.py`](../../../tools/mcp_server/langfuse_tracing.py)

**Best target direction**

Define a minimal TurnTrace contract with propagated identity, owned spans, explicit gaps and redaction. Each service adapts locally but must satisfy the shared trace tree.

**Acceptance evidence**

- One integration test asserts parent/child continuity across backend, world and AI.
- Telemetry failure leaves domain behavior intact and marks the trace partial.
- Credential and sensitive-text redaction is tested on every exporter.

### DRIFT-009 - Test presence and archived green runs can overstate proof

**Status:** `open_target`

**Historical assertions**

- Undiscovered tests, weak presence assertions and mock-only integration existed.
- Runner and CI truth needed a single explicit matrix.

**Current evidence**

- [`tests/run_tests.py`](../../../tests/run_tests.py)
- [`scripts/test_changed.py`](../../../scripts/test_changed.py)
- [`tests/reports/RUNNER_CI_TRUTH_MATRIX.md`](../../../tests/reports/RUNNER_CI_TRUTH_MATRIX.md)
- [`.github/workflows/quality-gate.yml`](../../../.github/workflows/quality-gate.yml)

**Best target direction**

Generate the CI/test matrix from one suite catalog. Gate orphan test files, hidden skips, mock-only integration labels and profile/CI divergence.

**Acceptance evidence**

- Every test file maps to exactly one declared suite or documented exception.
- The suite catalog deterministically generates local and CI commands.
- Disposable integration tests assert before/after external state equality.

### DRIFT-010 - Historical snapshots contain paths that no longer map to current architecture

**Status:** `superseded`

**Historical assertions**

- April repair packages represented their own canonical MVP directory.

**Current evidence**

- [`docs/architecture/evidence/architecture-drift-baseline.json`](../../../docs/architecture/evidence/architecture-drift-baseline.json)

**Best target direction**

Retain hashes, claim headings and path-diff evidence. Port only a claim or behavior after current-source reconciliation; never copy a full old package over HEAD.

**Acceptance evidence**

- Every harvested claim records provenance and one of four statuses.
- No build or test path depends on E:\New folder.
- The evidence snapshot can be regenerated without modifying the archive.

### DRIFT-011 - MVP completion labels are not architecture authority

**Status:** `superseded`

**Historical assertions**

- Many wave packages and repair bundles used final, complete or canonical in their filenames.

**Current evidence**

- [`docs/architecture/evidence/architecture-drift-baseline.json`](../../../docs/architecture/evidence/architecture-drift-baseline.json)
- [`docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md`](../../../docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md)

**Best target direction**

Use capability lifecycle states proposed, implemented, integrated, proven and regressed. Only production-path evidence advances a capability to proven.

**Acceptance evidence**

- Completion reports link source, behavioral test, runtime trace and user-visible outcome.
- A later failing proof moves the capability to regressed.
- Historical filenames never set current status automatically.

### DRIFT-012 - Architecture coverage metrics can hide shallow semantics

**Status:** `confirmed_current`

**Historical assertions**

- Architecture exports reported complete file and view coverage.

**Current evidence**

- [`tools/architecture_assurance/model_catalog.json`](../../../tools/architecture_assurance/model_catalog.json)
- [`tools/architecture_assurance/semantic_models.py`](../../../tools/architecture_assurance/semantic_models.py)
- [`docs/architecture/project/architecture-assurance/architecture.md`](../../../docs/architecture/project/architecture-assurance/architecture.md)

**Best target direction**

Keep model selection concern-driven and source-bound. Coverage remains supporting evidence; semantic analyzability, drill-down and correspondence determine acceptance.

**Acceptance evidence**

- All catalog source anchors resolve.
- Every view declares its concern and semantic relationships.
- A gate rejects generic evidence-star diagrams and fixed identical view profiles.
