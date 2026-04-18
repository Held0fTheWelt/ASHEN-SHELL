# ADR-0003: Single canonical scene identity surface across AI guidance and runtime commit

## Status

Accepted

## Context

Scene identifiers travel across authored content, AI guidance, and runtime-side commit behavior.
If more than one scene-identity vocabulary or remapping layer silently appears, the vertical slice can drift even when individual files still look plausible.

## Decision

1. ADR-0001 remains the **sole normative owner** of runtime authority.
2. ADR-0003 does **not** define runtime authority. It defines the narrower **canonical scene identity surface** and **scene-identity continuity rules** for the current GoC slice under the ADR-0001 authority model.
3. Maintain a **single owned scene-identity mapping surface** for the current GoC slice.
4. In the lean v24 package, the canonical mapping surface is the mapping logic inside `ai_stack/goc_scene_identity.py`, which is consumed by runtime-adjacent GoC YAML authority and guidance code such as `ai_stack/goc_yaml_authority.py` and `ai_stack/scene_director_goc.py`.
5. No second local scene-id remap should be introduced in downstream consumers without an explicit decision record.
6. Changes to the GoC scene-identity mapping must be accompanied by matching validation updates in the same change set.

## Runtime-critical implementation surfaces

- `ai_stack/goc_scene_identity.py`
- `ai_stack/goc_yaml_authority.py`
- `ai_stack/scene_director_goc.py`
- `content/modules/god_of_carnage/`

## Validation anchors

- `ai_stack/tests/test_goc_scene_identity.py`
- `ai_stack/tests/test_semantic_planner_contracts.py`
- `ai_stack/tests/test_goc_runtime_breadth_continuity_diagnostics.py`
- `backend/tests/content/test_god_of_carnage.py`

## Related

- [Vertical slice contract (GoC)](../MVPs/MVP_VSL_And_GoC_Contracts/VERTICAL_SLICE_CONTRACT_GOC.md)
- [Canonical turn contract (GoC)](../MVPs/MVP_VSL_And_GoC_Contracts/CANONICAL_TURN_CONTRACT_GOC.md)
- [God of Carnage module contract](../technical/architecture/god_of_carnage_module_contract.md)
- [Normative contracts index](../dev/contracts/normative-contracts-index.md)
