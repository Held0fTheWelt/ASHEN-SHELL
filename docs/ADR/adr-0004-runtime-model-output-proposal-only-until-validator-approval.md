# ADR-0004: Runtime model output is proposal-only until validator approval

## Status
Proposed (migrated excerpt from MVP docs)

## Date
2026-04-17

## Intellectual property rights
Repository authorship and licensing: see project LICENSE; contact maintainers for clarification.

## Privacy and confidentiality
This ADR contains no personal data. Implementers must follow the repository privacy and confidentiality policies, avoid committing secrets, and document any sensitive data handling in implementation steps.

## Context


## Decision
The model may suggest narrative text, triggers, and effects. No suggestion is authoritative until output validation and engine legality checks pass.

## Consequences
- the model cannot silently mutate truth
- blocked turns are first-class
- commit logic remains engine authority

## Testing


## References
docs/MVPs/MVP_Narrative_Governance_And_Revision_Foundation/02_architecture_decisions.md
