# World Engine - Commit Data Model

**Viewpoint:** `class`
**Concern:** Session truth, uncommitted proposal, commit decision and explicit persistence outcome

[PlantUML source](commit-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| StorySession | Aggregate live story truth and bindings | Monotonic revision and bound content | [`world-engine/world_engine/story_runtime/manager/session/session_payloads.py`](../../../../world-engine/world_engine/story_runtime/manager/session/session_payloads.py) |
| NarrativeProposal | Carry uncommitted AI result and evidence | No authoritative mutations | [`world-engine/world_engine/story_runtime/commit_models.py`](../../../../world-engine/world_engine/story_runtime/commit_models.py) |
| CommitDecision | Explain accepted or rejected mutation | Validation and policy evidence | [`world-engine/world_engine/story_runtime/manager/commit_finalization.py`](../../../../world-engine/world_engine/story_runtime/manager/commit_finalization.py) |
| PersistOutcome | Report whether the authoritative session sink accepted or skipped a write | Versioned persisted, skipped-simulation or no-store result | [`world-engine/world_engine/story_runtime/persist_outcome.py`](../../../../world-engine/world_engine/story_runtime/persist_outcome.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| StorySession | NarrativeProposal | bounds evaluation | base revision | [`world-engine/world_engine/story_runtime/commit_models.py`](../../../../world-engine/world_engine/story_runtime/commit_models.py) |
| NarrativeProposal | CommitDecision | is resolved as | validation evidence | [`world-engine/world_engine/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/world_engine/story_runtime/narrative_commit_resolution.py) |
| CommitDecision | PersistOutcome | requests authoritative write | one explicit persistence result | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |
| PersistOutcome | StorySession | confirms durable revision | in-memory revision advances only after sink success | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
