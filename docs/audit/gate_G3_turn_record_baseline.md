# Gate G3 Baseline: Canonical Dramatic Turn Record

## Gate

- Gate name: G3 Canonical Dramatic Turn Record
- Gate class: structural
- Audit subject: single canonical per-turn record, required sections/fields, and projection discipline

## Repository Inspection Targets

- `docs/CANONICAL_TURN_CONTRACT_GOC.md`
- `ai_stack/goc_turn_seams.py`
- `ai_stack/runtime_turn_contracts.py`
- `ai_stack/langgraph_runtime.py`
- `backend/app/services/ai_stack_evidence_service.py`
- `ai_stack/tests/test_goc_phase1_runtime_gate.py`

## Required Evidence

- canonical turn-record contract
- emitted runtime records containing required groups and fields
- proof compact/expanded views are projections from one canonical source
- tests over emitted record semantics

## Audit Methods Used In This Baseline

- contract inspection
- runtime packaging/projection static inspection
- static test-surface review (no runtime execution in this block)

## Command Strategy

| command | status | basis | promotion requirement |
| --- | --- | --- | --- |
| `python -m pytest ai_stack/tests/test_goc_phase1_runtime_gate.py -q --tb=short` | `pending-finalization-after-phase-0` | Path exists; execution deferred in this block. | Execute with finalized turn-record evidence capture and attach outputs. |
| additional turn-record module checks | `pending-finalization-after-phase-0` | Exact module set not frozen. | Freeze module selection and execute under documented environment. |

## Baseline Findings

1. A canonical turn-record contract document exists and is explicitly referenced by runtime seam code.
2. Runtime state and packaging in `ai_stack/langgraph_runtime.py` include session/turn/routing/retrieval/validation/graph diagnostics fields.
3. `ai_stack/goc_turn_seams.py` provides operator-canonical projection helpers and references canonical contract sections.
4. `ai_stack/runtime_turn_contracts.py` currently defines stable runtime constants but does not alone represent full contract section coverage.
5. Full field-completeness proof against all required record sections is incomplete without runtime trace evidence.

## Status Baseline

- structural_status: `yellow`
- closure_level_status: `level_a_capable`

Rationale: canonical contract and projection architecture are present, but complete section-level runtime parity is not fully evidenced in this static-only baseline.

## Evidence Quality

- evidence_quality: `medium`
- justification: strong contract + implementation references exist, but no executed turn traces were collected in this block.

## Execution Risks Carried Forward

- possible drift between documented canonical section schema and emitted runtime field shape
- compact/expanded projection parity needs runtime sample verification
- turn-record test execution remains pending
