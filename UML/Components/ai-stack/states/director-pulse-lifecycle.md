# AI Stack — Director Pulse Lifecycle

**Viewpoint:** `state`
**Concern:** Shadow/live dual mode and gathering pause semantics

[PlantUML source](director-pulse-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Idle | No director pulse is active | No background state mutation | [`ai_stack/story_runtime/director/director_pulse_shadow.py`](../../../../ai_stack/story_runtime/director/director_pulse_shadow.py) |
| Shadow Evaluation | Evaluate pulse without visible delivery | Evidence only | [`ai_stack/story_runtime/block_stream_dual_mode.py`](../../../../ai_stack/story_runtime/block_stream_dual_mode.py) |
| Live Proposal | Produce ordered visible blocks | Proposal-only output | [`ai_stack/story_runtime/block_stream_dual_mode.py`](../../../../ai_stack/story_runtime/block_stream_dual_mode.py) |
| Gathering Paused | Suspend mandatory beat consumption while player remains free | No forced actor return | [`ai_stack/story_runtime/session_loop/replanning.py`](../../../../ai_stack/story_runtime/session_loop/replanning.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Idle | session ready | pulse disabled until trigger | catalog contract |
| Idle | Shadow Evaluation | shadow trigger | dual-mode evidence only | [`ai_stack/story_runtime/director/director_pulse_shadow.py`](../../../../ai_stack/story_runtime/director/director_pulse_shadow.py) |
| Idle | Live Proposal | live trigger | proposal generation enabled | [`ai_stack/story_runtime/block_stream_dual_mode.py`](../../../../ai_stack/story_runtime/block_stream_dual_mode.py) |
| Live Proposal | Gathering Paused | required actors absent | pause mandatory beat consumption | [`ai_stack/story_runtime/session_loop/replanning.py`](../../../../ai_stack/story_runtime/session_loop/replanning.py) |
| Gathering Paused | Live Proposal | co-presence restored | resume without forced action | [`ai_stack/story_runtime/session_loop/replanning.py`](../../../../ai_stack/story_runtime/session_loop/replanning.py) |
| Shadow Evaluation | Idle | evidence emitted | no visible blocks committed | [`ai_stack/story_runtime/director/director_pulse_shadow.py`](../../../../ai_stack/story_runtime/director/director_pulse_shadow.py) |
| Live Proposal | Idle | proposal delivered | world-engine decides commit | [`ai_stack/story_runtime/block_stream_dual_mode.py`](../../../../ai_stack/story_runtime/block_stream_dual_mode.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
