# ADR-0025: Canonical Authored Content Model

Date: 2026-04-17

Status: Accepted

## Context

Content authoring in the repository uses scene/trigger/ending content modules under `content/modules/<module_id>/`. Multiple tools and projections consume these sources; a single canonical authored content model avoids divergence.

## Decision

- Declare the existing scene/trigger/ending module format under `content/modules/<module_id>/` as the canonical authored content model.
- Treat `ContentModule` and the backend loader (`backend/app/content/module_loader.py`) as the authoritative ingestion surface for authored content.
- Compile authored content into projection outputs: `runtime_projection`, `retrieval_corpus_seed`, and `review_export_seed`.

## Rationale

- Ensures a single source of truth for authored narrative intent.
- Simplifies tooling and reduces accidental divergence across runtime and governance layers.

## Consequences

- Consumers (World-Engine, review tools, RAG ingestion) must read the canonical compiled projections rather than ad-hoc source variants.
- Changes to the canonical model require an ADR and coordination across the runtime and backend teams.

## Migrated from

`docs/technical/content/canonical_authored_content_model.md` (Decision)

---

(Automated migration entry created 2026-04-17)
