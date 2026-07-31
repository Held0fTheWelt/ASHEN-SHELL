# Better Tomorrow — Drift-Sanierung: Gesamtplan bis Definition of Done

> **Für ausführende Agenten:** ERFORDERLICHE SUB-SKILL: `superpowers:subagent-driven-development` (empfohlen)
> oder `superpowers:executing-plans`. Schritte nutzen Checkbox-Syntax (`- [ ]`).

**Ziel:** Genau eine nachweisbare Autorität für Live-Session-Zustand, ein Commit-Vokabular, das freies Rollenspiel
tatsächlich trägt, messbare und begrenzte Kosten pro Zug — und ein Repository, in dem statische Aussagen wieder
beweiskräftig sind.

**Architektur:** Die World-Engine bleibt Heimat der Live-Autorität. Sie erhält zuerst Messbarkeit, dann ein
reiches Commit-Vokabular, dann die fehlenden Zustands-Governance-Modelle aus der ruhenden Backend-Generation.
Parallelwelten werden erst entfernt, nachdem ihre Fähigkeiten migriert sind. Produktionscode wird von
String-Shards zu echtem Python zurückgebaut, bevor Umbenennungen stattfinden.

**Tech-Stack:** Python 3.14 · FastAPI (world-engine) · Flask (backend) · LangGraph/LangChain · Langfuse ·
pytest · PlantUML · `tools/architecture_assurance` (Gates)

**Grundlage:** [`2026-07-31-better-tomorrow-drift-landscape-analysis.md`](2026-07-31-better-tomorrow-drift-landscape-analysis.md)

---

## Getroffene Entscheidungen (verbindlich für alle Wellen)

| # | Entscheidung | Konsequenz |
| --- | --- | --- |
| E1 | World-Engine bleibt Heimat der Live-Autorität; Fähigkeiten aus D26 werden dorthin migriert, **bevor** der ruhende Backend-Teil fällt | Welle 4 vor Welle 6 |
| E2 | String-Shard-Rückbau **vollständig** (202 Module), gestaffelt nach Autoritätsnähe | Welle 1 → 5 → 9 |
| E3 | `'fy'-suites` wird in ein eigenes Repository herausgelöst | Welle 9 |
| E4 | `world-engine/app` → `world_engine` umbenennen | Welle 6, **nach** vollständiger Entshardung |
| E5 | Absicht früherer Abschaltungen ist **nicht** rekonstruierbar → jede migrierte Fähigkeit erhält einen **ausdrücklichen Schalter mit dokumentierter Standardstellung** | Welle 4 |
| E6 | Interne Auflösungssprache bleibt Englisch, aber: eigene Routing-Task-Klasse `translation` auf günstiges Modell, harte Kostengrenze, Ergebnis-Cache pro Zug, volle Kostenattribution | Welle 0 + Welle 2 |
| E7 | Bei technischem Versagen: **erst** ein günstiger Wiederholungsversuch mit **reduziertem** Kontext, **dann** ein deterministischer Weiterspiel-Zug | Welle 4 |
| E8 | Zugbudget ist **weich**: messen und warnen; nur eine deutlich höhere harte Obergrenze bricht ab | Welle 0 |
| E9 | Freies Rollenspiel hat Vorrang: `blocked` ist reserviert für situativ tatsächlich Unmögliches | Welle 3 |

---

## Global Constraints

- **Python:** `>=3.14,<3.15` (`.python-version`, alle Workflows). Keine Rückportierung auf 3.10.
- **Keine neue Kompatibilitätsschicht.** Wenn eine Übergangsfassade unvermeidbar ist, braucht sie: benannten
  Besitzer, eng begrenzten Zweck, Nutzungsmessung, Ablaufkriterium, Removal-Ticket und einen Test, der verhindert,
  dass sie Autorität übernimmt.
- **Cleaning gehört in die Welle**, nicht in eine unbestimmte Schlussaktion.
- **`E:\New folder` ist read-only Archäologie.** Kein Build-, Import-, Test- oder Laufzeitpfad darf darauf zeigen.
- **Uncommittete Benutzeränderungen** (Stand `f06308d1`: 21 modifiziert, 4 unversioniert im Umfeld
  `tools/architecture_assurance`, `UML/Project/architecture-drift`) gehören dem Benutzer. Vor Wellenbeginn
  `git status` prüfen; nichts überschreiben, was nicht eindeutig zum Auftrag gehört.
- **Explizite Pfade beim Stagen.** Niemals `git add -A`. Vor jedem Commit `.git/index.lock` prüfen.
- **Jede Welle endet grün:** volle Testsuite der betroffenen Komponenten plus
  `python -m tools.architecture_assurance audit`.
- **Keine Statusbehauptung ohne Produktionspfad-Evidenz.** Dateipräsenz, Dateiname und ein grüner Altbericht
  gelten nicht als Beweis.

---

## Wellenübersicht

| Welle | Ziel | Drifts | Abhängig von |
| ---: | --- | --- | --- |
| 0 | Kostenwahrheit und Beobachtbarkeit an der Adapter-Naht | D27, D30, D29 (Messteil) | – |
| 1 | Entshardung des Autoritätspfads (world-engine Manager) | D15 (Teil 1), DRIFT-006 | 0 |
| 2 | Eine Schreibtopologie, eine Persistenz-Transaktion | D16, D17, D18, DRIFT-001 (Teil 1) | 1 |
| 3 | Reiches Commit-Vokabular für freies Rollenspiel | D31, DRIFT-002, DRIFT-005 | 2 |
| 4 | Fähigkeitsmigration + Fehlerverhalten | D26, D29 (Verhaltensteil), DRIFT-003 | 3 |
| 5 | Entshardung ai_stack + Backend-Game-API | D15 (Teil 2+3) | 4 |
| 6 | Paketnamen entkoppeln, Parallelwelten retiren | D14, D13, D21, DRIFT-001 (Rest) | 5 |
| 7 | Content-Wahrheit vereinheitlichen | DRIFT-004, D23 | 6 |
| 8 | Test-, CI- und Gate-Wahrheit | D19, D20, D25, DRIFT-007/008/009/012 | 6 |
| 9 | Werkzeugplattform herauslösen, Baum bereinigen | D22, D24, D15 (Rest `tools/`) | 8 |

**Reihenfolgeprinzip:** Messbarkeit → Beweisbarkeit → Autorität → Fachlichkeit → Struktur → Kosmetik.
Autoritäts- und Transaktionsgrenzen (Wellen 2–4) liegen vor allen Umbenennungen (Welle 6).

---

## Welle 0 — Kostenwahrheit und Beobachtbarkeit

**Ziel und Architekturentscheidung**
Jeder Modellaufruf wird kostenattribuiert — **an der Adapter-Naht, nicht an den Aufrufstellen**. Das ist die
Schlüsselentscheidung dieser Welle: die Aufrufstellen liegen sämtlich in String-Shards
(`executor_model_routing_invocation.py`, `executor_model_fallback.py`, `executor_output_translation.py`,
`executor_translation_adapter.py`, `executor_generation_self_correction.py`). Ein Zähl-Dekorator um den Adapter
erfasst sie alle, ohne einen einzigen Shard anzufassen. Damit ist Welle 0 vollständig unabhängig von Welle 1.

Die Welle zerfällt in drei Teile: **W0-A** wertet vorhandene Langfuse-Historie aus (kein Code), **W0-B** baut das
Ledger, **W0-C** führt Trace und Kostenbericht auf dieselbe Wahrheit zusammen.

**Enthaltene Drifts:** D27 (Kostenblindheit), D30 (degraded/failed ununterscheidbar), D29 (Messteil), D28 (Messteil)

**Voraussetzungen:** keine.

---

### W0-A — Langfuse-Archäologie (kein Code, zuerst)

Es existiert eine vollständige, self-hosted Langfuse-Umgebung mit **persistenten Volumes**
(`docker-compose.langfuse.yml:205-213`: `langfuse-postgres-data`, `langfuse-clickhouse-data`,
`langfuse-minio-data`, `langfuse-redis-data`, alle `driver: local`). Historische Traces früherer Spielsitzungen
sind daher vermutlich vorhanden. Start: `python docker-up.py langfuse-up`.

**Was die Historie liefern kann** (`LANGFUSE_CAPTURE_PROMPTS: true`, Prompt bis 20 000 Zeichen gespeichert):

| Messgröße | Quelle | Wert für den Plan |
| --- | --- | --- |
| Reale Zugzahl und Sitzungsverläufe | Trace-Namen `world-engine.turn.execute`, `world-engine.session.create` | Stichprobengröße |
| **Promptgröße pro Zug** | `prompt`-Feld der Observation `story.model.generation` | **Beziffert den Kontext-Bloat direkt, ohne Codeänderung** |
| Tokenverbrauch, Latenz, Tokens/s, Time-to-first-token | `usage_details`, `latency_ms`, `tokens_per_second`, `time_to_first_token_ms` | Kostenbasis je Generierung |
| Adapterverteilung, Invocation-Mode | Metadaten `adapter`, `primary_attempt_adapter`, `primary_attempt_invocation_mode` | Anteil Mock-/Fallback-/Degraded-Pfade |
| Turn-Art und Turn-Nummer | `turn_kind`, `turn_number`, `opening_turn` | Opening vs. laufender Zug |

**Was die Historie ausdrücklich NICHT liefern kann — und warum:**
`_emit_langfuse_evidence_observations_000.py:96-98` ruft `adapter.record_generation(name="story.model.generation", …)`
**einmal pro Zug**, rekonstruiert aus `path_summary`, gesteuert über
`record_final_generation or record_primary_attempt_generation` und markiert per Metadatum
`generation_observation_source: "primary_attempt" | "final"`.
Langfuse sieht also **höchstens zwei** Generierungen pro Zug. Übersetzung (2 Aufrufe), Self-Correction (bis 3)
und Fallback sind **auch in Langfuse unsichtbar** — dieselbe strukturelle Blindstelle wie bei `phase_costs`,
aus demselben Grund: beide werden aus `path_summary` gespeist.

**Konsequenz:** Die Zahl „Modellaufrufe pro Zug" ist aus der Historie **nicht** ableitbar und bleibt Aufgabe von
W0-B. Die Zahl „Promptgröße" und die Verteilung der Adapter-/Degradationspfade sind es sehr wohl.

**Abfragewerkzeug:** `tools/mcp_server/handlers/langfuse_verify/` (47 Dateien) enthält bereits einen
programmatischen Trace-Query-Pfad (`31_langfuse_trace_query.py`, `23_handler_trace_fetch_and_query.py`,
`20_runtime_matrix_query_client.py`, `43_handler_runtime_summary_views.py`). **Achtung:** Diese Dateien sind
selbst nummerierte Shards mit `loader.py:64` `exec(compiled, namespace)` — sie gehören zu D15 und werden erst in
Welle 9 zurückgebaut. Für W0-A werden sie **benutzt, nicht umgebaut**.

**Schritte**
- [ ] `python docker-up.py langfuse-up`; Erreichbarkeit und Datenbestand prüfen.
- [ ] Prüfen, ob die Volumes Daten enthalten (Trace-Anzahl, ältester und jüngster Trace).
- [ ] Über den vorhandenen Query-Pfad auswerten: Zugzahl, Promptgrößen-Verteilung (Median/p95),
      Tokenverbrauch, Latenz, Adapter- und Invocation-Mode-Verteilung, Anteil `opening_turn`.
- [ ] Ergebnis als `docs/superpowers/plans/baselines/W0A-langfuse-historie.md` ablegen und ins
      Fortschrittsprotokoll übernehmen.
- [ ] **Ausdrücklich festhalten**, welche Messgrößen die Historie nicht liefert (Aufrufzahl pro Zug).

**Exit-Kriterium W0-A:** Promptgrößen-Verteilung und Adapterverteilung liegen belegt vor, oder es ist belegt,
dass keine verwertbare Historie existiert (siehe Ausweichstrategie A15 im Cursor-Auftrag).

**Betroffene Dateien**
- Neu: `story_runtime_core/model_call_accounting.py` — `CountingModelAdapter`-Wrapper + `TurnCallLedger`
- Ändern: `world-engine/app/story_runtime/governed_runtime_adapters.py:60-75` — einziger Konstruktionsort aller
  produktiven Adapter (`OpenAIChatAdapter`, `OllamaAdapter`, `MockModelAdapter`); jeden beim Bauen wrappen
- Ändern: `ai_stack/telemetry/runtime_cost_attribution.py` — `aggregate_phase_costs` um Versuchsindex und
  Auslöser erweitern; neue Phasennamen `input_translation`, `output_translation`, `self_correction`, `fallback`
- Ändern: `world-engine/app/story_runtime/manager/model_costs_and_path_core.py:101-201` — nicht mehr nur den
  finalen Aufruf attribuieren, sondern das Ledger übernehmen
- Ändern: `world-engine/app/story_runtime/manager/story_window_entry_parts.py:257` — `quality_class` und
  `degradation_signals` durchreichen statt auf ein Boolean zu kollabieren
- Ändern: `world-engine/app/api/http_routes/common.py:80` — dasselbe Muster
- Ändern: `world-engine/app/story_runtime/manager/runtime_config.py` — weiche Budgetwerte
  (`turn_call_budget_soft`, `turn_call_budget_hard`) mit dokumentierten Defaults
- Test: `world-engine/tests/test_turn_cost_accounting.py` (neu),
  `world-engine/tests/test_quality_class_delivery.py` (neu)

**Implementierungsschritte**
- [ ] `TurnCallLedger` definieren: je Aufruf `phase`, `attempt_index`, `trigger`, `model_id`, `provider`,
      `input_tokens`, `output_tokens`, `duration_ms`, `success`.
- [ ] `CountingModelAdapter` als transparenter Wrapper um `BaseModelAdapter.generate`
      (`story_runtime_core/adapters.py:135-160`), der vor/nach dem Aufruf ins Ledger schreibt. Signatur und
      Rückgabetyp (`ModelCallResult`) bleiben unverändert.
- [ ] In `build_governed_model_adapters` jeden gebauten Adapter wrappen. Der Phasenname kommt aus einem
      Kontextvariablen-Stack, den die Knoten setzen — solange Shards nicht instrumentiert sind, fällt er auf
      `unattributed` zurück. **`unattributed` ist ein sichtbarer Zustand, kein stiller Default.**
- [ ] `aggregate_phase_costs` liefert zusätzlich `call_count`, `attributed_call_count`,
      `unattributed_call_count`.
- [ ] Weiches Budget: bei Überschreitung von `turn_call_budget_soft` ein Warnsignal ins Ledger und in den Trace;
      erst `turn_call_budget_hard` bricht ab. Defaults dokumentiert, Standardstellung begründet.
- [ ] `quality_class` (`ok|degraded|failed`) und `degradation_signals` bis in den ausgelieferten Block
      durchreichen. Das bisherige Boolean `degraded` bleibt vorerst als abgeleiteter Wert erhalten.

**Daten- und Vertragsmigration**
Der ausgelieferte Block bekommt zwei zusätzliche Felder (`quality_class`, `degradation_signals`). Additiv,
keine Feldentfernung — der Frontend-Renderer ignoriert unbekannte Felder. `phase_costs` bleibt formkompatibel,
gewinnt Einträge.

**Tests vor der Änderung**
- [ ] Charakterisierung: ein Zug mit erzwungener Self-Correction; festhalten, was `phase_costs` **heute** enthält
      (Erwartung: nur `model_generation`). Dieser Test wird nach der Änderung aktualisiert, nicht gelöscht.
- [ ] Charakterisierung: heutiges Auslieferungsformat des Blocks (Feldliste).

**Tests nach der Änderung**
- [ ] `test_every_model_call_is_ledgered` — Zug mit Übersetzung + Self-Correction ⇒
      `attributed_call_count == call_count`, `unattributed_call_count == 0`.
- [ ] `test_self_correction_attempts_are_separately_costed` — drei Versuche ⇒ drei Ledger-Einträge mit
      `attempt_index` 0,1,2.
- [ ] `test_soft_budget_warns_without_aborting` / `test_hard_budget_aborts`.
- [ ] `test_degraded_and_failed_are_distinguishable_at_delivery` — `quality_class` überlebt bis zum Block.

**Cleaning (in dieser Welle)**
- [ ] `_build_model_generation_phase_cost` verliert seine Sonderrolle als einzige Kostenquelle; toter Zweig
      `build_unavailable_phase_cost` für den Finalaufruf entfällt, sofern das Ledger ihn abdeckt.
- [ ] Löschkandidaten: keine Dateien; nur Sonderpfade innerhalb `model_costs_and_path_core.py`.

**SAD-/UML-Aktualisierung**
- [ ] `docs/architecture/project/observability-traceability/architecture.md`: Kostenattribution als eigener
      Baustein mit Quellanker.
- [ ] Neue UML-Sequenz `UML/Project/architecture-drift/turn-cost-ledger.puml` (Adapter-Naht → Ledger → Trace).

**W0-C — Trace und Kostenbericht auf dieselbe Wahrheit**
- [ ] `_emit_langfuse_evidence_observations` speist sich künftig aus dem Ledger statt aus `path_summary`:
      **je Modellaufruf eine Generation-Observation**, nicht mehr höchstens zwei pro Zug.
      Observation-Namen: `story.model.generation` (bestehend, für den Hauptaufruf),
      neu `story.model.translation.input`, `story.model.translation.output`,
      `story.model.self_correction`, `story.model.fallback`.
      Metadatum `attempt_index` an jeder Observation.
- [ ] **Hinweis zur Reihenfolge:** Der Emitter liegt in Shards
      (`_legacy_sources/_emit_langfuse_evidence_observations_00{0,1,2}.py`). Entweder dieses eine Modul aus
      Welle 1 vorziehen, oder W0-C nach Welle 1 nachziehen. **W0-A und W0-B bleiben davon unberührt** und
      liefern die Messung bereits vorher.
- [ ] Bestehende Langfuse-Evaluator-Filter prüfen: `langfuse_evaluator_catalog.py:59-72` filtert auf
      `Name: ["story.model.generation"]`. Zusätzliche Observation-Namen dürfen die vorhandenen Judges nicht
      versehentlich mitziehen — Filter entsprechend eingrenzen.

**Drift-Kanten- und Gate-Aktualisierung**
- [ ] Neue Kante `model-call-to-cost-ledger` (`effect: evidence_flow`) in `drift_edge_catalog.json`,
      Anker `story_runtime_core/model_call_accounting.py`.
- [ ] Envelope `turn-cost-envelope-v1` mit Feldern `call_count`, `attributed_call_count`, `quality_class`.
- [ ] Kante `ledger-to-langfuse-observation` (`effect: evidence_flow`), Anker der neue Emitter.
      Damit adressiert Welle 0 bereits einen Teil von `DRIFT-008` (Trace-Vollständigkeit).

**Rollback**
Der Wrapper ist ein reiner Dekorator. Rückbau = Wrapping in `build_governed_model_adapters` entfernen; alle
übrigen Änderungen sind additiv und inert.

**Exit-Kriterien**
- [ ] Ein realer Zug in Deutsch weist im Trace **alle** Modellaufrufe mit Phase und Versuchsindex aus.
- [ ] `unattributed_call_count == 0` für den Standard-Turn-Pfad.
- [ ] `quality_class` ist am Auslieferungsblock unterscheidbar.
- [ ] Volle world-engine- und ai_stack-Suite grün; `architecture_assurance audit` grün.

**Nachfolgende Abhängigkeiten:** Welle 2 (Übersetzungs-Routing braucht die Messung), Welle 4 (Budgetverhalten).

---

## Welle 1 — Entshardung des Autoritätspfads

**Ziel und Architekturentscheidung**
Der World-Engine-Manager wird wieder statisch analysierbar. Zuerst, weil `_finalize_committed_turn` — die
Commit-Finalisierung samt `_persist_session`-Aufruf — heute in sechs String-Shards liegt und jede Aussage über
die Schreibtopologie (Welle 2) sonst unbeweisbar bleibt.

**Enthaltene Drifts:** D15 (Teil 1), `DRIFT-006`

**Voraussetzungen:** Welle 0 (damit Verhaltensvergleiche messbar sind).

**Betroffene Dateien**
- Entfernen nach Rückbau: `world-engine/app/story_runtime/manager/_legacy_loader.py`,
  `_legacy_methods.py`, `_legacy_sources/**` (33 Dateien inkl. `manifest.py`)
- Ersetzen: die sechs Weiterleitungsmodule `legacy_build_langfuse_path_summary.py`,
  `legacy_emit_langfuse_evidence_observations.py`, `legacy_emit_langfuse_path_spans.py`,
  `legacy_emit_langfuse_runtime_aspect_observability.py`, `legacy_live_scene_blocks_from_visible_bundle.py`,
  `legacy_record_visible_projection_aspect.py`
- Neu (echte Module): `manager/commit_finalization.py` (aus `method:_finalize_committed_turn`, 6 Shards),
  `manager/narrator_path_opening_state.py` (aus `method:_build_narrator_path_opening_state`, 3 Shards),
  `manager/observability/langfuse_path_summary.py`, `.../langfuse_evidence_observations.py`,
  `.../langfuse_path_spans.py`, `.../langfuse_runtime_aspect_observability.py`,
  `manager/live_scene_blocks.py`, `manager/visible_projection_aspect.py`
- Test: `world-engine/tests/test_no_dynamic_source_assembly.py` (neu)

**Implementierungsschritte**
- [ ] Werkzeug `tools/architecture_assurance/unshard.py` bauen: liest `SOURCE`/`SOURCE_LINES` per `ast`,
      schreibt echten Python-Quelltext. Deterministisch, idempotent, dry-run-fähig.
- [ ] Je Zielmodul: Shards zusammenführen, als echtes Modul schreiben, Importe explizit machen
      (heute kommen Namen über `from ._deps import *`).
- [ ] `install_legacy_methods` durch normale Klassen-/Mixin-Definition ersetzen.
- [ ] `exec_top_level`-Aufrufe in den sechs Weiterleitungsmodulen durch echte Importe ersetzen; die
      Weiterleitungsmodule danach löschen und ihre Importeure umhängen.
- [ ] Gate-Test: kein Modul unter `world-engine/app` definiert `SOURCE`/`SOURCE_LINES`; kein `exec(compile(`.

**Daten- und Vertragsmigration:** keine. Reiner Strukturrückbau ohne Verhaltensänderung.

**Tests vor der Änderung**
- [ ] Characterization je Zielmodul: öffentliche Signaturen und Rückgabestrukturen des heutigen Verhaltens
      festhalten (`_finalize_committed_turn`, `_build_narrator_path_opening_state`, die vier Langfuse-Emitter,
      `_live_scene_blocks_from_visible_bundle`, `_record_visible_projection_aspect`).
- [ ] Voller Opening- und Turn-Durchlauf, Ergebnis als Referenz-Snapshot (Blockfolge, Diagnostik, Kostenledger).

**Tests nach der Änderung**
- [ ] Alle Characterization-Tests unverändert grün.
- [ ] Snapshot-Vergleich Opening/Turn identisch.
- [ ] `test_no_dynamic_source_assembly` grün für `world-engine/app`.
- [ ] Importgraph des Managers ist per `ast` vollständig auflösbar und azyklisch.

**Cleaning (in dieser Welle)**
- [ ] Löschen: `_legacy_loader.py`, `_legacy_methods.py`, `_legacy_sources/` (33 Dateien), die sechs
      `legacy_*.py`-Weiterleiter.
- [ ] Prüfen und entfernen: `from ._deps import *`-Sternimporte, sofern nur für die Shards nötig.
- [ ] `world-engine/app/story_runtime/manager/_imports_00.py` und `external_imports_core.py` auf tote
      Re-Exporte prüfen.
- [ ] Doku-/UML-Verweise auf `_legacy_*` entfernen.

**SAD-/UML-Aktualisierung**
- [ ] `docs/architecture/components/world-engine/architecture.md`: Manager-Zerlegung ohne dynamische Assemblierung.
- [ ] `UML/Components/world-engine/components/*`: `_legacy_loader`-Knoten entfernen, neue Module aufnehmen.

**Drift-Kanten- und Gate-Aktualisierung**
- [ ] `DRIFT-006` von `conflicting` auf `open_target` (Restumfang ai_stack/backend, Wellen 5/9).
- [ ] Neue Gate-Regel `BT-NO-DYNAMIC-SOURCE` im Audit, zunächst begrenzt auf `world-engine/app`.

**Rollback:** Welle ist ein einzelner, in sich geschlossener Commit-Block je Zielmodul; Rücknahme modulweise
per `git revert` möglich, solange Welle 2 nicht begonnen hat.

**Exit-Kriterien**
- [ ] Kein `SOURCE`-Modul und kein `exec(compile(` unter `world-engine/app`.
- [ ] `_finalize_committed_turn` ist normaler, lesbarer Python-Code mit sichtbarem `_persist_session`-Aufruf.
- [ ] Charakterisierung und Snapshots identisch; volle engine-Suite grün.

**Nachfolgende Abhängigkeiten:** Welle 2 (Schreibtopologie), Welle 3.

---

## Welle 2 — Eine Schreibtopologie, eine Persistenz-Transaktion

**Ziel und Architekturentscheidung**
Sieben Persistenzressourcen werden benannt und je genau einem Sink zugeordnet. Die Write-Surface-Prüfung wechselt
von *einem Aufrufliteral* auf ein **Ressourcenmodell**. `_persist_session` bekommt ein explizites Ergebnisobjekt
statt stiller `return`-Zweige. `live_run_instance` (Lobby/Run) wird als eigene Ressource anerkannt statt mit
`live_story_session` vermischt zu werden.

**Enthaltene Drifts:** D16, D17, D18 (Charakterisierung), `DRIFT-001` (Teil 1)

**Voraussetzungen:** Welle 1.

**Betroffene Dateien**
- `world-engine/app/story_runtime/manager/session/manager_init_and_persistence.py:264-310`
- `world-engine/app/story_runtime/manager/opening_execution.py:314`
- `world-engine/app/story_runtime/manager/player_visible_persistence.py:105`
- `world-engine/app/story_runtime/manager/commit_finalization.py` (aus Welle 1)
- `world-engine/app/api/http_routes/play_run_routes.py:95` — **Löschkandidat** (Route schreibt am Manager vorbei)
- `world-engine/app/runtime/manager.py` — 10 Store-Writes: Ressource als `live_run_instance` deklarieren
- `tools/architecture_assurance/drift_edges.py:63-209` — `validate_authoritative_write_surfaces` umbauen
- `tools/architecture_assurance/drift_edge_catalog.json:268-300`
- Test: `tests/architecture_assurance/test_write_surface_resources.py` (neu),
  `world-engine/tests/test_persist_session_outcomes.py` (neu),
  `world-engine/tests/test_rejected_proposal_leaves_revision.py` (neu, Charakterisierung)

**Implementierungsschritte**
- [ ] `PersistOutcome` als Ergebnistyp: `Persisted(revision)` | `SkippedSimulation` | `NoStoreConfigured`.
      `_persist_session` gibt ihn zurück; kein stiller `return` mehr.
- [ ] `session.revision` als Feld einführen und bei jedem tatsächlichen Schreibvorgang erhöhen.
      Ohne dieses Feld ist die DoD-Zusage „Ablehnung ändert keine Revision" nicht prüfbar.
- [ ] Opening als eigener Lifecycle-Übergang benennen (`persist_reason="session_opened"`), nicht als Commit.
- [ ] `play_run_routes.py:95` entfernen; der Manager erhält eine Methode
      `attach_runtime_profile_handoff(instance, handoff)`, die selbst persistiert.
- [ ] `write_surfaces` im Katalog auf sieben Ressourcen erweitern: `live_story_session`, `live_run_instance`,
      `branching_tree`, `branch_timeline`, `callback_web`, `consequence_cascade`, `backend_runtime_session`.
- [ ] Scan umbauen: Auflösung über **Store-Typ und Methodenname** statt über den punktierten Ausdruck;
      zusätzlich Aliaserkennung (lokale Zuweisung eines Store-Objekts) und ein Verbot
      „Route/Adapter ruft `*.store.save` direkt".
- [ ] Übersetzungs-Routing (E6): Task-Klasse `translation` mit eigenem, günstigem Modell und harter Kostengrenze;
      Ergebnis-Cache pro Zug (gleicher Text ⇒ ein Aufruf).

**Daten- und Vertragsmigration**
`session.revision` ist neu. Bestehende Session-Dateien haben es nicht: Loader setzt beim ersten Laden
`revision = 0` und schreibt erst beim nächsten regulären Schreibvorgang. Kein Migrationslauf nötig,
keine Formatänderung, die alte Leser bricht.

**Tests vor der Änderung**
- [ ] **Charakterisierung D18 (entscheidend):** Zug mit blockiertem Übergang
      (`unknown_target_scene` erzwingen) ⇒ Hash der Session-Datei vor und nach dem Zug festhalten.
      Dieser Test klärt endgültig, ob Ablehnungen heute schreiben. Er wird **nicht** vorher beantwortet, sondern
      gemessen.
- [ ] Charakterisierung: Zahl und Reihenfolge der Store-Writes eines Standardzuges.

**Tests nach der Änderung**
- [ ] `test_persist_session_returns_explicit_outcome` — alle drei Ergebnisfälle.
- [ ] `test_simulation_session_never_writes`.
- [ ] `test_route_cannot_write_store_directly` — Gate-Negativtest.
- [ ] `test_alias_write_is_detected` — `s = self._session_store; s.save(...)` ⇒ Gate rot.
- [ ] `test_second_writer_breaks_gate` — künstlicher Fremd-Callsite je Ressource ⇒ Gate rot.
- [ ] `test_translation_cache_single_call_per_identical_text`.

**Cleaning (in dieser Welle)**
- [ ] Löschen: `manager.store.save(instance)` in `play_run_routes.py:95`.
- [ ] Entfernen: stille `return`-Zweige in `_persist_session`.
- [ ] Entfernen: das alte literalbasierte `write_surfaces`-Schema aus dem Katalog (kein paralleles Zweitformat).

**SAD-/UML-Aktualisierung**
- [ ] `docs/architecture/components/world-engine/architecture.md`: Abschnitt „Persistenzressourcen und Sinks",
      sieben Ressourcen mit Owner, erlaubtem Writer, Transaktionsgrenze, Revisionsverhalten.
- [ ] `UML/Project/architecture-drift/runtime-authority-and-envelope.puml`: `live_run_instance` als eigene
      Ressource, nicht als Kompatibilitätspfad.

**Drift-Kanten- und Gate-Aktualisierung**
- [ ] `authority_invariants` je Ressource statt nur für `live_story_session`.
- [ ] `DRIFT-001` auf `confirmed current` setzen, Zielbeschreibung auf Ressourcentrennung ändern.
- [ ] Envelope um `session_revision` und `rejection_reason` erweitern.

**Rollback:** `PersistOutcome` ist additiv; Rücknahme = Rückgabewert ignorieren. Die Gate-Erweiterung ist
unabhängig rücknehmbar.

**Exit-Kriterien**
- [ ] Jede der sieben Ressourcen hat genau einen deklarierten Sink; ein künstlicher zweiter Writer bricht das Gate.
- [ ] Keine Route und kein Adapter schreibt an einem Manager vorbei.
- [ ] `session.revision` existiert; das Charakterisierungsergebnis zu D18 ist dokumentiert und dient Welle 3 als
      Ausgangspunkt.

**Nachfolgende Abhängigkeiten:** Welle 3, Welle 6.

---

## Welle 3 — Reiches Commit-Vokabular für freies Rollenspiel

**Ziel und Architekturentscheidung**
Das Commit-Vokabular der Autorität wird mindestens so reich wie das Auflösungsvokabular der KI. Die
Commit-Auflösung wechselt von der **Szenen-Übergangskarte** auf **Zustandsänderungen**; ein Szenenwechsel wird
ein Sonderfall davon. `blocked` ist danach reserviert für situativ tatsächlich Unmögliches (E9).

**Enthaltene Drifts:** D31, `DRIFT-002`, `DRIFT-005`

**Voraussetzungen:** Welle 2 (Revision und Ergebnisobjekt müssen existieren).

**Betroffene Dateien**
- `world-engine/app/story_runtime/commit_models.py:27` (`SituationStatus`), `:475-560` (Beat-Progression),
  `:577+` (`resolve_narrative_commit`)
- `world-engine/app/story_runtime/narrative_commit_resolution.py:37-104`
- `world-engine/app/story_runtime/narrative_threads.py:72-92`,
  `narrative_threads_update_passes.py:56`
- `world-engine/app/story_runtime/manager/degradation_and_turn_blocks.py:120`
- `ai_stack/contracts/action_resolution_contracts.py:101`,
  `ai_stack/story_runtime/player_action_resolution.py:445` (Abgleich, keine Verengung)
- Umbenennung Proposal-Semantik: `ai_stack/langgraph/runtime_executor/executor_validation_commit.py`,
  `executor_run_finish.py` → `commit`-Begriffe zu `proposal_finalize` (Wortwahl, keine Verhaltensänderung)
- Test: `world-engine/tests/test_partial_action_commit.py` (neu),
  `world-engine/tests/test_blocked_is_rare.py` (neu)

**Implementierungsschritte**
- [ ] `SituationStatus` erweitern: `continue | transitioned | partial | prevented | allowed_offscreen | blocked | terminal`.
- [ ] `eval_core_transition_rules` umbauen: Fehlt ein passender Szenenübergang, ist das **kein** Blocker.
      Ergebnis wird `partial` (Handlung wirkt auf Zustand, Szene bleibt) statt `blocked`.
      `blocked` nur noch bei explizit als unmöglich/unsicher aufgelöster Handlung.
- [ ] Beat-Progression: `partial`, `prevented`, `allowed_offscreen` dürfen fortschreiten.
      `advancement_reason` differenziert (`partial_effect_advance`, `prevented_but_witnessed`).
- [ ] Abbildungstabelle KI-Auflösungsstatus → `SituationStatus` explizit modellieren; jede Abbildung auf einen
      **ärmeren** Wert ist ein Fehler und wird getestet.
- [ ] Proposal-/Commit-Begriffe trennen: KI-seitig ausschließlich `proposal_*`, `CommitDecision` und
      `committed_*` bleiben der World-Engine vorbehalten.

**Daten- und Vertragsmigration**
`SituationStatus` gewinnt Werte. Konsumenten, die auf `{"continue","transitioned","blocked","terminal"}`
vergleichen, müssen ergänzt werden — betroffen: `narrative_threads.py:72`,
`narrative_threads_update_passes.py:56`, `degradation_and_turn_blocks.py:120`,
`ai_stack/contracts/hierarchical_memory_contracts.py:385`. Persistierte Altsessions enthalten nur alte Werte;
Leser behandeln unbekannte Werte als `continue` (vorwärtskompatibel).

**Tests vor der Änderung**
- [ ] Charakterisierung: freie Spielerhandlung ohne passenden Szenenübergang ⇒ heutiger Ausgang festhalten
      (Erwartung: `blocked`, `advanced=False`).
- [ ] Charakterisierung: Verteilung der `situation_status`-Werte über einen Beispiel-Spielverlauf.

**Tests nach der Änderung**
- [ ] `test_free_action_without_scene_transition_commits_partial` — Handlung wirkt, Beat schreitet fort.
- [ ] `test_blocked_only_for_impossible_action`.
- [ ] `test_no_resolution_status_maps_to_poorer_commit_status` — Vollständigkeit der Abbildungstabelle.
- [ ] `test_prevented_action_still_witnessed` — verhinderte Handlung erzeugt Wirkung und Sichtbarkeit.
- [ ] `test_ai_layer_uses_no_commit_vocabulary` — statischer Test gegen `commit`-Begriffe in ai_stack-Ausgaben.

**Cleaning (in dieser Welle)**
- [ ] Entfernen: Sonderzweige, die `blocked` aus fehlenden Transition-Hints ableiten
      (`transition_hints_missing`, `unknown_target_scene` als Blocker).
- [ ] Entfernen: `commit`-Wortverwendung in ai_stack-Knotennamen und -Payloads (Umbenennung, keine Fassade).

**SAD-/UML-Aktualisierung**
- [ ] `docs/architecture/components/world-engine/architecture.md`: Abschnitt „Handlungsergebnis-Vokabular"
      mit vollständiger Abbildungstabelle.
- [ ] `UML/Components/world-engine/states/*`: Zustandsmaschine mit den neuen Ausgängen.

**Drift-Kanten- und Gate-Aktualisierung**
- [ ] `DRIFT-002` und `DRIFT-005` auf Zielbeschreibung „reiches Vokabular" umstellen.
- [ ] Neue Gate-Regel: kein Auflösungsstatus ohne Abbildung.

**Rollback:** Die neuen Statuswerte sind additiv; Rücknahme = Abbildungstabelle auf die alten vier Werte
zurückstellen.

**Exit-Kriterien**
- [ ] Eine freie Handlung ohne vormodellierten Szenenübergang wirkt und lässt den Beat fortschreiten.
- [ ] `blocked` tritt im Beispielspielverlauf nur bei situativ Unmöglichem auf.
- [ ] Kein KI-Artefakt verwendet Commit-Vokabular.

**Nachfolgende Abhängigkeiten:** Welle 4.

---

## Welle 4 — Fähigkeitsmigration und Fehlerverhalten

**Ziel und Architekturentscheidung**
Die World-Engine erhält die fünf Modelle, die es dort heute nicht gibt und die nur in der ruhenden
Backend-Generation existieren. **Jede Fähigkeit kommt hinter einem ausdrücklichen Schalter mit dokumentierter
Standardstellung** (E5) — weil nicht rekonstruierbar ist, welche davon früher bewusst abgeschaltet wurden.
Zusätzlich wird das Verhalten bei technischem Versagen festgelegt (E7).

**Enthaltene Drifts:** D26, D29 (Verhaltensteil), `DRIFT-003`

**Voraussetzungen:** Welle 3.

**Betroffene Dateien**
- Vorlage (nur lesen, nicht kopieren): `backend/app/runtime/validation/mutation_policy.py`,
  `backend/app/runtime/turn/turn_executor.py:202,291,418`,
  `backend/app/runtime/narrative/narrative_commit.py:38,72`,
  `backend/app/runtime/ai/ai_failure_recovery.py` (990 Z.),
  `backend/app/runtime/scene_legality.py`
- Neu in world-engine: `app/story_runtime/state_deltas.py` (Delta + Guard + akzeptiert/abgelehnt),
  `app/story_runtime/mutation_policy.py`, `app/story_runtime/source_gate.py`,
  `app/story_runtime/failure_recovery.py`, `app/story_runtime/scene_legality.py`
- Ändern: `app/story_runtime/commit_models.py` (Deltas in die Commit-Auflösung einbinden),
  `manager/runtime_config.py` (fünf Schalter mit dokumentierten Defaults)
- Ändern: `ai_stack/langgraph/runtime_executor/executor_generation_self_correction.py` — reduzierter
  Kontext beim Wiederholungsversuch (E7). **Achtung: Shard — wird in Welle 5 zurückgebaut.** Falls die Änderung
  vor Welle 5 nötig ist, dieses eine Modul vorziehen und einzeln entsharden.
- Test: `world-engine/tests/test_state_delta_partial_acceptance.py`,
  `test_technical_failure_fallback_chain.py`, `test_capability_switch_defaults.py`

**Implementierungsschritte**
- [ ] Delta-Modell: `StateDelta`, `GuardOutcome`, `accepted_deltas`, `rejected_deltas`. Ein Zug kann
      **teilweise** wirken — das ist die technische Grundlage für `partial` aus Welle 3.
- [ ] `MutationPolicy`: welche Zustandsänderungen sind erlaubt, welche brauchen Begründung. Standardstellung
      **permissiv** (E9): erlaubt, sofern nicht ausdrücklich verboten.
- [ ] Source-Gate: Herkunft einer vorgeschlagenen Änderung prüfen (Spieler / KI / autorisiertes Skript) und
      ablehnungsfähig committen (`narrative_commit_for_source_gate_rejection`-Äquivalent).
- [ ] Failure-/Recovery-Policies: `RetryPolicy`, `ReducedContextRetryPolicy`, `FallbackResponderPolicy`,
      `SafeTurnPolicy`, `StateSnapshot`, `RestorePolicy`.
- [ ] **E7-Kette bei technischem Versagen:** (1) ein günstiger Wiederholungsversuch mit **reduziertem** Kontext
      — nicht mit wachsendem, wie heute; (2) danach ein deterministischer Weiterspiel-Zug: die Handlung findet
      statt, wirkt minimal, die Szene läuft weiter, intern klar als `technically_reduced` markiert und von
      `narratively_prevented` unterscheidbar.
- [ ] `allow_degraded_commit_after_retries`: bleibt vorhanden, wird aber durch die E7-Kette ersetzt; der
      degradierte Commit ist nicht mehr der Standardausgang, sondern der deterministische Weiterspiel-Zug ist es.
- [ ] Fünf Schalter in `runtime_config.py`, jeder mit Kommentar: Zweck, Standardstellung, Begründung der
      Standardstellung, und was ein Abschalten bedeutet.

**Daten- und Vertragsmigration**
`accepted_deltas`/`rejected_deltas` werden Teil des Commit-Records. Altsessions haben sie nicht; Leser
behandeln Abwesenheit als „alles akzeptiert" (entspricht dem heutigen Verhalten).

**Tests vor der Änderung**
- [ ] Charakterisierung: heutiges Verhalten bei erschöpfter Self-Correction (mit Kostenledger aus Welle 0) —
      Aufrufzahl, Prompt-Länge je Versuch, Endzustand.
- [ ] Charakterisierung: heutiger Endzustand bei fehlendem Fallback-Adapter.

**Tests nach der Änderung**
- [ ] `test_partial_delta_acceptance_commits_partially`.
- [ ] `test_reduced_context_retry_is_cheaper_than_first_attempt` — Prompt-Länge Versuch 2 < Versuch 1
      (heute ist es umgekehrt).
- [ ] `test_deterministic_continuation_needs_no_model_call` — Ledger zeigt null zusätzliche Aufrufe.
- [ ] `test_technically_reduced_is_distinguishable_from_narratively_prevented`.
- [ ] `test_each_capability_switch_has_documented_default`.
- [ ] `test_mutation_policy_default_is_permissive`.

**Cleaning (in dieser Welle)**
- [ ] Entfernen: der wachsende Retry-Prompt in `_self_correct_generation`
      (`model_prompt + prior_output + rewrite_instruction` → reduzierter Delta-Auftrag).
- [ ] **Noch nicht** löschen: der Backend-Cluster bleibt bis Welle 6 als Referenz stehen. Löschen erst nach
      bestandener Migration.

**SAD-/UML-Aktualisierung**
- [ ] `docs/architecture/components/world-engine/architecture.md`: fünf neue Bausteine mit Quellankern und
      Schalterstellungen.
- [ ] `UML/Components/world-engine/activity/`: Aktivitätsdiagramm der E7-Kette.

**Drift-Kanten- und Gate-Aktualisierung**
- [ ] `DRIFT-003`: Feldbeweis von Token-Präsenz auf **Flussbeweis** umstellen (Kontrakttest je Feld statt
      `token in file`).
- [ ] Envelope um `degraded_mode`, `trace_completeness`, `accepted_deltas`, `rejected_deltas` erweitern.

**Rollback:** Jede Fähigkeit ist einzeln abschaltbar (das ist der Zweck der Schalter). Rücknahme einer
Fähigkeit = Schalter auf `off`, kein Code-Rückbau nötig.

**Exit-Kriterien**
- [ ] Alle fünf Fähigkeiten existieren im World-Engine-Produktionspfad und sind durch Kontrakttests belegt.
- [ ] Der Wiederholungsversuch ist billiger als der Erstversuch.
- [ ] Technisches Versagen führt zu einem Weiterspiel-Zug ohne zusätzlichen Modellaufruf.
- [ ] Jeder Schalter hat eine dokumentierte und begründete Standardstellung.

**Nachfolgende Abhängigkeiten:** Welle 6 (erst jetzt darf der Backend-Cluster fallen).

---

## Welle 5 — Entshardung ai_stack und Backend-Game-API

**Ziel:** Die restlichen 171 Shard-Module werden echter Python-Code — zuerst der AI-Turn-Pfad (63), dann die
spielerseitige Backend-Game-API (66), zuletzt `backend/app` im Übrigen.

**Enthaltene Drifts:** D15 (Teil 2+3)

**Voraussetzungen:** Welle 4. (Ausnahme: `executor_generation_self_correction.py` darf in Welle 4 vorgezogen werden.)

**Betroffene Dateien**
- `ai_stack/**` — 63 Module mit `SOURCE`/`SOURCE_LINES`, Kern: `ai_stack/langgraph/runtime_executor/**` (66 Dateien)
- `backend/app/api/v1/game_routes.py:12-68` — `_IMPLEMENTATION_FILES` (29 Dateien) und `_load_game_route_implementation`
- `backend/app/api/v1/game/**` — 29 Implementierungsdateien
- `backend/app/services/governance/governance_runtime_service.py:70`
- Test: Erweiterung von `test_no_dynamic_source_assembly` auf `ai_stack` und `backend/app`

**Implementierungsschritte**
- [ ] `unshard.py` (Welle 1) wiederverwenden, Reihenfolge: `runtime_executor` → übriges `ai_stack` →
      `backend/app/api/v1/game/` → übriges `backend/app`.
- [ ] `game_routes.py`: `_IMPLEMENTATION_FILES` + `exec` durch echte Modulimporte und explizite
      Blueprint-Registrierung ersetzen.
- [ ] Gate-Regel `BT-NO-DYNAMIC-SOURCE` auf `ai_stack` und `backend/app` ausweiten.

**Daten-/Vertragsmigration:** keine.

**Tests vor der Änderung**
- [ ] Route-Inventar der Game-API festhalten (Pfad, Methode, Handler-Name) — der Vergleich nach dem Rückbau ist
      der Beweis, dass keine Route verloren ging.
- [ ] Characterization je Executor-Knoten (Ein-/Ausgabestruktur des `RuntimeTurnState`).

**Tests nach der Änderung**
- [ ] `test_game_route_inventory_unchanged` — identische Routenliste.
- [ ] Alle Executor-Charakterisierungen grün.
- [ ] `test_no_dynamic_source_assembly` grün für `world-engine/app`, `ai_stack`, `backend/app`.

**Cleaning:** Löschen aller `SOURCE`/`SOURCE_LINES`-Module nach Rückbau; Entfernen von
`_read_implementation_source`, `_load_game_route_implementation`, `_IMPLEMENTATION_FILES`.

**SAD-/UML:** `docs/architecture/components/{ai-stack,backend}/architecture.md` — Modulstruktur ohne dynamische
Assemblierung; Turn-Graph-UML mit echten Quellankern.

**Gates:** `DRIFT-006` schließen (Rest `tools/` in Welle 9). Anker im `model_catalog.json` zeigen jetzt auf
echten Code statt auf Stringblobs.

**Rollback:** modulweise `git revert`.

**Exit-Kriterien:** Kein `exec(compile(` in `world-engine/app`, `ai_stack`, `backend/app`; Routeninventar
unverändert; volle Suiten grün.

---

## Welle 6 — Paketnamen entkoppeln, Parallelwelten retiren

**Ziel:** `world-engine/app` → `world_engine` (E4). Danach: ruhender Backend-Cluster entfernen, Routing-Governance
als eigenes Subsystem modellieren, verwaiste Module löschen.

**Enthaltene Drifts:** D14, D13, D21, `DRIFT-001` (Rest)

**Voraussetzungen:** Welle 5 (Umbenennung nur auf echtem Python, nicht in Stringliteralen).

**Betroffene Dateien**
- `world-engine/app/**` (376 getrackte Dateien) → `world-engine/world_engine/**`
- `conftest.py:33-37` — `sys.path`-Manipulation entfernen
- `world-engine/tests/conftest.py:113` — Neu-Import-Trick entfernen
- Entfernen: `backend/app/runtime/{manager.py,engine.py,turn/,narrative/,ai/,ai_turn/,supervisor/,validation/,presentation/,canonical/,transitional/,cache/,scene_legality.py,session/session_store.py}`
- Behalten und verschieben: `backend/app/runtime/{routing/,model_routing.py,model_routing_contracts.py,routing_registry_bootstrap.py,input_interpreter.py,runtime_models.py,session/session_persistence.py}` → `backend/app/model_governance/`
- Entfernen: `world-engine/app/runtime/{session_manager.py,turn_executor.py,branching_turn_executor.py,actor_lane.py,object_admission.py,state_delta.py}` + zugehörige Tests
- DB: Tabelle `runtime_sessions` + Migration

**Implementierungsschritte**
- [ ] Umbenennung mechanisch (`git mv` + Import-Rewrite), `world_engine/__init__.py` mit echtem Inhalt.
- [ ] `sys.path`-Vorspiel aus beiden `conftest.py` entfernen.
- [ ] Leser der Tabelle `runtime_sessions` ermitteln; falls Operator-/QA-Sichten daraus lesen, auf die
      World-Engine-Quelle umstellen; **erst danach** Tabelle und Migration entfernen.
- [ ] Ruhenden Backend-Cluster entfernen, inkl. `backend/tests/runtime/**`.
- [ ] Routing-Governance nach `backend/app/model_governance/` verschieben und als eigenes Subsystem in
      `config.json` aufnehmen (es ist keine Turn-Autorität und darf nicht so heißen).
- [ ] Verwaiste world-engine-Module samt ihrer Tests entfernen.

**Daten-/Vertragsmigration:** Entfernen der Tabelle `runtime_sessions` ist die einzige Datenmigration.
Vorher Leserprüfung, Backup, reversible Migration.

**Tests vor der Änderung**
- [ ] `test_import_determinism` — gleicher Import ⇒ gleiche Datei, unabhängig von Suite und CWD.
- [ ] Konsumentennachweis je Löschkandidat (Import-, Callsite-, String- und Registry-Suche).

**Tests nach der Änderung**
- [ ] `test_no_sys_path_manipulation_in_conftest`.
- [ ] `test_no_module_without_production_consumer_in_runtime`.
- [ ] `test_runtime_sessions_table_absent`.
- [ ] Alle Suiten ohne Pfad-Vorspiel grün.

**Cleaning:** siehe Löschliste oben; zusätzlich Doku-, UML-, CI- und Packaging-Verweise auf `app.` unter
world-engine.

**SAD-/UML:** Subsystemliste in `config.json` und `model_catalog.json` um `model-governance` erweitern;
`world-engine`-Elemente auf neue Pfade umhängen; `DRIFT-001`-Kante `world-engine:runtime` neu binden.

**Gates:** `DRIFT-001` schließen. Import-Gate gegen Wiedereinführung des Backend-Turn-Clusters.

**Rollback:** Umbenennung ist ein einzelner mechanischer Commit; Rücknahme per `git revert`. Die Löschungen
sind einzeln revertierbar, solange Welle 7 nicht begonnen hat.

**Exit-Kriterien:** `python -c "import world_engine"` eindeutig; kein Modul ohne Produktionskonsument unter
`world_engine/runtime`; Backend enthält keine zweite Turn-Autorität mehr; Routing-Governance ist als eigenes
Subsystem gebunden.

---

## Welle 7 — Content-Wahrheit vereinheitlichen

**Ziel:** YAML unter `content/` ist die einzige autorisierte Inhaltsquelle; ein versionierter, kompilierter
Content-Vertrag ist die einzige Laufzeitquelle. Kein produktspezifisches Python in `story_runtime_core`.

**Enthaltene Drifts:** `DRIFT-004`, D23

**Voraussetzungen:** Welle 6.

**Betroffene Dateien**
- `content/modules/**` (184 YAML)
- `backend/app/content/module_loader.py`, `module_validator.py`
- `world_engine/content/backend_loader.py`
- `story_runtime_core/goc_solo_builtin_catalog.py`, `goc_solo_builtin_catalog_actions.py`,
  `goc_solo_builtin_roles_rooms.py`, `goc_solo_builtin_template.py` — **Löschkandidaten**
- `ai_stack/story_runtime/god_of_carnage/**` (≈26 Module) — auf Anti-Corruption-Adapter reduzieren
- `ai_stack/langgraph/runtime_executor/executor_goc_canonical_content.py`
- `tools/architecture_assurance/config.json:107` — Lane-Root `content-authority` korrigieren (zeigt heute auf
  Python-Builtins)

**Implementierungsschritte**
- [ ] Kompilierten Content-Vertrag mit `content_version` und `source_provenance` je Fakt definieren.
- [ ] Kompilierung deterministisch machen (wiederholter Export byte-identisch).
- [ ] Builtins aus YAML generieren oder entfernen; kein handgepflegtes Inhalts-Python.
- [ ] Produktspezifische ai_stack-Module auf Projektionen ohne eigene Faktenhoheit reduzieren.

**Tests vorher:** Content-Provenienz-Charakterisierung — welcher Laufzeitfakt kommt heute woher.
**Tests nachher:** `test_every_runtime_fact_traces_to_module_and_version`;
`test_no_product_python_overrides_authored_fact`; `test_content_compilation_is_deterministic`.

**Cleaning:** Löschen der vier `goc_solo_builtin_*`-Module; Entfernen konstanter Inhaltsdefinitionen aus
ai_stack; Korrektur der Lane-Roots.

**SAD-/UML:** `docs/architecture/components/content-authority/architecture.md`; Content-Flow-UML.
**Gates:** `DRIFT-004` schließen.
**Rollback:** Builtins sind bis zum Abschluss der Welle parallel lauffähig; Rücknahme = Generierung abschalten.
**Exit-Kriterien:** Kein Laufzeitfakt ohne Modulpfad und Version; wiederholter Export byte-identisch.

---

## Welle 8 — Test-, CI- und Gate-Wahrheit

**Ziel:** Ein Suite-Katalog erzeugt CI; Deckungskennzahlen messen etwas; Modellelemente tragen genau eine
Autoritätsrolle; Trace-Lücken sind sichtbar.

**Enthaltene Drifts:** D19, D20, D25, `DRIFT-007`, `DRIFT-008`, `DRIFT-009`, `DRIFT-012`

**Voraussetzungen:** Welle 6.

**Betroffene Dateien**
- `tests/run_tests.py` (2538 Z.) — Suite-Katalog wird alleinige Quelle
- `.github/workflows/*.yml` (15 Dateien) — Schritte aus dem Katalog generieren
- `tools/architecture_assurance/audit.py:239-242,313` — Deckungssemantik
- `tools/architecture_assurance/manifest_builder.py:174-199` — `out_of_scope` begründungspflichtig
- `tools/architecture_assurance/model_catalog.json` — Element-Aliasing auflösen
- `tools/architecture_assurance/drift_edges.py:515-560` — Feldbeweis von Token-Präsenz auf Kontraktbeweis
- `world_engine/observability/trace.py`, `backend/app/api/v1/game/player_turn_trace_start.py`,
  `ai_stack/langfuse/langfuse_evidence.py`, `tools/mcp_server/langfuse_tracing.py`

**Implementierungsschritte**
- [ ] Suite-Katalog um jede heute nicht zugeordnete Testdatei ergänzen (809 Testdateien insgesamt) oder eine
      begründete Ausnahme eintragen.
- [ ] Workflow-Schritte generieren; direkter `pytest`-Aufruf in Workflows per Gate verbieten.
- [ ] `out_of_scope` nur mit Grundkategorie (`generated`, `vendored`, `test-fixture`, `archived`); Anteil je
      Subsystem gedeckelt, Trendverschlechterung bricht das Gate.
- [ ] Element-Aliasing auflösen: kein Element trägt zwei disjunkte Autoritätsrollen
      (heute u. a. `validation`==`commit`, `session`==`proposal`, `store`==`persistence`==`store_node`).
- [ ] `TurnTrace`-Kontrakt: propagierte Identität, eigene Spans, **explizite Lücken**, Redaktion.
      Fehlende Spans erscheinen als Lücke, nie als Vollständigkeit.
- [ ] Player-Visible-Block-Schema versionieren; Renderer erschöpfend über alle Varianten; Reconnect-Test auf
      Reihenfolge und Deduplizierung.

**Tests vorher:** Waisenliste der Testdateien; heutige Deckungszahlen als Referenz.
**Tests nachher:** `test_every_test_file_has_suite_or_exception`; `test_no_direct_pytest_in_workflows`;
`test_out_of_scope_requires_reason`; `test_no_element_has_two_authority_roles`;
`test_trace_gap_is_reported_as_partial`; `test_reconnect_has_no_duplicate_or_reordered_blocks`.

**Cleaning:** Entfernen doppelter Workflow-Schritte; Entfernen der festen Census-Sollwerte in `config.json:37-46`
zugunsten begründeter Schwellen; Entfernen verwaister Testdateien nach Konsumentennachweis.

**SAD-/UML:** `docs/architecture/project/{quality-gates,observability-traceability}/architecture.md`.
**Gates:** `DRIFT-007/008/009` schließen; `DRIFT-012` von `confirmed_current` auf geschlossen — diesmal belegt.
**Rollback:** Gate-Schwellen sind konfigurierbar; Rücknahme = alte Schwellen.
**Exit-Kriterien:** Kein direkter `pytest`-Aufruf in Workflows; keine Waisen; keine tautologische Kennzahl;
JSON, JUnit und SARIF bilden denselben Audit ab.

---

## Welle 9 — Werkzeugplattform herauslösen, Baum bereinigen

**Ziel:** `'fy'-suites` wird ein eigenes Repository (E3); der Arbeitsbaum enthält keine Archäologie mehr;
`tools/` wird entshardet.

**Enthaltene Drifts:** D22, D24, D15 (Rest `tools/`: 43 Module)

**Voraussetzungen:** Welle 8.

**Betroffene Dateien**
- `'fy'-suites/**` (1047 getrackte Dateien) → eigenes Repository
- `pyproject.toml` — `packages.find where` und `[project.scripts]` (10 Werkzeug-Einträge) zurück auf das Produkt
- `.github/workflows/fy-{contractify,despaghettify,docify}-gate.yml`
- `conftest.py:38-41` — `'fy'-suites` aus `sys.path`
- `.worktrees/mvp-v24-integration/`, `.claude/worktrees/coverage-improvement/`, prunable Worktree
- `ArchitecturalKnowledgeDB/` (unversionierte Vollkopie; CI nutzt gepinnten externen Checkout),
  `Better Tomorrow/` (leeres Verzeichnis)
- Wurzel-Altlasten: `audit_*.json` (9), `engine_run_last.txt`, `mvp4_test_results.txt`,
  `test_trace_*.py`, `test_langfuse_e2e.py`, `tmp/`, `tmp_coauth_dbg/`, `.state_tmp/`, `.tmp_goc_pdf/`
- `tools/**` — 43 Shard-Module

**Implementierungsschritte**
- [ ] `'fy'-suites` mit Historie in ein eigenes Repository überführen (`git subtree split`), dort versionieren,
      hier als Entwicklungsabhängigkeit konsumieren.
- [ ] `pyproject.toml` auf das Produkt umstellen; Werkzeug-Skripte entfernen.
- [ ] Die drei `fy-*`-Workflows entfernen oder in das neue Repository verschieben.
- [ ] `delagecy`-Register verliert jede Statusautorität; verbleibende offene Punkte in das Driftregister überführen.
- [ ] `git worktree prune`; verwaiste Worktree-Verzeichnisse entfernen; `__pycache__` beider
      Interpreter-Generationen bereinigen (2933 × cpython-310, 1794 × cpython-314).
- [ ] `tools/` entsharden; Gate-Regel `BT-NO-DYNAMIC-SOURCE` repoweit.

**Tests vorher:** Nachweis, dass kein Produktionspfad `'fy'-suites` importiert (außer `conftest.py`).
**Tests nachher:** `test_no_fy_suites_import_in_product`; `test_no_orphan_worktree_directories`;
`test_single_interpreter_generation`; `test_no_dynamic_source_assembly` repoweit.

**Cleaning:** siehe Dateiliste; zusätzlich `.gitignore`-Einträge für `'fy'-suites` entfernen.
**SAD-/UML:** Subsystem `quality-gates` von der Werkzeugplattform entkoppeln.
**Gates:** D15 endgültig schließen.
**Rollback:** Das Subtree-Split lässt die Historie im alten Repo intakt; Rücknahme = Verzeichnis
zurückspielen.
**Exit-Kriterien:** Produkt-Repo enthält keine Werkzeugplattform; kein `SOURCE`-Modul repoweit; keine
Repo-Kopien im Arbeitsbaum.

---

## Definition of Done (Gesamtprogramm)

Der Plan ist erst abgeschlossen, wenn **alle** folgenden Punkte durch Produktionspfad-Evidenz belegt sind —
Dateipräsenz, Dateiname und grüne Altberichte zählen ausdrücklich nicht.

**Autorität und Persistenz**
- [ ] Genau eine autoritative Live-Session-Write-Topologie; sieben benannte Ressourcen mit je einem Sink.
- [ ] Keine nicht katalogisierte Session-Persistenz-Callsite; ein künstlicher zweiter Writer bricht das Gate.
- [ ] Ablehnungen verändern keine persistierte Revision (`session.revision` existiert und wird geprüft).
- [ ] Proposal und Commit sind typologisch **und** sprachlich getrennt.

**Fachlichkeit (freies Rollenspiel)**
- [ ] Das Commit-Vokabular ist mindestens so reich wie das Auflösungsvokabular der KI; kein Status wird auf einen
      ärmeren Wert abgebildet.
- [ ] Eine freie Handlung ohne vormodellierten Szenenübergang wirkt und lässt den Beat fortschreiten.
- [ ] `blocked` tritt nur bei situativ tatsächlich Unmöglichem auf.
- [ ] Alle Pflichtfelder überleben ihre modellierten Envelope-Intervalle — geprüft per Kontrakttest, nicht per
      Token-Präsenz.
- [ ] Beat- und Canonical-Path-Autorität ist eindeutig; YAML bleibt nachvollziehbare authored content truth.

**Kosten und Betrieb**
- [ ] Jeder Modellaufruf ist kostenattribuiert; `unattributed_call_count == 0`.
- [ ] Kosten pro Zug sind aus dem Trace rekonstruierbar, inklusive Übersetzung, Self-Correction und Fallback.
- [ ] Weiches Budget warnt, harte Obergrenze bremst; Überschreitung ist ein benannter Zustand.
- [ ] Der Wiederholungsversuch ist billiger als der Erstversuch.
- [ ] Technisches Versagen führt zu einem deterministischen Weiterspiel-Zug ohne zusätzlichen Modellaufruf und
      ist von erzählerischer Verhinderung unterscheidbar.
- [ ] Primary, Degraded, Recovery und Reconnect sind getestet.

**Sichtbarkeit und Beweisbarkeit**
- [ ] Player-visible Projektionen sind vollständig, geordnet und dedupliziert.
- [ ] Trace-Lücken werden als partiell ausgewiesen, nie als vollständig.
- [ ] `quality_class` ist bis zur Auslieferung unterscheidbar; kein Kollaps auf ein Boolean.
- [ ] JSON, JUnit und SARIF bilden denselben Audit ab; `dry-run` schreibt nichts; wiederholte Exporte sind idempotent.
- [ ] UML-Vorschauen werden als CI-Artefakt veröffentlicht, auch bei Gate-Fehlern.

**Struktur und Altpfade**
- [ ] Kein `SOURCE`/`SOURCE_LINES`-Modul und kein `exec(compile(` im gesamten Repository.
- [ ] Kein Legacy-Loader, Re-Export, Registry-Eintrag oder stiller Fallback hält die alte Architektur am Leben.
- [ ] Keine Paketnamenskollision; kein `sys.path`-Vorspiel in `conftest.py`.
- [ ] Obsolete Pfade sind physisch **und** funktional entfernt; keine unnötigen Kompatibilitätsadapter.
- [ ] Jede verbliebene Übergangsfassade hat Besitzer, Zweck, Nutzungsmessung, Ablaufkriterium, Removal-Ticket
      und einen Test gegen Autoritätsübernahme.

**Tests und Gates**
- [ ] Alle Tests gehören zu einem Suite-Katalog oder einer begründeten Ausnahme.
- [ ] Integrationstests verwenden reale, strikt disposable Grenzen.
- [ ] Keine tautologische Deckungskennzahl; `out_of_scope` ist begründet und gedeckelt.
- [ ] SAD, UML, Source-Bindings und Canon stimmen mit dem Code überein.
- [ ] Git-, Source-, Import-, Callsite-, Test- und Drift-Gates sind grün.
- [ ] Jede gelöste Drift besitzt Produktionspfad-Evidenz.

---

## Selbstprüfung des Plans

**Abdeckung gegen das Driftregister:** DRIFT-001 (W2/W6) · DRIFT-002 (W3) · DRIFT-003 (W4/W8) ·
DRIFT-004 (W7) · DRIFT-005 (W3) · DRIFT-006 (W1/W5/W9) · DRIFT-007 (W8) · DRIFT-008 (W8) · DRIFT-009 (W8) ·
DRIFT-010/011 (superseded, keine Arbeit) · DRIFT-012 (W8) · D13 (W6) · D14 (W6) · D15 (W1/W5/W9) ·
D16 (W2) · D17 (W2) · D18 (W2 Messung, W3/W4 Behebung) · D19 (W8) · D20 (W8) · D21 (W6) · D22 (W9) ·
D23 (W7) · D24 (W9) · D25 (W8) · D26 (W4) · D27 (W0) · D28 (W0/W2) · D29 (W0/W4) · D30 (W0) · D31 (W3).
**Keine Lücke.**

**Reihenfolgeprüfung:** Autoritäts- und Transaktionsgrenzen (W2–W4) liegen vor der Umbenennung (W6).
Entshardung des Autoritätspfads (W1) liegt vor jeder Aussage über Schreibtopologie (W2). Fähigkeitsmigration
(W4) liegt vor dem Entfernen der Quelle (W6). Messung (W0) liegt vor jeder Kostenentscheidung.

**Bekannte Restunsicherheiten**
- Der Umfang von Welle 5 (171 Module) ist der größte Einzelposten. Falls sich der Rückbau als riskanter
  erweist als angenommen, ist die Welle nach Subsystem teilbar (ai_stack / backend), ohne die Reihenfolge zu
  verletzen.
- Der Leserkreis der DB-Tabelle `runtime_sessions` ist statisch nicht abschließend bestimmbar (möglicher
  Zugriff außerhalb Python). Welle 6 beginnt deshalb mit einer Leserprüfung, nicht mit der Löschung.
- Die reale Häufigkeit von `blocked` und die reale durchschnittliche Aufrufzahl pro Zug sind unbekannt, weil sie
  nie gemessen wurden. Welle 0 liefert beide Zahlen; die Schwellenwerte in W3 und W4 werden erst danach
  festgelegt.
