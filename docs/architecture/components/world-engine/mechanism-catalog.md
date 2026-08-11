# World Engine mechanism catalog

**Owner:** [World Engine SAD](architecture.md) · **Reconciled commit:** `a1b5db907b0484f8898f5caf3fdc57edd6efb46c`

This catalog maps design mechanisms to the canonical source/model and records whether the current implementation conforms. Historical mechanisms that no longer belong in the target architecture remain discoverable through Git and the retired ADR archive, not as empty active headings.

| ID | Mechanism | Canonical evidence | Current posture | Repair reference |
| --- | --- | --- | --- | --- |
| WE-M01 | Single live commit authority | [SAD D1](architecture.md#d1-world-engine-owns-live-story-commit-authority), [ADR-0001](../../decisions/ADR-0001-single-live-story-commit-authority.md) | Partial | [AR-V001](../../violations/README.md#ar-v001-proposal-finalization-resembles-a-second-commit) |
| WE-M02 | Proposal-only AI boundary | [SAD D2](architecture.md#d2-ai-results-remain-proposals-until-world-engine-accepts-them), [primary sequence](../../../../UML/Components/world-engine/sequence/primary-turn-sequence.md) | Partial | AR-V001 |
| WE-M03 | Revision-bound turn envelope | [SAD §8](architecture.md#turn-envelope), [ADR-0002](../../decisions/ADR-0002-versioned-turn-envelope.md) | Target | AR-V002 |
| WE-M04 | Canonical lifecycle | [SAD D5](architecture.md#d5-one-canonical-lifecycle-and-one-persistence-edge), [turn activity](../../../../UML/Components/world-engine/activity/canonical-turn-activity.md) | Partial | AR-V005 |
| WE-M05 | Atomic persist then project | [primary sequence](../../../../UML/Components/world-engine/sequence/primary-turn-sequence.md), [`story_session_store.py`](../../../../world-engine/world_engine/story_runtime/story_session_store.py) | Partial | AR-V002, AR-V005 |
| WE-M06 | No-write degraded path | [degraded sequence](../../../../UML/Components/world-engine/sequence/degraded-turn-sequence.md) | Normative model; production proof incomplete | AR-V002 |
| WE-M07 | Session lifecycle | [session lifecycle](../../../../UML/Components/world-engine/states/session-lifecycle.md) | Implemented with compatibility residue | AR-V005 |
| WE-M08 | Cross-service turn trace | [ADR-0005](../../decisions/ADR-0005-cross-service-turn-trace.md) | Partial | AR-V006 |
| WE-M09 | Typed player-visible projection | [ADR-0004](../../decisions/ADR-0004-player-visible-block-envelope.md) | Partial | AR-V004 |
| WE-M10 | Semantic input ingress | [SAD D14](architecture.md#d14-semantic-player-input-enters-once), [D14 model](../../../../UML/Components/world-engine/decisions/d14-semantic-input-ingress.md) | Partial | AR-V002 |
| WE-M11 | Actor/situation changes as committed data | [SAD D6](architecture.md#d6-actor-and-situation-changes-are-committed-data), [D6 model](../../../../UML/Components/world-engine/decisions/d6-w5-actor-tracking.md) | Partial | AR-V005 |

`Partial` means that source evidence exists but one or more normative invariants are not yet proven end to end. It must not be reported as architectural conformance.
