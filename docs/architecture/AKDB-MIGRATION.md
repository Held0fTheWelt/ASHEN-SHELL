# Migration from embedded AKDB 0.1

## Decision

The executable AKDB 0.1 source copy formerly stored below
`ArchitecturalKnowledgeDB/` is retired. Better Tomorrow now owns its assurance
schemas, tests, bindings and gates. Current AKDB is consumed only as the
external, commit-pinned integration described in `AKDB-AUTHORITY.md`.

## Preserved evidence

`evidence/2026-07-30-legacy-akdb-retirement-manifest.json` records SHA-256 and
byte size for all 126 tracked files removed from the embedded copy. It also
records six ignored runtime artifacts that existed in the original working
copy:

- the SQLite database and its WAL/SHM files;
- a dated SQLite backup;
- the previous server stdout/stderr logs.

Those ignored runtime artifacts are deliberately not imported into the new
canon, moved, rewritten or deleted. Legacy database assertions are not trusted
as Better Tomorrow architecture truth until corroborated by current source and
the new binding manifests.

## Rollback

1. Restore the retired source files from the Git parent of this migration.
2. Verify their hashes against the retirement manifest.
3. Stop every process using the legacy SQLite files before opening a backup.
4. Use the old database only for forensic comparison; do not overwrite current
   Better Tomorrow SADs, bindings or canon from it.

Rollback does not change the external AKDB dependency lock and does not bypass
the Better Tomorrow architecture gate.

## Definition of done

- the embedded executable package, container definition, scripts and old tests
  are absent from the tracked tree;
- the tombstone is the only tracked file below `ArchitecturalKnowledgeDB/`;
- external AKDB revision and capabilities are locked;
- all integration state is rooted in the test temporary directory;
- generation and exports are idempotent and dry-run is non-writing;
- JSON, JUnit and SARIF derive from one audit;
- the Better Tomorrow architecture gate and existing documentation gate pass.
