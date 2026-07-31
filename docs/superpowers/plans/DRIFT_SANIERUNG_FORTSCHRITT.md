# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 3 (ready to commit) → starting 4
Aktueller Schritt: Wave 3 commit vocabulary complete; Wave 4 capability migration next
Letzter grüner Commit: `5122b1d4` on `drift-sanierung/w2-write-topology` (W3 pending commit on `drift-sanierung/w3-commit-vocabulary`)
Baseline-Testlauf: W3 unit bundle 7 passed (`test_partial_action_commit`, `test_blocked_is_rare`, beat carry-forward); narrative_commit 13 passed before concurrent/Langfuse flush hang (env)

## Wellen
- [x] W0 Kostenwahrheit (W0-A A16/A17; W0-B done; W0-C ledger→Langfuse after W1 unshard)
- [x] W1 Entshardung Autoritätspfad (world-engine manager SOURCE/exec removed)
- [x] W2 Schreibtopologie (PersistOutcome, revision, 7-resource gate, play_run bypass, translation cache, D18)
- [x] W3 Commit-Vokabular (SituationStatus + partial off-map; mapping table; beat reasons)
- [ ] W4 Fähigkeitsmigration
- [ ] W5 Entshardung Rest
- [ ] W6 Paketnamen + Retirement
- [ ] W7 Content-Wahrheit
- [ ] W8 Test-/CI-/Gate-Wahrheit
- [ ] W9 Werkzeugplattform + Hygiene

## Messergebnisse aus Welle 0
Aus W0-A (Langfuse-Historie):
- Verwertbare Historie vorhanden? (ja/nein, Trace-Anzahl, Zeitraum): **nein** — health OK (`3.174.1`), traces API **401** with current `.env` keys (A17 key/project mismatch). See `baselines/W0A-langfuse-historie.md`.
- Promptgröße pro Zug (Median / p95): unavailable (no auth)
- Tokenverbrauch, Latenz, Tokens/s (final generation): unavailable
- Adapter- und Invocation-Mode-Verteilung: unavailable

Aus W0-B (Instrumentierung):
- Modellaufrufe pro Zug (Median / p95): pending reference playthrough after ledger wiring
- Kostenanteil Übersetzung: pending reference playthrough
- Häufigkeit `blocked` im Beispielspielverlauf: pending (W3 unit: blocked only for unknown_target_scene)

Abgleich:
- Differenz zwischen Langfuse-Sicht (max. 2/Zug) und gemessener Aufrufzahl: history unusable; ledger is source of truth going forward

## Entscheidungen, die ich selbst getroffen habe
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 0 | Soft/hard budget defaults | soft=12, hard=24 | A10 — generous until W0 playthrough measures exist |
| 2026-07-31 | 0 | Phase attribution without shard edits | contextvars + stack-frame hints for known executor methods | Avoid editing SOURCE shards in W0; unattributed remains visible |
| 2026-07-31 | 0 | W0-C timing | Defer Langfuse per-call emission until W1 unshards emitter | Explicitly allowed by runway |
| 2026-07-31 | 0 | quality_class delivery | Confirmed already present in story_window_entry_parts; add contract tests | Code wins over analysis (A14) — collapse already fixed at delivery |
| 2026-07-31 | 2 | Backend write sink naming | `backend:database` for `backend_runtime_session` | Matches existing catalog sink vocabulary |
| 2026-07-31 | 3 | Off-map / missing hints | `partial` + `allowed=True`, not `blocked` | E9 / D31 — free RP over transition-card absolutism |
| 2026-07-31 | 3 | `unknown_target_scene` | Remains `blocked` | Situatively impossible (scene not in projection) |
| 2026-07-31 | 3 | Beat on partial/prevented/offscreen | `advanced=True` with differentiated reasons | Exit criterion: free action lets beat progress |
| 2026-07-31 | 3 | AI→Situation mapping | Explicit table; never poorer than AI status | Wave 3 contract tests |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Vorgeschlagene Auflösung |
| --- | --- | --- | --- | --- |
| P-MCP-1 | 0+ | claude-context MCP error / not connected | Cannot use mandated search_code | Retry when MCP recovers; used plan anchors + targeted reads |
| P-W0A-1 | 0 | Langfuse API 401 with local keys | Interactive project/key bootstrap needed | Operator sets keys in local `.env`; re-run W0-A query |
| P-W0-BASE | 0 | Full world-engine baseline hung/interrupted ~48% | Time box; A4 pre-existing reds | Re-run full suite after W1; compare failure set |
| P-LANGFUSE-FLUSH | 3 | Manager integration tests hang on Langfuse OTEL flush / DNS | Local env points at unreachable host | Disable Langfuse in test env or mock adapter flush; not a W3 logic failure |
| P-W3-AI-RENAME | 3 | Full `commit_*` → `proposal_*` rename in ai_stack shards | Shards; large blast radius; W5 unshards | Partial deferral: mapping + WE vocabulary done; shard rename with W5 |
| P-G4-ASSURANCE | * | User WIP under tools/architecture_assurance + UML | G4 — do not overwrite | Leave unstaged; only touch plan-required catalog/edges when needed |

## Journal
- 2026-07-31: Branch `drift-sanierung/w0-cost-truth` from `f06308d1`. User WIP preserved (G4).
- 2026-07-31 W0–W2: see prior commits `3e4b02cb` → `7959c848` → `6f6015f6` → `5122b1d4`.
- 2026-07-31 W3: Extended `SituationStatus`; `eval_core_transition_rules` → partial for off-map / missing hints; beat reasons; `situation_status_mapping.py`; tests; SAD §4.2.
- 2026-07-31: Next = Wave 4 capability switches + state deltas + E7 failure chain (permissive MutationPolicy per E9, not backend deny-by-default copy).
