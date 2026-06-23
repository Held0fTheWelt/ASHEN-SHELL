# Project-wide architecture TRACEABILITY

| Layer | SAD | UML | Gate |
| --- | --- | --- | --- |
| Components (8) | `docs/architecture/components/*/architecture.md` | `UML/Components/*/` | `test_sad_exists_with_arc42_sections` |
| Project (7) | `docs/architecture/project/*/architecture.md` | `UML/Project/*/` (where applicable) | `test_uml_packages_for_rollout_complete_rows` |
| ADR absorption | [DECISION_REGISTRY.md](DECISION_REGISTRY.md) | — | `scripts/adr_retirement_audit.py` |
| Contracts | `docs/architecture/contracts/` | turn-execution-canonical UML | `test_runtime_contracts_listed_in_normative_index` |
| Links | — | — | `scripts/architecture_link_audit.py --check` |
| Rollout truth | [ROLLOUT.md](ROLLOUT.md) | [DOC-HEALTH.md](../DOC-HEALTH.md) | `test_rollout_lists_world_engine_complete` |

Evidence snapshots: [`evidence/`](../evidence/).
