# Source-bound semantic UML (Better Tomorrow)

Implementation-facing diagrams for component SADs and project workflows. Each package has `README.md`,
`TRACEABILITY.md`, and diagram folders with a PlantUML source plus a Markdown element/relationship
companion.

## Read this first

1. This README for conventions.
2. `Components/<slug>/README.md` for a deployable component.
3. `Project/<workflow>/README.md` for cross-cutting flows.
4. `TRACEABILITY.md` in each package to verify claims against code and tests.

## Viewpoint selection

There is no fixed diagram count or universal four-view profile. Each SAD selects the viewpoints needed
to make its actual concerns analyzable. The corpus currently combines context, container, component,
sequence, activity, state, class/data, deployment and use-case models.

Every modeled element states responsibility, contract and source anchor. Every edge names its semantics
and interaction contract. The source of these projections is
[`tools/architecture_assurance/model_catalog.json`](../tools/architecture_assurance/model_catalog.json).

The whole-system package adds two drift-specific models:

- [architecture archaeology](Project/ecosystem-topology/components/architecture-archaeology.md)
- [historical claim classification](Project/ecosystem-topology/states/claim-classification.md)

## Templates

Copy from [`_templates/c4/`](_templates/c4/) when adding a new component package.

## Validation

Run the dedicated semantic architecture gate:

```powershell
python -m tools.architecture_assurance generate --dry-run
python -m tools.architecture_assurance audit --dry-run
```

The architecture-assurance workflow renders every checked-in `.puml` file as
SVG with checksum-pinned PlantUML `1.2024.8`. It preserves the `UML/` directory
structure, verifies that source and preview counts match, writes `SHA256SUMS`
and `RENDERER.txt`, and uploads the result as the
`better-tomorrow-uml-previews` CI artifact.
