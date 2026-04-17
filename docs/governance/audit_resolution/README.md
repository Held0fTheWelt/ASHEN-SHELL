# Audit resolution artifacts

Three-layer model (restart-safe governance):

| File | Role |
|------|------|
| [audit_resolution_master_prompt.md](audit_resolution_master_prompt.md) | Universal instructions for agents and humans (no case-specific IDs or repo paths). |
| [audit_resolution_input_world_of_shadows_2026-04-12.md](audit_resolution_input_world_of_shadows_2026-04-12.md) | Case input: audit source, scope, findings, evidence tags, constraints. |
| [audit_resolution_state_world_of_shadows.md](audit_resolution_state_world_of_shadows.md) | Living state: registers, blockers, validation evidence index, closure, decision log. |
| [CLOSURE_PACKET_world_of_shadows_2026-04-12.md](CLOSURE_PACKET_world_of_shadows_2026-04-12.md) | Closure checklist and gate commands (links into state Part K). |

These are **not** ADRs. ADRs live in [`docs/ADR/README.md`](../../ADR/README.md).
