# SPEC 05 — Retrieval & Context Packs

Status: Proposed
Date: 2026-06-16
Depends on: SPEC_01 (ADRs/FTS), SPEC_02 (UML), SPEC_03 (consistency/links), SPEC_04 (provenance/staleness)

## 1. Purpose

The agent-context headline feature: search across all knowledge types and build **authority-aware
context packs** for a task. This is where the whole graph (ADRs, UML, links, provenance, staleness)
is assembled into one task-shaped bundle that separates normative knowledge from evidence. This spec
also introduces the FastAPI HTTP surface from the base OpenAPI contract.

## 2. Scope

In scope:

- Extend FTS5 (ADR-only in SPEC_01) to all item types: definitions, rules, source areas, UML
  elements.
- Context-pack builder (base spec §9): input = project, task, optional source paths, requested
  types, max items, include/exclude flags; output = summary, hard guardrails, relevant ADRs, active
  rules, canonical definitions, UML elements, source areas, Git provenance evidence, staleness
  warnings, excluded/superseded items.
- Authority resolver that orders and labels every item (normative vs. evidence).
- **Optional semantic retrieval hook:** a pluggable `EmbeddingProvider` interface. Default is
  FTS-only (autark, zero deps). When a provider is configured, results are merged with FTS via
  reciprocal-rank fusion. The product never hard-depends on embeddings.
- FastAPI HTTP surface implementing the base OpenAPI contract (`/projects`, `/search`,
  `/context-pack`, `/origin/explain`, `/staleness`, `/git/scan`, `/index/rebuild`).
- `validate_task_context`: check a proposed task against ADRs/rules using retrieval + the SPEC_03
  consistency engine.

Out of scope: shipping/training an embedding model (provider is pluggable, default off), cloud
services, multi-user.

## 3. Success criteria

1. A context pack for a task returns hard guardrails and accepted ADRs first, with superseded items
   excluded (or clearly marked), and evidence (Git/inferred) separated from normative items.
2. Search returns project-local + explicitly imported shared items only; never a silent global
   search.
3. With no embedding provider configured, the system is fully functional on FTS alone.
4. The HTTP contract matches the base OpenAPI sketch; MCP tools and HTTP routes call the same core.

## 4. Data model

Reuse `fts_knowledge` (extend population to all item types) and `context_pack_runs` (run history).
An optional vector-index table is introduced only when a semantic provider is enabled; it is not
part of the default schema.

## 5. Module layout

```
architectural_knowledge_db/
  retrieval/
    fts.py            # full-text query across item types
    embedding.py      # EmbeddingProvider interface (default: none)
    fusion.py         # reciprocal-rank fusion when a provider is present
  context/
    builder.py        # assemble context pack
    authority.py      # authority ordering + normative/evidence labeling
    validate.py       # validate_task_context
  api/
    app.py            # FastAPI application
    routes.py         # OpenAPI-contract routes
```

## 6. MCP tools

- `akdb_search(project_id, query, include_types?, limit?)`
- `akdb_get_context_pack(project_id, task, source_paths?, include_git_provenance?, include_staleness?, max_items?)`
- `akdb_validate_task_context(project_id, task, source_paths?)`

## 7. Testing

- Authority-ordering and normative-vs-evidence separation on a seeded multi-type fixture.
- Superseded/excluded handling in context packs.
- Project-scope enforcement on search and context packs.
- FTS recall on fixtures; fusion correctness when a stub embedding provider is present.
- HTTP contract tests against the OpenAPI sketch.

## 8. Open decisions

- Default `max_items` and per-type caps for context packs — tuned during planning against real ADR
  retrieval quality.
- Whether `validate_task_context` returns a blocking verdict or advisory findings — proposed
  default: advisory, consistent with the rest of the product.
