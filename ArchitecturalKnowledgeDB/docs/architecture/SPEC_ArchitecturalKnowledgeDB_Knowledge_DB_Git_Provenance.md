# ArchitecturalKnowledgeDB Knowledge DB with Git Provenance and Multi-Project Knowledge Spaces

## 1. Purpose

ArchitecturalKnowledgeDB is a local knowledge database and context service for coding agents, UML editors, and MCP clients. It stores and exposes structured architecture knowledge across multiple projects.

ArchitecturalKnowledgeDB exists to answer questions such as:

- Which ADRs, rules, definitions, UML elements, and source areas are relevant to this task?
- Why does this code exist?
- Which decision introduced this rule?
- Which UML diagram may be stale because related code changed after the diagram?
- Which source paths are governed by a specific ADR?
- Which project-local conventions apply to this repository path?
- Which shared definitions apply across projects?

ArchitecturalKnowledgeDB is not an AI runtime and does not modify source code, UML models, or Git repositories by default.

## 2. Product boundary

ArchitecturalKnowledgeDB is an external tool for coding agents and architecture knowledge management. It is not a Tiny Tool Development plugin. It may index Tiny Tool Development repositories, but this is only a registered source project, not a product dependency.

ArchitecturalKnowledgeDB clients may include:

- Claude/Codex/Cursor-like coding agents
- MCP clients
- a graphical UML editor
- documentation tools
- local admin UI
- CLI workflows
- future source-analysis services

## 3. Design principles

### 3.1 DB-first, file-friendly

The local database is the primary working state for structured knowledge. Files remain important as import/export formats and as versionable artifacts.

Supported file formats:

- Markdown ADRs and specs
- PlantUML diagrams
- Mermaid diagrams
- JSON/YAML rules and project registries
- OpenAPI contracts
- future optional DOCX/PDF import pipelines

### 3.2 Multi-project from day one

The data model must support multiple projects before the first implementation milestone is complete. No table should assume one global project.

Every project-scoped record must carry a `project_id`. Shared records must belong to a declared shared knowledge space.

### 3.3 Git as linked provenance, not stored repository content

ArchitecturalKnowledgeDB does not copy `.git` internals into the database. Git repositories are registered by path or URL metadata. ArchitecturalKnowledgeDB may store selected read-only metadata such as commit hashes, timestamps, changed files, branch labels, and knowledge-to-commit links.

Git metadata provides historical evidence, not normative architecture authority.

### 3.4 Authority-aware context

Not all knowledge has equal authority. Context packs must preserve authority level:

- hard guardrail
- accepted ADR
- active rule
- canonical definition
- current UML model
- source-area evidence
- Git provenance evidence
- historical context
- superseded decision
- deprecated compatibility

### 3.5 Read-only by default

ArchitecturalKnowledgeDB may read source trees and Git metadata. It must not mutate repositories, source files, UML files, or Git state unless a future explicit write-mode ADR permits it.

## 4. Core concepts

### 4.1 Project

A project is an isolated knowledge space with its own ADRs, UML models, rules, definitions, repositories, source areas, and context-pack history.

Examples:

- `architectural-knowledge-db`
- `uml-editor`
- `world-engine`
- `unreal-integration-intelligence`
- `internal-index-service`
- `llm-store`

### 4.2 Shared knowledge space

A shared knowledge space stores reusable definitions, rules, or patterns that may be linked into multiple projects.

Examples:

- `shared.agent-rules`
- `shared.architecture-terms`
- `shared.uml-conventions`

A project may import shared knowledge explicitly. Shared knowledge must never silently override project-local ADRs.

### 4.3 Knowledge item

A knowledge item is any structured entity that can be indexed, linked, searched, exported, and included in context packs.

Types:

- ADR
- definition
- rule
- UML diagram
- UML element
- source area
- codebase convention
- agent instruction
- Git commit evidence
- Git file history evidence
- context-pack result

### 4.4 Source area

A source area is a named repository path or path pattern with semantic meaning.

Example:

```json
{
  "project_id": "architectural-knowledge-db",
  "source_area_id": "knowledge-store",
  "path_patterns": ["app/knowledge/**", "schema/**"],
  "description": "Persistence and schema layer for structured knowledge records."
}
```

### 4.5 Origin trail

An origin trail explains how a code area, UML element, rule, or ADR came into being.

It may include:

- explicit ADR links
- related UML elements
- source area mapping
- commits that introduced or changed related files
- related files frequently changed together
- warnings about stale docs or diagrams

Origin trails are evidence bundles, not legal proof.

## 5. System architecture

```text
ArchitecturalKnowledgeDB Service
  FastAPI HTTP API
  MCP tool adapter
  CLI
  Admin UI

ArchitecturalKnowledgeDB Core
  project registry
  knowledge model
  context-pack builder
  import/export pipelines
  authority resolver
  relationship graph
  provenance/evolution analyzer

Storage
  SQLite database
  FTS5 search tables
  optional JSON columns
  optional future vector index

External sources
  local repositories mounted read-only
  docs folders
  UML folders
  rules folders
  linked Git repositories
```

## 6. Storage model

The MVP uses SQLite with WAL mode and FTS5. Tables must be project-aware.

Major table groups:

- project registry
- repository registry
- knowledge items
- ADRs
- definitions
- rules
- UML diagrams/elements/relationships
- source areas
- knowledge links
- Git commits and changed-file metadata
- file history summaries
- staleness reports
- context pack runs
- FTS documents

The database must be portable and stored under a configurable data root, for example:

```text
/data/architectural_knowledge_db.sqlite
```

## 7. Git provenance model

ArchitecturalKnowledgeDB registers repositories and stores selected metadata:

- commit hash
- repository id
- author name or configured anonymized author id
- optional hashed author email
- commit date
- message summary
- changed file paths
- file change type
- branch/tag labels when available
- knowledge links inferred or explicit

ArchitecturalKnowledgeDB does not store:

- `.git/objects`
- full repository history blobs
- secrets
- remote credentials
- raw author emails by default
- full diffs by default

Optional later mode may store small diffs for ADR/UML/rule files only, gated by configuration.

## 8. Multi-project behavior

### 8.1 Project isolation

Default queries only return data from the requested project and explicitly imported shared spaces.

### 8.2 Cross-project links

Cross-project links are allowed but explicit.

Examples:

- `uml-editor` consumes shared UML notation rules from `shared.uml-conventions`
- `architectural-knowledge-db` references `internal-index-service` as a possible future indexing peer
- `world-engine` links to shared agent rules but keeps its ADR authority local

### 8.3 Collision handling

IDs are unique inside a project. Globally stable identifiers should use:

```text
project_id:item_type:item_id
```

Example:

```text
world-engine:adr:ADR-0068
architectural-knowledge-db:rule:db-first-primary-state
```

## 9. Context packs

A context pack is a task-specific bundle for an agent or client.

Input:

- project id
- task description
- optional source paths
- requested knowledge types
- maximum item count
- include/exclude flags

Output:

- summary
- hard guardrails
- relevant ADRs
- active rules
- canonical definitions
- UML elements
- source areas
- Git provenance evidence
- staleness warnings
- excluded/superseded items

Context packs must separate normative knowledge from evidence.

## 10. MCP tools

Initial tools:

- `architectural_knowledge_db_search`
- `architectural_knowledge_db_get_context_pack`
- `architectural_knowledge_db_get_adr`
- `architectural_knowledge_db_get_rules_for_path`
- `architectural_knowledge_db_get_uml_context`
- `architectural_knowledge_db_explain_origin`
- `architectural_knowledge_db_get_git_provenance`
- `architectural_knowledge_db_get_staleness_report`
- `architectural_knowledge_db_validate_task_context`

## 11. Admin UI

The first admin UI should be minimal:

- list projects
- add/edit project
- register repositories
- show index status
- rebuild project index
- inspect ADRs/rules/definitions
- inspect repository provenance scan status
- run test context-pack query
- show stale UML/ADR warnings

## 12. Docker deployment

Docker is supported but not required.

Default container behavior:

- FastAPI service on port `8787`
- data volume mounted at `/data`
- source repositories mounted read-only under `/sources`
- no project mutation
- no Git mutation
- no background task faster than configured scan intervals

## 13. Non-goals

The MVP must not:

- generate code patches
- mutate Git repositories
- make architecture decisions automatically
- replace Git
- require embeddings
- require cloud services
- become a full UML editor
- treat Git correlations as authoritative rules
- silently merge project spaces

## 14. Success criteria

The MVP is successful when a coding agent can ask:

```text
Give me the context pack for modifying the ArchitecturalKnowledgeDB ADR storage layer.
```

and receive:

- the DB-first ADR
- relevant source areas
- active rules
- relevant UML/store records
- Git provenance showing when related files were introduced or changed
- warnings against replacing DB primary state with file-only logic

The UML editor is successful when it can ask:

```text
What decisions and source areas are linked to this UML element, and is this diagram stale?
```

and receive a structured, authority-aware answer.
