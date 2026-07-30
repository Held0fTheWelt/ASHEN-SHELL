# World Engine - Commit Data Model

**Viewpoint:** `class`
**Concern:** Session truth, uncommitted proposal and explicit commit decision

[PlantUML source](commit-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| StorySession | Aggregate live story truth and bindings | Monotonic revision and bound content | [`world-engine/app/story_runtime/commit_models.py`](../../../../world-engine/app/story_runtime/commit_models.py) |
| NarrativeProposal | Carry uncommitted AI result and evidence | No authoritative mutations | [`world-engine/app/story_runtime/commit_models.py`](../../../../world-engine/app/story_runtime/commit_models.py) |
| CommitDecision | Explain accepted or rejected mutation | Validation and policy evidence | [`world-engine/app/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/app/story_runtime/narrative_commit_resolution.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| StorySession | NarrativeProposal | bounds evaluation | base revision | [`world-engine/app/story_runtime/commit_models.py`](../../../../world-engine/app/story_runtime/commit_models.py) |
| NarrativeProposal | CommitDecision | is resolved as | validation evidence | [`world-engine/app/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/app/story_runtime/narrative_commit_resolution.py) |
| CommitDecision | StorySession | advances when accepted | monotonic revision | [`world-engine/app/story_runtime/story_session_store.py`](../../../../world-engine/app/story_runtime/story_session_store.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
