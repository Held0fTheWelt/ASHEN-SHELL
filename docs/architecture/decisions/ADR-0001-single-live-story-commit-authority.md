# ADR-0001 — Single live story commit authority

**Decision status:** Accepted
**Implementation state:** Partial
**Owners:** World Engine
**Date:** 2026-08-11
**Supersedes:** retired ADR-0001, ADR-0002, ADR-0004, ADR-0021, ADR-0033, ADR-0038
**Violations:** `AR-V001`, `AR-V005`

## Context

Historical runtime generations introduced separate notions of graph commit, session commit,
runtime profile state and player projection. Git history shows repeated attempts to consolidate
these paths. Current code has materially improved the authority boundary, but AI-internal commit
vocabulary and oversized finalization logic can still conceal a second decision or writer.

## Decision drivers

- rejected proposals must never mutate live story truth;
- exactly one component must own live revision;
- compatibility paths must remain replaceable;
- recovery must not fabricate canon.

## Considered options

1. **Distributed commit across AI and World Engine.** Rejected because ownership, rollback and
   revision conflicts become ambiguous.
2. **Backend-owned session transaction.** Rejected because the backend lacks live narrative state
   and would duplicate World Engine authority.
3. **World-Engine-only commit with proposal adapters.** Accepted.

## Decision

World Engine is the sole authority that creates a `CommitDecision`, mutates a live `StorySession`
and advances its revision. AI, backend, compatibility runtime and frontend may propose, validate,
translate, proxy, project or render. They may not perform an authoritative live-story write.

## Consequences

Every turn has one logical writer and explicit no-write rejection. Existing AI `commit` names must
be renamed or proven to mean proposal finalization only. Compatibility runtime can survive only as
a named adapter. World Engine finalization must be decomposed without creating new writer paths.

## Implementation correspondence

| Target element | Current evidence | State | Closure evidence |
| --- | --- | --- | --- |
| Turn serialization | `manager/turn_execution.py::_execute_turn_locked` | Partial | concurrent-turn rejection test |
| Commit decision | `narrative_commit_resolution.py` | Partial | accepted/rejected decision contract test |
| Session sink | `story_session_store.py` via manager persistence | Monitored | static one-writer gate + sink-spy integration test |
| AI proposal boundary | `governed_runtime_adapters.py` | Nonconforming vocabulary | no AI live-writer capability and renamed proposal types |

## Git and historical lineage

The June SAD/ADR consolidation (`5f036699`, `e8695b5f`) preserved the authority intent. The July
unsharding and package repair (`7959c848`, `4c358c65`) made the current writer path inspectable.
These commits explain the path; this ADR defines the target.
