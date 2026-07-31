# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 2 (partial)
Aktueller Schritt: PersistOutcome + revision landed; write-surface resource model still open
Letzter grüner Commit: `7959c848` on `drift-sanierung/w1-unshard-authority` (W0 also `3e4b02cb`)
Baseline-Testlauf: `docs/superpowers/plans/baselines/W0-vorher.txt` (partial — interrupted ~48%; focused W0/W1/W2 tests green)

## Wellen
- [x] W0 Kostenwahrheit (W0-A A16/A17; W0-B done; W0-C ledger→Langfuse after W1 unshard)
- [x] W1 Entshardung Autoritätspfad (world-engine manager SOURCE/exec removed)
- [ ] W2 Schreibtopologie (PersistOutcome + revision started; gate/resources incomplete)
- [ ] W3 Commit-Vokabular
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
- Häufigkeit `blocked` im Beispielspielverlauf: pending (W3-relevant)

Abgleich:
- Differenz zwischen Langfuse-Sicht (max. 2/Zug) und gemessener Aufrufzahl: history unusable; ledger is source of truth going forward

## Entscheidungen, die ich selbst getroffen habe
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 0 | Soft/hard budget defaults | soft=12, hard=24 | A10 — generous until W0 playthrough measures exist |
| 2026-07-31 | 0 | Phase attribution without shard edits | contextvars + stack-frame hints for known executor methods | Avoid editing SOURCE shards in W0; unattributed remains visible |
| 2026-07-31 | 0 | W0-C timing | Defer Langfuse per-call emission until W1 unshards emitter | Explicitly allowed by runway |
| 2026-07-31 | 0 | quality_class delivery | Confirmed already present in story_window_entry_parts; add contract tests | Code wins over analysis (A14) — collapse already fixed at delivery |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Vorgeschlagene Auflösung |
| --- | --- | --- | --- | --- |
| P-MCP-1 | 0 | claude-context MCP `Not connected` | Cannot use mandated search_code | Retry when MCP recovers; used plan anchors + targeted reads |
| P-W0A-1 | 0 | Langfuse API 401 with local keys | Interactive project/key bootstrap needed | Operator sets keys in local `.env`; re-run W0-A query |
| P-W0C-1 | 0 | Per-call Langfuse observations | Emitter still in shards | Complete in W1 then finish W0-C |
| P-W0-BASE | 0 | Full world-engine baseline hung/interrupted ~48% | Time box; A4 pre-existing reds | Re-run full suite after W1; compare failure set |
| P-ENV-RESTORE | 0 | Brief accidental wipe of catalog envelopes during edge append | Restored from UML markdown + earlier read proofs | Verified via `test_drift_edges.py` 6/6 |

## Journal
- 2026-07-31: Branch `drift-sanierung/w0-cost-truth` from `f06308d1`. User WIP preserved (G4).
- 2026-07-31 W0-A: `langfuse-up` OK; history unusable (401) → A16/A17; wrote `W0A-langfuse-historie.md`.
- 2026-07-31 W0-B: Added `story_runtime_core/model_call_accounting.py`, wrapped governed adapters, extended `aggregate_phase_costs`, soft/hard budgets in `runtime_config`, ledger bind in `turn_execution`, tests 9 passed.
- 2026-07-31: Drift edges `model-call-to-cost-ledger` + `ledger-to-langfuse-observation` + `turn-cost-envelope-v1`; UML `turn-cost-ledger.puml`; observability SAD note. `test_drift_edges.py` 6 passed.
