# ADR-0006 — Honest architecture evidence and conformance reporting

**Decision status:** Accepted
**Implementation state:** Implemented
**Owners:** Architecture Assurance
**Date:** 2026-08-11
**Supersedes:** fixed four-view depth profile and aggregate representation metric
**Violations:** `AR-V007`, `AR-V008`, `AR-V009`

## Context

The current assurance successfully prevents missing files, invalid anchors and shallow generic
diagrams. It still reports discovered units classified as `out_of_scope` as represented, and formal
SAD checks cannot detect additive ADR dumps, stale navigation or disconnected runtime sequences.

## Decision

Architecture reporting separates direct architectural representation, explicit exclusion,
unmapped current implementation and known violation. Only direct representation counts as model
coverage. Exclusions require a bounded reason. Unmapped units remain visible debt. Sequence views
that claim end-to-end behavior must form a connected entry-to-response flow. Document freshness is
bound to a Git commit, not only a date.

Every discovered in-scope semantic unit must be owned by a declared building block. Narrow source
paths take precedence over bounded aggregate blocks, allowing helpers to be represented without
inventing one architectural component per function. Critical subsystems require 100% direct
representation; mapping does not imply that the implementation conforms to its target design.

## Considered options

- Retain one 100% aggregate metric: rejected because it hides debt.
- Create one building block per discovered helper: rejected because function census is not architecture.
- Classify critical surfaces and expose the remainder honestly: accepted.

## Consequences

Reported coverage may decrease while ownership gaps are exposed; the gate now prevents those gaps
from becoming a stable end state. A passing evidence pipeline may coexist with known architectural
nonconformance, but the report must state that posture. README,
rollout and health indexes should be generated or cross-checked from one catalog.

## Implementation correspondence

This decision is implemented in the architecture-assurance audit, semantic model validation and
documentation gates. Closure requires tests proving direct representation equals the complete
in-scope census, a known violation produces nonconformant posture, and disconnected end-to-end views
fail.

## Git and historical lineage

Commit `5bb589e9` introduced source-bound assurance; `18591e80` replaced generic fixed profiles;
`de2cff5b` added drift edges. This ADR is the next synthesis step: evidence must reveal architecture
quality and known implementation error, not only artifact completeness.
