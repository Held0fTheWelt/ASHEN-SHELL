# Architecture Governance architecture models

Decision, authority, exception and promotion governance spanning architecture documents and runtime control-plane policies.

**Architecture authority:** Accepted decisions and explicit runtime governance services own policy; archives and reports are evidence, not parallel decision authority.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Maintainer interaction with decision and runtime governance | `context` | [Architecture Governance - Context](context/governance-context.md) | D1 |
| Decision registry, SAD, runtime policy, evidence and gate chain | `component` | [Architecture Governance - Components](components/governance-components.md) | D1, D2 |
| Proposals, accepted decisions and bounded exceptions | `class` | [Architecture Governance - Decision Model](classes/decision-model.md) | D2 |
| Draft, proposal, acceptance and supersession with preserved lineage | `state` | [Architecture Governance - Decision Lifecycle](states/decision-lifecycle.md) | D3 |
| Accepted policy becomes audited runtime configuration and gate evidence | `sequence` | [Architecture Governance - Runtime Policy Change](sequence/runtime-policy-change.md) | D1, D2 |

## Drift focus

ADRs were absorbed and archived while runtime policy services expanded. Models preserve decision lineage and prevent archive text or operator projections from becoming a second truth.

[Decision/view/source traceability](TRACEABILITY.md)
