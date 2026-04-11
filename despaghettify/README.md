# Despaghettify

Zentraler Ort für den **Despaghettifizierungs-** und **Struktur-/Spaghetti-Check-Zyklus** inkl. **Execution-Governance-State-Hub** unter [`state/`](state/README.md).

| Datei | Rolle |
|-------|--------|
| [`despaghettification_implementation_input.md`](despaghettification_implementation_input.md) | Kanonische **Inputliste**, DS-Koordination, Struktur-Scan-Tabelle, Umsetzungsreihenfolge, Arbeitslog (Templates). |
| [`spaghetti-check-task.md`](spaghetti-check-task.md) | **Analyse-Spur:** AST-/Spaghetti-Check; Pflege von § *Letzter Struktur-Scan*, **Informations-Inputliste** und **Empfohlene Umsetzungsreihenfolge** (ohne Code-Änderung). |
| [`spaghetti-solve-task.md`](spaghetti-solve-task.md) | **Umsetzungs-Spur:** Reihenfolge prüfen/ggf. überarbeiten; dann **Welle für Welle** implementieren bis zur sachlichen **Erfolgsmeldung** (Pre/Post, Completion Gate). |

**Werkzeuge** (bleiben unter `tools/`): `spaghetti_ast_scan.py`, `ds005_runtime_import_check.py`.

**Governance / Pre–Post:** [`state/README.md`](state/README.md), [`state/EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md).
