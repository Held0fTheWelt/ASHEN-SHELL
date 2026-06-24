# world-engine Mechanism Catalog

**Owner:** [world-engine SAD](architecture.md)
**Status:** mixed mechanism catalog; runtime authority and turn execution surfaces implemented
**Last reconciled:** 2026-06-23

| ID | Mechanism | Definition | Normative sources | UML / evidence | Proof state |
| --- | --- | --- | --- | --- | --- |
| WE-M01 | Runtime authority | world-engine owns authoritative live session state, turn count, and committed consequences. | [SAD D1](architecture.md#d1-runtime-authority-in-world-engine) | [C4 context](../../../../UML/Components/world-engine/components/c4-context.md), [d1 decision](../../../../UML/Components/world-engine/decisions/d1-runtime-authority.md) | Implemented |
| WE-M02 | Proposal-only AI ingress | Model output is proposal until validator approval; failed validation leaves committed state unchanged. | [SAD D2](architecture.md#d2-runtime-model-output-is-proposal-only-until-validator-approval) | [primary sequence](../../../../UML/Components/world-engine/sequence/world-engine-primary-turn-sequence.md) | Implemented |
| WE-M03 | Live commit semantics | Real, mock, and fallback adapters mark `live_success` honestly without writing false canon. | [SAD D3](architecture.md#d3-live-runtime-commit-semantics-for-real-ai-mock-fallback-and-visible-story-output) | [degraded sequence](../../../../UML/Components/world-engine/sequence/world-engine-degraded-turn-sequence.md) | Implemented |
| WE-M04 | Director thin path | Default player turns route resolver → Director → narrator realization without heavyweight graph detours. | [SAD D4](architecture.md#d4-director-realization-thin-path-resolver-director-narrator) | [d4 decision](../../../../UML/Components/world-engine/decisions/d4-director-thin-path.md) | Implemented |
| WE-M05 | Canonical turn lifecycle | Single commit / persist / project path with explicit turn envelope and phased rollout. | [SAD D5](architecture.md#d5-canonical-turn-lifecycle-and-single-commit-persist-project-path) | [d5 decision](../../../../UML/Components/world-engine/decisions/d5-canonical-turn-lifecycle.md) | Implemented |
| WE-M06 | Scene identity surface | Scene identity stays compatible across compile, AI guidance, and commit records. | [SAD D7](architecture.md#d7-scene-identity-compatibility-surface-across-compile-ai-guidance-and-commit) | [session states](../../../../UML/Components/world-engine/states/world-engine-story-session-states.md) | Implemented |
| WE-M07 | Configurable validation | Validation strategy is explicit, configurable, and observable per turn class. | [SAD D11](architecture.md#d11-validation-strategy-must-be-explicit-and-configurable) | [evidence matrix](evidence-matrix.md) | Partial |
| WE-M08 | Preview session isolation | Preview sessions cannot mutate or leak into active runtime stores. | [SAD D12](architecture.md#d12-preview-sessions-must-be-isolated-from-active-runtime) | [evidence matrix](evidence-matrix.md) | Implemented |
| WE-M09 | Opening economy | Story opening uses bounded warmup and phase-aligned economy defaults. | [SAD D13](architecture.md#d13-story-opening-economy-warmup-and-phase-alignment) | [evidence matrix](evidence-matrix.md) | Partial |
| WE-M10 | Semantic input ingress | Player input translation produces bounded semantic evidence before runtime guards. | [SAD D14](architecture.md#d14-semantic-player-input-translation-ingress) | [d14 decision](../../../../UML/Components/world-engine/decisions/d14-semantic-input-ingress.md) | Implemented |
| WE-M11 | W5 actor tracking | Actor locations and participation projections feed narrator and director surfaces. | [SAD D6](architecture.md#d6-w5-actor-tracking) | [d6 decision](../../../../UML/Components/world-engine/decisions/d6-w5-actor-tracking.md) | Partial |
| WE-M12 | W5 narrator strict mode | Actor-situation surface defaults to strict narrator mode after W5 framing. | [SAD D15](architecture.md#d15-w5-narrator-strict-mode-becomes-the-default-actor-situation-surface) | [evidence matrix](evidence-matrix.md) | Proposed |
| WE-M13 | Legacy area field retirement | Legacy narrator consequence `area` fields retire after W5 location framing lands. | [SAD D16](architecture.md#d16-retire-legacy-narrator-consequence-area-fields-after-w5-location-framing) | [evidence matrix](evidence-matrix.md) | Proposed |

## WE-M01

## WE-M02

## WE-M03

## WE-M04

## WE-M05

## WE-M06

## WE-M07

## WE-M08

## WE-M09

## WE-M10

## WE-M11

## WE-M12

## WE-M13
