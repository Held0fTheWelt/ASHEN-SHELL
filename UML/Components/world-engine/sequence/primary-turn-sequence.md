# World Engine - Primary Turn

**Viewpoint:** `sequence`
**Concern:** End-to-end authoritative turn from player intent to committed event

[PlantUML source](primary-turn-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Submit semantic intent and observe committed narrative | Ticket-bound session | [`world-engine/app/api/story_ws.py`](../../../../world-engine/app/api/story_ws.py) |
| Backend | Authenticate and proxy play operations | Signed internal request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Turn Execution | Run the canonical lifecycle for one player command | Exactly one commit or explicit rejection | [`world-engine/app/story_runtime/manager/turn_execution.py`](../../../../world-engine/app/story_runtime/manager/turn_execution.py) |
| Canonical Turn Lifecycle | Enforce interpret, propose, validate, commit ordering | No render before commit | [`world-engine/app/story_runtime/canonical_turn_lifecycle.py`](../../../../world-engine/app/story_runtime/canonical_turn_lifecycle.py) |
| Live Governance | Apply runtime policy and authority guards | Fail-closed mutation policy | [`world-engine/app/story_runtime/live_governance.py`](../../../../world-engine/app/story_runtime/live_governance.py) |
| AI Proposal Bridge | Request and normalize AI proposal packets | Proposal-only anti-corruption layer | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| Commit Resolution | Validate proposal against world truth and policy | Accepted/rejected decision with evidence | [`world-engine/app/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/app/story_runtime/narrative_commit_resolution.py) |
| Story Session Store | Persist committed state and monotonic revision | Atomic session update | [`world-engine/app/story_runtime/story_session_store.py`](../../../../world-engine/app/story_runtime/story_session_store.py) |
| Delivery Surfaces | Publish committed blocks and state | Post-commit events only | [`world-engine/app/api/story_ws.py`](../../../../world-engine/app/api/story_ws.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Backend | submits intent | authenticated player request | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Turn Execution | Canonical Turn Lifecycle | executes canonical phases | ordered lifecycle | [`world-engine/app/story_runtime/canonical_turn_lifecycle.py`](../../../../world-engine/app/story_runtime/canonical_turn_lifecycle.py) |
| Canonical Turn Lifecycle | Live Governance | checks authority and policy | fail closed | [`world-engine/app/story_runtime/live_governance.py`](../../../../world-engine/app/story_runtime/live_governance.py) |
| Live Governance | AI Proposal Bridge | requests bounded proposal | proposal-only | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| AI Proposal Bridge | Commit Resolution | returns candidate | proposal plus evidence | [`world-engine/app/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/app/story_runtime/narrative_commit_resolution.py) |
| Commit Resolution | Story Session Store | commits accepted delta | atomic revision or no write | [`world-engine/app/story_runtime/story_session_store.py`](../../../../world-engine/app/story_runtime/story_session_store.py) |
| Story Session Store | Delivery Surfaces | publishes committed result | post-commit only | [`world-engine/app/api/story_ws.py`](../../../../world-engine/app/api/story_ws.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
