# ADR-0004: Multi-Project Knowledge Spaces from Day One

## Status

Proposed

## Context

ArchitecturalKnowledgeDB is intended to support multiple independent projects and tool ecosystems. The first known clients include a UML editor, external coding agents, and several distinct codebases. Some projects may share definitions or agent rules, but project-local ADRs and rules must remain isolated unless an explicit cross-project link exists.

If multi-project behavior is added later, early schemas and APIs are likely to assume a single global knowledge space. That would create migration debt and unsafe context mixing.

## Decision

ArchitecturalKnowledgeDB will be multi-project-first.

Every project-scoped table must include `project_id`. Shared knowledge must live in explicit shared knowledge spaces. Queries must require a project id unless they are administrative global queries.

Cross-project links are allowed only as explicit relationship records.

## Consequences

The MVP schema includes:

- `projects`
- `knowledge_spaces`
- `project_imports`
- `repositories`
- project-scoped ADRs, rules, definitions, UML records, source areas, Git provenance, and context-pack runs

Tool calls must include `project_id` for normal operations.

## Query behavior

Default query scope:

```text
project-local records + explicitly imported shared spaces
```

No default query should search all projects unless the caller requests an admin/global scope.

## Cross-project links

Cross-project links are supported for cases such as:

- shared UML notation conventions
- shared agent rules
- dependency relationships between tools
- reusable architecture definitions

Cross-project links must not silently override local decisions.

## Non-goals

The MVP does not implement multi-user permissions, cloud tenancy, or remote synchronization. Multi-project means local project isolation and explicit knowledge-space linking, not SaaS tenancy.
