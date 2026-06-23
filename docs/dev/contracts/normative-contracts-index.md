# Normative contracts index

**When to read what** for implementers. These documents **bind** behavior for the GoC slice and runtime authority; they are **not** casual onboarding.

**Architecture entry:** [`docs/architecture/START-HERE.md`](../../architecture/START-HERE.md) · **Contract folder:** [`docs/architecture/contracts/`](../../architecture/contracts/README.md)

## Runtime and platform authority

| Document | Binding scope |
|----------|----------------|
| [world-engine SAD](../../architecture/components/world-engine/architecture.md) | Authoritative play service architecture (replaces spine stub) |
| [`runtime-authority-and-state-flow.md`](../../architecture/contracts/runtime/runtime-authority-and-state-flow.md) | Consolidated authority: world-engine owns live sessions; backend owns governance/publishing |
| [`player_input_interpretation_contract.md`](../../architecture/contracts/runtime/player_input_interpretation_contract.md) | Interpretation pipeline expectations |

## Runtime aspect contracts (Pi-scoped)

Full table (25 contracts). Canonical folder: [`docs/architecture/contracts/runtime/`](../../architecture/contracts/runtime/).

| Document | Owning SAD | Binding scope |
| --- | --- | --- |
| [`a1_free_input_primary_runtime_path.md`](../../architecture/contracts/runtime/a1_free_input_primary_runtime_path.md) | frontend + world-engine | Pi-scoped runtime aspect: a1 free input primary runtime path |
| [`active_listening_contract.md`](../../architecture/contracts/runtime/active_listening_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: active listening contract |
| [`callback_web_contract.md`](../../architecture/contracts/runtime/callback_web_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: callback web contract |
| [`consequence_cascade_contract.md`](../../architecture/contracts/runtime/consequence_cascade_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: consequence cascade contract |
| [`director_realization_thin_path_contract.md`](../../architecture/contracts/runtime/director_realization_thin_path_contract.md) | world-engine + ai-stack | Pi-scoped runtime aspect: director realization thin path contract |
| [`expectation_variation_contract.md`](../../architecture/contracts/runtime/expectation_variation_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: expectation variation contract |
| [`genre_awareness_contract.md`](../../architecture/contracts/runtime/genre_awareness_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: genre awareness contract |
| [`improvisational_coherence_contract.md`](../../architecture/contracts/runtime/improvisational_coherence_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: improvisational coherence contract |
| [`meta_narrative_awareness_contract.md`](../../architecture/contracts/runtime/meta_narrative_awareness_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: meta narrative awareness contract |
| [`narrative_momentum_contract.md`](../../architecture/contracts/runtime/narrative_momentum_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: narrative momentum contract |
| [`no_dead_end_recovery_contract.md`](../../architecture/contracts/runtime/no_dead_end_recovery_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: no dead end recovery contract |
| [`pacing_rhythm_contract.md`](../../architecture/contracts/runtime/pacing_rhythm_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: pacing rhythm contract |
| [`player_input_interpretation_contract.md`](../../architecture/contracts/runtime/player_input_interpretation_contract.md) | ai-stack | Pi-scoped runtime aspect: player input interpretation contract |
| [`relationship_state_machine_contract.md`](../../architecture/contracts/runtime/relationship_state_machine_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: relationship state machine contract |
| [`runtime-authority-and-state-flow.md`](../../architecture/contracts/runtime/runtime-authority-and-state-flow.md) | world-engine + backend | Pi-scoped runtime aspect: runtime authority and state flow |
| [`runtime_diagnostic_snapshot_v1_contract.md`](../../architecture/contracts/runtime/runtime_diagnostic_snapshot_v1_contract.md) | observability project SAD | Pi-scoped runtime aspect: runtime diagnostic snapshot v1 contract |
| [`sensory_context_contract.md`](../../architecture/contracts/runtime/sensory_context_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: sensory context contract |
| [`social_pressure_contract.md`](../../architecture/contracts/runtime/social_pressure_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: social pressure contract |
| [`story_runtime_complete_playable_mvp.md`](../../architecture/contracts/runtime/story_runtime_complete_playable_mvp.md) | world-engine | Pi-scoped runtime aspect: story runtime complete playable mvp |
| [`subtext_interpretation_contract.md`](../../architecture/contracts/runtime/subtext_interpretation_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: subtext interpretation contract |
| [`symbolic_object_resonance_contract.md`](../../architecture/contracts/runtime/symbolic_object_resonance_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: symbolic object resonance contract |
| [`temporal_control_contract.md`](../../architecture/contracts/runtime/temporal_control_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: temporal control contract |
| [`tonal_consistency_contract.md`](../../architecture/contracts/runtime/tonal_consistency_contract.md) | ai-stack + world-engine | Pi-scoped runtime aspect: tonal consistency contract |
| [`world_engine_authoritative_narrative_commit.md`](../../architecture/contracts/runtime/world_engine_authoritative_narrative_commit.md) | world-engine | Pi-scoped runtime aspect: world engine authoritative narrative commit |
| [`world_engine_authoritative_runtime_and_system_interactions.md`](../../architecture/contracts/runtime/world_engine_authoritative_runtime_and_system_interactions.md) | world-engine | Pi-scoped runtime aspect: world engine authoritative runtime and system interactions |

### Top-level platform contracts

| Document | Owning SAD | Binding scope |
| --- | --- | --- |
| [`turn_execution_contract.md`](../../architecture/contracts/turn_execution_contract.md) | world-engine + turn-execution-canonical UML | Canonical turn ingress → commit → project |
| [`session_authority_contract.md`](../../architecture/contracts/session_authority_contract.md) | world-engine + backend | Session authority seam |

Stubs remain at former `docs/technical/runtime/*.md` paths.

## God of Carnage (MVP vertical slice)

| Document | Binding scope |
|----------|----------------|
| [`VERTICAL_SLICE_CONTRACT_GOC.md`](../../MVPs/MVP_VSL_And_GoC_Contracts/VERTICAL_SLICE_CONTRACT_GOC.md) | Slice boundaries, YAML authority, graph reality anchor |
| [`CANONICAL_TURN_CONTRACT_GOC.md`](../../MVPs/MVP_VSL_And_GoC_Contracts/CANONICAL_TURN_CONTRACT_GOC.md) | Turn schema, seams, validation/commit/render semantics |
| [`GATE_SCORING_POLICY_GOC.md`](../../MVPs/MVP_VSL_And_GoC_Contracts/GATE_SCORING_POLICY_GOC.md) | Gate/scoring and failure-to-response policy for slice QA |

## Freeze and roadmap (context, amend carefully)

| Document | Notes |
|----------|--------|
| [`FREEZE_OPERATIONALIZATION_MVP_VSL.md`](../../MVPs/MVP_VSL_And_GoC_Contracts/FREEZE_OPERATIONALIZATION_MVP_VSL.md) | Phase 0 freeze operationalization |
| [`ROADMAP_MVP_VSL.md`](../../MVPs/MVP_VSL_And_GoC_Contracts/ROADMAP_MVP_VSL.md) | Target product arc — aspirational vs shipped must be labeled in stakeholder docs |

## RAG (active technical)

| Document | Notes |
|----------|--------|
| [`RAG.md`](../../technical/ai/RAG.md) | Canonical retrieval, governance lanes, profiles |

Historical task narratives: [`docs/archive/rag-task-legacy/`](../../archive/rag-task-legacy/).

## API reference

| Document | Audience |
|----------|----------|
| [`docs/api/REFERENCE.md`](../../api/REFERENCE.md) | Backend REST surface (large) |
| [`docs/api/README.md`](../../api/README.md) | API doc hub |

## Audit and gates (engineering program, not product docs)

Under `docs/audit/` — use for **closure evidence**, **test suite rationale**, and **dependency gates**. Do not route end users here.

Runtime-intelligence maturity and ADR relations live in [`capability_matrix_status_and_adr_relations.md`](../../MVPs/capability_matrix_status_and_adr_relations.md). Dated verification snapshots live in [`capability_matrix_verification_log.md`](../../MVPs/capability_matrix_verification_log.md), and promotion/live-claim rules live in [`capability_matrix_live_claim_gates.md`](../../MVPs/capability_matrix_live_claim_gates.md). Use these files to distinguish historical Π vocabulary from implemented generic runtime aspect names.

## Related

- [Runtime authority and session lifecycle (developer seam)](../architecture/runtime-authority-and-session-lifecycle.md)
- [Glossary](../../reference/glossary.md)
