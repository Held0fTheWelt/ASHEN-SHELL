# Architecture lineage and intent recovery

Git and the external AKDB integration provide read-only provenance for architecture work. Lineage
answers why a component or seam exists, which prior implementation it replaced, and whether its
documentation is stale. It does not automatically decide which historical state was correct.

## Architecture-documentation lineage

| Commit | Change | Architectural meaning |
| --- | --- | --- |
| `5f036699` | retired active ADRs into SAD §9 | preserved decisions but began concentrating chronology in SADs |
| `e8695b5f` | completed SAD restructure and documentation gates | established arc42 shape, mechanism catalogs and retirement parity |
| `5bb589e9` | modernized architecture assurance and externalized AKDB | introduced source bindings, deterministic canon and fixed depth views |
| `18591e80` | replaced generic depth with semantic models | introduced concern-specific elements, relations and source anchors |
| `de2cff5b` | added drift edges and remediation runway | connected historical claims to current code and target directions |
| `7959c848` | unsharded World Engine manager authority path | made the current finalization and persistence path inspectable |
| `a1b5db90` | retargeted assurance after package rename | reconciled generated evidence to current `world_engine` paths |

## Lineage contract

For an architecture claim, AKDB/Git provenance should expose:

| Field | Purpose |
| --- | --- |
| stable claim or element ID | survive file moves and terminology changes |
| historical source and snapshot hash | identify the original assertion |
| first-seen and last-touch commit | establish chronology and staleness |
| rename/move chain | distinguish deletion from relocation |
| co-change evidence | identify likely coupled implementation surfaces |
| current source and test anchors | show present implementation truth |
| active ADR | identify normative target authority |
| violation and closure evidence | make disagreement and repair explicit |

## Interpretation rules

1. A previous implementation is evidence of intent, not proof that it should be restored.
2. A source move does not close a violation; behavior and authority must be reconciled.
3. A green historical test is not current production-path proof.
4. Conflicting historical and current claims remain visible until an ADR selects a target.
5. Generated lineage records are immutable evidence; human diagnosis and target decisions remain
   reviewable documents.

## Current lineage routes

- [Git/archaeology baseline](architecture-drift-baseline.md)
- [Drift reconciliation](architecture-drift-reconciliation.md)
- [AKDB authority and safety boundary](../AKDB-AUTHORITY.md)
- [Architecture violation register](../violations/README.md)

The canonical AKDB file projection now includes the system SAD, active ADRs, violation register,
implementation scenarios, data/deployment contracts and this lineage record. This lets an external
AKDB export traverse history → current implementation → target → proof without making the external
database the authoring authority.
