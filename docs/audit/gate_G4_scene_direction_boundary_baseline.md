# Gate G4 Baseline: Scene Direction Boundary

## Gate

- Gate name: G4 Scene Direction Boundary
- Gate class: structural
- Audit subject: deterministic-first bounded scene-direction architecture and forbidden-behavior prevention

## Repository Inspection Targets

- `ai_stack/scene_director_goc.py`
- `ai_stack/goc_turn_seams.py`
- `ai_stack/langgraph_runtime.py`
- `docs/CANONICAL_TURN_CONTRACT_GOC.md`
- `ai_stack/tests/test_goc_phase1_runtime_gate.py`
- `ai_stack/tests/test_goc_phase2_scenarios.py`

## Required Evidence

- mapped scene-direction subdecision matrix fields
- deterministic and bounded seams around model proposals
- anti-overwrite safeguards for director-selected fields
- scenario tests showing bounded behavior

## Audit Methods Used In This Baseline

- static scene-direction seam analysis
- contract-to-implementation comparison
- static scenario-test surface review (no test execution in this block)

## Command Strategy

| command | status | basis | promotion requirement |
| --- | --- | --- | --- |
| `python -m pytest ai_stack/tests/test_goc_phase1_runtime_gate.py -q --tb=short` | `pending-finalization-after-phase-0` | Path exists; not executed in this block. | Execute with scene-direction matrix evidence capture. |
| `python -m pytest ai_stack/tests/test_goc_phase2_scenarios.py -q --tb=short` | `pending-finalization-after-phase-0` | Path exists; not executed in this block. | Execute with bounded-behavior assertions and trace samples. |

## Baseline Findings

1. `scene_director_goc.py` contains deterministic selection helpers (`select_single_scene_function`) and frozen-vocab assertions for scene/pacing/silence decisions.
2. Runtime and seam code include validation and projection boundaries around model generation and commit seams.
3. Explicit standalone subdecision matrix artifact mapping is incomplete in this block; matrix semantics are partially embedded in code but not fully enumerated as one canonical matrix reference.
4. No executed scenario evidence is attached yet for forbidden-behavior absence.

## Status Baseline

- structural_status: `yellow`
- closure_level_status: `level_a_capable`

Rationale: deterministic-first bounded architecture is materially present, but complete matrix traceability and runtime scenario enforcement evidence remain incomplete.

## Evidence Quality

- evidence_quality: `medium`
- justification: substantial static seam evidence exists, but required scenario/runtime proof was not executed in this block.

## Execution Risks Carried Forward

- incomplete explicit subdecision matrix traceability
- potential hidden unclassified branches without executed scenario coverage
- pending runtime scenario verification commands
