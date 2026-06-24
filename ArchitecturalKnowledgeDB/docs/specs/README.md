# ArchitecturalKnowledgeDB Implementation Specs

These specs extend the base ArchitecturalKnowledgeDB design in [../architecture/SPEC_ArchitecturalKnowledgeDB_Knowledge_DB_Git_Provenance.md](../architecture/SPEC_ArchitecturalKnowledgeDB_Knowledge_DB_Git_Provenance.md) into implementable vertical slices for ADR/Markdown round-tripping, structured diagram editing, consistency checks, retrieval, Git provenance, and the local admin UI.

## Design Decisions Driving These Specs

- **DB-first working state.** The SQLite database is the working copy. File trees are import sources and export targets.
- **Folder-based round-trip.** ADR and diagram folders are configurable. Import reads from them; export writes back to them.
- **Structured diagram model.** Diagrams are stored as structured elements and relationships, with preserved extras for hand-written source.
- **Gated writes.** Agents edit the database. Files only change through explicit export, so Git review stays in the author's hands.

## Spec Sequence

| # | Spec | Depends on |
| --- | --- | --- |
| 1 | [SPEC_01 - ADR vertical slice](SPEC_01_ADR_ROUNDTRIP_AND_AUTHORING.md): DB foundation, ADR import/export round-trip, MCP authoring, and minimal consistency | none |
| 2 | [SPEC_02 - Structured UML round-trip](SPEC_02_STRUCTURED_UML_ROUNDTRIP.md): PlantUML to structured model, preserved extras, conformance gate | 1 |
| 3 | [SPEC_03 - Consistency and cross-link integrity](SPEC_03_CONSISTENCY_AND_CROSSLINK_INTEGRITY.md): contradictions, supersede integrity, ADR-diagram links, broken links, impact of change | 1, 2 |
| 4 | [SPEC_04 - Git provenance and staleness](SPEC_04_GIT_PROVENANCE_AND_STALENESS.md): repository registry, read-only scan, origin trail, drift | 1 |
| 5 | [SPEC_05 - Retrieval and context packs](SPEC_05_RETRIEVAL_AND_CONTEXT_PACKS.md): FTS5, authority-aware context-pack builder, optional semantic recall | 1-4 |
| 6 | [SPEC_06 - Admin UI](SPEC_06_ADMIN_UI.md): projects, import/export runs, consistency and staleness dashboards | 1-5 |

Specs are intentionally local-first: FastAPI + SQLite + Typer CLI, no cloud service required.

These are AKDB implementation specs, not Tiny Tools SAD/UML authority documents. Cross-project SAD/UML synchronization belongs in the public `D:\TinyToolDevelopment\Git` tree.
