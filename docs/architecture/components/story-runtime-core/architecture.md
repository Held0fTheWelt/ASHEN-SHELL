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

## 4. Solution Strategy

Extract shared shapes from deprecated backend runtime toward importable package (`story_runtime_core`).

## 5. Building Block View

| Block | Path |
| --- | --- |
| Branching | `story_runtime_core/branching/` |
| GoC builtin template | `goc_solo_builtin_template.py`, catalog/roles modules |
| Tests | `story_runtime_core/tests/` |

## 6. Runtime View

Imported by world-engine tests and runtime; provides template/catalog data, not live orchestration.

## 7. Deployment View

Python package at repo root on `PYTHONPATH`.

## 8. Crosscutting Concepts

Despaghettify moved builtins out of `builtins.py` into explicit template modules.

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

**Decision.** `story_runtime_core.language_adapter` remains a compatibility import surface only; canonical language I/O contract lives in `ai_stack.language_io.language_adapter`. No content-module locale lookup tables in shared core.

**Evidence.** [content-authority SAD D3](../content-authority/architecture.md#d3-remove-content-locale-runtime-lookups), [`ai_stack/language_io/`](../../../../ai_stack/language_io/).

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

**Evidence.** [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py), [`story_runtime_core/tests/test_player_input_intent_contract.py`](../../../../story_runtime_core/tests/test_player_input_intent_contract.py).

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

## 10. Quality Requirements

`story_runtime_core/tests/`, importers must not reintroduce authority.

## 11. Risks & Technical Debt

Consumers must not treat helpers as commit owners.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Builtin template | Canonical GoC solo structure definitions |
