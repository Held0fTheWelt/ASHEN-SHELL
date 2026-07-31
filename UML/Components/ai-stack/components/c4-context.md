# AI Stack — System Context

**Viewpoint:** `context`
**Concern:** Proposal authority and external collaborators

[PlantUML source](c4-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| World Engine | Provide authoritative session context and accept or reject proposals | Turn request and validated proposal boundary | [`world-engine/world_engine/story_runtime/manager/runtime_manager.py`](../../../../world-engine/world_engine/story_runtime/manager/runtime_manager.py) |
| AI Stack | Produce bounded narrative proposals and evidence | No direct authoritative session write | [`ai_stack/__init__.py`](../../../../ai_stack/__init__.py) |
| Model Provider | Generate model completion | Governed route, budget and timeout | [`ai_stack/operational_profile.py`](../../../../ai_stack/operational_profile.py) |
| Content Authority | Supply canonical scenes, actors and policies | Compiled immutable content inputs | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| World Engine | AI Stack | requests narrative proposal | session context plus semantic input | [`world-engine/world_engine/story_runtime/manager/turn_execution.py`](../../../../world-engine/world_engine/story_runtime/manager/turn_execution.py) |
| AI Stack | Model Provider | invokes governed model route | provider/model/budget policy | [`ai_stack/langgraph/runtime_executor/executor_model_routing_invocation.py`](../../../../ai_stack/langgraph/runtime_executor/executor_model_routing_invocation.py) |
| Content Authority | AI Stack | supplies canon | read-only compiled content | [`ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py`](../../../../ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py) |
| AI Stack | World Engine | returns proposal and evidence | uncommitted runtime package | [`ai_stack/langgraph/runtime_executor/executor_run_finish.py`](../../../../ai_stack/langgraph/runtime_executor/executor_run_finish.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
