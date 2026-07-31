# content-authority — Software Architecture (arc42)

**Component:** content-authority · **Folder:** `content/modules/` · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

YAML-first authored modules define the formally permitted possibility space for stories. God of Carnage
is the reference module; runtime profiles (e.g. solo) are not content modules.

Authors express canon as structured YAML trees; the backend compilation step produces runtime projections
the engine may load. Writers-room and research outputs remain drafts until human governance publishes
them through the content pipeline.

## 2. Constraints

AI may not invent canon ([mvp-live-runtime-completion SAD §2](../../project/mvp-live-runtime-completion/architecture.md#2-constraints)); engine validates against compiled projections.

## 3. Context & Scope

In scope: `content/modules/god_of_carnage/**`, `_template/`. Out of scope: live session execution.

<!-- BEGIN BT-SEMANTIC-DEPTH:3 -->
### Evidence-grounded scope and authority

Authored module truth, schemas, compilation and runtime consumption for Better Tomorrow experiences.

**Authority rule:** Versioned YAML modules own authored facts; compilers and runtimes may validate and project them but may not create competing content truth.

**Git/archaeology scope:** `content`, `backend/app/content`, `world-engine/world_engine/content`, `ai_stack/story_runtime/god_of_carnage`

| Context concern | Model | Boundary statement |
| --- | --- | --- |
| Authored truth and its validating and consuming systems | [Content Authority - Context](../../../../UML/Components/content-authority/context/content-authority-context.md) | Versioned YAML modules own authored facts; compilers and runtimes may validate and project them but may not create competing content truth. |

Historical MVP and work-order material is classified evidence, not an authority source. Current code and accepted decisions win; conflicts remain explicit until a target decision is accepted.
<!-- END BT-SEMANTIC-DEPTH:3 -->

## 4. Solution Strategy

Module.yaml + canonical_path + locations/characters/objects/knowledge/direction trees; backend compiles for engine consumption.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Module root | `content/modules/god_of_carnage/module.yaml` |
| Canonical path | `canonical_path/*.yaml` |
| Template | `content/modules/_template/` |

<!-- BEGIN BT-SEMANTIC-DEPTH:5 -->
### Source-bound building-block catalog

Each block has one stated responsibility, an interaction or ownership contract, and a current source anchor. The list is individualized for this scope; it is not derived from a fixed diagram count.

| Block | Kind | Responsibility | Contract | Source |
| --- | --- | --- | --- | --- |
| Content Author (`author`) | `actor` | Define experience facts, locations, objects and dramatic policy | Schema-conforming module changes | [`content/modules/_template/README.md`](../../../../content/modules/_template/README.md) |
| Canonical Path (`canonical_path`) | `class` | Express authored dramatic invariants without scripting player choice | Schema-governed beats and alternatives | [`content/modules/god_of_carnage/canonical_path/_schema.yaml`](../../../../content/modules/god_of_carnage/canonical_path/_schema.yaml) |
| Narrative Policies (`policies`) | `class` | Bound memory, aspects, beats and phase behavior | Declarative policy YAML | [`content/modules/god_of_carnage/narrative_aspect_policy.yaml`](../../../../content/modules/god_of_carnage/narrative_aspect_policy.yaml) |
| Scene Graph (`scene_graph`) | `class` | Describe spaces, actors, objects and connections | Stable identifiers and references | [`content/modules/god_of_carnage/scene_graph.yaml`](../../../../content/modules/god_of_carnage/scene_graph.yaml) |
| AI Content Adapter (`ai_adapter`) | `component` | Translate canonical content into proposal context | Provenance-preserving read model | [`ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py`](../../../../ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py) |
| Backend Module Compiler (`compiler`) | `component` | Load, validate and normalize authored documents | Deterministic module model or diagnostics | [`backend/app/content/module_loader.py`](../../../../backend/app/content/module_loader.py) |
| Module Validator (`validator`) | `component` | Enforce schemas and cross-document references | Fail-closed validation findings | [`backend/app/content/module_validator.py`](../../../../backend/app/content/module_validator.py) |
| World Content Loader (`world_loader`) | `component` | Materialize published content for live sessions | Read-only runtime projection | [`world-engine/world_engine/content/backend_loader.py`](../../../../world-engine/world_engine/content/backend_loader.py) |
| Draft (`draft`) | `state` | Accept author changes | Not runtime-consumable | [`backend/app/content/module_models.py`](../../../../backend/app/content/module_models.py) |
| Published (`published`) | `state` | Expose immutable content version | Active version pointer | [`backend/app/content/module_service.py`](../../../../backend/app/content/module_service.py) |
| Runtime Projection (`consumed`) | `state` | Serve content to a bound session | No mutation of authored truth | [`world-engine/world_engine/content/backend_source.py`](../../../../world-engine/world_engine/content/backend_source.py) |
| Validated (`validated`) | `state` | Record successful structural checks | All references resolve | [`backend/app/content/module_validator.py`](../../../../backend/app/content/module_validator.py) |
| Authored Module (`module`) | `system` | Hold canonical versioned content truth | module.yaml plus referenced YAML documents | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
<!-- END BT-SEMANTIC-DEPTH:5 -->

## 6. Runtime View

Publish/compile pipeline (backend) → runtime projection loaded by world-engine for play.

<!-- BEGIN BT-SEMANTIC-DEPTH:6 -->
### Dynamic viewpoint suite

| Runtime concern | Viewpoint | Model | Modeled interactions |
| --- | --- | --- | ---: |
| Fail-closed path from author change to runtime-readable version | `activity` | [Content Authority - Publication Flow](../../../../UML/Components/content-authority/activity/content-publication-flow.md) | 4 |
| Validation, publication and runtime binding states | `state` | [Content Authority - Lifecycle](../../../../UML/Components/content-authority/states/content-lifecycle.md) | 6 |

The ordered sequence/activity relationships and state transitions are validated against the catalog. Generic arrows such as "evidence for boundary" are not accepted as runtime semantics.
<!-- END BT-SEMANTIC-DEPTH:6 -->

## 7. Deployment View

Content ships in repo; not a separate deployable process.

<!-- BEGIN BT-SEMANTIC-DEPTH:7 -->
### Deployment and operational boundary evidence

This scope does not claim an independently deployable runtime. Its deployment effect is expressed through the owning systems and the following implementation roots:

- `content`
- `backend/app/content`
- `world-engine/world_engine/content`
- `ai_stack/story_runtime/god_of_carnage`

A deployment boundary is not inferred from a directory. Process, store, transport and trust contracts must be named by a deployment view or delegated to an owning SAD.
<!-- END BT-SEMANTIC-DEPTH:7 -->

## 8. Crosscutting Concepts

Writers-room drafts are not production truth.

<!-- BEGIN BT-SEMANTIC-DEPTH:8 -->
### Explicit interaction and dependency contracts

| From | To | Semantics | Contract | Evidence |
| --- | --- | --- | --- | --- |
| Backend Module Compiler | Module Validator | requests validation | normalized module candidate | [`backend/app/content/module_validator.py`](../../../../backend/app/content/module_validator.py) |
| Authored Module | Backend Module Compiler | is compiled by | complete referenced document set | [`backend/app/content/module_loader_documents.py`](../../../../backend/app/content/module_loader_documents.py) |
| Authored Module | Canonical Path | contains | dramatic invariants only | [`content/modules/god_of_carnage/canonical_path/_schema.yaml`](../../../../content/modules/god_of_carnage/canonical_path/_schema.yaml) |
| Authored Module | Narrative Policies | contains | declarative runtime bounds | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| Authored Module | Scene Graph | contains | referentially complete scene graph | [`content/modules/god_of_carnage/scene_graph.yaml`](../../../../content/modules/god_of_carnage/scene_graph.yaml) |
| Module Validator | World Content Loader | releases version | validation success only | [`backend/app/content/module_service.py`](../../../../backend/app/content/module_service.py) |
| World Content Loader | AI Content Adapter | supplies bounded facts | session-bound content projection | [`world-engine/world_engine/content/backend_loader.py`](../../../../world-engine/world_engine/content/backend_loader.py) |
<!-- END BT-SEMANTIC-DEPTH:8 -->

## 9. Architecture Decisions

| ID | Title | Status | Migrated from |
| --- | --- | --- | --- |
| D1 | Canonical authored content model | Accepted | ADR-0025 |
| D2 | Canonical content authority (MVP) | Accepted | MVP1-005 |
| D3 | Content locale removal / language boundaries | Accepted | ADR-0037-CONTENT |

### D1: Canonical Authored Content Model

**Status:** Accepted
**Origin:** ADR-0025 (retired 2026-06-23)

**Context.** Content authoring in the repository uses structured content modules under
`content/modules/<module_id>/`. Multiple tools and projections consume these
sources; a single canonical authored content model avoids divergence.

The model has moved beyond the early flat scene/trigger/ending file set. The
current contract prefers modular authority surfaces: locations describe places,
objects describe inspectable things, character folders describe people and
relationships, and `canonical_path/` describes directed story order by
reference.

**Decision.** - Declare the structured module format under `content/modules/<module_id>/` as
  the canonical authored content model.
- Treat `ContentModule` and the backend loader (`backend/app/content/module_loader.py`) as the authoritative ingestion surface for authored content.
- Compile authored content into projection outputs: `runtime_projection`, `retrieval_corpus_seed`, and `review_export_seed`.
- Content modules must not duplicate location, object, character, or language
  meaning in parallel lookup databases. Directed story and runtime guidance
  reference canonical content IDs rather than restating prose.

**Consequences.** - Consumers (World-Engine, review tools, RAG ingestion) must read the canonical compiled projections rather than ad-hoc source variants.
- Changes to the canonical model require an ADR and coordination across the runtime and backend teams.

**Implementation status.** **Implemented and stable.**

- `content/modules/<module_id>/` YAML format is the canonical authored content
  model (god_of_carnage/, etc.). Current modules may be folder-based: canonical
  path, locations, objects, characters, knowledge, direction, and module policy
  live as separate authority surfaces.
- `backend/app/content/module_loader.py` and `backend/app/content/module_models.py` are the authoritative ingestion surface.
- `backend/app/content/compiler/` compiles to three projections: `runtime_projection`, `retrieval_corpus_seed`, `review_export_seed`.
- World-Engine, review tools, and RAG (`ai_stack/rag/__init__.py`) consume compiled projections.
- `docs/technical/content/canonical_authored_content_model.md` and `docs/dev/architecture/content-modules-and-compiler-pipeline.md` document the pipeline with "Migrated Decision: See ADR-0025" pointers.
- YAML > published snapshots > writers-room > builtins authority precedence is enforced in the loader.
- Status promoted from "Proposed" because the decision has been stable through MVP1–MVP4.

**Testing.** Contract / unit coverage as cited in **References**; extend this section when a dedicated gate exists. Revisit this ADR if enforcement drifts or the decision is bypassed in code review.

**Evidence.** `docs/architecture/components/content-authority/architecture.md#d1-canonical-authored-content-model` (archived — see `docs/archive/adr-retired-2026/`)

### D2: Canonical content authority (MVP)

**Status:** Accepted · **Origin:** MVP1-005

**Context.** MVP1 required a hard boundary between authored story modules and runtime templates so AI stages cannot invent canon at load or turn time; violations fail closed at compile and session bootstrap.

**Decision.** MVP content authority flows through compile/publish pipeline before engine load; AI may not invent canon ([mvp-live-runtime-completion SAD §2](../../project/mvp-live-runtime-completion/architecture.md#2-constraints)).

**Evidence.** [`tests/smoke/test_goc_module_structure_smoke.py`](../../../../tests/smoke/test_goc_module_structure_smoke.py), GoC foundation gates.

### D3: Remove Content Locale Runtime Lookups

**Status:** Accepted
**Origin:** ADR-0037-CONTENT (retired 2026-06-23)

**Context.** The earlier story-runtime shell treated player language as a module-owned
lookup problem. Module string files, locale directories, phrase rules, actor
alias matchers, and per-language action maps tried to map utterances into
runtime actions.

That design was not general. It created a second description database beside
locations, objects, characters, canonical path content, and module policy. It
also made German support look correct only for the phrases already written into
the engine.

**Decision.** 1. Content modules must not ship locale lookup directories, phrase-rule files,
   verb maps, action maps, actor-name text matchers, or duplicate language
   description databases.
2. `ai_stack.language_io.language_adapter` exposes a content-derived semantic
   catalog and an AI resolution contract. `story_runtime_core.language_adapter`
   remains a compatibility import only.
3. Player input is labeled with `session_input_language`. Player-visible output
   is governed separately by `session_output_language`.
4. The AI normalizes player input into the module's declared authoring language
   for internal grounding when the player language differs. If player language
   and module language already match, the language pipeline is a no-op diagnostic
   boundary, not a translation call. Visible narration is produced in the
   requested output language.
5. Thin deterministic interpreters may recognize structural control surfaces
   such as empty input, punctuation-only input, slash commands, meta control,
   and quoted speech previews. They must not decide natural-language actions,
   target actors, scene functions, or social moves through word lists.
6. Output-language support is owned by the story output module. Deterministic
   source paths, narrator-path openings, and Souffleuse guidance may produce
   module-language source blocks, but they must not satisfy another output
   language by reading localized content fields, per-language prompt prose, or
   code-level translated strings. If source language and output language match,
   output realization is skipped and recorded as not required.
7. Tests may use tiny language-specific stubs to prove that the output module
   was invoked. They must not encode production story prose as the expected
   answer.

**Consequences.** - Meaning is resolved semantically against authored locations, objects,
  characters, and policy surfaces.
- Unknown or underspecified actions remain clarification requests instead of
  being guessed by code-level phrase rules.
- Runtime language support scales through the AI adapter contract rather than
  per-module lookup tables.
- Runtime tests must assert the semantic contract, content IDs, and structured
  diagnostics, not phrase fixtures.
- Player-visible German can still be tested, but the provenance must identify
  the output module rather than a content-locale lookup.

**Evidence.** `docs/architecture/components/backend/architecture.md#d3-test-suite-split-in-orchestrator` (archived — see `docs/archive/adr-retired-2026/`)

 Quality Requirements

`tests/smoke/test_goc_module_structure_smoke.py`, content validators, GoC gate tests.

<!-- BEGIN BT-SEMANTIC-DEPTH:9 -->
### Decision-to-view correspondence

| Decision(s) | Concern | Viewpoint | Model |
| --- | --- | --- | --- |
| `D1`, `D2` | Authored truth and its validating and consuming systems | `context` | [Content Authority - Context](../../../../UML/Components/content-authority/context/content-authority-context.md) |
| `D1`, `D3` | Validation and projection seams from YAML to runtime | `component` | [Content Authority - Compilation Components](../../../../UML/Components/content-authority/components/content-compilation-components.md) |
| `D2`, `D3` | Fail-closed path from author change to runtime-readable version | `activity` | [Content Authority - Publication Flow](../../../../UML/Components/content-authority/activity/content-publication-flow.md) |
| `D1` | Relationships among scene truth, canonical path and narrative policies | `class` | [Content Authority - Data Model](../../../../UML/Components/content-authority/classes/content-data-model.md) |
| `D2`, `D3` | Validation, publication and runtime binding states | `state` | [Content Authority - Lifecycle](../../../../UML/Components/content-authority/states/content-lifecycle.md) |

The correspondence is intentionally many-to-many: one decision may require structural, dynamic, data and deployment evidence, and one model may make several decisions analyzable together.
<!-- END BT-SEMANTIC-DEPTH:9 -->

## 10. Quality Requirements

- Canonical content roots and runtime template adapters must be discoverable.
- Accepted authority decisions require bindings to the content compiler,
  resolver or canonical source tree.
- Required depth views must link their modeled elements to those anchors.

## 11. Risks & Technical Debt

No second module in MVP scope—engine must stay generic per mvp-live-runtime-completion anti-creep policy.

<!-- BEGIN BT-SEMANTIC-DEPTH:11 -->
### Git-grounded drift profile

Content has moved between generic templates, God of Carnage specializations, backend compilation, world-engine loading and AI adapters. The models expose duplicate vocabularies and projection seams.

| Tracked files | Lifetime commits | Recent path touches | Recent renames |
| ---: | ---: | ---: | ---: |
| 219 | 85 | 713 | 59 |

| Drift claim | Status | Concern | Target direction |
| --- | --- | --- | --- |
| `DRIFT-004` | `conflicting` | Authored content truth has several executable projections | Keep YAML modules as authored truth, generate or validate a versioned compiled content contract once, and make world-engine/AI consumers read that contract through anti-corruption adapters. |
| `DRIFT-005` | `open_target` | Beat and canonical-path authority in the live turn | Model authored canonical constraints separately from live beat state. World-engine owns live progression; AI may propose beat effects; frontend displays only committed player-safe projections. |

[Git/archaeology baseline](../../evidence/architecture-drift-baseline.md) · [Drift reconciliation and target directions](../../evidence/architecture-drift-reconciliation.md)

These entries are review inputs, not automatic design decisions. Conflicting/open items close only through accepted target decisions and the listed behavioral evidence.
<!-- END BT-SEMANTIC-DEPTH:11 -->

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Runtime profile | Selection of how a module runs, not a content module |
