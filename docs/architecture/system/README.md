# System architecture

This package is the canonical entry point for the Better Tomorrow / World of Shadows
software architecture.

1. Read the [system SAD](architecture.md).
2. Follow a runtime scenario under [`../scenarios/`](../scenarios/README.md).
3. Inspect the owning component SAD for implementation detail.
4. Read the linked active ADR and architecture violation before changing a boundary.

The system SAD separates three statements that must never be collapsed:

- **Observed:** behavior or structure present in the current implementation.
- **Normative:** accepted target architecture.
- **Repair:** an explicit migration from observed to normative behavior.

Historical artifacts and Git evidence explain why code exists. They do not make an
observed implementation normative.
