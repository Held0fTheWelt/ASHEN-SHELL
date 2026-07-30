# Story Runtime Core - Authority Context

**Viewpoint:** `context`
**Concern:** Portable contracts versus live and proposal authorities

[PlantUML source](story-runtime-core-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| World Engine | Own and commit live story state | Calls pure shared contracts | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| Story Runtime Core | Provide portable domain contracts and deterministic algorithms | Python package without service authority | [`story_runtime_core/__init__.py`](../../../../story_runtime_core/__init__.py) |
| AI Stack | Produce proposals using shared semantic contracts | Proposal-only integration | [`ai_stack/story_runtime/player_action_resolution.py`](../../../../ai_stack/story_runtime/player_action_resolution.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| World Engine | Story Runtime Core | uses contracts | host retains authority | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| AI Stack | Story Runtime Core | uses semantic models | proposal-only values | [`ai_stack/story_runtime/player_action_resolution.py`](../../../../ai_stack/story_runtime/player_action_resolution.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
