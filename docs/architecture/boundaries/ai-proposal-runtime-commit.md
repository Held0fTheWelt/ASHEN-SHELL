# AI proposal ↔ runtime commit

**Owning SAD:** [world-engine](../components/world-engine/architecture.md) D2, [ai-stack](../components/ai-stack/architecture.md) D1.

Models and LangGraph nodes produce **structured proposals**. Only world-engine validation and commit seams
may change authoritative session state. `ai_stack` never writes committed truth directly.

Evidence: [ADR-0004](../../archive/adr-retired-2026/adr-0004-runtime-model-output-proposal-only-until-validator-approval.md),
[turn execution contract](../contracts/turn_execution_contract.md).
