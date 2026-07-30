# ArchitecturalKnowledgeDB is not vendored

The embedded AKDB 0.1 implementation was retired on 2026-07-30.

Better Tomorrow uses its own architecture-assurance schemas, gates and tests.
AKDB integration uses the external revision pinned in
`tools/architecture_assurance/akdb.lock.json`.

Do not restore executable AKDB sources or copy a database into this directory.
See `docs/architecture/AKDB-AUTHORITY.md` and
`docs/architecture/AKDB-MIGRATION.md`.

An ignored `.akdb/` directory may still exist in an older developer working
copy. It is retained only for manual forensic rollback and must never be used
by tests or automatic canon migration.
