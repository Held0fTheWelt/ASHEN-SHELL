# Drift-Sanierung — Human-Gate-Entscheidungen

**Datum:** 2026-07-31
**Entschieden von:** Benutzer (explizit, auf Vorlage des Planers)
**Gilt für Branch:** `drift-sanierung/w6-package-retirement`
**Stand bei Entscheidung:** HEAD `de2cff5b`

Dieses Dokument ersetzt die Zeilen „BLOCKED — awaiting explicit user yes" in
`DRIFT_SANIERUNG_FORTSCHRITT.md` und `DRIFT_SANIERUNG_ABSCHLUSS.md`.
Bei Widerspruch gilt dieses Dokument.

---

## G1 — Kein Push

**Unverändert: kein Push.** Der Branch bleibt lokal, bis der Benutzer Merge und Push
getrennt freigibt. Keine Ausnahme, auch nicht für einen „nur Dokumentation"-Commit.

---

## G2 — `runtime_sessions` droppen: **FREIGEGEBEN, mit Auflage**

Der Drop ist genehmigt. Die im Reader-Audit vorgeschlagene Reihenfolge wird um einen
Schritt erweitert, weil eine reversible Down-Migration nur die *leere* Tabelle
wiederherstellt, nicht ihren Inhalt.

### Auszuführende Schritte

1. **Zeilen zählen.** `SELECT COUNT(*) FROM runtime_sessions;`
   Zahl in `baselines/W6-G2-runtime-sessions-readers.md` protokollieren, mit Datum.

2. **Bei Zeilenzahl > 0: einmalig archivieren.**
   Vollständiger Export aller Zeilen nach
   `docs/superpowers/plans/baselines/W6-G2-runtime-sessions-archive.json`.
   Kopf des Artefakts: Exportzeitpunkt, Zeilenzahl, Quell-Schema, erzeugender Commit.
   Das Artefakt wird committet — es ist nach dem Drop die einzige Datenquelle.
   Bei Zeilenzahl 0 entfällt der Export; die 0 wird trotzdem protokolliert.

3. **Alembic-Migration.** `DROP TABLE runtime_sessions`, `downgrade` legt die Tabelle
   strukturgleich wieder an. In den Docstring der Migration gehört ausdrücklich:
   *downgrade stellt die Struktur wieder her, nicht die Daten — diese liegen
   ausschließlich im Archiv-Artefakt aus Schritt 2.*

4. **Code entfernen.** `RuntimeSessionRecord` aus `backend/app/models/__init__.py`
   austragen, `backend/app/models/world_engine/runtime_session.py` löschen.

5. **Gate.** `test_runtime_sessions_table_absent` als Exit-Kriterium hinzufügen.

6. **Nachweis.** Migration einmal `up` und einmal `down` gegen die lokale Datenbank
   fahren, beide Ergebnisse im Baseline-Dokument festhalten.

### Grenze der Evidenz — bitte ernst nehmen

Der statische Scan belegt sauber, dass **kein Python-Lese- oder Schreibpfad** existiert.
Er belegt prinzipbedingt **nicht**, dass keine externe SQL-, BI-, Reporting- oder
Operator-View auf die Tabelle zugreift. Wenn bei der Ausführung ein solcher Zugriff
auftaucht: **anhalten und melden**, nicht umgehen und nicht wegkonfigurieren.

---

## G3 — fy-suites-Split: **NICHT JETZT**

Die Richtung bleibt unverändert: `'fy'-suites` gehört langfristig in ein eigenes
Repository. Der **Zeitpunkt** ist verschoben.

**Bedingung:** Der Split wird erst ausgeführt, wenn der Sanierungs-Branch gemergt
**und** gepusht ist — als eigene, klar abgegrenzte Operation.

**Begründung:** `git subtree split` plus neues Remote plus Entfernen aus `conftest.py`,
Workflows und `pyproject.toml` sind ein umfangreicher Eingriff. Solange der
Sanierungs-Branch weder integriert noch gesichert ist, verteuert das jeden Rollback
erheblich. Der eigentliche Schutz ist ohnehin bereits gelandet:
`tests/gates/test_no_fy_suites_import_in_product.py` verhindert, dass Produktcode
fy-Werkzeug importiert. Das war der Großteil des Werts.

**Bis dahin verboten:** kein `git subtree split`, kein neues Remote, kein Löschen unter
`'fy'-suites/**`, keine Änderung an `conftest.py`-Pfaden zu diesem Zweck.

`P-G3-FY` bleibt geparkt — aber mit dokumentierter Bedingung statt mit offenem
„awaiting yes". Die Vorbereitung in `baselines/W9-G3-fy-suites-split-prep.md` bleibt
gültig und wird nicht angefasst.

---

## G4 — architecture_assurance-WIP: **FREIGEGEBEN, bereits ausgeführt**

Der Benutzer hat das Committen des WIP freigegeben. Ausgeführt in **`de2cff5b`**
(2026-07-31 09:40) zusammen mit den Analysedokumenten und Beweis-Baselines.

**Damit sind zwei geparkte Probleme entsperrt:**

- **`P-W8-ASSURE-CI`** — `.github/workflows/architecture-assurance.yml` kann jetzt auf
  `tests/run_tests.py` migriert werden. Ziel: Direct-pytest-Allowlist auf **0**.
- **`P-W8-ALIAS`** — die eingefrorenen Element-Doppelrollen im `model_catalog.json`
  können jetzt aufgelöst werden; der Katalog ist nicht länger durch fremden WIP blockiert.

**Hinweis zur Ausführung:** `de2cff5b` mischt Werkzeug-WIP und Sanierungs-Dokumentation
in einem Commit. Das ist hingenommen und wird **nicht** nachträglich aufgeteilt —
History-Rewrite auf einem Branch, der ohnehin gemergt werden soll, wäre teurer als der
Nutzen. Künftige Commits trennen Werkzeug und Dokumentation wieder.

---

## Folge für die Restliste

Nach G2 und den beiden entsperrten Problemen bleiben in `DRIFT_SANIERUNG_ABSCHLUSS.md §9`
offen:

| Punkt | Status nach diesen Entscheidungen |
| --- | --- |
| G2 Persistenz-Drop | **ausführbar** — Schritte oben |
| G3 externes fy-Repository | **bewusst verschoben** — Bedingung: nach Merge + Push |
| architecture-assurance.yml direct pytest | **ausführbar** — G4 entsperrt |
| Model-Catalog-Doppelrollen | **ausführbar** — G4 entsperrt |
| Voller Playthrough / `unattributed_call_count == 0` | offen — braucht laufenden Stack |
| UML-CI-Artefakt / SARIF-JUnit-Identität | offen — nicht neu verifiziert |
| `--suite all` grün | offen — nicht behauptet |
| Reconnect-Block-Ordering-Gate | offen — bestehender E2E-Test deckt es nicht ab |

**Nicht abgeschlossen melden, solange G2 nicht ausgeführt ist.** Die Wellen W0–W9 sind
ohne den Persistenz-Drop nicht vollständig, weil die dormante Tabelle genau die Residue
ist, deren Entfernung Welle 6 begründet hat.
