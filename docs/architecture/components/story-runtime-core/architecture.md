# story-runtime-core — Software Architecture (arc42)

**Component:** story-runtime-core · **Folder:** `story_runtime_core/` · **Last reconciled:** `2026-06-24`

## 1. Introduction & Goals

Shared library for interpretation contracts, branching, locale, recovery helpers, and GoC builtin
templates—consumed by backend and world-engine without implying execution authority.

The package exists so duplicated runtime shapes do not live in both Flask and FastAPI trees. Importing
code here must remain free of side effects that imply live play: no socket listeners, no graph executor
construction, and no direct mutation of session stores owned by world-engine.

## 2. Constraints

Must not host HTTP or turn commit logic ([world-engine D1](../world-engine/architecture.md#d1-runtime-authority-in-world-engine)).

## 3. Context & Scope

In scope: reusable models/adapters. Out of scope: FastAPI apps, LangGraph executor.

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Dependency-light shared contracts for semantic player input, committed truth, consequence propagation, branching and delivery adapters.

**Authority rule:** The package owns portable domain contracts and pure algorithms; it does not own a live session, transport or persistence.

**Git/archaeology scope:** `story_runtime_core`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Portable contracts versus live and proposal authorities | [Story Runtime Core - Authority Context](../../../../UML/Components/story-runtime-core/context/story-runtime-core-context.md) | The package owns portable domain contracts and pure algorithms; it does not own a live session, transport or persistence. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

## 4. Solution Strategy

Extract shared shapes from deprecated backend runtime toward importable package (`story_runtime_core`).

## 5. Building Block View

| Block | Path |
| --- | --- |
| Branching | `story_runtime_core/branching/` |
| GoC solo runtime profile | `content/modules/god_of_carnage/runtime_profiles/god_of_carnage_solo.yaml` |
| Tests | `story_runtime_core/tests/` |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound building-block catalog

Each block has one stated responsibility, an interaction or ownership contract, and a current source anchor. The list is individualized for this scope; it is not derived from a fixed diagram count.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| CommittedTruth (`snapshot`) | `class` | Carry confirmed story facts | Runtime-supplied immutable snapshot | [`story_runtime_core/committed_truth.py`](../../../../story_runtime_core/committed_truth.py) |
| ConsequenceOutcome (`outcome`) | `class` | Describe calculated effects | Deterministic ordered effects | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |
| PlayerActionIntent (`action`) | `class` | Carry semantic player intent | Validated intent fields | [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py) |
| Boundary Adapters (`adapters`) | `component` | Map host-specific data to shared contracts | Anti-corruption mapping | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |
| Branching (`branching`) | `component` | Forecast alternatives without committing them | Explicit hypothetical state | [`story_runtime_core/branching/forecast.py`](../../../../story_runtime_core/branching/forecast.py) |
| Committed Truth (`truth`) | `component` | Represent authoritative facts supplied by a runtime | Immutable snapshot/value semantics | [`story_runtime_core/committed_truth.py`](../../../../story_runtime_core/committed_truth.py) |
| Consequence Cascade (`consequences`) | `component` | Compute deterministic downstream effects | Pure input/output transform | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |
| Domain Models (`models`) | `component` | Define actions, scenes, actors and outcomes | Serializable value objects | [`story_runtime_core/models.py`](../../../../story_runtime_core/models.py) |
| Input Intent (`intent`) | `component` | Normalize player language into semantic intent | Locale-independent intent contract | [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py) |
| Runtime Delivery (`delivery`) | `component` | Adapt portable outcomes to callbacks and web delivery | No ownership transfer | [`story_runtime_core/runtime_delivery.py`](../../../../story_runtime_core/runtime_delivery.py) |
| Adapted (`adapted`) | `state` | Map into host contract | Authority remains with caller | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |
| Candidate (`candidate`) | `state` | Represent unvalidated shared-domain value | No host commitment | [`story_runtime_core/models.py`](../../../../story_runtime_core/models.py) |
| Validated (`validated`) | `state` | Meet portable invariants | Safe to return to host | [`story_runtime_core/model_registry.py`](../../../../story_runtime_core/model_registry.py) |
| AI Stack (`ai`) | `system` | Produce proposals using shared semantic contracts | Proposal-only integration | [`ai_stack/story_runtime/player_action_resolution.py`](../../../../ai_stack/story_runtime/player_action_resolution.py) |
| Story Runtime Core (`core`) | `system` | Provide portable domain contracts and deterministic algorithms | Python package without service authority | [`story_runtime_core/__init__.py`](../../../../story_runtime_core/__init__.py) |
| World Engine (`world`) | `system` | Own and commit live story state | Calls pure shared contracts | [`world-engine/world_engine/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/world_engine/story_runtime/governed_runtime_adapters.py) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Imported by world-engine tests and runtime; provides template/catalog data, not live orchestration.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| Host data crosses portable algorithms and returns without authority transfer | `sequence` | [Story Runtime Core - Host Adapter Flow](../../../../UML/Components/story-runtime-core/sequence/host-adapter-flow.md) | 7 |
| Validation and host adaptation of uncommitted shared values | `state` | [Story Runtime Core - Value Lifecycle](../../../../UML/Components/story-runtime-core/states/value-lifecycle.md) | 4 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

Python package at repo root on `PYTHONPATH`.

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

This scope does not claim an independently deployable runtime. Its deployment effect is expressed through the owning systems and the following implementation roots:

- `story_runtime_core`

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

Despaghettify moved builtins out of `builtins.py` into explicit template modules.

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| PlayerActionIntent | CommittedTruth | evaluated against | revision-bound semantics | [`story_runtime_core/input_interpreter.py`](../../../../story_runtime_core/input_interpreter.py) |
| Boundary Adapters | Domain Models | maps host values | explicit anti-corruption layer | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |
| Branching | Runtime Delivery | returns outcome | host decides commit | [`story_runtime_core/runtime_delivery.py`](../../../../story_runtime_core/runtime_delivery.py) |
| Consequence Cascade | Branching | feeds alternatives | hypothetical only | [`story_runtime_core/branching/forecast.py`](../../../../story_runtime_core/branching/forecast.py) |
| Story Runtime Core | Domain Models | exports | stable public values | [`story_runtime_core/__init__.py`](../../../../story_runtime_core/__init__.py) |
| Input Intent | Committed Truth | is evaluated against | confirmed facts only | [`story_runtime_core/input_interpreter.py`](../../../../story_runtime_core/input_interpreter.py) |
| Domain Models | Input Intent | constrains | semantic action vocabulary | [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py) |
| CommittedTruth | ConsequenceOutcome | produces | ordered explainable effects | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |
| Committed Truth | Consequence Cascade | bounds cascade | pure deterministic input | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

## 9. Architecture Decisions

| ID | Title | Status | Notes |
| --- | --- | --- | --- |
| D1 | Shared extraction direction | Accepted | backend-runtime-classification |
| D2 | Language adapter compatibility seam | Accepted | ADR-0037-CONTENT |
| D3 | Aspect ledger contracts | Accepted | UML d3-aspect-ledger-contracts |
| D4 | Commit semantics helpers | Accepted | ADR-0039 committed-truth boundary |
| D5 | Session authority types | Accepted | session_authority_contract |
| D6 | Pi contract vocabulary | Accepted | ADR-0039 intent taxonomy |
| D7 | Opening readiness | Accepted | branching forecast opening lane |
| D8 | Environment state contracts | Accepted | evidence projection helpers |

### D1: Shared extraction direction

**Status:** Accepted · **Origin:** backend-runtime-classification

**Context.** Flask backend and world-engine both needed shared interpretation types without duplicating authority.

**Decision.** Shared runtime shapes (templates, adapters, interpretation contracts) live in `story_runtime_core/` for import by world-engine and backend. Importers must not treat helpers as commit owners — execution authority stays in world-engine ([world-engine SAD D1](../world-engine/architecture.md#d1-runtime-authority-in-world-engine)).

**Evidence.** [`story_runtime_core/`](../../../../story_runtime_core/), [`docs/technical/architecture/backend-runtime-classification.md`](../../../technical/architecture/backend-runtime-classification.md).

### D2: Language adapter compatibility seam

**Status:** Accepted · **Origin:** ADR-0037-CONTENT (compat layer)

**Context.** Content locale lookups were removed from runtime paths; shared core must not reintroduce authority while legacy imports still resolve during the W5 migration window.

**Decision.** `story_runtime_core.language_adapter` remains a compatibility import surface only; canonical language I/O contract lives in `ai_stack.language_io.language_adapter`. No content-module locale lookup tables in shared core. The `story-runtime-core` package declares an optional `[language]` extra in `pyproject.toml` documenting the runtime `ai_stack` peer dependency (monorepo: repo-root `PYTHONPATH`; no separate PyPI wheel). New code imports `ai_stack.language_io` directly; the shim stays until W5 migration completes.

**Evidence.** [content-authority SAD D3](../content-authority/architecture.md#d3-remove-content-locale-runtime-lookups), [`ai_stack/language_io/`](../../../../ai_stack/language_io/), [`story_runtime_core/pyproject.toml`](../../../../story_runtime_core/pyproject.toml).

### D3: Aspect ledger contracts

**Status:** Accepted · **Origin:** UML d3-aspect-ledger-contracts

**Context.** Turn execution surfaces dozens of runtime aspects (input, validation, voice, beat, commit). Without shared vocabulary for aspect record shape, each consumer invents incompatible ledger rows and gates cannot compare expected versus actual evidence across backend and world-engine.

**Decision.** Shared core exposes serialization helpers and stable JSON-safe projections consumed by ai-stack aspect record builders. Aspect identifiers and record envelopes remain contract-owned in `ai_stack/contracts/` and runtime executor modules; `story_runtime_core` supplies portable helpers only and never writes commit authority.

**Evidence.** [`story_runtime_core/serialization.py`](../../../../story_runtime_core/serialization.py), [`story_runtime_core/evidence_projection_helpers.py`](../../../../story_runtime_core/evidence_projection_helpers.py), [UML d3-aspect-ledger-contracts](../../../../UML/Components/story-runtime-core/decisions/d3-aspect-ledger-contracts.md).

### D4: Commit semantics helpers

**Status:** Accepted · **Origin:** ADR-0039 committed-truth boundary

**Context.** Runtime history mixes recoverable rejection rows with committed story truth. Feedback graphs such as callback-web and consequence-cascade must not seed from playable recovery turns or projection failures.

**Decision.** `story_runtime_core.committed_truth` and `story_runtime_core.recovery` publish predicates and recovery record builders that classify rows by schema/status/commit fields—not by generated narration. Consumers filter history before seeding bounded feedback graphs; recoverable outcomes remain auditable but excluded from committed-truth scope.

**Evidence.** [`story_runtime_core/committed_truth.py`](../../../../story_runtime_core/committed_truth.py), [`story_runtime_core/recovery/no_dead_end.py`](../../../../story_runtime_core/recovery/no_dead_end.py), [`story_runtime_core/tests/test_no_dead_end_recovery.py`](../../../../story_runtime_core/tests/test_no_dead_end_recovery.py).

### D5: Session authority types

**Status:** Accepted · **Origin:** session_authority_contract

**Context.** Backend and world-engine must agree which process owns session identity, turn numbering, and commit seams without duplicating authority markers in each service tree.

**Decision.** Session authority boundaries are documented in `docs/architecture/contracts/session_authority_contract.md`. Shared core types (`ExperienceKind`, participant modes, template models) describe experience shape only; they do not perform session creation, routing, or commit. Importers treat `story_runtime_core` models as portable data, not authority owners.

**Evidence.** [`docs/architecture/contracts/session_authority_contract.md`](../../contracts/session_authority_contract.md), [`story_runtime_core/experience_template_models.py`](../../../../story_runtime_core/experience_template_models.py), [`tests/test_session_authority.py`](../../../../tests/test_session_authority.py).

### D6: Pi contract vocabulary

**Status:** Accepted · **Origin:** ADR-0039 intent taxonomy

**Context.** Player-input kind lists were copied into tests, gates, and runtime surfaces, causing drift when taxonomy expanded (movement, perception, social nonverbal, mixed lanes).

**Decision.** `story_runtime_core.player_input_intent_contract` is the single shared taxonomy: kind sets, family helpers, commit-flag defaults, and speech-projection guards. Runtime and tests import from this module instead of hardcoding kind strings; semantic resolution defers classification to AI ingress while using the contract for downstream routing.

`InterpretedInputKind` in `models.py` is a thin structural preview (eight values) produced by `input_interpreter` before AI ingress. It is not the authoritative taxonomy. When semantic resolution is unavailable, the executor falls back using:

| Structural (`InterpretedInputKind`) | Intent fallback (`player_input_kind`) | Graph routing (`input_kind`) |
| --- | --- | --- |
| speech | speech | speech |
| action | action | action |
| mixed | mixed | mixed |
| reaction | speech | speech |
| intent_only | speech | speech |
| ambiguous | ambiguous | action |
| explicit_command | unclear | speech |
| meta | meta | meta |

Canonical mapping constants: `STRUCTURAL_KIND_TO_INTENT_FALLBACK` and `STRUCTURAL_KIND_TO_INPUT_ROUTING` in `player_input_intent_contract.py`.

**Evidence.** [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py), [`story_runtime_core/models.py`](../../../../story_runtime_core/models.py), [`story_runtime_core/tests/test_player_input_intent_contract.py`](../../../../story_runtime_core/tests/test_player_input_intent_contract.py).

### D7: Opening readiness

**Status:** Accepted · **Origin:** branching forecast opening lane

**Context.** Opening turns (turn_number ≤ 0, engine establishment) need distinct envelope handling from live player turns so branching forecasts, director hints, and playability gates do not treat establishment as a normal player move.

**Decision.** Shared branching helpers (`branching/forecast.py`) emit opening-specific forecast envelopes with `turn_kind` opening/engine_opening semantics. Director surface hints load authored guidance from content modules without implying commit. Opening classification uses `player_input_intent_contract` opening kind; live orchestration remains in world-engine/ai-stack graph nodes.

**Evidence.** [`story_runtime_core/branching/forecast.py`](../../../../story_runtime_core/branching/forecast.py), [`story_runtime_core/director_surface_hints.py`](../../../../story_runtime_core/director_surface_hints.py), [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py).

### D8: Environment state contracts

**Status:** Accepted · **Origin:** evidence projection helpers

**Context.** Scene projections, observability tree classification, and bounded evidence hashes must stay consistent when runtime aspects emit location or scene-energy payloads across backend traces and world-engine commits.

**Decision.** `evidence_projection_helpers` provides stable hashing, deduplication, and compact text for evidence bundles. `observability_tree_policy` classifies observation trees (including `scene_projection`) so Langfuse and gate consumers share vocabulary. Environment actor-location substrate remains world-engine owned; shared core supplies projection helpers only.

**Evidence.** [`story_runtime_core/evidence_projection_helpers.py`](../../../../story_runtime_core/evidence_projection_helpers.py), [`story_runtime_core/observability_tree_policy.py`](../../../../story_runtime_core/observability_tree_policy.py), [`story_runtime_core/tests/test_observability_tree_policy.py`](../../../../story_runtime_core/tests/test_observability_tree_policy.py).

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D1` | Portable contracts versus live and proposal authorities | `context` | [Story Runtime Core - Authority Context](../../../../UML/Components/story-runtime-core/context/story-runtime-core-context.md) |
| `D1`, `D2` | Pure model, intent, truth, consequence, branching and delivery seams | `component` | [Story Runtime Core - Components](../../../../UML/Components/story-runtime-core/components/domain-components.md) |
| `D1`, `D3` | Host data crosses portable algorithms and returns without authority transfer | `sequence` | [Story Runtime Core - Host Adapter Flow](../../../../UML/Components/story-runtime-core/sequence/host-adapter-flow.md) |
| `D2` | Intent, committed truth and calculated outcomes | `class` | [Story Runtime Core - Contract Data Model](../../../../UML/Components/story-runtime-core/classes/contract-data-model.md) |
| `D3` | Validation and host adaptation of uncommitted shared values | `state` | [Story Runtime Core - Value Lifecycle](../../../../UML/Components/story-runtime-core/states/value-lifecycle.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

`story_runtime_core/tests/`, importers must not reintroduce authority.

## 11. Risks & Technical Debt

Consumers must not treat helpers as commit owners.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

Shared code risks becoming a second runtime. Models separate pure contracts from world-engine ownership and reveal adapters that have accumulated product-specific behavior.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 54 | 76 | 194 | 0 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| Scope-specific watch | `open_target` | No global claim currently maps to this root. | Keep source-bound views and review on structural Git changes. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Builtin template | Canonical GoC solo structure definitions |
