# Content Authority - Lifecycle

**Viewpoint:** `state`
**Concern:** Validation, publication and runtime binding states

[PlantUML source](content-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Draft | Accept author changes | Not runtime-consumable | [`backend/app/content/module_models.py`](../../../../backend/app/content/module_models.py) |
| Validated | Record successful structural checks | All references resolve | [`backend/app/content/module_validator.py`](../../../../backend/app/content/module_validator.py) |
| Published | Expose immutable content version | Active version pointer | [`backend/app/content/module_service.py`](../../../../backend/app/content/module_service.py) |
| Runtime Projection | Serve content to a bound session | No mutation of authored truth | [`world-engine/world_engine/content/backend_source.py`](../../../../world-engine/world_engine/content/backend_source.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Draft | module created | unique module id | catalog contract |
| Draft | Validated | validation passes | zero blocking findings | [`backend/app/content/module_validator.py`](../../../../backend/app/content/module_validator.py) |
| Validated | Draft | content changes | revalidation required | [`backend/app/content/module_service.py`](../../../../backend/app/content/module_service.py) |
| Validated | Published | version activated | immutable version and audit | [`backend/app/content/module_service.py`](../../../../backend/app/content/module_service.py) |
| Published | Runtime Projection | session binds version | stable content version | [`world-engine/world_engine/content/backend_source.py`](../../../../world-engine/world_engine/content/backend_source.py) |
| Runtime Projection | Published | session ends | authored version unchanged | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
