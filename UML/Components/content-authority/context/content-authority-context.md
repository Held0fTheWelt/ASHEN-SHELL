# Content Authority - Context

**Viewpoint:** `context`
**Concern:** Authored truth and its validating and consuming systems

[PlantUML source](content-authority-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Content Author | Define experience facts, locations, objects and dramatic policy | Schema-conforming module changes | [`content/modules/_template/README.md`](../../../../content/modules/_template/README.md) |
| Authored Module | Hold canonical versioned content truth | module.yaml plus referenced YAML documents | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| Backend Module Compiler | Load, validate and normalize authored documents | Deterministic module model or diagnostics | [`backend/app/content/module_loader.py`](../../../../backend/app/content/module_loader.py) |
| Module Validator | Enforce schemas and cross-document references | Fail-closed validation findings | [`backend/app/content/module_validator.py`](../../../../backend/app/content/module_validator.py) |
| World Content Loader | Materialize published content for live sessions | Read-only runtime projection | [`world-engine/app/content/backend_loader.py`](../../../../world-engine/app/content/backend_loader.py) |
| AI Content Adapter | Translate canonical content into proposal context | Provenance-preserving read model | [`ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py`](../../../../ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Content Author | Authored Module | authors | reviewable YAML change | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| Authored Module | Backend Module Compiler | is compiled by | complete referenced document set | [`backend/app/content/module_loader_documents.py`](../../../../backend/app/content/module_loader_documents.py) |
| Module Validator | World Content Loader | releases version | validation success only | [`backend/app/content/module_service.py`](../../../../backend/app/content/module_service.py) |
| World Content Loader | AI Content Adapter | supplies bounded facts | session-bound content projection | [`world-engine/app/content/backend_loader.py`](../../../../world-engine/app/content/backend_loader.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
