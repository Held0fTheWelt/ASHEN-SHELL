# AUFTRAG — Better Tomorrow: vollständige Drift-Sanierung (Welle 0 bis 9)

> **Dies ist ein Ein-Schuss-Auftrag.** Du arbeitest ihn vollständig durch, von Welle 0 bis Welle 9, bis die
> Definition of Done erfüllt ist. Du hörst nicht nach einer Welle auf. Du fragst nicht nach der nächsten
> Freigabe, außer bei den vier ausdrücklich benannten Human-Gates. Wenn du blockierst, weichst du nach den
> hinterlegten Ausweichstrategien aus und arbeitest weiter.

---

## 0. Mission

Das Projekt „Better Tomorrow" (= „World of Shadows", Repository `D:\WorldOfShadows`) ist ein Live-Rollenspiel mit
Beat-Struktur am Beispiel „God of Carnage". Es hat teilweise funktioniert, war aber **massiv zu teuer**, ließ sich
**nicht warten** und **nicht diagnostizieren**.

Deine Mission: Genau eine nachweisbare Autorität für den Live-Session-Zustand herstellen, ein Commit-Vokabular
schaffen, das freies Rollenspiel tatsächlich trägt, die Kosten pro Zug messbar und begrenzt machen — und das
Repository in einen Zustand bringen, in dem statische Aussagen wieder beweiskräftig sind.

**Erfolgsmaß:** Die vollständige Definition of Done in Abschnitt 9 ist erfüllt, jeder Punkt durch
Produktionspfad-Evidenz belegt.

---

## 1. Deine drei Wahrheitsquellen (in dieser Rangfolge)

1. **Der aktuelle Quellcode und beobachtbares Verhalten.** Höchste Autorität. Wenn ein Dokument dem Code
   widerspricht, hat der Code recht — und du korrigierst das Dokument.
2. **Der Analysebericht** `docs/superpowers/plans/2026-07-31-better-tomorrow-drift-landscape-analysis.md`.
   Enthält das vollständige Driftregister (DRIFT-001…012 neu bewertet, D13…D31 neu), die Autoritätsmatrix,
   den Envelope-Feldfluss, das Legacy-Inventar und den Abhängigkeitsgraphen. **Lies ihn vollständig, bevor du
   beginnst.**
3. **Der Gesamtplan** `docs/superpowers/plans/2026-07-31-better-tomorrow-drift-remediation-runway.md`.
   Enthält die zehn Wellen mit Zielen, betroffenen Dateien, Schritten, Tests, Cleaning, SAD-/UML-Pflege,
   Gate-Änderungen, Rollback und Exit-Kriterien. **Er ist deine Arbeitsanweisung.**

**Ausdrücklich KEINE Autorität:**
- Dateinamen, insbesondere `_legacy_*`, `final`, `complete`, `canonical`.
- Statuslabels und alte grüne Testberichte (`tests/reports/**`, `audit_*.json`, `engine_run_last.txt`).
- Das Legacy-Register der Werkzeugplattform (`'fy'-suites/delagecy/legacy_removal_tracker.md`) — es widerspricht
  dem Code nachweislich (führt `world-engine/app/runtime/branching_turn_executor.py:110` als
  „approved_for_removal", die Datei existiert weiter).
- `E:\New folder` — read-only Archäologie. Historische MVPs, Arbeitsaufträge und Zip-Pakete. Du darfst dort
  **lesen**, um Entstehung und Motivation zu verstehen. Du darfst von dort **niemals** importieren, kopieren,
  bauen oder eine Abhängigkeit ableiten.

---

## 2. Verbindliche Entscheidungen (bereits getroffen, nicht neu verhandeln)

| # | Entscheidung |
| --- | --- |
| **E1** | Die World-Engine bleibt Heimat der Live-Autorität. Fähigkeiten aus D26 werden dorthin migriert, **bevor** der ruhende Backend-Cluster entfernt wird. |
| **E2** | String-Shard-Rückbau **vollständig** (202 Module), gestaffelt nach Autoritätsnähe: world-engine → ai_stack → backend → tools. |
| **E3** | `'fy'-suites` wird in ein eigenes Repository herausgelöst (Welle 9). |
| **E4** | `world-engine/app` → `world_engine` umbenennen — **erst nach** vollständiger Entshardung. |
| **E5** | Welche Fähigkeiten früher **absichtlich** abgeschaltet wurden, ist aus dem Repo nachweisbar nicht rekonstruierbar. Deshalb: jede migrierte Fähigkeit bekommt einen **ausdrücklichen Schalter mit dokumentierter und begründeter Standardstellung**. Du rätst nicht. |
| **E6** | Interne Auflösungssprache bleibt Englisch. Aber: eigene Routing-Task-Klasse `translation` auf ein günstiges Modell, harte Kostengrenze, Ergebnis-Cache pro Zug, volle Kostenattribution. |
| **E7** | Bei **technischem** Versagen (Modell liefert nichts Brauchbares / Budget erschöpft): erst **ein** günstiger Wiederholungsversuch mit **reduziertem** Kontext, dann ein deterministischer Weiterspiel-Zug ohne weiteren Modellaufruf. |
| **E8** | Zugbudget ist **weich**: messen und warnen; nur eine deutlich höhere harte Obergrenze bricht ab. |
| **E9** | Freies Rollenspiel hat Vorrang. `MutationPolicy` startet **permissiv** (erlaubt, sofern nicht ausdrücklich verboten). `blocked` ist reserviert für situativ tatsächlich Unmögliches. |

**Wichtige Klarstellung zu E9:** Das Delta-/Guard-Modell aus Welle 4 ist **keine Verschärfung**. Es erlaubt,
dass eine Handlung *teilweise* wirkt, statt sie ganz oder gar nicht zu übernehmen. Die heutige
Alles-oder-nichts-Logik auf der Szenen-Übergangskarte ist die restriktive Variante. Wenn du an irgendeiner
Stelle vor der Wahl stehst, mehr zu erlauben oder mehr zu blockieren: **erlaube mehr.**

---

## 3. Die sieben systemischen Ursachen (damit du das Muster erkennst)

Du wirst diesen Mustern immer wieder begegnen. Erkenne sie und wiederhole sie nicht:

1. **Metrikgetriebenes Refactoring.** Dateien wurden auf Größenmetriken getrimmt, indem Code in Strings
   verwandelt wurde (`SOURCE_LINES = [...]` + `exec(compile(...))`). 202 Module. **Erzeuge niemals ein solches
   Modul.**
2. **Additive Reparaturwellen ohne Retirement.** Jede Reparatur legte eine neue Generation *neben* die alte.
   Ergebnis: drei Runtime-Generationen, sieben Persistenzressourcen. **Wenn du etwas ersetzt, entfernst du das
   Ersetzte in derselben Welle.**
3. **Gates prüfen Deklaration statt Verhalten.** Katalog gegen Katalog, Token-Präsenz statt Fluss, tautologische
   Deckungsquoten. **Jede neue Prüfung muss am Produktionspfad ansetzen.**
4. **Zwei konkurrierende Governance-Welten** im selben Repo.
5. **Paket-/Pfad-Mehrdeutigkeit.** `backend/app` und `world-engine/app` heißen beide `app`, aufgelöst über
   `sys.path`-Reihenfolge in `conftest.py:33-37`.
6. **Dateiname als Statusbeweis.**
7. **Reichtum wird an der Autoritätsgrenze eingeebnet.** Dreimal dasselbe Muster: sieben KI-Auflösungsstatus →
   vier Commit-Status; vier Qualitätsklassen → ein Boolean; Runtime-Intelligenz → flache Spielerprojektion.
   **Wenn du eine Grenze anfasst: verarme sie nicht.**

---

## 4. Arbeitsmodus

### 4.1 Fortschrittsprotokoll (ZUERST anlegen — überlebenswichtig)

Cursor-Sessions brechen ab. Damit ein frischer Agent nahtlos weitermacht, führst du ein Protokoll:

**Datei:** `docs/superpowers/plans/DRIFT_SANIERUNG_FORTSCHRITT.md`

Lege sie als **allererste Handlung** an (falls sie schon existiert: lies sie und mach dort weiter, wo sie endet).
Format:

```markdown
# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: <n>
Aktueller Schritt: <Kurzbeschreibung>
Letzter grüner Commit: <sha>
Baseline-Testlauf: <Pfad zur Baseline-Datei>

## Wellen
- [ ] W0 Kostenwahrheit
- [ ] W1 Entshardung Autoritätspfad
- [ ] W2 Schreibtopologie
- [ ] W3 Commit-Vokabular
- [ ] W4 Fähigkeitsmigration
- [ ] W5 Entshardung Rest
- [ ] W6 Paketnamen + Retirement
- [ ] W7 Content-Wahrheit
- [ ] W8 Test-/CI-/Gate-Wahrheit
- [ ] W9 Werkzeugplattform + Hygiene

## Messergebnisse aus Welle 0
Aus W0-A (Langfuse-Historie):
- Verwertbare Historie vorhanden? (ja/nein, Trace-Anzahl, Zeitraum):
- Promptgröße pro Zug (Median / p95):
- Tokenverbrauch, Latenz, Tokens/s (final generation):
- Adapter- und Invocation-Mode-Verteilung:

Aus W0-B (Instrumentierung):
- Modellaufrufe pro Zug (Median / p95):
- Kostenanteil Übersetzung:
- Häufigkeit `blocked` im Beispielspielverlauf:

Abgleich:
- Differenz zwischen Langfuse-Sicht (max. 2/Zug) und gemessener Aufrufzahl:

## Entscheidungen, die ich selbst getroffen habe
| Datum | Welle | Frage | Entscheidung | Begründung |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Vorgeschlagene Auflösung |

## Journal
(ein Absatz je abgeschlossenem Schritt: was, Evidenz, Testausgabe)
```

Aktualisiere die Datei **nach jedem abgeschlossenen Schritt**, nicht erst am Wellenende. Committe sie mit.

### 4.2 Vorflug (vor jeder Welle)

- [ ] `git status` prüfen. **Die uncommitteten Änderungen des Benutzers gehören ihm.** Stand bei Auftragserteilung:
      21 modifizierte + 4 unversionierte Dateien im Umfeld `tools/architecture_assurance`,
      `UML/Project/architecture-drift`, `tests/architecture_assurance`, `docs/architecture/**`.
      Du überschreibst und löschst dort nichts, was nicht eindeutig zum Auftrag gehört. Im Zweifel: unberührt lassen.
- [ ] `.git/index.lock` prüfen — falls vorhanden, warten statt zu erzwingen (parallele Sessions möglich).
- [ ] Baseline-Testlauf erzeugen und ablegen (siehe 4.5). **Ohne Baseline keine Welle.**
- [ ] Wellenabschnitt im Gesamtplan vollständig lesen.
- [ ] Die im Wellenabschnitt genannten Quellanker öffnen und verifizieren, dass sie noch stimmen
      (Zeilennummern verschieben sich). Wenn ein Anker nicht mehr passt: neuen suchen, im Plan korrigieren,
      im Protokoll vermerken.

### 4.3 Arbeitsweise innerhalb einer Welle

Strikt test-getrieben, Charakterisierung zuerst:

1. **Characterization Test schreiben** — er hält fest, was das System **heute** tut, nicht was es soll.
   Er muss **grün** sein, bevor du irgendetwas änderst.
2. **Failing Test für das Zielverhalten schreiben.** Ausführen, Fehlschlag **beobachten**, Fehlermeldung
   prüfen. Ein Test, den du nicht hast fehlschlagen sehen, beweist nichts.
3. **Minimale Implementierung**, bis der Test grün ist.
4. **Alle Tests** der betroffenen Komponente ausführen. Charakterisierungstests müssen grün bleiben oder
   bewusst aktualisiert werden (mit Begründung im Protokoll).
5. **Cleaning in derselben Welle** — siehe 4.4.
6. **Committen.** Kleine, thematisch geschlossene Commits.

### 4.4 Cleaning-Pflicht (keine kosmetische Abschlussarbeit)

„Entfernt" heißt nicht, dass der Primärpfad den Code nicht mehr aufruft. Vor jeder Löschung:

1. Aktueller Consumer- und Importnachweis (statisch **und** String-/Registry-Suche).
2. Git-Historie und ursprünglicher Zweck (`git log`, `git blame`).
3. Characterization Tests für noch relevantes Verhalten.
4. Nachgewiesener Ersatzpfad.
5. Tests für Primary-, Degraded- und Recovery-Verhalten.
6. Suche nach dynamischen und stringbasierten Referenzen —
   **kritisch in diesem Repo**, weil 202 Module Code als Strings enthalten. Ein `grep` auf den Symbolnamen
   findet Referenzen, die ein Importgraph übersieht.
7. Überprüfbarer Retirement-Plan im Protokoll.

Nach der Löschung entfernst du in derselben Welle auch: Importe und Re-Exporte, Loader und dynamische Loader,
Registry-Einträge und Dispatch-Tabellen, Kompatibilitätsfassaden, tote Manager-Methoden, veraltete
Konfigurationen und Feature-Flags, Startup-/DI-Pfade, veraltete Tests und Fixtures, Mock-Adapter die nur den
alten Pfad erhalten, Dokumentationsverweise, UML-Knoten und -Beziehungen, CI- und Skript-Einträge,
Packaging-Verweise, Datenmigrationen, obsolete Telemetrie- und Trace-Namen, leere Module und reine
Weiterleitungsdateien.

**Bevorzuge vollständiges Entfernen.** Wenn eine Übergangsfassade unvermeidbar ist, braucht sie alle sechs:
benannten Besitzer, eng begrenzten Zweck, Nutzungsmessung, Ablaufkriterium, Removal-Ticket, und einen Test,
der verhindert, dass sie wieder Autorität übernimmt. Fehlt eines davon: nicht bauen.

### 4.5 Testausführung

Der Suite-Katalog ist `tests/run_tests.py` (2538 Zeilen). **Achtung:** Bis Welle 8 rufen die CI-Workflows
`pytest` direkt auf und **nicht** diesen Katalog — beide Wahrheiten existieren nebeneinander. Bis Welle 8
führst du **beide** aus.

Baseline-Verfahren: Vor jeder Welle einen vollständigen Lauf der betroffenen Suiten in eine Datei unter
`docs/superpowers/plans/baselines/W<n>-vorher.txt` schreiben. Das Repo hat vorbestehende rote Tests
(z. B. `world-engine/tests/test_turn_execution.py` mit einem bekannten Importfehler auf
`app.runtime.session_manager`). **Ein vorbestehend roter Test ist kein Grund, die Welle zu stoppen** — aber er
darf nicht *zusätzlich* rot werden, und die Menge der roten Tests darf nach der Welle nicht wachsen.

Relevante Suiten:
```
python tests/run_tests.py --suite all
python -m pytest world-engine/tests -q
python -m pytest ai_stack/tests -q
python -m pytest backend/tests -q
python -m pytest tests/ -q
python -m tools.architecture_assurance generate --dry-run
python -m tools.architecture_assurance audit
```

### 4.6 Die Langfuse-Umgebung — vorhandene Messungen zuerst nutzen

Es existiert eine vollständige, self-hosted Langfuse-Installation mit **persistenten Volumes**
(`docker-compose.langfuse.yml:205-213`). Historische Traces früherer Spielsitzungen sind daher vermutlich
vorhanden. **Nutze sie, bevor du instrumentierst** — sie kosten dich nichts und liefern echte Zahlen.

**Starten:**
```
python docker-up.py langfuse-up
```
(`docker-up.py:8-10`; die reine Anwendung ohne Langfuse startet mit `python docker-up.py --no-langfuse up`.)

**Programmatisch abfragen** statt über die UI: `tools/mcp_server/handlers/langfuse_verify/` (47 Dateien)
enthält bereits einen Trace-Query-Pfad — `31_langfuse_trace_query.py`,
`23_handler_trace_fetch_and_query.py`, `20_runtime_matrix_query_client.py`,
`43_handler_runtime_summary_views.py`. **Diese Dateien sind selbst nummerierte Shards** mit
`loader.py:64` `exec(compiled, namespace)`; sie gehören zu D15 und werden erst in Welle 9 zurückgebaut.
In Welle 0 **benutzt** du sie, du baust sie nicht um.

**Was die Historie liefert:** Zugzahl und Sitzungsverläufe (Trace-Namen `world-engine.turn.execute`,
`world-engine.session.create`) · **Promptgröße pro Zug** (`LANGFUSE_CAPTURE_PROMPTS: true`, Prompt bis
20 000 Zeichen gespeichert — das beziffert den Kontext-Bloat direkt, ohne eine Zeile Code) · Tokenverbrauch,
Latenz, Tokens/s, Time-to-first-token · Adapter- und Invocation-Mode-Verteilung · `turn_kind`, `turn_number`,
`opening_turn`.

**Was die Historie ausdrücklich NICHT liefert — und warum das wichtig ist:**
`_emit_langfuse_evidence_observations_000.py:96-98` ruft
`adapter.record_generation(name="story.model.generation", …)` **einmal pro Zug**, rekonstruiert aus
`path_summary`, markiert per Metadatum `generation_observation_source: "primary_attempt" | "final"`.
Langfuse sieht also **höchstens zwei** Generierungen pro Zug. Die beiden Übersetzungsaufrufe, die bis zu drei
Self-Correction-Versuche und der Fallback sind **auch in Langfuse unsichtbar** — dieselbe strukturelle
Blindstelle wie bei `phase_costs`, weil beide aus derselben `path_summary` gespeist werden.

**Also:** Die Zahl „Modellaufrufe pro Zug" ist aus der Historie **nicht** ableitbar. Sie bleibt Aufgabe der
Instrumentierung in W0-B. Nimm keine Zahl aus Langfuse als Aufrufzahl — sie wäre systematisch zu niedrig.
Genau diese Diskrepanz ist der Kern von D27.

### 4.7 Commits

- Explizite Pfade stagen. **Niemals `git add -A`.**
- Auf einem Arbeitsbranch arbeiten, nicht direkt auf `master`. Branch: `drift-sanierung/w<n>-<kurzname>`.
- Commit-Nachricht: was und warum, nicht wie. Keine Statusbehauptungen wie „complete" ohne Evidenz.
- Kein `git push`, kein Merge nach `master` — das ist ein Human-Gate (siehe 6).

---

## 5. Die zehn Wellen — Kurzfassung

Die vollständigen Anweisungen stehen im Gesamtplan. Hier nur Ziel, Reihenfolgegrund und das Abbruchkriterium.

| Welle | Ziel | Warum hier | Fertig, wenn |
| ---: | --- | --- | --- |
| **0** | **W0-A** vorhandene Langfuse-Historie auswerten (kein Code) · **W0-B** Kostenattribution an der **Adapter-Naht**, weiches Budget, `quality_class` bis zur Auslieferung · **W0-C** Langfuse-Emission aus dem Ledger speisen | Unabhängig von allem. Liefert die Zahlen, die W3 und W4 brauchen. W0-A und W0-B brauchen **keinen** Shard-Rückbau; nur W0-C berührt einen Shard und darf nach W1 nachgezogen werden. | `unattributed_call_count == 0`; alle Aufrufe im Trace mit Phase und Versuchsindex; Promptgrößen-Verteilung belegt |
| **1** | Entshardung des world-engine-Managers (33 `_legacy_sources` + Loader + 6 Weiterleiter) | `_finalize_committed_turn` enthält den Persistenzaufruf. Ohne Rückbau ist W2 unbeweisbar. | Kein `SOURCE`-Modul unter `world-engine/app`; Charakterisierung identisch |
| **2** | Sieben Persistenzressourcen mit je einem Sink; `PersistOutcome`; `session.revision` | Autoritätsgrenze vor Fachlichkeit | Künstlicher zweiter Writer bricht das Gate; keine Route schreibt am Manager vorbei |
| **3** | `SituationStatus` um `partial`/`prevented`/`allowed_offscreen` erweitern; Commit auf Zustandsänderungen statt Übergangskarte | Das Produktziel. Braucht die Revision aus W2. | Freie Handlung ohne Szenenübergang wirkt und lässt den Beat fortschreiten |
| **4** | Fünf Fähigkeiten migrieren (Delta/Guard, MutationPolicy, Source-Gate, Recovery-Policies, Ending-Legalität) + E7-Kette | Migration **vor** Löschung der Quelle | Alle fünf im World-Engine-Produktionspfad durch Kontrakttest belegt; Retry billiger als Erstversuch |
| **5** | Entshardung ai_stack (63) + Backend-Game-API (66) + Rest backend | Vor der Umbenennung, damit W6 auf echtem Python arbeitet | Routeninventar unverändert; kein `exec(compile(` in den drei Produktionsrooten |
| **6** | `world-engine/app` → `world_engine`; ruhenden Backend-Cluster entfernen; Routing-Governance nach `backend/app/model_governance/`; verwaiste Module löschen | Erst nach Migration (W4) und Entshardung (W5) | Import ist eindeutig; kein Modul ohne Produktionskonsument unter `world_engine/runtime` |
| **7** | YAML als einzige autorisierte Inhaltsquelle; kompilierter Content-Vertrag; `goc_solo_builtin_*` entfernen | Nach der Strukturbereinigung | Jeder Laufzeitfakt trägt Modulpfad und Version; Export byte-identisch wiederholbar |
| **8** | Suite-Katalog erzeugt CI; `out_of_scope` begründungspflichtig; Element-Aliasing auflösen; `TurnTrace`-Kontrakt | Parallel zu W7 möglich | Kein direkter `pytest`-Aufruf in Workflows; keine tautologische Kennzahl |
| **9** | `'fy'-suites` herauslösen; `tools/` entsharden; Arbeitsbaum bereinigen | Zuletzt, weil es die Werkzeuge selbst betrifft | Kein `SOURCE`-Modul repoweit; keine Repo-Kopien im Arbeitsbaum |

**Parallelisierung:** W7 und W8 hängen beide nur von W6 ab und sind voneinander unabhängig — du darfst sie in
beliebiger Reihenfolge oder verschränkt bearbeiten. Alle anderen Wellen sind strikt sequenziell.

**Vier Zahlen aus Welle 0, die du später brauchst:** Modellaufrufe pro Zug (Median und p95) · Promptgröße pro
Zug (Median und p95) · Kostenanteil der Übersetzung · Häufigkeit von `blocked` im Beispielspielverlauf.
Die Promptgröße kommt aus W0-A (Langfuse-Historie), die übrigen drei aus W0-B (Instrumentierung). Trage alle
ins Protokoll ein. Die Schwellenwerte in W3 und W4 legst du **auf Basis dieser Zahlen** fest, nicht nach Gefühl.

---

## 6. Human-Gates — nur diese vier Fälle stoppen dich

Bei allem anderen entscheidest du selbst nach den Regeln in Abschnitt 7.

| Gate | Warum | Was du tust |
| --- | --- | --- |
| **G1** | `git push` oder Merge nach `master`/`main` | Nie autonom. Arbeite auf dem Branch weiter, sammle die Commits. |
| **G2** | Löschen der DB-Tabelle `runtime_sessions` (Welle 6) | Leserkreis ist statisch nicht bestimmbar. Führe die Leserprüfung durch, dokumentiere das Ergebnis, **frage dann**. Arbeite in der Zwischenzeit am Rest von W6 weiter. |
| **G3** | Herauslösen von `'fy'-suites` in ein eigenes Repository (Welle 9) | Erzeugt ein neues Repo außerhalb dieses Baums. Bereite den `git subtree split` vor, dokumentiere den Befehl, **frage dann**. Arbeite an den übrigen W9-Punkten weiter. |
| **G4** | Eine Änderung würde uncommittete Benutzerdateien berühren | Nicht anfassen. Im Protokoll unter „Geparkte Probleme" eintragen, an anderer Stelle weiterarbeiten. |

Wenn ein Gate dich blockiert: **du hörst nicht auf.** Du parkst den Punkt und arbeitest den Rest der Welle
und die nächsten Wellen ab, soweit sie nicht davon abhängen.

---

## 7. Ausweichstrategien

Das Herzstück dieses Auftrags. Wenn eines dieser Probleme auftritt, wendest du die Regel an und arbeitest
weiter. Du fragst nicht nach.

### A1 — Charakterisierungstest lässt sich nicht schreiben (kein reproduzierbarer Pfad)

Ursache meist: der Pfad erfordert einen echten Modellaufruf oder eine externe Grenze.
**Regel:** Ersetze den Modellaufruf durch einen deterministischen Adapter (`MockModelAdapter` aus
`story_runtime_core/adapters.py` oder ein Testadapter nach dem Muster in
`ai_stack/tests/test_context_synthesis_retry_loop.py:20`). Wenn auch das nicht geht, charakterisiere die
**nächstinnere** Schicht, die deterministisch ist, und notiere im Protokoll ausdrücklich, welche äußere Schicht
unbelegt bleibt. **Fahre fort.** Ein unbelegter Rand ist besser als eine gestoppte Welle — aber er wird benannt,
nicht verschwiegen.

### A2 — Entshardung erzeugt abweichendes Verhalten

Ursache meist: die Shards wurden per `exec(..., module.__dict__)` bzw. `exec(..., globals(), namespace)`
ausgeführt und sahen Namen, die ein normales Modul nicht sieht (Sternimporte aus `._deps`, injizierte Globals).
**Regel:** Nicht raten. Vergleiche die Namensräume: dekodiere den Shard, sammle alle freien Namen per `ast`, und
mache jeden einzelnen zu einem expliziten Import. Wenn ein Name nirgends auflösbar ist, war er zur Laufzeit
injiziert — suche den Injektionsort (`_deps.py`, `_imports_00.py`, `external_imports_core.py`). **Erst wenn die
Charakterisierung wieder grün ist, gilt das Modul als zurückgebaut.**

### A3 — Eine Welle ist zu groß für eine Session

Besonders Welle 5 (171 Module).
**Regel:** Teile nach Subsystem oder Modulgruppe, **niemals** nach „erste Hälfte / zweite Hälfte". Jede
Teilwelle muss für sich grün sein und committet werden. Trage die Teilung ins Protokoll ein. Die
Wellenreihenfolge bleibt unverletzt, solange du keine spätere Welle vorziehst.

### A4 — Testsuite ist rot, aber schon vorher

**Regel:** Baseline aus 4.5 vergleichen. Wenn derselbe Test schon vorher rot war: notieren, weiterarbeiten,
**nicht reparieren** (das ist nicht dein Auftrag und erzeugt Rauschen). Wenn er *neu* rot ist: das ist deine
Änderung, sofort beheben, bevor du weitermachst.

### A5 — Das Architektur-Gate wird rot wegen fester Sollwerte

`tools/architecture_assurance/config.json:37-46` enthält harte Census-Zahlen (`discovered: 7511`,
`views: 89`, …). Jede Strukturänderung verschiebt sie.
**Regel:** Zuerst `python -m tools.architecture_assurance generate` laufen lassen und prüfen, ob die
Abweichung nur die regenerierten Manifeste betrifft. Wenn ja: Sollwerte anpassen **und im Commit begründen**,
warum die neue Zahl korrekt ist. Wenn die Abweichung ein echtes Finding ist (`BT-BINDING-MISSING`,
`BT-REPRESENTATION-ORPHAN`, `BT-VIEW-DEPTH`): das Finding beheben, nicht die Schwelle senken.
**Niemals eine Schwelle senken, um ein Finding verschwinden zu lassen.**

### A6 — Umbenennung (Welle 6) bricht Importe, die `grep` nicht findet

**Regel:** Nach der mechanischen Umbenennung drei zusätzliche Suchläufe:
(1) String-Literale mit `"app."` / `'app.'`; (2) `importlib.import_module`-Aufrufe mit zusammengesetzten Namen;
(3) Registry-/Dispatch-Tabellen und YAML-/JSON-Konfigurationen. Erst wenn alle drei leer sind, ist die
Umbenennung abgeschlossen. Der Test `test_import_determinism` ist der Abschlussbeweis.

### A7 — Drei Behebungsversuche sind gescheitert

**Regel:** Das ist kein Implementierungsproblem mehr, sondern ein Architekturproblem. Höre auf, Symptome zu
reparieren. Schreibe im Protokoll unter „Geparkte Probleme" auf: was du dreimal versucht hast, was jedes Mal
passierte, und welche Architekturannahme dadurch fragwürdig wird. Dann **arbeite an der nächsten unabhängigen
Aufgabe weiter**. Komm später zurück — oft löst eine spätere Welle das Problem nebenbei (typisch: ein Problem
in W2 löst sich, nachdem W1 den Code lesbar gemacht hat).

### A8 — Die Migration einer D26-Fähigkeit passt nicht auf die World-Engine-Datentypen

Der Backend-Code ist auf `SessionState` und `ContentModule` des Backends zugeschnitten.
**Regel:** Du migrierst das **Modell**, nicht den Code. Lies die Backend-Implementierung als Spezifikation,
schreibe eine neue Implementierung gegen die World-Engine-Typen, und belege die Äquivalenz durch Tests, die
dasselbe fachliche Verhalten prüfen. Kopiere niemals eine Datei zwischen den Subsystemen.

### A9 — Unklar, ob eine Fähigkeit früher absichtlich abgeschaltet wurde

**Regel:** Siehe E5 — das ist nachweisbar nicht rekonstruierbar. `degraded` taugt nicht als Beleg, weil es an
der Auslieferungsgrenze vier verschiedene Fälle auf ein Boolean kollabiert
(`story_window_entry_parts.py:257`). Du rätst nicht und du recherchierst nicht weiter. Du baust die Fähigkeit
hinter einem Schalter, wählst eine Standardstellung nach E9 (im Zweifel permissiv), und dokumentierst im
Schalterkommentar: Zweck, Standardstellung, Begründung, und was ein Abschalten bewirkt.

### A10 — Ein Schwellenwert wird gebraucht, aber die Messung fehlt

**Regel:** Wenn Welle 0 abgeschlossen ist, stehen die Zahlen im Protokoll — benutze sie. Wenn nicht:
implementiere den Mechanismus mit einem **bewusst großzügigen** Wert, markiere ihn im Code als
`# TODO(threshold): auf Basis der W0-Messung festlegen` und trage ihn im Protokoll unter „Geparkte Probleme"
ein. **Blockiere nicht.** Ein großzügiger Wert schadet weniger als eine gestoppte Welle — und weniger als ein
geratener strenger Wert, der Spielzüge abschneidet.

### A11 — Ein Löschkandidat hat noch einen Konsumenten, den der Plan nicht kennt

**Regel:** Löschen aufschieben, Konsumenten dokumentieren, prüfen ob der Konsument selbst obsolet ist. Wenn ja:
beide in derselben Welle entfernen. Wenn nein: den Ersatzpfad für diesen Konsumenten bauen, **dann** löschen.
Niemals löschen und den Konsumenten brechen lassen.

### A12 — Ein Test verlangt Verhalten, das E9 widerspricht

Es gibt Tests, die das heutige restriktive Verhalten festschreiben (z. B. dass eine Handlung ohne passenden
Szenenübergang `blocked` ergibt).
**Regel:** Der Test bildet den Ist-Zustand ab, nicht den Zielzustand. Aktualisiere ihn, dokumentiere die
Änderung im Protokoll mit Verweis auf E9 und D31. **Lösche ihn nicht** — er wird zum Test des neuen Verhaltens.

### A13 — Der Kontext reicht nicht, um eine große Datei zu bearbeiten

Betroffen u. a. `tests/run_tests.py` (2538 Z.), `world-engine/app/runtime/manager.py` (782 Z.),
`model_catalog.json` (873 Z. / 172 KB).
**Regel:** Nicht die ganze Datei neu schreiben. Gezielte Bereichsbearbeitungen mit vorherigem Lesen genau des
betroffenen Bereichs. Bei JSON-Katalogen: mit einem kleinen Python-Skript ändern statt von Hand, damit die
Struktur nicht bricht — und das Skript nach Gebrauch löschen (es ist kein Produktionsartefakt).

### A15 — Langfuse startet nicht, oder Docker ist nicht verfügbar

**Regel:** Kein Blocker. Die Langfuse-Historie ist eine **Abkürzung**, keine Voraussetzung. Notiere im
Protokoll, was genau fehlschlug (Befehl, Ausgabe), überspringe W0-A und beginne direkt mit W0-B
(Adapter-Ledger). Die Instrumentierung liefert dieselben Zahlen — sie kostet nur einen zusätzlichen
Spieldurchlauf. Versuche den Start **einmal** erneut nach dem offensichtlichen Fix (fehlende `.env`-Werte:
`docker-up.py:62-110` enthält die Defaults). Danach: weiterarbeiten, nicht reparieren.

### A16 — Langfuse läuft, enthält aber keine oder unbrauchbare historische Daten

**Regel:** Auch kein Blocker. Halte im Protokoll fest: Trace-Anzahl, ältester und jüngster Trace, warum
unbrauchbar (z. B. nur Testläufe, nur `mock`-Adapter, falsches `environment`). Gehe zu W0-B. **Erzeuge nach
W0-B einen eigenen Referenz-Spieldurchlauf** und miss daran — das ist ohnehin die sauberere Grundlage, weil du
dann jeden Aufruf siehst und nicht nur zwei.

### A17 — Langfuse-Schlüssel oder Projekt fehlen

`LANGFUSE_PUBLIC_KEY` und `LANGFUSE_SECRET_KEY` sind in `docker-compose.langfuse.yml:70-71` leer vorbelegt.
**Regel:** Beim ersten Start ein lokales Projekt anlegen und die Schlüssel in die lokale `.env` eintragen —
**nicht** in eine getrackte Datei. `.env` ist gitignored (`.gitignore`), `.env.langfuse.example` ist die
Vorlage. Wenn das Anlegen scheitert: A15 anwenden.

### A18 — Die historischen Daten widersprechen dem Analysebericht

**Regel:** Die Daten gewinnen — sie sind Laufzeitevidenz, der Bericht ist statische Analyse und markiert
Verhaltensaussagen ausdrücklich als **[V]** (vermutet). Korrigiere den Bericht, notiere die Korrektur im
Protokoll, arbeite weiter. Das ist ein **erwünschtes** Ergebnis, kein Problem: genau dafür wird gemessen.
Ein Widerspruch bei D18 (schreiben Ablehnungen?) oder D31 (wie oft `blocked`?) ist besonders wertvoll —
trage ihn prominent ins Protokoll ein, weil er die Schwellenwerte in W3 und W4 beeinflusst.

### A14 — Etwas im Repo widerspricht dem Analysebericht

**Regel:** Der Code gewinnt (Abschnitt 1). Korrigiere den Bericht, notiere die Korrektur im Protokoll,
arbeite weiter. Das ist erwartet: Zeilennummern verschieben sich, und der Bericht wurde ohne Codeausführung
erstellt — Verhaltensaussagen darin sind ausdrücklich als **[V]** (vermutet) markiert und müssen von dir
gemessen werden, nicht geglaubt.

---

## 8. Was du niemals tust

- Einen `SOURCE`/`SOURCE_LINES`-String-Shard oder `exec(compile(...))` neu erzeugen.
- Eine neue Kompatibilitätsschicht, Weiterleitungsfassade oder Abstraktion einführen, die nur eine weitere
  Architekturwahrheit schafft.
- Eine Gate-Schwelle senken, um ein Finding zum Verschwinden zu bringen.
- Aus `E:\New folder` importieren, kopieren oder eine Abhängigkeit ableiten.
- `git add -A` verwenden.
- `git push`, mergen oder auf `master` committen.
- Uncommittete Benutzerdateien überschreiben oder löschen.
- Eine Welle als abgeschlossen melden, ohne dass ihre Exit-Kriterien belegt sind.
- Ein Testergebnis behaupten, das du nicht ausgeführt hast. Wenn ein Test fehlschlägt: sag es mit der Ausgabe.
- Einen Schritt überspringen und ihn als erledigt markieren.
- Bei Unsicherheit über E9 die restriktivere Variante wählen.

---

## 9. Definition of Done

Erst wenn **alle** Punkte belegt sind, ist der Auftrag erfüllt. Dateipräsenz, Dateiname und grüne Altberichte
zählen ausdrücklich nicht als Beleg.

**Autorität und Persistenz**
- [ ] Genau eine autoritative Live-Session-Write-Topologie; sieben benannte Ressourcen mit je einem Sink.
- [ ] Keine nicht katalogisierte Session-Persistenz-Callsite; ein künstlicher zweiter Writer bricht das Gate.
- [ ] Ablehnungen verändern keine persistierte Revision (`session.revision` existiert und wird geprüft).
- [ ] Proposal und Commit sind typologisch und sprachlich getrennt.

**Fachlichkeit (freies Rollenspiel)**
- [ ] Das Commit-Vokabular ist mindestens so reich wie das Auflösungsvokabular der KI; kein Status wird auf
      einen ärmeren Wert abgebildet.
- [ ] Eine freie Handlung ohne vormodellierten Szenenübergang wirkt und lässt den Beat fortschreiten.
- [ ] `blocked` tritt nur bei situativ tatsächlich Unmöglichem auf.
- [ ] Alle Pflichtfelder überleben ihre modellierten Envelope-Intervalle — per Kontrakttest, nicht per
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
- [ ] JSON, JUnit und SARIF bilden denselben Audit ab; `dry-run` schreibt nichts; wiederholte Exporte sind
      idempotent.
- [ ] UML-Vorschauen werden als CI-Artefakt veröffentlicht, auch bei Gate-Fehlern.

**Struktur und Altpfade**
- [ ] Kein `SOURCE`/`SOURCE_LINES`-Modul und kein `exec(compile(` im gesamten Repository.
- [ ] Kein Legacy-Loader, Re-Export, Registry-Eintrag oder stiller Fallback hält die alte Architektur am Leben.
- [ ] Keine Paketnamenskollision; kein `sys.path`-Vorspiel in `conftest.py`.
- [ ] Obsolete Pfade sind physisch und funktional entfernt; keine unnötigen Kompatibilitätsadapter.
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

## 10. Abschlussbericht

Wenn die Definition of Done erfüllt ist, schreibe
`docs/superpowers/plans/DRIFT_SANIERUNG_ABSCHLUSS.md` mit:

1. Je Welle: was gebaut, was gelöscht, welche Tests belegen es (mit tatsächlicher Testausgabe).
2. Die drei Messwerte aus Welle 0 **und** dieselben Messwerte nach Welle 4 — der Kostenvergleich ist das
   wichtigste Einzelergebnis dieses Auftrags.
3. Alle Entscheidungen, die du selbst getroffen hast, mit Begründung.
4. Alle geparkten Probleme, die offen geblieben sind, mit Vorschlag zur Auflösung.
5. Die vier Human-Gates: welche wurden erreicht, was steht zur Freigabe an.
6. Eine ehrliche Restliste: was ist **nicht** belegt, und warum.

**Punkt 6 ist Pflicht.** Ein Abschlussbericht ohne Restliste ist ein Warnsignal, kein Erfolg.

---

## 11. Jetzt anfangen

1. Lies `docs/superpowers/plans/2026-07-31-better-tomorrow-drift-landscape-analysis.md` vollständig.
2. Lies `docs/superpowers/plans/2026-07-31-better-tomorrow-drift-remediation-runway.md` vollständig.
3. Lege `docs/superpowers/plans/DRIFT_SANIERUNG_FORTSCHRITT.md` an (oder lies sie, falls vorhanden).
4. `git status` prüfen, Arbeitsbranch anlegen.
5. Baseline-Testlauf für Welle 0 erzeugen.
6. **W0-A zuerst:** `python docker-up.py langfuse-up`, historische Traces auswerten (Abschnitt 4.6).
   Das kostet dich fast nichts und liefert die Promptgrößen-Verteilung ohne eine einzige Codeänderung.
   Wenn es fehlschlägt: A15/A16/A17 anwenden und direkt mit W0-B weitermachen.
7. Dann W0-B, W0-C, und weiter durch alle Wellen.

Arbeite durch bis Welle 9. Halte nur an den vier Human-Gates an — und auch dort nur für den betroffenen Punkt,
nicht für den ganzen Auftrag.
