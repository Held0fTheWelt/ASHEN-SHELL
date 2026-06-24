# Git Provenance and Evolution Specification

## 1. Purpose

The Git Provenance and Evolution Layer makes source code explainable through historical evidence. It links code areas, ADRs, UML elements, rules, and definitions to repository evolution.

The layer answers:

- When was this file or source area introduced?
- Which commits changed this ADR or UML diagram?
- Which code files changed together with this rule?
- Which diagrams appear stale compared to source history?
- What is the origin trail for this source path?

## 2. Repository linking model

Repositories are registered per project. A repository record includes:

- repository id
- project id
- local path
- optional sanitized remote url
- default branch name
- scan policy
- include/exclude patterns
- last scan status

ArchitecturalKnowledgeDB reads from the registered repository path. It does not store `.git` internals.

## 3. Metadata stored

MVP metadata:

- commit hash
- short hash
- commit date
- commit message subject
- commit message body optional/configurable
- author display name optional
- author email hash optional
- changed file path
- change type: added, modified, deleted, renamed, copied, unknown
- previous path for renames
- line counts optional
- scan timestamp

## 4. Metadata not stored by default

- raw `.git` objects
- full blobs
- full diffs
- credentials
- raw remote tokens
- raw author emails
- arbitrary binary file contents

## 5. Knowledge link inference

ArchitecturalKnowledgeDB may infer weak links when a commit changes both knowledge files and source files.

Examples:

- ADR + source files changed in one commit
- UML file + implementation files changed in one commit
- rule file + tests changed in one commit

Inferred links must have a confidence level and evidence source.

```json
{
  "link_type": "git_cochange_inferred",
  "confidence": "medium",
  "evidence": "commit abc123 changed ADR-0002 and schema/architectural_knowledge_db.sql"
}
```

## 6. Explicit provenance links

Users or importers may create explicit links:

```json
{
  "source_item": "architectural-knowledge-db:adr:ADR-0002",
  "target": "architectural-knowledge-db:source_area:knowledge-store",
  "link_type": "governs",
  "evidence": "manual"
}
```

Explicit links outrank inferred Git co-change links.

## 7. Staleness analysis

ArchitecturalKnowledgeDB computes staleness hints when related source files changed after a knowledge item.

Example signal:

```text
UML diagram last changed 2026-06-01.
Related source area changed 14 times since 2026-06-01.
Status: review recommended.
```

Staleness levels:

- `current`
- `watch`
- `review_recommended`
- `likely_stale`
- `unknown`

Staleness must not automatically mark an ADR invalid.

## 8. Origin trail output

`architectural_knowledge_db_explain_origin` returns:

- target path or item id
- project
- summary
- explicit knowledge links
- inferred Git links
- first known commit
- last changed commit
- frequently co-changed files
- related ADRs/rules/UML/definitions
- staleness warnings
- authority separation notes

## 9. CLI commands

Recommended commands:

```bash
architectural-knowledge-db repo add --project architectural-knowledge-db --path /sources/architectural-knowledge-db
architectural-knowledge-db git scan --project architectural-knowledge-db
architectural-knowledge-db origin explain --project architectural-knowledge-db --path app/knowledge/adr_store.py
architectural-knowledge-db stale report --project uml-editor
```

## 10. Safety requirements

- Git operations are read-only.
- Repositories mounted into Docker should be mounted read-only by default.
- No credentials are persisted.
- Remote URLs are sanitized before storage.
- Author email storage is disabled by default.
