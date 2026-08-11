# Active architecture decisions

This directory contains the small active decision set for the target architecture. Section 9 of
the system and component SADs summarizes these decisions; it does not duplicate their complete
context and trade-offs.

| ADR | Status | Implementation state | Supersedes / consolidates |
| --- | --- | --- | --- |
| [ADR-0001](ADR-0001-single-live-story-commit-authority.md) | Accepted | Partial | retired runtime-authority and proposal-only ADRs |
| [ADR-0002](ADR-0002-versioned-turn-envelope.md) | Accepted | Partial | scattered turn/projection correspondence decisions |
| [ADR-0003](ADR-0003-single-compiled-content-projection.md) | Accepted | Nonconforming | retired authored-content authority decisions |
| [ADR-0004](ADR-0004-player-visible-block-envelope.md) | Accepted | Partial | retired player-shell and block-rendering decisions |
| [ADR-0005](ADR-0005-cross-service-turn-trace.md) | Accepted | Partial | retired observability and trace-correlation decisions |
| [ADR-0006](ADR-0006-honest-architecture-evidence.md) | Accepted | Implementing | fixed-profile/count-based architecture assurance |
| [ADR-0007](ADR-0007-bounded-emergent-narration.md) | Accepted | Partial | rigid canonical-path and free-action repair lineage |
| [ADR-0008](ADR-0008-module-language-boundaries.md) | Accepted | Partial | retired language-ingress and translation decisions |

## Status model

Decision status and implementation state are independent:

- `Proposed`, `Accepted`, `Superseded`, `Rejected` describe the decision.
- `Not started`, `Partial`, `Conforming`, `Nonconforming`, `Regressed` describe code.

An accepted ADR with nonconforming code must link an open architecture violation.

New decisions use [ADR-TEMPLATE.md](ADR-TEMPLATE.md).
