# Story Runtime Core - Components

**Viewpoint:** `component`
**Concern:** Pure model, intent, truth, consequence, branching and delivery seams

[PlantUML source](domain-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Story Runtime Core | Provide portable domain contracts and deterministic algorithms | Python package without service authority | [`story_runtime_core/__init__.py`](../../../../story_runtime_core/__init__.py) |
| Domain Models | Define actions, scenes, actors and outcomes | Serializable value objects | [`story_runtime_core/models.py`](../../../../story_runtime_core/models.py) |
| Input Intent | Normalize player language into semantic intent | Locale-independent intent contract | [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py) |
| Committed Truth | Represent authoritative facts supplied by a runtime | Immutable snapshot/value semantics | [`story_runtime_core/committed_truth.py`](../../../../story_runtime_core/committed_truth.py) |
| Consequence Cascade | Compute deterministic downstream effects | Pure input/output transform | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |
| Branching | Forecast alternatives without committing them | Explicit hypothetical state | [`story_runtime_core/branching/forecast.py`](../../../../story_runtime_core/branching/forecast.py) |
| Runtime Delivery | Adapt portable outcomes to callbacks and web delivery | No ownership transfer | [`story_runtime_core/runtime_delivery.py`](../../../../story_runtime_core/runtime_delivery.py) |
| Boundary Adapters | Map host-specific data to shared contracts | Anti-corruption mapping | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Story Runtime Core | Domain Models | exports | stable public values | [`story_runtime_core/__init__.py`](../../../../story_runtime_core/__init__.py) |
| Domain Models | Input Intent | constrains | semantic action vocabulary | [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py) |
| Input Intent | Committed Truth | is evaluated against | confirmed facts only | [`story_runtime_core/input_interpreter.py`](../../../../story_runtime_core/input_interpreter.py) |
| Committed Truth | Consequence Cascade | bounds cascade | pure deterministic input | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |
| Consequence Cascade | Branching | feeds alternatives | hypothetical only | [`story_runtime_core/branching/forecast.py`](../../../../story_runtime_core/branching/forecast.py) |
| Branching | Runtime Delivery | returns outcome | host decides commit | [`story_runtime_core/runtime_delivery.py`](../../../../story_runtime_core/runtime_delivery.py) |
| Boundary Adapters | Domain Models | maps host values | explicit anti-corruption layer | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
