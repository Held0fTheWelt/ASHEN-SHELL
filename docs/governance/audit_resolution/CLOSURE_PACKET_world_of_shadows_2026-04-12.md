# Audit resolution closure packet — World of Shadows (2026-04-12)

**Purpose:** Checklist and pointers for governance closure. **Authoritative registers** live in [audit_resolution_state_world_of_shadows.md](audit_resolution_state_world_of_shadows.md).

## Pre-closure checklist (per finding)

- [ ] Status transitions follow [Part I](audit_resolution_master_prompt.md) rules in the state file.
- [ ] Part **K** evidence index rows exist with SHA / build id and “proves” statement.
- [ ] Documentation obligations ticked or deferred with **blocker** row.
- [ ] Dependent prevention / SPR items: no open blocker unless residual risk **accepted** (named owner, review date).
- [ ] **Part J** reopen log updated if closure was challenged.

## Engineering evidence (fill after merge)

| Gate | Command / location | Notes |
|------|--------------------|-------|
| World-engine fast tests | `cd world-engine && python -m pytest tests/ -m "not slow and not websocket" -q` | Includes narrative commit + persistence |
| Backend compiler test | `cd backend && python -m pytest tests/content/test_content_compiler.py -q` | Scene row `id` / `scene_id` contract |

Link CI run URLs and commit SHAs into the **state** document Part K table when closing.

## Residual risk and management decisions

Record in state file: risk acceptance, scope compression, or SPR depth trade-offs (see state “Management decision points”).
