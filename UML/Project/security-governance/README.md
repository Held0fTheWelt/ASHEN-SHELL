# Security Governance architecture models

Identity, authorization, credential, secret, mutation-audit and trust-boundary governance across Better Tomorrow.

**Architecture authority:** Backend security governance owns credential and privileged-policy mutations; clients and adapters may submit intent but never store or reveal secret truth.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Player and operator trust relationships with backend security authority | `context` | [Security Governance - Context](context/security-context.md) | D1 |
| Frontend, API, service, credential, runtime-secret, audit and MCP boundaries | `component` | [Security Governance - Trust Components](components/trust-components.md) | D1, D2 |
| Privileged intent becomes encrypted state and redacted audit | `sequence` | [Security Governance - Credential Mutation](sequence/credential-mutation.md) | D1, D2 |
| Authorization grant, encrypted secret and redacted audit event | `class` | [Security Governance - Data Model](classes/security-data-model.md) | D2 |
| Absent, sealed, active, rotating and revoked provider credentials | `state` | [Security Governance - Credential Lifecycle](states/credential-lifecycle.md) | D3 |
| Browser trust boundary, backend secret authority, encrypted store and provider call | `deployment` | [Security Governance - Deployment](deployment/security-deployment.md) | D1, D3 |

## Drift focus

Credential handling and runtime providers expanded across a very large split service while frontend, MCP and world-engine each enforce partial guards. Models expose the complete trust chain and secret lifecycle.

[Decision/view/source traceability](TRACEABILITY.md)
