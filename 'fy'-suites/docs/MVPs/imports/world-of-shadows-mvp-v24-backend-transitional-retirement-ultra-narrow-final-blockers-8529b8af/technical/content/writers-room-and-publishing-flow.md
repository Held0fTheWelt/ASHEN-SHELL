# Writers’ Room and publishing flow

## Canonical authored content

- **Source of truth for runtime:** YAML modules under `content/modules/<module_id>/` (`module.yaml`, `scenes.yaml`, characters, triggers, transitions, endings, relationships, …).
- **Loader / models:** `backend/app/content/module_loader.py`, `module_models.py`.
- **Compiler:** `backend/app/content/compiler/` produces projections consumed by runtime, retrieval, and review.

## Three projections

1. **`runtime_projection`** — consumed by world-engine story runtime loading.
2. **`retrieval_corpus_seed`** — feeds RAG ingestion (`ai_stack/rag.py`).
3. **`review_export_seed`** — governance and review surfaces.

Conceptual model (authored shapes and invariants): [`canonical_authored_content_model.md`](canonical_authored_content_model.md) (same folder).

## God of Carnage binding

For GoC, **YAML is primary**; builtins must not silently override YAML. See [`docs/MVPs/MVP_VSL_And_GoC_Contracts/VERTICAL_SLICE_CONTRACT_GOC.md`](../../MVPs/MVP_VSL_And_GoC_Contracts/VERTICAL_SLICE_CONTRACT_GOC.md).

## Writers’ Room workflow (backend-first)

Primary path: `POST /api/v1/writers-room/reviews`.

Stages (see `workflow_manifest.stages` in payloads):

1. Request intake (JWT).
2. LangGraph Writers’ Room **seed** workflow.
3. `wos.context_pack.build` (domain `writers_room`) — retrieval analysis.
4. Shared model routing + adapters — proposal generation.
5. Structured artifact packaging (comments, patch/variant candidates).
6. `wos.review_bundle.build` — governance envelope.
7. LangChain retriever bridge preview for cross-stack visibility.
8. **Human review** — `accept` | `reject` | `revise` via `POST .../reviews/<id>/decision`.

Outputs are **recommendation-only** until publishing governance applies changes. Publishing authority stays in **backend/admin** processes, not in model output alone.


## Writers’ Room ↔ RAG overlap boundary (current governed seam)

The current package allows a **bounded overlap seam** only in these roles:

- **`retrieval_context_provider`** — RAG returns retrieval hits, snippets, ranking notes, and governance fields for Writers’ Room review work.
- **`context_pack_assembly`** — Writers’ Room may call `wos.context_pack.build` in `writers_room` mode to assemble a review/support pack.
- **`recommendation_support`** — Writers’ Room may use that context pack to produce issue lists, comments, patch candidates, and variant candidates.

The current package does **not** allow this overlap to erase authority boundaries:

- **`publish_authority`** stays in backend/admin review and publish governance.
- **`canonical_truth_boundary`** stays with authored/published YAML and any publish-governed canonical module material.
- **`runtime_context_consumer`** for live committed play stays in world-engine; runtime committed truth is not owned by Writers’ Room and is not produced by RAG.

### Allowed vs forbidden today

**Writers’ Room may:**

- request retrieval/context support for a review task;
- inspect ranked sources, snippets, governance notes, and context-pack assembly output;
- turn that support into recommendation artifacts and review bundles.

**Writers’ Room must not:**

- auto-publish retrieved or generated material;
- treat retrieval output as authored canon by itself;
- mutate runtime committed truth directly;
- bypass human/backend review for canonical promotion.

### Overlap-boundary matrix

| Concern | Writers’ Room role | RAG role | Authority today | Forbidden |
|---|---|---|---|---|
| retrieval request | asks for bounded review context | serves as `retrieval_context_provider` | request is allowed; authority remains policy-gated retrieval | Writers’ Room cannot request canon promotion by retrieval alone |
| context-pack assembly | consumes `wos.context_pack.build` output for review work | assembles/supports `context_pack_assembly` payloads | retrieval/context only | context pack is not publish approval and not runtime truth |
| recommendation generation | turns context into comments, issues, patch/variant candidates | supplies supporting evidence only | Writers’ Room recommendation flow | RAG cannot become author/publisher of canon |
| publish decision | submits bounded artifacts for review | none beyond support context already returned | backend/admin + human review | no auto-publish from retrieval or Writers’ Room output |
| canonical content promotion | cannot promote by itself | cannot promote by itself | publish governance over canonical content | retrieved text/support cannot self-promote to canon |
| runtime committed truth | no direct authority | no direct authority | world-engine committed runtime state | Writers’ Room/RAG cannot mutate committed runtime truth directly |

Bounded decision log: [`governance/V24_WRITERS_ROOM_RAG_OVERLAP_LEDGER.md`](../../../governance/V24_WRITERS_ROOM_RAG_OVERLAP_LEDGER.md).

## Duplicate-truth warning (demo tree)

`writers-room/app/models/implementations/god_of_carnage/` may hold markdown and registry assets that can **diverge** from `content/modules/god_of_carnage/`. Treat **canonical module YAML** as runtime truth unless product policy states otherwise.

## Related

- [`docs/technical/ai/RAG.md`](../ai/RAG.md)
- [`docs/technical/integration/MCP.md`](../integration/MCP.md)
- Dev-oriented compiler notes: [`docs/dev/architecture/content-modules-and-compiler-pipeline.md`](../../dev/architecture/content-modules-and-compiler-pipeline.md)
