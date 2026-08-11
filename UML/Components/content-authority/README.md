# Content Authority architecture models

Authored module truth, schemas, compilation and runtime consumption for Better Tomorrow experiences.

**Architecture authority:** Versioned YAML modules own authored facts; compilers and runtimes may validate and project them but may not create competing content truth.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Authored truth and its validating and consuming systems | `context` | [Content Authority - Context](context/content-authority-context.md) | D1, D2 |
| Validation and projection seams from YAML to runtime | `component` | [Content Authority - Compilation Components](components/content-compilation-components.md) | D1, D3 |
| Fail-closed path from author change to runtime-readable version | `activity` | [Content Authority - Publication Flow](activity/content-publication-flow.md) | D2, D3 |
| Relationships among scene truth, canonical path and narrative policies | `class` | [Content Authority - Data Model](classes/content-data-model.md) | D1, D4, D5 |
| Validation, publication and runtime binding states | `state` | [Content Authority - Lifecycle](states/content-lifecycle.md) | D2, D3 |

## Drift focus

Content has moved between generic templates, God of Carnage specializations, backend compilation, world-engine loading and AI adapters. The models expose duplicate vocabularies and projection seams.

[Decision/view/source traceability](TRACEABILITY.md)
