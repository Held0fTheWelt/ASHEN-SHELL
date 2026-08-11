# ADR-0003 — Single compiled content projection

**Decision status:** Accepted
**Implementation state:** Nonconforming
**Owners:** Content Authority, Backend compiler, World Engine
**Date:** 2026-08-11
**Supersedes:** retired canonical-authored-content and runtime-locale decisions
**Violations:** `AR-V003`

## Context

Authored YAML, backend compiler structures, World Engine loading and AI-specific projections all
exist for legitimate reasons. They become an architectural defect when more than one executable
projection can override authored facts or when provenance and version are lost between consumers.

## Decision drivers

- authors need one durable source;
- runtime consumers need deterministic validated data;
- product-specific Python must not become a second content authority;
- preview and active versions must remain isolated.

## Considered options

1. Let each runtime consumer parse YAML independently. Rejected due to semantic drift.
2. Keep hand-maintained Python mirrors. Rejected due to dual truth.
3. Compile once into a versioned projection and adapt at consumer boundaries. Accepted.

## Decision

Reviewed YAML modules are authored truth. One deterministic compiler produces a versioned,
provenance-carrying runtime projection. World Engine and AI consume that projection through
anti-corruption adapters; no adapter may invent or override an authored fact.

## Consequences

Legacy GoC-specific Python must be classified, migrated or deleted. Compilation and publication
need reproducibility and backward-compatibility tests. Runtime startup must fail explicitly when a
required projection version is unsupported.

## Implementation correspondence

Current anchors include `content/modules/god_of_carnage/module.yaml`,
`backend/app/content/module_loader.py`, `world-engine/world_engine/content/backend_loader.py` and
`ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py`. Their coexistence is
evidence for the migration boundary, not proof of conformance.

The player-visible projection selection seam now consumes
`runtime_governance_policy.visible_projection` through
`world-engine/world_engine/story_runtime/manager/visible_projection_policy.py`. The policy has a
closed generic default and selects rich projection, deterministic fallback, opening shaping,
diagnostics and input attribution without inspecting a module ID. This is a conforming slice, not
closure of the ADR: compiler-level schema/version enforcement and removal of product-specific
Python projections are still required.

## Git and historical lineage

Content-module commits from May show the authored-model intent; later loader and runtime repairs
show why consumer projections appeared. The lineage is retained in the architecture drift baseline.
