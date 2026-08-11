# Crosscutting architecture concepts

Crosscutting portfolios explain implementation mechanisms but remain subordinate to the
[system SAD](../system/architecture.md) and active ADRs.

| Concept | Current detailed portfolio | Normative decisions |
| --- | --- | --- |
| Runtime authority and correspondence | [World Engine](../components/world-engine/architecture.md) | ADR-0001, ADR-0002 |
| Content authority | [Content Authority](../components/content-authority/architecture.md) | ADR-0003 |
| Player delivery | [Frontend](../components/frontend/architecture.md) | ADR-0004 |
| Observability | [Observability & Traceability](../project/observability-traceability/architecture.md) | ADR-0005 |
| Security | [Security Governance](../project/security-governance/architecture.md) | owned security decisions |
| Quality and test proof | [Quality Gates](../project/quality-gates/architecture.md) | ADR-0006 + suite contracts |
| Governance and revision | [Governance](../project/governance/architecture.md) | active ADR lifecycle |
| Documentation supply chain | [Documentation Supply Chain](../project/documentation-supply-chain/architecture.md) | ADR-0006 |

These documents may use arc42-shaped sections for local readability. They do not each define an
independent whole-system architecture.
