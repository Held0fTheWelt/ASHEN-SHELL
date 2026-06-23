# Code-aligned UML (World of Shadows)

Implementation-facing diagrams for component SADs and project workflows. Each package has `README.md`,
`TRACEABILITY.md`, and diagram folders with `.md` (Mermaid preview) + `.puml` source companions.

## Read this first

1. This README for conventions.
2. `Components/<slug>/README.md` for a deployable component.
3. `Project/<workflow>/README.md` for cross-cutting flows.
4. `TRACEABILITY.md` in each package to verify claims against code and tests.

## Required folders (component minimum)

- `components/` — C4 context, container, component
- `sequence/` — primary and degraded paths
- `states/` — lifecycle diagrams
- optional: `flow/`, `use-cases/`, `classes/`

## Templates

Copy from [`_templates/c4/`](_templates/c4/) when adding a new component package.

## Validation

Run [`tests/gates/test_architecture_documentation_gate.py`](../tests/gates/test_architecture_documentation_gate.py).
