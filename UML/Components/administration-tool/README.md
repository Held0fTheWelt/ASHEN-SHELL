# Administration Tool architecture models

Operator-facing Flask application for read models, governed mutations, moderation and runtime diagnostics.

**Architecture authority:** The tool owns presentation and operator intent only; backend governance services remain mutation authority.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Who operates the tool and where mutation authority resides | `context` | [Administration Tool — System Context](components/c4-context.md) | D2 |
| How routes, policy, security and templates collaborate without owning domain state | `component` | [Administration Tool — Internal Components](components/c4-component.md) | D1, D2 |
| End-to-end authorization and delegation of an operator mutation | `sequence` | [Administration Tool — Governed Mutation](sequence/governed-mutation-sequence.md) | D2 |
| Browser, administration process and backend trust boundary | `deployment` | [Administration Tool — Deployment](deployment/administration-tool-deployment.md) | D2 |

## Drift focus

Git history shows rapid expansion of manage templates and route-registration splits. Models separate page routing, proxy policy and backend mutation authority so presentation growth cannot become an accidental control plane.

[Decision/view/source traceability](TRACEABILITY.md)
