# Story Runtime Core - Contract Data Model

**Viewpoint:** `class`
**Concern:** Intent, committed truth and calculated outcomes

[PlantUML source](contract-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| PlayerActionIntent | Carry semantic player intent | Validated intent fields | [`story_runtime_core/player_input_intent_contract.py`](../../../../story_runtime_core/player_input_intent_contract.py) |
| CommittedTruth | Carry confirmed story facts | Runtime-supplied immutable snapshot | [`story_runtime_core/committed_truth.py`](../../../../story_runtime_core/committed_truth.py) |
| ConsequenceOutcome | Describe calculated effects | Deterministic ordered effects | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| PlayerActionIntent | CommittedTruth | evaluated against | revision-bound semantics | [`story_runtime_core/input_interpreter.py`](../../../../story_runtime_core/input_interpreter.py) |
| CommittedTruth | ConsequenceOutcome | produces | ordered explainable effects | [`story_runtime_core/consequences/consequence_cascade.py`](../../../../story_runtime_core/consequences/consequence_cascade.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
