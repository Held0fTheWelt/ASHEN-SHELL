# Multi-Project Model Specification

## 1. Purpose

ArchitecturalKnowledgeDB must support several projects from the beginning. Each project has separate ADRs, UML models, rules, definitions, repositories, source areas, Git provenance, and context-pack history.

## 2. Project identifiers

Project IDs are stable lowercase identifiers:

```text
architectural-knowledge-db
uml-editor
world-engine
unreal-integration-intelligence
internal-index-service
llm-store
```

A globally stable item reference uses:

```text
<project_id>:<item_type>:<local_id>
```

Example:

```text
architectural-knowledge-db:adr:ADR-0002
uml-editor:uml_element:class.ModelCanvas
```

## 3. Knowledge spaces

A knowledge space can be:

- `project`: owned by one project
- `shared`: imported by multiple projects
- `archive`: read-only historical space

Shared knowledge spaces are explicit:

```text
shared.agent-rules
shared.architecture-terms
shared.uml-conventions
```

## 4. Project imports

A project may import shared spaces:

```yaml
projects:
  - id: uml-editor
    imports:
      - shared.uml-conventions
      - shared.agent-rules
```

Imports are visible in context packs but must be marked as shared.

## 5. Query scope

Normal queries require `project_id`.

Default scope:

```text
requested project + imported shared spaces
```

Admin scope may query all projects, but this must be explicit.

## 6. Collision handling

If a project-local definition conflicts with a shared definition, project-local knowledge wins inside that project unless an accepted ADR states otherwise.

Context packs should warn about conflicts instead of silently merging definitions.

## 7. Cross-project links

Cross-project links are represented as knowledge links and must include:

- source project id
- source item id
- target project id
- target item id
- relationship type
- authority/evidence level

Examples:

- `references`
- `depends_on`
- `imports_definition`
- `related_tooling`
- `shared_convention`

## 8. Storage requirement

Every project-scoped table must contain `project_id`.

Every API endpoint for normal data access must accept or infer exactly one project id. If not possible, it must reject the call rather than search all projects silently.
