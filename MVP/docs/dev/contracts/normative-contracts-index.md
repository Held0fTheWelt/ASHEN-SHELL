# Normative contracts index (lean v24)

Developer-facing index of the **binding runtime and governance anchors** that remain inside the curated v24 package.

This page replaces the removed original-repository contract-entry role with a **v24-resident** navigation anchor.
It intentionally lists only the contracts that materially matter for lean-package governance and runtime-readiness continuation.

## Runtime authority and backend classification

| Document | Binding scope |
|----------|---------------|
| [ADR-0001: Runtime authority in world-engine](../../ADR/adr-0001-runtime-authority-in-world-engine.md) | World-engine is the authoritative runtime host; backend remains governance/publishing/policy |
| [ADR-0002: Backend session surface quarantine](../../ADR/adr-0002-backend-session-surface-quarantine.md) | Transitional backend session surfaces must not be mistaken for authoritative runtime truth |
| [Runtime authority and state flow](../../technical/runtime/runtime-authority-and-state-flow.md) | Consolidated technical ownership and session-flow explanation |
| [Backend runtime classification](../../technical/architecture/backend-runtime-classification.md) | Backend versus world-engine seam classification and allowed responsibilities |
| [Operational governance runtime](../../operations/OPERATIONAL_GOVERNANCE_RUNTIME.md) | Operator-facing governance posture for runtime-critical seams |

## Canonical turn and vertical-slice anchors

| Document | Binding scope |
|----------|---------------|
| [Vertical slice contract (GoC)](../../MVPs/MVP_VSL_And_GoC_Contracts/VERTICAL_SLICE_CONTRACT_GOC.md) | Slice boundaries, governing seams, and expected runtime path |
| [Canonical turn contract (GoC)](../../MVPs/MVP_VSL_And_GoC_Contracts/CANONICAL_TURN_CONTRACT_GOC.md) | Turn semantics, validation/commit/render discipline |
| [Gate scoring policy (GoC)](../../MVPs/MVP_VSL_And_GoC_Contracts/GATE_SCORING_POLICY_GOC.md) | Slice QA and gate interpretation |
| [ADR-0003: Scene identity canonical surface](../../ADR/adr-0003-scene-identity-canonical-surface.md) | Single canonical scene-identity seam across AI guidance and runtime commit |
| [God of Carnage module contract](../../technical/architecture/god_of_carnage_module_contract.md) | Module-shape and content/runtime expectations for the current vertical slice |

## Normative vocabulary ownership

| Vocabulary term | Normative owner | Downstream / dependent users |
|---|---|---|
| `runtime authority` | `ADR-0001` | ADR-0002, ADR-0003, Runtime authority and state flow, Backend runtime classification, Canonical runtime contract |
| `backend session surface` | `ADR-0002` | Backend runtime classification, Canonical runtime contract, operator / MCP-facing backend session surfaces |
| `canonical scene identity surface` | `ADR-0003` | Vertical slice contract (GoC), Canonical turn contract (GoC), GoC module contract |

Ownership rule:
- The owner row above defines the term normatively.
- Downstream anchors may reference the term only in dependent form and must not read like competing co-definitions.

## API, MCP, and public/player truth boundaries

| Document | Binding scope |
|----------|---------------|
| [OpenAPI anchor](../../api/openapi.yaml) | Declared backend HTTP surface where still relevant for tooling and integration |
| [MCP technical integration](../../technical/integration/MCP.md) | MCP canonical surface and operator/developer integration boundaries |
| [Service boundaries](../../technical/architecture/service-boundaries.md) | Player/public/admin/backend/world-engine boundary map |
| [Writers-room and publishing flow](../../technical/content/writers-room-and-publishing-flow.md) | Authoring → review → publish → runtime authority seam |

## Runtime-critical code and validation anchors

These are **not** normative documents by themselves, but they are the primary implementation and evidence surfaces repeatedly referenced by the contracts above.

- `backend/app/api/v1/session_routes.py`
- `backend/app/services/game_service.py`
- `backend/app/web/routes.py`
- `world-engine/app/story_runtime/manager.py`
- `ai_stack/mcp_canonical_surface.py`
- `ai_stack/langgraph_runtime.py`
- `story_runtime_core/input_interpreter.py`

## Governance continuity

- [FY baseline summary](../../../governance/FY_BASELINE_SUMMARY.md)
- [Source-preservation ledger](../../../governance/V24_SOURCE_PRESERVATION_LEDGER.md)
- [Governance attachment report](../../../validation/V24_GOVERNANCE_ATTACHMENT_REPORT.md)

## Scope note

This index is intentionally **lean**.
It does **not** restore every historical contract page from the original repository.
It restores the **practical contract-entry role** needed for v24 governance attachment and re-audit continuity.
