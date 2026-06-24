# D4: Language adapter compatibility seam

**Owner SAD:** [story-runtime-core SAD](../../../../docs/architecture/components/story-runtime-core/architecture.md#d2-language-adapter-compatibility-seam)
**Origin:** ADR-0037-CONTENT (compat layer)
**Status:** Accepted

## Context

Canonical language I/O lives in `ai_stack.language_io.language_adapter`. Legacy
imports still resolve through `story_runtime_core.language_adapter` during the
W5 migration window.

## Decision

`story_runtime_core.language_adapter` is a re-export only. Semantic catalog
construction, `prepare_player_input_semantic_resolution`, and
`load_session_language_model_directive` execute in `ai_stack.language_io`.

`story_runtime_core.player_input_intent_contract` remains the shared taxonomy
imported by the AI-stack adapter (no circular authority in shared core).

## Consequences

- Importing `story_runtime_core` for language helpers pulls `ai_stack` at runtime.
- `pyproject.toml` does not declare `ai_stack` as a dependency (packaging gap).
- Live turn graph language ingress is owned by world-engine / ai_stack LangGraph
  executor, not this package.

## Evidence

| Kind | Link |
| --- | --- |
| Shim | `story_runtime_core/language_adapter.py` |
| Canonical | `ai_stack/language_io/language_adapter.py` |
| Contract | `story_runtime_core/player_input_intent_contract.py` |
| Sequence | [language-resolution-chain](../sequence/language-resolution-chain.md) |
