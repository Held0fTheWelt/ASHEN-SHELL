# MVP Roadmap

## MVP 01: Multi-Project Knowledge DB Foundation

Goal: Build the local DB-first foundation with project isolation.

Scope:

- SQLite schema with `project_id` in project-scoped tables
- project registry
- shared knowledge spaces
- project imports
- knowledge item base table
- ADR/rule/definition tables
- source area table
- FTS5 table
- CLI project registration
- basic search API

Acceptance criteria:

- two projects can be registered
- same ADR id can exist in two different projects without collision
- default search requires `project_id`
- imported shared space records are included only when configured

## MVP 02: ADR/Rules/Definitions Import-Export

Goal: Make structured architecture knowledge editable and portable.

Scope:

- Markdown ADR import/export
- YAML/JSON rules import/export
- glossary/definition import/export
- status/supersedes/superseded-by parsing
- authority-level handling
- context pack without Git provenance

Acceptance criteria:

- ADR-0002 can be imported into project `architectural-knowledge-db`
- active rules can be queried for a source area
- context pack separates hard guardrails from notes

## MVP 03: Git Repository Registry and Provenance Scan

Goal: Link repositories and scan selected Git metadata read-only.

Scope:

- repository registration per project
- Git read-only scanner
- commit metadata import
- changed file path import
- file history summary
- sanitized remote handling
- no `.git` internals stored

Acceptance criteria:

- repository can be registered under one project
- scan stores commit hashes and changed paths
- file history reports first seen, last changed, change count
- author email is not stored by default

## MVP 04: Origin Trail and Staleness Reports

Goal: Explain why code exists and which knowledge may be stale.

Scope:

- knowledge-to-file explicit links
- inferred co-change links
- `architectural_knowledge_db_explain_origin`
- UML/ADR/source staleness reports
- context-pack Git evidence section

Acceptance criteria:

- origin explanation for a source path includes related ADR/rules/source areas
- Git evidence is clearly marked as evidence, not authority
- stale UML diagram warning can be generated from changed related source files

## MVP 05: UML Knowledge Store

Goal: Add UML diagrams/elements as structured knowledge.

Scope:

- PlantUML import/export
- Mermaid import/export
- UML diagrams table
- UML elements and relationships
- UML-to-ADR/rule links
- UML staleness UI/API

Acceptance criteria:

- UML editor can fetch related ADRs/rules for an element
- diagram can be marked `review_recommended` when source changed after diagram

## MVP 06: MCP and Admin Layer

Goal: Expose ArchitecturalKnowledgeDB to coding agents and local administration.

Scope:

- MCP tool manifest endpoint
- MCP tool executor or server adapter
- admin UI for projects/repositories/index status
- context-pack preview
- staleness report page

Acceptance criteria:

- coding agent can call `architectural_knowledge_db_get_context_pack`
- UML editor can call `architectural_knowledge_db_get_uml_context`
- admin user can run project Git scan manually
