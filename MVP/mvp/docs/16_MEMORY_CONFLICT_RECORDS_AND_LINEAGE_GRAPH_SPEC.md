# 16 — Memory Conflict Records and Lineage Graph Specification

Each conflict must be a first-class object with conflict class, involved records, same-slot decision, severity, suggested resolution, human-review requirement, and closure state.

The lineage graph must track:
- supersedes
- derived_from
- contradicted_by
- supported_by
- invalidated_by
