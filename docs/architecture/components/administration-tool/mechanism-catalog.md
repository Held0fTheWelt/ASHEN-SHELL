# administration-tool Mechanism Catalog

**Owner:** [administration-tool SAD](architecture.md)
**Status:** restructured mechanism catalog
**Last reconciled:** 2026-06-23

| ID | Mechanism | Definition | Normative sources | UML / evidence | Proof state |
| --- | --- | --- | --- | --- | --- |
| AT-M01 | Debug panel bounds | Collapsible session diagnostics driven only by `DebugPanelOutput`. | [SAD D1](architecture.md#d1-debug-panel-ui-bounded-diagnostics-in-session-ui) | [TRACEABILITY](../../../../UML/Components/administration-tool/TRACEABILITY.md) | Implemented |
| AT-M02 | Security control plane | Governance mutations route through backend admin APIs only. | [SAD D2](architecture.md#d2-admin-security-control-plane) | [security-governance D3](../../project/security-governance/architecture.md#d3-security-governance-admin-control-plane) | Implemented |
| AT-M03 | Route registration split | Proxy, pages, manage, and security modules register independently (despaghettify DS-004). | [SAD §4](architecture.md#4-solution-strategy) | [`route_registration_*.py`](../../../../administration-tool/route_registration_*.py) | Implemented |
| AT-M04 | Backend proxy boundary | Operator UI never holds world-engine credentials; diagnostics via backend only. | [SAD §2](architecture.md#2-constraints) | [world-engine thin-path proxy](../world-engine/decision-detail.md#d4-director-thin-path-adr-0062) | Implemented |
| AT-M05 | Incremental manage decks | Large trace payloads load after first paint on manage surfaces. | [SAD §4](architecture.md#4-solution-strategy) | [`test_manage_governance_console_and_runtime_config_truth.py`](../../../../administration-tool/tests/test_manage_governance_console_and_runtime_config_truth.py) | Partial |

## AT-M01

## AT-M02

## AT-M03

## AT-M04

## AT-M05
