# Gate G5 Baseline: Retrieval Governance

## Gate

- Gate name: G5 Retrieval Governance
- Gate class: structural
- Audit subject: authored-vs-derived separation, governance lanes, and runtime retrieval visibility

## Repository Inspection Targets

- `ai_stack/rag.py`
- `docs/rag_retrieval_hardening.md`
- `docs/rag_retrieval_subsystem_closure.md`
- `docs/rag_task3_source_governance.md`
- `docs/rag_task4_evaluation_harness.md`
- `ai_stack/tests/test_rag.py`
- `ai_stack/tests/retrieval_eval_scenarios.py`
- `ai_stack/tests/test_goc_phase4_reliability_breadth_operator.py`

## Required Evidence

- explicit authored truth references
- explicit derived retrieval substrate references
- retrieval source-class metadata
- lane and visibility governance metadata
- runtime turn retrieval traces

## Audit Methods Used In This Baseline

- retrieval governance contract inspection
- lane/visibility static inspection
- static test surface review (no runtime execution in this block)

## Command Strategy

| command | status | basis | promotion requirement |
| --- | --- | --- | --- |
| `python -m pytest ai_stack/tests/test_rag.py -q --tb=short` | `pending-finalization-after-phase-0` | Path exists; not executed in this block. | Execute and attach retrieval provenance/governance test outputs. |
| `python -m pytest ai_stack/tests/test_goc_phase4_reliability_breadth_operator.py -q --tb=short` | `pending-finalization-after-phase-0` | Path exists; not executed in this block. | Execute with runtime evidence trace capture. |
| retrieval scenario module checks | `pending-finalization-after-phase-0` | Scope not frozen to an exact module set. | Freeze scenario module scope and execute. |

## Baseline Findings

1. `ai_stack/rag.py` defines explicit governance lane (`SourceEvidenceLane`) and visibility class (`SourceVisibilityClass`) models.
2. Retrieval pipeline exports source lane/visibility metadata into retrieval hits and trace summaries.
3. Policy/governance versioning (`RETRIEVAL_POLICY_VERSION`) and route posture (`retrieval_route`) are explicit in code.
4. Runtime turn-level proof of retrieval governance visibility is partially evidenced by integration code references, but no runtime execution traces were captured in this block.

## Status Baseline

- structural_status: `yellow`
- closure_level_status: `level_a_capable`

Rationale: retrieval governance structures are strongly present, but runtime trace-backed proof for all required assertions is incomplete without executed tests.

## Evidence Quality

- evidence_quality: `medium`
- justification: direct code and governance-doc evidence is strong; runtime test/trace execution was intentionally not performed in this block.

## Execution Risks Carried Forward

- retrieval provenance completeness in live runtime outputs remains unverified in this block
- retrieval scenario command scope remains pending finalization
- absence of executed traces may hide edge-case governance drift
