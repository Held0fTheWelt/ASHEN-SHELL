# SPEC 02 — Structured UML Round-Trip

Status: Proposed
Date: 2026-06-16
Depends on: SPEC_01 (DB foundation, round-trip pattern, MCP spine)

## 1. Purpose

Store UML diagrams as a **fully structured model** (elements + relationships) in the database and
keep a **lossless round-trip** with the PlantUML folder, so the agent and author can edit diagrams
at the model level while the `.puml` files remain reliable export targets.

This reconciles two requirements that are in tension: "fully structured UML model" and
"import/export must always work". The reconciliation is: a structured core for what we model, a
preserved-extras mechanism for everything else, and a conformance gate that proves losslessness on
the real corpus.

## 2. Scope

In scope:

- PlantUML parser → structured model for the diagram kinds actually used: class, activity/flow,
  object, sequence, state, use-case.
- Structured model → PlantUML renderer (deterministic).
- Preserved-extras mechanism for anything not structurally modeled.
- Round-trip conformance gate over the real `.puml` corpus.
- MCP UML authoring tools (diagram + element + relationship level).
- CLI import/export for the UML folder.

Out of scope (later specs / never): image rendering, auto-layout, semantic ADR↔UML linking
(SPEC_03), new diagram kinds beyond the six above modeled structurally (they fall back to
passthrough), Mermaid as a UML source (embedded mermaid in ADRs stays verbatim per SPEC_01).

## 3. Success criteria

1. Every existing `.puml` imports without loss; each diagram can reproduce its original bytes from
   `raw_source`.
2. `parse → render → parse` yields an identical structured model (idempotent); byte-stable after a
   one-time normalization, verified across the whole real UML corpus.
3. Every identifier, relationship, note, stereotype, and skinparam present in the source is present
   after round-trip (no semantic loss), including constructs the structured model does not
   understand.
4. The agent can, via MCP: list diagrams, read a structured diagram, add/update an element, add a
   relationship, and export — producing a clean, reviewable Git diff in the UML folder.

## 4. The structured-core + preserved-extras model

Reuse the base `uml_diagrams`, `uml_elements`, `uml_relationships` tables. Additions:

- `uml_diagrams`: add `raw_source TEXT` (safety net) and `diagram_kind TEXT`
  (`class|activity|object|sequence|state|usecase|unknown`). Reuse `model_json` to hold
  **header extras** (`@startuml` arguments, `title`, `skinparam*`, `!define`/`!include`,
  preprocessor lines, leading comments) and **ordered passthrough tokens** with positional anchors.
- `uml_elements`: structured nodes — `element_type` (`class|interface|enum|actor|usecase|state|participant|object|...`),
  `name`, plus `metadata_json` carrying `stereotype`, `alias`, members (attributes/methods for class
  diagrams), and type-specific extras (color, attached notes, port hints).
- `uml_relationships`: edges — `relationship_type`
  (`extends|implements|association|dependency|composition|aggregation|transition|message|include|extend|...`),
  source/target element refs, `label`, plus `metadata_json` carrying arrow style, direction,
  multiplicity, and extras.

**Passthrough tokens** are the key to "always works": any line or block the structured parser does
not model (a complex `note ... end note`, `legend`, `!include`, preprocessor macro, an unknown
construct) is captured as an opaque token anchored to its position in the diagram's token stream.
The renderer re-emits these verbatim in order. The parser therefore never fails — unmodeled input
degrades to faithful passthrough rather than an error.

## 5. Round-trip pipeline

- **Import** (`uml.import_diagrams(folder, project_id)`): per `.puml`, detect `diagram_kind`,
  tokenize, build the structured model + positional passthrough tokens, persist with `raw_source`.
- **Export** (`uml.export_diagrams(folder, project_id)`): render structured elements/relationships
  interleaved with passthrough tokens by position; re-apply header/layout extras; write into the
  UML folder.
- **Conformance gate** (`uml.check(folder)`): for every file `parse → render → parse` equals the
  model; idempotent and byte-stable after one normalization; plus a semantic-coverage assertion
  (every identifier/relationship/note/stereotype/skinparam in the source survives). Runs over the
  whole real corpus in CI — this is the release gate for the lossless invariant.

## 6. Module layout

```
architectural_knowledge_db/uml/
  detect.py        # diagram-kind detection
  tokenizer.py     # PlantUML -> token stream
  parser.py        # tokens -> structured model + passthrough
  renderer.py      # structured model + passthrough -> PlantUML
  roundtrip.py     # import/export orchestration + conformance check
```

The parser/renderer are pure functions over text and the structured model; `roundtrip` owns
persistence. Per-kind logic lives behind `detect`/`parser` so adding a kind is a localized change.

## 7. MCP UML authoring tools

Read:
- `akdb_list_diagrams(project_id, kind?, limit?)`
- `akdb_get_diagram(project_id, diagram_id)` → structured elements + relationships + extras summary

Write (DB-first; files change only via export):
- `akdb_add_uml_element(project_id, diagram_id, element_type, name, attrs?)`
- `akdb_update_uml_element(project_id, element_id, changes)`
- `akdb_add_uml_relationship(project_id, diagram_id, source, target, relationship_type, label?)`
- `akdb_export_uml(project_id, folder?)`
- `akdb_import_uml(project_id, folder?)`

The structured elements created here are the anchor targets for ADR↔UML element-level links in
SPEC_03.

## 8. Testing

- **Round-trip property test** over the entire real `.puml` corpus: idempotency + no semantic loss
  vs. `raw_source`.
- **Golden-file tests per diagram kind** (class/activity/object/sequence/state/use-case).
- **Passthrough preservation tests:** skinparams, `note`/`legend`, `!include`, preprocessor lines,
  and a deliberately unknown construct all survive round-trip byte-for-byte.
- **MCP tool tests:** add/update element and relationship produce expected model + exported file.

## 9. Primary risk and mitigation

Lossless structured round-trip of hand-written PlantUML is the hardest part of the whole product.
Mitigations, in order of strength:

1. `raw_source` safety net — the original is always reproducible.
2. Passthrough tokens — anything unmodeled is preserved verbatim, so import never destroys content.
3. Conformance gate over the real corpus — losslessness is a tested release gate, not a hope.
4. Structural support limited to the six diagram kinds in use; everything else degrades to
   passthrough.

## 10. Open decisions

- Granularity of positional anchors for passthrough (line-level vs. block-level) — proposed default:
  block-level anchored between structured statements, refined during planning.
- Whether class-diagram members are first-class rows or live in element `metadata_json` — proposed
  default: `metadata_json` for this spec, promote to rows only if SPEC_03 needs member-level links.
