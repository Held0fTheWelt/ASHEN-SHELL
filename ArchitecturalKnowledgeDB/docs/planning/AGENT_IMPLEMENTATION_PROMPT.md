# Agent Implementation Prompt

You are implementing ArchitecturalKnowledgeDB, a local multi-project architecture knowledge database and agent context service.

## Goal

Build the first implementation milestone for ArchitecturalKnowledgeDB:

- multi-project-first SQLite schema
- DB-first ADR/rule/definition/source-area store
- linked read-only Git provenance scanner
- authority-aware context packs
- basic FastAPI and CLI surface
- MCP-ready tool manifest

## Hard boundaries

Do not implement AI reasoning, embeddings, vector DBs, code patching, Git writes, repository mutation, or a full UML editor in this milestone.

Do not copy `.git` internals into the database. Store only selected metadata obtained through read-only Git commands or a Git library.

Every normal data-access operation must require `project_id`. No silent global search.

## Required stack

- Python 3.11+
- FastAPI
- Typer
- SQLite with FTS5
- Pydantic models
- pytest
- Dockerfile and docker-compose sample

## Initial tasks

1. Create repository structure.
2. Add SQLite schema and migration runner.
3. Implement project registry.
4. Implement repository registry.
5. Implement ADR/rule/definition/source-area stores.
6. Implement FTS indexer.
7. Implement context-pack builder without embeddings.
8. Implement Git read-only scan for commit metadata and changed files.
9. Implement file history summaries.
10. Implement `explain_origin` for source paths using explicit and inferred links.
11. Expose FastAPI routes.
12. Expose CLI commands.
13. Export MCP manifest.
14. Add tests for project isolation, Git read-only behavior, and context-pack authority ordering.

## Report format

When complete, report:

- files changed
- implemented features
- known limitations
- tests run
- example CLI commands
- example API responses
- remaining backlog
