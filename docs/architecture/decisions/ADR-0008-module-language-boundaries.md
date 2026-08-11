# ADR-0008 — Module-owned semantic and output language boundaries

**Decision status:** Accepted
**Implementation state:** Implemented; live replay proof gap
**Owners:** AI Stack, Content Authority
**Date:** 2026-08-11
**Violations:** `AR-V011`

## Context

The language adapter promised semantic translation without phrase maps, but hard-coded English as
the internal and authored language. The output gateway then assumed every visible text originated
in English and skipped translation whenever the target was English. This works accidentally for an
English-authored module, but it is wrong for non-English modules and for already localized blocks.

## Decision drivers

- modules may be authored in any declared language;
- semantic normalization and visible translation occur only when source and target differ;
- translation must preserve structured block identity and actor attribution;
- no locale phrase, verb, actor or target maps may enter engine code;
- language provenance must be observable and replayable.

## Decision

Every module declares `authoring_language`, `internal_resolution_language` and
`default_session_output_language`. Input is normalized from `session_input_language` to the
declared internal language before grounding only when those languages differ. Visible output is
translated from its declared `source_language` to `session_output_language` only when those
languages differ.

The primary semantic field is `normalized_internal_text`. `normalized_english_text` remains a
temporary compatibility alias only when the declared internal language is English. Output
translation operates on typed visible fields and records source/target provenance; it must not
flatten or reclassify blocks.

## Consequences

English is a valid module choice, not an engine invariant. The English-named input field remains a
schema compatibility alias, not a downstream semantic dependency. Missing source language is
interpreted from the module policy and reported as compatibility behavior, never from the target
language.

## Implementation correspondence

| Target element | Current evidence | State | Closure evidence |
| --- | --- | --- | --- |
| Module declaration | `content/modules/god_of_carnage/module.yaml#language` | Conforming | loader test |
| Neutral ingress contract | `language_io/language_adapter.py::build_semantic_resolution_contract` | Conforming | contract test |
| Runtime source-aware ingress | `langgraph_runtime_executor_impl.py::_translate_player_input` | Conforming | same/different internal-language tests |
| Neutral internal consumers | interpretation, retrieval and realization in `langgraph_runtime_executor_impl.py` | Conforming | non-English consumer-path tests |
| Runtime source-aware egress | `langgraph_runtime_executor_impl.py::_translate_output` | Conforming | non-English-source-to-English test |
| Neutral action frame | `contracts/action_resolution_contracts.py::PlayerActionFrameContract` | Conforming | neutral precedence and English-compatibility tests |
| Persisted graph-to-engine replay | full runtime fixture | Proof gap | non-English module replay test |

## Git and AKDB lineage

Retired decisions ADR-0037, ADR-0054 and ADR-0055 captured the intended module-language-first
boundary. Their intent was not fully implemented. This active ADR consolidates the target and
keeps the incompatible English assumptions visible through `AR-V011` until migration is complete.
