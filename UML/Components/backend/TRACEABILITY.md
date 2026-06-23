# backend TRACEABILITY

| Diagram | Claim | Source | Test / gate |
| --- | --- | --- | --- |
| c4-context | No direct player → world-engine auth on primary path | `backend/app/api/v1/` | foundation gate |
| c4-container | game_service sole play proxy | `game_service.py` | `backend/tests/` |
| session proxy sequence | Turn forwarding only | `game_routes` | `test_goc_mvp01_mvp02_foundation_gate.py` |
| SAD D1 | Session quarantine | backend SAD §9 D1 | ADR-0002 |
