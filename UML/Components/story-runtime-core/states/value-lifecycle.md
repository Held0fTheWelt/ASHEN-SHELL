# Story Runtime Core - Value Lifecycle

**Viewpoint:** `state`
**Concern:** Validation and host adaptation of uncommitted shared values

[PlantUML source](value-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Candidate | Represent unvalidated shared-domain value | No host commitment | [`story_runtime_core/models.py`](../../../../story_runtime_core/models.py) |
| Validated | Meet portable invariants | Safe to return to host | [`story_runtime_core/model_registry.py`](../../../../story_runtime_core/model_registry.py) |
| Adapted | Map into host contract | Authority remains with caller | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Candidate | value created | uncommitted | catalog contract |
| Candidate | Validated | invariants pass | portable contract valid | [`story_runtime_core/model_registry.py`](../../../../story_runtime_core/model_registry.py) |
| Validated | Adapted | host mapping succeeds | explicit adapter | [`story_runtime_core/adapters.py`](../../../../story_runtime_core/adapters.py) |
| Adapted | Final | returned | caller retains authority | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
