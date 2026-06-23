# Content module ↔ runtime profile

**Owning SAD:** [content-authority](../components/content-authority/architecture.md).

`content/modules/<module_id>/` holds authored YAML truth. Runtime profiles (e.g. `god_of_carnage_solo`) are
**not** content modules—they select how a module runs. The engine loads compiled projections; it does not
author canon.

Evidence: [ADR-0025](../../archive/adr-retired-2026/adr-0025-canonical-authored-content-model.md), [content-authority SAD D1](../components/content-authority/architecture.md#d1-canonical-authored-content-model).
