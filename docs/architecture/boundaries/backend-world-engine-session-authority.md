# Backend ↔ world-engine session authority

**Owning SAD:** [world-engine](../components/world-engine/architecture.md) D1, [backend](../components/backend/architecture.md) D2.

The play service (`world-engine/`) is the **sole authority** for committed live story session state and
turn execution. The Flask backend validates requests, persists platform data, and **proxies** play
operations through `game_service` HTTP clients—it does not commit narrative state.

Evidence: [ADR-0001](../../archive/adr-retired-2026/adr-0001-runtime-authority-in-world-engine.md) (absorbed), [ADR-0002](../../archive/adr-retired-2026/adr-0002-backend-session-surface-quarantine.md),
[`tests/gates/test_goc_mvp01_mvp02_foundation_gate.py`](../../../tests/gates/test_goc_mvp01_mvp02_foundation_gate.py).
