# AI Stack architecture models

Proposal-producing narrative intelligence layer: semantic ingress, retrieval, director planning, realization, validation and runtime evidence.

**Architecture authority:** AI output is a proposal. World-engine validation and commit remain the only live-story authority.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Proposal authority and external collaborators | `context` | [AI Stack — System Context](components/c4-context.md) | D1, D10 |
| Major execution, retrieval, planning, validation and evidence seams | `container` | [AI Stack — Runtime Containers](components/c4-container.md) | D2, D3, D5, D10 |
| Internal responsibilities and contracts on the canonical proposal path | `component` | [AI Stack — Proposal Pipeline Components](components/c4-component.md) | D1, D5, D6, D12, D18 |
| Ordered proposal production from semantic input to validation evidence | `sequence` | [AI Stack — Primary Turn Proposal](sequence/ai-stack-primary-turn-sequence.md) | D1, D5, D6, D18 |
| How a runtime query becomes a bounded provenance-preserving context pack | `sequence` | [AI Stack — RAG Context Fabric](sequence/rag-context-fabric-sequence.md) | D3, D4, D18 |
| Data contracts carried between retrieval, planning, realization and validation | `class` | [AI Stack — Runtime Proposal Data Model](classes/runtime-proposal-data-model.md) | D3, D4, D6, D12, D17, D18 |
| Shadow/live dual mode and gathering pause semantics | `state` | [AI Stack — Director Pulse Lifecycle](states/director-pulse-lifecycle.md) | D15, D16 |

## Drift focus

The May refactor moved hundreds of modules into langgraph, story_runtime, RAG and capability packages. Models expose those seams and the still-hot runtime_executor split rather than treating ai_stack as one box.

[Decision/view/source traceability](TRACEABILITY.md)
