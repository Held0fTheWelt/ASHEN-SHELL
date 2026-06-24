# story-runtime-core — Software Architecture (arc42)

**Component:** story-runtime-core · **Folder:** `story_runtime_core/` · **Last reconciled:** `2026-06-23`

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

## 10. Quality Requirements

`story_runtime_core/tests/`, importers must not reintroduce authority.

## 11. Risks & Technical Debt

Consumers must not treat helpers as commit owners.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Builtin template | Canonical GoC solo structure definitions |
