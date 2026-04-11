# Task: Despaghettifizierung umsetzen (Welle für Welle)

*Pfad:* `despaghettify/spaghetti-solve-task.md` — Überblick: [README.md](README.md).

**Gegenstück** zu [spaghetti-check-task.md](spaghetti-check-task.md): Dort werden Metriken erhoben und die Inputliste (Scan, DS-Tabelle, **vorgeschlagene** Umsetzungsreihenfolge) befüllt — **ohne** Code zu ändern. **Hier** prüft der Umsetzungs-Agent die **Empfohlene Umsetzungsreihenfolge**, schlägt bei Bedarf eine **Überarbeitung** vor, implementiert anschließend **eigenständig** nach den Despaghettify-Regeln **Welle für Welle** bzw. **Task für Task** (typisch **eine Session ≈ eine Welle** oder ein klar abgegrenzter Teil einer Phase), bis die abgestimmte Liste **abgearbeitet** ist und ein **Erfolg** sachlich vermeldet werden darf.

## Bindende Quellen

| Dokument | Rolle |
|----------|--------|
| [despaghettification_implementation_input.md](despaghettification_implementation_input.md) | Kanon: **Informations-Inputliste**, **Empfohlene Umsetzungsreihenfolge**, § *DS-ID → primärer Workstream*; nach jeder Welle § *Pflege dieser Datei* einhalten. |
| [state/EXECUTION_GOVERNANCE.md](state/EXECUTION_GOVERNANCE.md) | **Completion Gate**, Pre/Post-Artefakte, State aus Evidenz — für jede strukturelle Welle verbindlich. |
| [state/WORKSTREAM_INDEX.md](state/WORKSTREAM_INDEX.md) | Slugs und Zuordnung zu `artifacts/workstreams/<slug>/pre|post/`. |
| Passendes `state/WORKSTREAM_*_STATE.md` | Vor Start lesen; nach der Welle aus Post-Evidenz aktualisieren. |
| [spaghetti-check-task.md](spaghetti-check-task.md) | Nach **größeren** Wellen oder am Ende optional erneut ausführen, um Scan und Inputliste an den neuen Repo-Stand anzugleichen. |

## Nicht tun

- **`docs/archive/documentation-consolidation-2026/*`** nicht anfassen (siehe Check-Task).
- **Keinen** Abschluss- oder Erfolgs-Claim ohne Erfüllung des **Completion Gate** aus `EXECUTION_GOVERNANCE.md`.
- **Nicht** dieselbe **DS-ID** parallel zu einem anderen Owner bearbeiten (Koordination in der Inputliste).
- Keine „stille“ Abkürzung: fehlende Pre/Post oder fehlender Pre→Post-Vergleich = **Stop**, nicht weiterschreiben.

## Phase 1 — Umsetzungsreihenfolge prüfen (und ggf. überarbeiten)

1. **Inputliste lesen:** § *Informations-Inputliste* und § *Empfohlene Umsetzungsreihenfolge* vollständig; **DS-ID → Workstream**-Tabelle abgleichen.
2. **Konsistenzcheck:** Jede Phasen-Zeile referenziert **existierende** DS-IDs; Abhängigkeiten (Schnittstellen vor Massenverschiebung, Kollisionen aus der Spalte *Kollisionshinweis*) sind **plausibel** und mit dem Repo-Stand vereinbar.
3. **Contradiction Stop Rule:** Widerspruch zwischen Repo, State-Dokumenten und Tabelle → stoppen, im betroffenen `WORKSTREAM_*_STATE.md` oder in der Inputliste unter *Offene Schwerpunkte* / Phasen-Anmerkung festhalten, Reihenfolge **erst** nach Klärung anpassen.
4. **Überarbeitung:** Wenn die Reihenfolge angepasst werden muss: **dieselbe** Inputliste aktualisieren (Phasen-Tabelle, ggf. Kurzlogik/Anmerkungen); keine parallele „Geheim-Plan“-Datei.

## Phase 2 — Schleife: eine Welle pro klarer Einheit

Pro **Welle** (oder pro **DS-ID**, wenn explizit eine-ID-eine-Welle vereinbart):

1. **State lesen:** `EXECUTION_GOVERNANCE.md`, `WORKSTREAM_INDEX.md`, zugehöriges `WORKSTREAM_*_STATE.md`.
2. **Pre:** Artefakte unter `despaghettify/state/artifacts/workstreams/<slug>/pre/` anlegen (Namenskonvention und Mindestinhalt wie in der Inputliste / Governance — u. a. menschenlesbar + bevorzugt maschinenlesbar).
3. **Umsetzung:** Code/Struktur gemäß **Richtung** in der DS-Zeile; Verhalten bewahren, relevante Tests/CI grün halten.
4. **Post:** Artefakte unter `…/post/`; **Pre→Post** dokumentiert vergleichen.
5. **State & Inputliste:** `WORKSTREAM_*_STATE.md` und [despaghettification_implementation_input.md](despaghettification_implementation_input.md) gemäß § *Pflege dieser Datei bei strukturellen Wellen* (Tabelle, Scan bei messbarer Änderung, Umsetzungsreihenfolge bei verschobener Priorität, optional Arbeitslog).
6. **Nächste Welle:** erst starten, wenn Schritt 5 für die aktuelle ID/Phase erledigt ist und keine offenen Widersprüche dem Gate widersprechen.

**Session-Disziplin:** Lieber **eine** abgeschlossene Welle pro Session als halbe Wellen über viele Chats — erleichtert Review, PRs und Nachvollziehbarkeit.

## Phase 3 — Abschluss und Erfolgsmeldung

Ein **Erfolg** darf nur vermeldet werden, wenn **alle** in der **abgestimmten** § *Empfohlene Umsetzungsreihenfolge* vorgesehenen DS-/Phasen-Einheiten den **Completion Gate** passiert haben **und** die Inputliste den Stand widerspiegelt (abgeschlossene Zeilen markiert, Reihenfolge konsistent).

**Erfolgsnachricht (inhaltlich mindestens):**

- Welche **DS-ID(s)** / Phasen **fertig** sind (Referenz auf Inputliste und Workstream-State).
- Kurz: **Tests/CI** (was gelaufen ist) und wo **Pre/Post** liegen.
- Optional: Verweis auf einen nachgelagerten Lauf von [spaghetti-check-task.md](spaghetti-check-task.md), wenn Zahlen für Stakeholder relevant sind.

**Nicht** als Gesamterfolg werten: Teilweise umgesetzte Liste, fehlende Artefakte, oder „fast grün“ ohne dokumentierten Pre→Post-Vergleich.

## Beziehung zum Check-Task

| Aspekt | [spaghetti-check-task.md](spaghetti-check-task.md) | spaghetti-solve-task.md (dieses Dokument) |
|--------|---------------------------------------------------|---------------------------------------------|
| Code ändern | Nein | Ja (strukturell, wellenweise) |
| Inputliste | Scan + DS-Tabelle + Reihenfolge **vorschlagen** | Reihenfolge **prüfen/überarbeiten**, dann Tabelle/Scan/Log **bei Umsetzung** pflegen |
| Artefakte Pre/Post | Nur bei expliziter Wave durch anderen Prozess | **Pflicht** je Welle laut Governance |

---

*Ziel:* Von der **Analyse-Spur** (Check) zur **Ausführungs-Spur** (Solve) ohne Governance-Lücke — bis die Despag-Liste sachlich abgearbeitet ist.
