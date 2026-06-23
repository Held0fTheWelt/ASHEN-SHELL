# Canonical turn lifecycle sequence

```mermaid
sequenceDiagram
  participant P as Player
  participant B as backend
  participant W as world-engine
  participant A as ai_stack
  P->>B: player input
  B->>W: turn request
  W->>A: graph execute (proposal)
  A-->>W: proposal
  W->>W: validate_seam
  W->>W: commit_seam + persist
  W->>W: project visible blocks
  W-->>B: TurnExecutionResult
  B-->>P: rendered response
```

Normative: [`turn_execution_contract.md`](../../../../docs/architecture/contracts/turn_execution_contract.md), GoC [`CANONICAL_TURN_CONTRACT_GOC.md`](../../../../docs/MVPs/MVP_VSL_And_GoC_Contracts/CANONICAL_TURN_CONTRACT_GOC.md).
