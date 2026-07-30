# Content Authority - Data Model

**Viewpoint:** `class`
**Concern:** Relationships among scene truth, canonical path and narrative policies

[PlantUML source](content-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Authored Module | Hold canonical versioned content truth | module.yaml plus referenced YAML documents | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| Scene Graph | Describe spaces, actors, objects and connections | Stable identifiers and references | [`content/modules/god_of_carnage/scene_graph.yaml`](../../../../content/modules/god_of_carnage/scene_graph.yaml) |
| Canonical Path | Express authored dramatic invariants without scripting player choice | Schema-governed beats and alternatives | [`content/modules/god_of_carnage/canonical_path/_schema.yaml`](../../../../content/modules/god_of_carnage/canonical_path/_schema.yaml) |
| Narrative Policies | Bound memory, aspects, beats and phase behavior | Declarative policy YAML | [`content/modules/god_of_carnage/narrative_aspect_policy.yaml`](../../../../content/modules/god_of_carnage/narrative_aspect_policy.yaml) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Authored Module | Scene Graph | contains | referentially complete scene graph | [`content/modules/god_of_carnage/scene_graph.yaml`](../../../../content/modules/god_of_carnage/scene_graph.yaml) |
| Authored Module | Canonical Path | contains | dramatic invariants only | [`content/modules/god_of_carnage/canonical_path/_schema.yaml`](../../../../content/modules/god_of_carnage/canonical_path/_schema.yaml) |
| Authored Module | Narrative Policies | contains | declarative runtime bounds | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
