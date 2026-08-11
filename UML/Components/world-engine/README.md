# World Engine architecture models

Authoritative live story runtime coordinating sessions, content, AI proposals, validation, commit, persistence and delivery.

**Architecture authority:** World Engine exclusively owns live session state and commit decisions; AI, backend and frontend are collaborators with narrower authority.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Live authority among player, backend, content and AI proposal collaborators | `context` | [World Engine - System Context](components/c4-context.md) | D1, D4 |
| API, canonical manager, compatibility runtime, persistence and observability | `container` | [World Engine - Runtime Containers](components/c4-container.md) | D1, D5 |
| Canonical interpret, govern, propose, validate, commit and delivery seams | `component` | [World Engine - Turn Components](components/c4-component.md) | D1, D4, D6, D15 |
| End-to-end authoritative turn from player intent to committed event | `sequence` | [World Engine - Primary Turn](sequence/primary-turn-sequence.md) | D1, D4 |
| Provider or validation failure preserves committed truth | `sequence` | [World Engine - Degraded Turn](sequence/degraded-turn-sequence.md) | D5, D14 |
| Decision points between proposal, rejection, commit and delivery | `activity` | [World Engine - Canonical Turn Activity](activity/canonical-turn-activity.md) | D1, D4, D6 |
| Session creation, serialized turns, degradation, recovery and closure | `state` | [World Engine - Session Lifecycle](states/session-lifecycle.md) | D5, D6 |
| Session truth, uncommitted proposal and explicit commit decision | `class` | [World Engine - Commit Data Model](classes/commit-data-model.md) | D1, D4 |
| Client boundary, authoritative service, AI collaborator and session persistence | `deployment` | [World Engine - Deployment](deployment/world-engine-deployment.md) | D1, D5 |

## Drift focus

The engine contains both world_engine/story_runtime and world_engine/runtime generations plus manager decompositions and legacy surfaces. Models make the canonical turn path, compatibility seams and commit authority testable.

[Decision/view/source traceability](TRACEABILITY.md)
