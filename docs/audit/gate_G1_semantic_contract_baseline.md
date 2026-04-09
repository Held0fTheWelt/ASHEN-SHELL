# Gate G1 Baseline: Shared Semantic Contract

## Gate

- Gate name: G1 Shared Semantic Contract
- Gate class: structural
- Audit subject: canonical semantic vocabulary ownership, cross-surface reuse, and redefinition prevention

## Repository Inspection Targets

- `docs/ROADMAP_MVP_GoC.md`
- `ai_stack/goc_frozen_vocab.py`
- `ai_stack/mcp_canonical_surface.py`
- `ai_stack/goc_turn_seams.py`
- `ai_stack/langgraph_runtime.py`
- `ai_stack/tests/test_goc_frozen_vocab.py`
- `backend/app/services/writers_room_model_routing.py`
- `backend/app/services/improvement_task2a_routing.py`

## Required Evidence

- canonical semantic artifact(s)
- semantic import/reference traces across runtime, writers-room, improvement, admin
- equality checks for required semantic sets
- tests proving no productive local override

## Audit Methods Used In This Baseline

- static contract inspection
- symbol/reference tracing
- static test intent review (no runtime execution in this block)

## Command Strategy

| command | status | basis | promotion requirement |
| --- | --- | --- | --- |
| `python -m pytest ai_stack/tests/test_goc_frozen_vocab.py -q --tb=short` | `pending-finalization-after-phase-0` | Path exists; not executed in this block. | Execute with finalized cross-surface semantic mapping and capture test evidence in report revision. |
| semantic reference grep patterns | `pending-finalization-after-phase-0` | Pattern set not frozen as canonical command inventory. | Freeze pattern set tied to roadmap-required labels and re-run references. |

## Baseline Findings

1. `ai_stack/goc_frozen_vocab.py` is a real canonical semantic artifact for the GoC slice, with frozen label sets and assertion helpers.
2. The vocabulary labels currently emphasize scene/pacing/continuity/failure semantics, while roadmap G1 mandatory equality set names (`task_types`, `model_roles`, `fallback_classes`, `decision_classes`, `routing_labels`, `scene_direction_subdecision_labels`) are only partially represented one-to-one.
3. Backend writers-room/improvement routing surfaces consume shared routing contracts (`TaskKind`, `RouteReasonCode`) via runtime contract modules, which supports semantic reuse.
4. Admin semantic derivation-from-canonical evidence is partial in this block; explicit proof that admin semantic lists are fully derived from one canonical artifact is not yet complete.

## Status Baseline

- structural_status: `yellow`
- closure_level_status: `level_a_capable`

Rationale: a canonical semantic source exists and is reused in key paths, but full equality-proof and cross-surface semantic normalization to roadmap label sets is incomplete.

## Evidence Quality

- evidence_quality: `medium`
- justification: strong static code/document evidence exists for canonical vocabulary and consumer reuse, but runtime execution and full equality-set verification were not completed in this block.

## Execution Risks Carried Forward

- semantic label normalization gap between roadmap required set names and current code symbol names
- unresolved proof that all admin-facing semantic values are canonical-derived
- pending command finalization for semantic trace commands
