# 12 — Memory Core Architecture

Memory is domain-aware, partitioned, temporally valid, lineage-aware, conflict-aware, threshold-aware, and effect-aware.

Every memory record must carry:
- domain type
- assertion mode
- authority level
- review status
- partition key
- slot key
- temporal validity
- provenance
- effect surfaces
- confidence and conflict risk

Required engines:
- identity and slotting
- conflict detection
- temporal validity classification
- relevance scoring
- retrieval planning
- transformation runtime
- threshold engine
- effect surface activation
- governed consolidation
