# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 4 (committing) → W5 next
Aktueller Schritt: Wave 4 D26 models + E7 policies + capability switches landed
Letzter grüner Commit: `fc362157` (W3); W4 commit pending on `drift-sanierung/w4-capability-migration`
Baseline-Testlauf: W4 unit **10 passed** (`test_state_delta_*`, switches, E7 chain)

## Wellen
- [x] W0 Kostenwahrheit
- [x] W1 Entshardung Autoritätspfad
- [x] W2 Schreibtopologie
- [x] W3 Commit-Vokabular
- [x] W4 Fähigkeitsmigration (models + switches + E7 policies; shard self-correction edit deferred)
- [ ] W5 Entshardung Rest
- [ ] W6 Paketnamen + Retirement
- [ ] W7 Content-Wahrheit
- [ ] W8 Test-/CI-/Gate-Wahrheit
- [ ] W9 Werkzeugplattform + Hygiene

## Entscheidungen, die ich selbst getroffen habe
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 3 | Off-map / missing hints | `partial` + allowed | E9 |
| 2026-07-31 | 3 | AI shard commit rename | Defer to W5 | SOURCE_LINES blast radius |
| 2026-07-31 | 4 | MutationPolicy stance | Permissive forbid-list (not backend deny-by-default) | E9; do not copy dormant policy |
| 2026-07-31 | 4 | Capability switch defaults | All five ON | E5 — gap was absence, not proven intentional disable |
| 2026-07-31 | 4 | Self-correction shard E7 edit | Park to W5 | File is mid-class SOURCE_LINES chunk; unshard tool is manager-specific |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Vorgeschlagene Auflösung |
| --- | --- | --- | --- | --- |
| P-MCP-1 | * | claude-context MCP error | search_code unavailable | Retry / reindex |
| P-LANGFUSE-FLUSH | 3 | Manager tests hang on Langfuse flush | Local DNS/host | Disable Langfuse in test env |
| P-W3-AI-RENAME | 3 | ai_stack commit vocabulary rename | Shards | W5 |
| P-W4-SHARD-E7 | 4 | Growing retry prompt still in `executor_generation_self_correction.py` SOURCE_LINES | Cannot safely patch mid-class shard | Unshard in W5 then shrink retry prompt |
| P-G4-ASSURANCE | * | User WIP under architecture_assurance | G4 | Leave unstaged |

## Journal
- 2026-07-31 W3 commit `fc362157` on `drift-sanierung/w3-commit-vocabulary`.
- 2026-07-31 W4: added `state_deltas`, `mutation_policy`, `source_gate`, `scene_legality`, `failure_recovery`, `delta_evaluation`; commit record v5 fields; five switches; tests 10 passed.
- Next: Wave 5 unshard ai_stack + backend game API; then W6+.
