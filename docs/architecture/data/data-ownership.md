# Data ownership and authoritative writers

This matrix separates current storage mechanisms from normative authority. Multiple resources may
exist legitimately; overlapping writers for the same truth may not.

| Resource | Normative owner | Authoritative writer / sink | Readers | Consistency | Current posture |
| --- | --- | --- | --- | --- | --- |
| Live story session | World Engine | `StoryRuntimeManager._persist_session` → `JsonStorySessionStore.save` | World Engine, bounded diagnostics | monotonic revision, serialized mutation | Conforming, guard against compatibility writers |
| Live run instance | World Engine runtime adapter | `RuntimeManager.store.save` | backend launch/proxy, diagnostics | run metadata, not story revision | Separate resource; distinction must remain explicit |
| Branching tree | World Engine | `_persist_branching_tree_record` | turn planning and diagnostics | replace by session/version | Needs envelope correspondence proof |
| Branch timeline | World Engine | `_persist_branch_timeline_record` | runtime projection | replace by session/version | Needs envelope correspondence proof |
| Callback web | World Engine | `_persist_callback_web_record` | planner/runtime | post-commit derived record | Must not become second story truth |
| Consequence cascade | World Engine | `_persist_consequence_cascade_record` | planner/runtime | post-commit derived record | Must not become second story truth |
| Authored module | Content Authority | reviewed YAML publication | compiler and authoring tools | immutable versioned source | Normative source |
| Compiled content projection | Content compiler boundary | deterministic compiler output | World Engine and AI adapters | content-version bound | Nonconforming multiplicity; `AR-V003` |
| Platform identity/account | Backend | backend repositories/database | frontend, administration tool | transactional platform data | Outside live-story authority |
| Governed runtime settings | Backend control plane | settings service/repository | runtime adapters | audited versioned mutation | Must not mutate session truth directly |
| Player-visible envelope | World Engine projection | post-commit projection builder | backend transport, frontend renderer | ordered, versioned immutable delivery | Partial; `AR-V004` |
| Turn trace | Distributed, contract owned | service-local adapters | operators and evaluators | propagated identity, explicit gaps | Partial; `AR-V006` |

## Writer invariant

For each authoritative resource, the architecture model declares one logical writer. Helper methods
and adapters may participate in that writer path but may not create an alternative commit decision.
Architecture assurance must detect new sink callsites and require either ownership mapping or a
violation entry.
