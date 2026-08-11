# Architecture violation register

This register makes incorrect, conflicting or insufficiently proven implementation visible without
turning it into a target decision. Entries are linked to Git/AKDB lineage, current source, active
ADRs and executable closure evidence.

## Status semantics

| Status | Meaning |
| --- | --- |
| `nonconforming` | Current evidence conflicts with an accepted target. |
| `proof-gap` | Repair evidence exists, but the production path is not yet proven. |
| `structural-debt` | Current structure impedes enforcement or safe repair. |
| `resolved` | Target and implementation agree and closure evidence is current. |

`resolved` is reversible: a failing closure test moves the item to `regressed` or reopens it.

## Active register

| ID | Status | Severity | Concern | Active decision | Drift lineage |
| --- | --- | --- | --- | --- | --- |
| `AR-V001` | `nonconforming` | High | AI proposal finalization still resembles commit authority | ADR-0001 | DRIFT-002 |
| `AR-V002` | `proof-gap` | High | Dramatic turn fields are not proven end to end | ADR-0002 | DRIFT-003, DRIFT-005 |
| `AR-V003` | `nonconforming` | High | Authored content has multiple executable projections | ADR-0003 | DRIFT-004 |
| `AR-V004` | `proof-gap` | High | Player delivery can flatten runtime intelligence | ADR-0004 | DRIFT-007 |
| `AR-V005` | `structural-debt` | Medium | World Engine finalization remains an oversized mixed-responsibility seam | ADR-0001 | DRIFT-006 |
| `AR-V006` | `proof-gap` | Medium | Turn traces are fragmented across local adapters | ADR-0005 | DRIFT-008 |
| `AR-V007` | `resolved` | Medium | Parallel World Engine UML projections defined the same concern | ADR-0006 | DRIFT-012 |
| `AR-V008` | `nonconforming` | Medium | arc42 structure is present but major SADs remain ADR accumulations | ADR-0006 | DRIFT-011, DRIFT-012 |
| `AR-V009` | `resolved` | High | Aggregate coverage counted unmapped code as represented | ADR-0006 | DRIFT-012 |
| `AR-V010` | `proof-gap` | High | Bounded emergence is repaired, but full live-model replay evidence is still incomplete | ADR-0007 | DRIFT-003, DRIFT-005 |
| `AR-V011` | `proof-gap` | High | Neutral language consumers are repaired; non-English live replay remains unproven | ADR-0008 | DRIFT-004 |

## Detailed violations

### AR-V001 — Proposal finalization resembles a second commit

- **Historical intent:** graph validation and session commit evolved as different seams so model
  output could be checked before world mutation.
- **Current evidence:** `ai_stack/langgraph/runtime_executor/executor_validation_commit.py`,
  `executor_run_finish.py`, and World Engine `narrative_commit_resolution.py`.
- **Conflict:** AI-internal commit names and payloads can obscure which component owns the only
  authoritative decision.
- **Target:** `ValidatedProposal` crosses into World Engine; only World Engine creates
  `CommitDecision` and writes live revision.
- **Repair:** rename and narrow AI types, reject writer capability in AI, preserve compatibility
  through an adapter.
- **Closure:** static no-writer gate plus rejected-proposal and exactly-one-sink integration tests.

### AR-V002 — Turn-envelope correspondence is not production-proven

- **Historical intent:** planning, validation and beat systems were intended to enrich the same
  player turn.
- **Current evidence:** planner and committed-context fields exist at multiple stages; drift edges
  document expected carriers.
- **Gap:** producer and consumer source anchors do not prove the same production turn preserved a
  value through every boundary.
- **Target:** [ADR-0002](../decisions/ADR-0002-versioned-turn-envelope.md).
- **Closure:** seeded distinctive values observed after commit, persistence and player delivery;
  every discarded value has a decision reason.

### AR-V003 — Multiple executable content projections

- **Historical intent:** YAML-first authored modules allow reviewable content independent of runtime
  code.
- **Current evidence:** YAML module, backend loader/validator, World Engine loader and AI GoC
  authority adapter all project the model. The main finalization dispatch now reads the neutral
  `visible_projection_policy.v1`; an arbitrary configured module can select the rich adapter and an
  unconfigured module remains on generic blocks.
- **Conflict:** duplicated vocabularies and product-specific Python can still become a second
  truth. Policy schema enforcement at compilation and neutralization of the remaining GoC-named
  projection helpers are incomplete.
- **Target:** one versioned compiled projection with provenance and anti-corruption adapters.
- **Closure:** deterministic compile hash, cross-consumer contract test, and gate rejecting authored
  fact overrides in product-specific Python. Also require a second-module projection contract test
  without any engine-source module identifier.

### AR-V004 — Player delivery can flatten committed semantics

- **Historical intent:** MVP5 block rendering preserved cinematic direction and role-sensitive
  output.
- **Current evidence:** `story_window_entry_parts.py`, `story_ws.py`,
  `play_narrative_stream.js`, `play_block_renderer.js`.
- **Gap:** all delivery modes are not proven exhaustive over one versioned block schema.
- **Target:** [ADR-0004](../decisions/ADR-0004-player-visible-block-envelope.md).
- **Closure:** REST/WS/replay parity, unknown-version behavior and reconnect ordering tests.

### AR-V005 — Oversized finalization seam

- **Historical intent:** repeated manager splits tried to isolate turn phases without changing
  behavior.
- **Current evidence:** `_finalize_committed_turn` currently combines resolution, session mutation,
  beat/context projection, diagnostics, post-commit refresh and persistence in one large method.
- **Debt:** the correct authority is visible, but responsibilities and failure boundaries are hard
  to verify independently.
- **Target:** cohesive phases with one orchestrator and unchanged single-writer invariant.
- **Repair order:** characterization → extract pure projection → extract persistence outcome →
  extract post-commit hooks → remove obsolete compatibility shards.
- **Closure:** behavior-equivalence tests and no additional sink callsite.

### AR-V006 — Fragmented cross-service trace

- **Historical intent:** MVP4 made runtime decisions explainable to operators.
- **Current evidence:** separate backend, World Engine, AI/Langfuse and MCP trace adapters.
- **Gap:** no single executable proof currently guarantees parent/child continuity, redaction and
  explicit telemetry gaps across the production path.
- **Target:** [ADR-0005](../decisions/ADR-0005-cross-service-turn-trace.md).
- **Closure:** disposable end-to-end trace contract test plus telemetry-failure isolation test.

### AR-V007 — Parallel UML truth

- **Historical evidence:** old hand-written and newer generated World Engine sequence/state models
  coexisted and were referenced by different architecture documents.
- **Resolution:** the three duplicate sequence/state pairs and their inbound references were removed;
  Git retains their lineage.
- **Target:** one canonical concern ID and one source-bound model; historical views live only in Git.
- **Closure evidence:** catalog validation, link audit, and SAD bindings resolve only
  `primary-turn-sequence`, `degraded-turn-sequence`, and `session-lifecycle`.

### AR-V008 — SADs remain decision accumulations

- **Current evidence:** AI Stack §9 is about 82% of its SAD; MVP completion §9 is about 92%.
- **Conflict:** chronological ADR text hides goals, decomposition and runtime architecture.
- **Target:** §9 is a concise decision index; active ADRs own trade-offs; program evidence and
  historical details are separate.
- **Closure:** synthesis gate checks decision ratio, ordered IDs, active ADR links and non-placeholder
  arc42 sections.

### AR-V009 — Coverage metric hides unmapped implementation

- **Historical evidence:** 7,500 units were classified and reported as 100% represented even though
  more than 5,000 used a generic `archived` out-of-scope reason.
- **Resolution:** audit reports direct representation and total classification separately. Component
  and project SADs now declare bounded aggregate blocks for supporting implementation, with the most
  specific declared source path retaining precedence.
- **Target:** direct representation, explicit exclusion, unmapped current implementation and known
  violation are separate metrics.
- **Closure evidence:** repository-gate assertions require
  `represented == classified == discovered`, 100% direct representation, zero out-of-scope units,
  and a configured per-critical-subsystem representation floor of `1.0`.

### AR-V010 — Canonical and emergent dramaturgy compete

- **Historical cause:** free-action repair changed commit acceptance and canonical pointer behavior
  without changing every downstream consumer of the current canonical step.
- **Current evidence:** the semantic planner derived mandatory dialogue from canonical beats and
  LDSS deterministically rendered the same step on player turns.
- **Repair now present:** module/profile narrative modes, reference-only content frames, an LDSS
  mode boundary and `NarrativeMoveProposal.v1` prevent those consumers from silently treating the
  step as mandatory. Rejoin scene functions are module policy rather than engine constants.
- **Evidence now present:** deterministic planner and World Engine multi-turn tests prove two
  off-path pressure moves, a configured reference-opportunity rejoin, unchanged canonical pointer,
  preserved player-visible prose and one `world_engine_story_runtime` state writer.
- **Remaining gap:** a recorded live-model graph-to-replay run must prove the same properties without
  injecting deterministic graph envelopes.
- **Closure:** live-model replay fixture plus current deterministic multi-turn and delivery tests.

### AR-V011 — Neutral language boundary with English compatibility debt

- **Historical cause:** semantic translation was designed around the first English-authored module
  and the implementation promoted that module choice into an engine rule.
- **Repair now present:** ingress, interpretation, action resolution, retrieval and realization use
  `normalized_internal_text` as their primary field. One explicit compatibility reader accepts
  `normalized_english_text` only when `internal_resolution_language == en`; non-English envelopes
  cannot populate or override the alias.
- **Evidence now present:** non-English unit/integration paths cover same-language ingress,
  interpreted envelopes, action-frame precedence, retrieval query construction and realization
  prompts. Existing English envelopes retain their compatibility alias.
- **Remaining gap:** a persisted, full graph-to-World-Engine replay from a genuinely non-English
  module declaration is not yet recorded.
- **Target:** [ADR-0008](../decisions/ADR-0008-module-language-boundaries.md).
- **Closure:** retain the neutral-consumer and compatibility tests, then add the non-English module
  end-to-end replay fixture.

## Provenance

The detailed historical claims remain generated from
[`drift_claim_catalog.json`](../../../tools/architecture_assurance/drift_claim_catalog.json) in the
[drift reconciliation](../evidence/architecture-drift-reconciliation.md). Git and AKDB evidence may
change diagnosis or staleness. Closing or changing a target requires an active ADR.
