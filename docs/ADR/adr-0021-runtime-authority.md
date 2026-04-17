# ADR-0021: Runtime Authority — World-Engine as authoritative runtime host

Date: 2026-03-30

Status: Accepted

## Context

A cross-cutting decision was made to centralize authoritative story session execution in the World-Engine runtime. The existing backend retains governance, publishing and review responsibilities while runtime lifecycle and state progression move to World-Engine.

## Decision

- Declare the World-Engine as the authoritative runtime host for story sessions.
- Keep backend as the governance/publishing/review layer.
- Extract shared runtime business logic into `story_runtime_core` and treat it as the canonical shared library for runtime behavior.

## Rationale

- Separates concerns between execution (World-Engine) and governance (backend).
- Improves operational isolation and clarity of responsibilities.
- Enables a single authoritative runtime state for session progression, reducing divergence.

## Consequences

- Backend session APIs move toward World-Engine-hosted execution paths.
- Compatibility shims may be needed during migration; these must be explicitly labeled as transitional.
- No duplicate business logic should be introduced; shared logic should live in `story_runtime_core`.

## Migrated from

`docs/archive/architecture-legacy/runtime_authority_decision.md` (Decision summary)

---

(Automated migration entry created 2026-04-17)
