# 20 — Retrieval Task Profiles and Hybrid Index Consistency Specification

Required retrieval profiles:
- runtime question
- diagnosis
- audit
- research
- authoring
- world-state continuity

Retrieval layers:
1. lexical search
2. semantic rerank
3. authority/relevance rerank
4. task-profile filtering
5. degraded-mode policy

The index model must expose snapshot generation, stale/building/failed states, read-after-write policy, and profile-specific degraded behavior.
