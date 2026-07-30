# Architecture Assurance architecture models

Executable architecture correspondence system for declarations, source bindings, semantic views, drift evidence, reports and canonical AKDB export.

**Architecture authority:** Human-authored SAD decisions and the semantic model catalog define intent; source anchors and Git evidence establish implementation correspondence; generated evidence never invents authority.

## Viewpoint map

| Concern | Viewpoint | Model | Decisions |
| --- | --- | --- | --- |
| Human intent, repository truth and disposable external AKDB | `context` | [Architecture Assurance - Context](context/assurance-context.md) | D1, D4 |
| Discovery, correspondence, semantic projection, audit, reporting and canon seams | `component` | [Architecture Assurance - Components](components/assurance-components.md) | D1, D2, D3 |
| From authored intent and source discovery to classified evidence | `activity` | [Architecture Assurance - Audit Flow](activity/audit-flow.md) | D1, D2 |
| Audit, multi-format reporting, canonical export and external validation | `sequence` | [Architecture Assurance - Export Sequence](sequence/export-sequence.md) | D3, D4 |
| Declarations, correspondence bindings and explainable findings | `class` | [Architecture Assurance - Evidence Model](classes/evidence-model.md) | D1 |
| Intent, correlation, evaluation, export and later drift | `state` | [Architecture Assurance - Evidence Lifecycle](states/evidence-lifecycle.md) | D2, D3 |

## Drift focus

The previous migration proved file coverage while shallow star diagrams hid semantic gaps. This model separates discovery, correspondence, interpretation, projection and export.

[Decision/view/source traceability](TRACEABILITY.md)
