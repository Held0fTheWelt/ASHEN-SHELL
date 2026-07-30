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

## 4. Solution Strategy

Module.yaml + canonical_path + locations/characters/objects/knowledge/direction trees; backend compiles for engine consumption.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Module root | `content/modules/god_of_carnage/module.yaml` |
| Canonical path | `canonical_path/*.yaml` |
| Template | `content/modules/_template/` |

## 6. Runtime View

Publish/compile pipeline (backend) → runtime projection loaded by world-engine for play.

## 7. Deployment View

Content ships in repo; not a separate deployable process.

## 8. Crosscutting Concepts

Writers-room drafts are not production truth.

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

## 10. Quality Requirements

- Canonical content roots and runtime template adapters must be discoverable.
- Accepted authority decisions require bindings to the content compiler,
  resolver or canonical source tree.
- Required depth views must link their modeled elements to those anchors.

## 11. Risks & Technical Debt

No second module in MVP scope—engine must stay generic per mvp-live-runtime-completion anti-creep policy.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Runtime profile | Selection of how a module runs, not a content module |
