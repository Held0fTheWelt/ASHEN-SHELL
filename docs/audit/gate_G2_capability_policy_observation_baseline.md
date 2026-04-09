# Gate G2 Baseline: Capability / Policy / Observation Separation

## Gate

- Gate name: G2 Capability / Policy / Observation Separation
- Gate class: structural
- Audit subject: separation of capability truth, policy truth, and runtime observation truth

## Repository Inspection Targets

- `ai_stack/capabilities.py`
- `ai_stack/operational_profile.py`
- `backend/app/runtime/model_inventory_contract.py`
- `backend/app/runtime/model_routing_contracts.py`
- `backend/app/runtime/model_routing.py`
- `backend/app/runtime/model_routing_evidence.py`
- `backend/app/runtime/area2_routing_authority.py`
- `backend/tests/runtime/test_model_routing_evidence.py`
- `backend/tests/runtime/test_decision_policy.py`

## Required Evidence

- distinct structures for capability, policy, and observation
- routing records containing policy identity/version and route reasoning
- fallback-chain and route-reason visibility
- test evidence that observation does not overwrite policy

## Audit Methods Used In This Baseline

- static structure review
- routing-evidence contract review
- static test intent review (no runtime execution in this block)

## Command Strategy

| command | status | basis | promotion requirement |
| --- | --- | --- | --- |
| `cd backend && python -m pytest tests/runtime/test_model_routing_evidence.py -q --tb=short --no-cov` | `repo-verified` | Path exists; backend command pattern documented in `docs/testing-setup.md` and `backend/app/runtime/area2_validation_commands.py`. | Execute and attach output evidence when running verification pass. |
| `cd backend && python -m pytest tests/runtime/test_decision_policy.py -q --tb=short --no-cov` | `repo-verified` | Path exists; backend command pattern and flags documented. | Execute and attach output evidence when running verification pass. |

## Baseline Findings

1. Capability/policy/observation boundaries are structurally explicit:
   - capability-facing specs in `model_inventory_contract.py`
   - policy/routing contracts in `model_routing_contracts.py`
   - observation payload in `model_routing_evidence.py`
2. Routing evidence includes route reason, fallback chain, escalation/degradation flags, and policy/selection alignment diagnostics.
3. Tests directly target routing evidence shape and policy taxonomy validation.
4. This block did not execute runtime tests, so behavioral confirmation remains pending despite strong static readiness.

## Status Baseline

- structural_status: `yellow`
- closure_level_status: `level_a_capable`

Rationale: structural separation is well represented and test surfaces are present, but runtime execution evidence is not yet attached in this block.

## Evidence Quality

- evidence_quality: `medium`
- justification: comprehensive static contracts and tests exist, but no executed runtime proof is included in this baseline output.

## Execution Risks Carried Forward

- unexecuted test commands leave runtime behavior confirmation pending
- policy-version identity presence in live routing traces still requires run-time capture evidence
