# Start Here

This package should be read as a single integrated MVP with a current-state overlay.

## Reading order

### 1. Current-state honesty
Read:
- `docs/57_CURRENT_STATE_PROTOCOL.md`
- `docs/61_CURRENT_STATE_VALIDATION_REPORT.md`
- `docs/64_RELEASE_NOTES_V22_CURRENT_STATE.md`

### 2. Product truth
Read:
- `docs/00_WORLD_OF_SHADOWS_MVP_V21_CANONICAL.md`
- `docs/01_RUNTIME_CONSTITUTION.md`
- `docs/03_FIVE_LAYER_EXECUTION_ARCHITECTURE.md`
- `docs/06_WORLD_ENGINE_PRODUCT_SPEC.md`

### 3. Memory/runtime depth
Read:
- `docs/12_MEMORY_CORE_ARCHITECTURE.md`
- `docs/13_ENTITY_IDENTITY_AND_FACT_SLOTTING_SPEC.md`
- `docs/16_MEMORY_CONFLICT_RECORDS_AND_LINEAGE_GRAPH_SPEC.md`
- `docs/17_MEMORY_THRESHOLD_ENGINE_SPEC.md`
- `docs/18_MEMORY_EFFECT_SURFACE_ACTIVATION_ENGINE_SPEC.md`
- `docs/19_MEMORY_TRANSFORMATION_RUNTIME_SPEC.md`
- `docs/20_RETRIEVAL_TASK_PROFILES_AND_HYBRID_INDEX_CONSISTENCY_SPEC.md`

### 4. Implementation path
Read:
- `docs/39_REFERENCE_IMPLEMENTATION_AND_TEST_PLAN.md`
- `docs/42_IMPLEMENTATION_TRUTH_MATRIX.md`
- `docs/48_CANONICAL_IMPLEMENTATION_PROTOCOL.md`
- `docs/49_CANONICAL_TARGET_SURFACES.md`
- `docs/50_IMPLEMENTATION_WORKSTREAMS.md`
- `docs/51_AUDIT_TRANSLATION_RULES.md`
- `docs/52_VALIDATION_RUNBOOK.md`
- `docs/53_DELIVERABLE_CONTRACT.md`
- `docs/54_COMPONENT_BLUEPRINTS.md`
- `docs/55_NO_STUB_IMPLEMENTATION_RULES.md`

### 5. Audit cycle and re-audit continuity
Read:
- `docs/58_AUDIT_CYCLE_PROTOCOL.md`
- `docs/59_NEXT_WORK_FIELD_SELECTION_POLICY.md`
- `docs/60_REAUDIT_CONTINUITY_CHECKLIST.md`
- `docs/62_AUDIT_SYSTEM_MASTERPROMPT.md`
- `docs/63_IMPLEMENTATION_HANDOFF_TEMPLATE.md`

### 6. Executable proof
Run:
```bash
cd reference_scaffold
python -m pip install -e .[test]
pytest -q
```

## What “current-state-overhauled MVP” means here

This package still uses the v21 canonical target as its base.
The v22 delivery layer adds:
- explicit current-state truthfulness,
- a real validation note from this delivery run,
- and an iterative audit-control layer for the next implementation cycles.

It does **not** claim that every repository production feature already exists in code.
