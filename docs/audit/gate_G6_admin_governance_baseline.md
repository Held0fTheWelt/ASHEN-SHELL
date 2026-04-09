# Gate G6 Baseline: Admin Governance

## Gate

- Gate name: G6 Admin Governance
- Gate class: structural
- Audit subject: admin authority boundaries (control plane yes, semantic authorship no)

## Repository Inspection Targets

- `administration-tool/app.py`
- `backend/app/api/v1/ai_stack_governance_routes.py`
- `backend/app/api/v1/improvement_routes.py`
- `backend/tests/test_game_admin_routes.py`
- `backend/tests/test_admin_security.py`
- `tests/smoke/test_admin_startup.py`

## Required Evidence

- admin-manageable policy/operations surfaces
- prevention of direct semantic-authoring operations
- versioned/review-visible admin change traces
- route-level authorization/security checks

## Audit Methods Used In This Baseline

- static admin route and governance-surface inspection
- static security test review
- static startup smoke-surface review (no runtime execution in this block)

## Command Strategy

| command | status | basis | promotion requirement |
| --- | --- | --- | --- |
| `python -m pytest tests/smoke/test_admin_startup.py -v --tb=short` | `pending-finalization-after-phase-0` | Path exists; test quality is lightweight and environment-sensitive. | Execute in controlled environment and attach startup evidence. |
| `cd backend && python -m pytest tests/test_game_admin_routes.py tests/test_admin_security.py -q --tb=short --no-cov` | `repo-verified` | Paths exist; backend command conventions documented. | Execute and attach authorization/governance outcomes. |

## Baseline Findings

1. Admin control-plane UI routes and governance views are explicitly present in `administration-tool/app.py`.
2. Governance APIs in `backend/app/api/v1/ai_stack_governance_routes.py` are moderator/admin protected and primarily evidence-oriented (`session-evidence`, `improvement-packages`, `release-readiness`).
3. Improvement governance state in `improvement_service.py` includes explicit review states (`pending_governance_review`, `governance_accepted`, `governance_rejected`) and decision history.
4. Security test coverage exists (`test_admin_security.py`), and admin game-route governance flows are tested (`test_game_admin_routes.py`).
5. Full proof that no admin path can introduce shared semantic truth drift still requires combined route-level runtime evidence beyond static review.

## Status Baseline

- structural_status: `yellow`
- closure_level_status: `level_a_capable`

Rationale: strong governance and security scaffolding is present, but strict semantic-boundary proof is not fully closed without executed route/security evidence.

## Evidence Quality

- evidence_quality: `medium`
- justification: direct implementation and tests are available, but this baseline does not include command execution output for final behavioral confirmation.

## Execution Risks Carried Forward

- semantic-boundary enforcement across all admin-capable write paths requires explicit runtime verification
- smoke startup tests are lightweight placeholders and may underrepresent production boundary behavior
- pending execution of verified backend commands for conclusive route/security evidence
