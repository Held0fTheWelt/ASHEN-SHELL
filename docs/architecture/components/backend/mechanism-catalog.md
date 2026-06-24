# backend Mechanism Catalog

**Owner:** [backend SAD](architecture.md)
**Status:** restructured mechanism catalog
**Last reconciled:** 2026-06-23

| ID | Mechanism | Definition | Normative sources | UML / evidence | Proof state |
| --- | --- | --- | --- | --- | --- |
| BE-M01 | Session surface quarantine | Backend proxies play; no competing commit logic. | [SAD D1](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M02 | Player session bundle | Runtime readiness bundle for player HTTP surface. | [SAD D2](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M03 | Story API proxy | Forwards story operations to world-engine. | [SAD D3](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M04 | ADR-0041 readiness consumer | Veto-only runtime readiness overlay when flagged. | [SAD D4](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M05 | WebSocket ticket bridge | Shared-secret tickets for live play. | [SAD D5](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M06 | Content publish boundary | Sole publish path for canon content. | [SAD D6](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M07 | Game service orchestration | Coordinates bootstrap and play sessions. | [SAD D7](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
| BE-M08 | Diagnostics proxy | Operator diagnostics without engine duplication. | [SAD D8](architecture.md#9-architecture-decisions) | [TRACEABILITY](..\..\..\..\UML\Components\backend/TRACEABILITY.md) | Partial |
