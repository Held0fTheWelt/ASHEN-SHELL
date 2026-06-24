# Implementation Backlog

## Epic A: Repository and project skeleton

- Create Python package `architectural_knowledge_db`
- Add FastAPI service
- Add Typer CLI
- Add SQLite connection manager
- Add migration runner
- Add configuration loader
- Add Dockerfile and docker-compose sample

## Epic B: Multi-project schema

- Implement `projects`
- Implement `knowledge_spaces`
- Implement `project_imports`
- Add project-aware repository pattern to all services
- Reject non-admin queries without project id
- Add tests for project isolation

## Epic C: Knowledge DB core

- Implement `knowledge_items`
- Implement ADR store
- Implement definition store
- Implement rules store
- Implement source area store
- Implement knowledge links
- Implement FTS indexing
- Add import/export contracts

## Epic D: Context pack builder

- Implement task query normalization
- Retrieve relevant ADRs/rules/definitions/source areas
- Resolve authority order
- Include superseded warnings
- Include imported shared spaces with source labels
- Emit JSON context pack
- Store context pack run history

## Epic E: Git provenance layer

- Implement repository registry
- Implement Git CLI read-only adapter
- Implement commit scan
- Implement changed file scan
- Implement file history summary
- Sanitize remote URLs
- Hash or omit author emails
- Add tests verifying `.git` internals are not stored

## Epic F: Origin and staleness

- Implement explicit knowledge-to-file links
- Implement co-change inference
- Implement origin trail generation
- Implement staleness report generator
- Add confidence/evidence labels
- Add context pack Git evidence section

## Epic G: UML store

- Implement UML diagram record
- Implement UML element record
- Implement UML relationship record
- Implement PlantUML basic parser
- Implement Mermaid basic parser
- Add UML-to-ADR/rule linking
- Add UML staleness reports

## Epic H: MCP/API/Admin

- Implement OpenAPI routes
- Implement MCP manifest route
- Implement MCP tool dispatcher
- Add minimal admin UI
- Add project list page
- Add repository scan page
- Add context-pack preview page
- Add origin trail page

## Epic I: Validation and guardrails

- Ensure read-only source mounts work
- Ensure no Git writes are possible in MVP
- Add tests for project isolation
- Add tests for authority ordering
- Add tests for staleness report generation
- Add tests for origin trail output
- Add tests for sanitized repository metadata
