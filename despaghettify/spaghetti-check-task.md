# Task: Struktur- / Spaghetti-Check (reproduzierbar)

*Pfad:* `despaghettify/spaghetti-check-task.md` — Überblick: [README.md](README.md).

Dieser Auftrag beschreibt die **vollständige** Analyse-Spur für den Despaghettify-Hub: **Strukturmetriken** erheben, **Hotspots** benennen, die kanonische [Inputliste](despaghettification_implementation_input.md) an drei Stellen pflegen — **Letzter Struktur-Scan**, **Informations-Inputliste** (Tabelle), **Empfohlene Umsetzungsreihenfolge** (Vorschlag) — **ohne** Code-Refactors (Umsetzung bleibt beim Despag-Umsetzer und folgt [`EXECUTION_GOVERNANCE.md`](state/EXECUTION_GOVERNANCE.md) bei echten Wellen).

## Bindende Quellen

| Dokument | Rolle |
|----------|--------|
| [despaghettification_implementation_input.md](despaghettification_implementation_input.md) | **Letzter Struktur-Scan** (Zahlen, Datum, Score), **Informations-Inputliste** (DS-Zeilen aus Befund), **Empfohlene Umsetzungsreihenfolge** (Phasen-Tabelle aus Abhängigkeiten ableiten); § **DS-ID → primärer Workstream** bei neuen IDs mitpflegen. |
| [tools/spaghetti_ast_scan.py](../tools/spaghetti_ast_scan.py) | Kanonische Ausführung der Metriken (Repo-Wurzel = CWD). |
| [state/EXECUTION_GOVERNANCE.md](state/EXECUTION_GOVERNANCE.md) | Analyse und Markdown-Pflege erzeugen **keine** neuen Pre/Post-Artefakte; die entstehen erst, wenn eine **Wave** mit Evidenz anläuft. |
| Lokale Planung / Issues | Scan-Zahlen und vorgeschlagene Reihenfolge nur nach Abstimmung in externe Tickets spiegeln; im Repo genügen die drei Inputlisten-Abschnitte. |

## Nicht tun

- **Nicht** `docs/archive/documentation-consolidation-2026/*` ändern.
- **Keine** Prozent-Scores als „objektive“ Wahrheit verkaufen — höchstens **heuristische** Einordnung in der Scan-Tabelle.
- **Kein** Ersatz für grüne CI: Scan ist **Lesart**, Tests bleiben authoritative.

## Umfang des Python-AST-Laufs (fix)

Diese Verzeichnisse **immer** einbeziehen (Pfade relativ zur Repository-Wurzel):

- `backend/app`
- `world-engine/app`
- `ai_stack`
- `story_runtime_core`
- `tools/mcp_server`
- `administration-tool`

**Ignorieren:** `.state_tmp`, `site/`, `node_modules`, `.venv`, `venv`, `__pycache__` (und alles unterhalb davon).

## Reproduktion: AST-Scan-Skript

**Im Repository vorhanden:** [tools/spaghetti_ast_scan.py](../tools/spaghetti_ast_scan.py) — bei Änderung der Metrikdefinition **Task-Dokument und Skript gemeinsam** pflegen.

Der folgende Block ist eine **Kopie** der Logik (falls das Skript fehlt oder abweicht):

```python
from __future__ import annotations

import ast
from pathlib import Path

IGNORE = (".state_tmp", "/site/", "node_modules", ".venv", "venv", "__pycache__")
ROOTS = [
    Path("backend/app"),
    Path("world-engine/app"),
    Path("ai_stack"),
    Path("story_runtime_core"),
    Path("tools/mcp_server"),
    Path("administration-tool"),
]


def walk(root: Path):
    for p in root.rglob("*.py"):
        s = p.as_posix()
        if any(x in s for x in IGNORE):
            continue
        yield p


def nest_depth(body: list[ast.stmt], d: int = 0) -> int:
    m = d
    for b in body:
        if isinstance(b, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.Try)):
            m = max(m, d + 1)
            for attr in ("body", "orelse", "handlers", "finalbody"):
                sub = getattr(b, attr, None)
                if isinstance(sub, list):
                    m = max(m, nest_depth(sub, d + 1))
    return m


def metrics(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(n, "end_lineno", None) or n.lineno
            out.append((n.name, end - n.lineno + 1, nest_depth(n.body, 0), path))
    return out


def main() -> None:
    allm = []
    for r in ROOTS:
        if r.exists():
            for p in walk(r):
                allm.extend(metrics(p))
    long50 = [x for x in allm if x[1] > 50]
    long100 = [x for x in allm if x[1] > 100]
    deep6 = [x for x in allm if x[2] >= 6]
    print("Total functions:", len(allm))
    print(">50 lines:", len(long50), ">100 lines:", len(long100), "nesting>=6:", len(deep6))
    long100.sort(key=lambda x: -x[1])
    print("Top 12 longest:")
    for name, lines, nd, p in long100[:12]:
        print(f"  {lines:4d}L depth~{nd} {p.as_posix()}:{name}")
    deep6.sort(key=lambda x: (-x[2], -x[1]))
    print("Top 6 nesting:")
    for name, lines, nd, p in deep6[:6]:
        print(f"  depth {nd} {lines:4d}L {p.as_posix()}:{name}")
    ate = Path("backend/app/runtime/ai_turn_executor.py")
    if ate.exists():
        raw = len(ate.read_text(encoding="utf-8", errors="replace").splitlines())
        ex = [x for x in metrics(ate) if x[0] == "execute_turn_with_ai"]
        print("ai_turn_executor.py lines:", raw)
        if ex:
            print("execute_turn_with_ai:", ex[0][1], "lines depth~", ex[0][2])


if __name__ == "__main__":
    main()
```

Ausführung von der **Repository-Wurzel**:

```bash
python tools/spaghetti_ast_scan.py
```

## Zusatzchecks (fix)

1. **Duplikat Builtins:** Suche nach `def build_god_of_carnage_solo` in `**/builtins.py` (Backend + World-Engine) — Zustand in Scan-Tabelle kurz erwähnen, solange das für euch ein offenes Builtins-/Drift-Thema ist.
2. **Import-Workarounds (Stichprobe):** unter `backend/app/runtime` nach `TYPE_CHECKING`, `avoid circular`, `circular dependency` greppen — nur qualitativ („weiterhin vorhanden“ / „weniger Treffer“), keine vollständige Graph-Analyse nötig.

## Pflege der Inputliste (drei Pflichtblöcke)

Alles in [despaghettification_implementation_input.md](despaghettification_implementation_input.md):

### 1) Letzter Struktur-Scan

- **Datum** und Metriken (**N**, **L₅₀**, **L₁₀₀**, **D₆**, **S**) aus dem Skriptlauf; **Score *S*** und Zähler konsistent zur Formel in der Inputliste.
- **Zusatzchecks** (Builtins, Runtime-Stichprobe `TYPE_CHECKING` / Zirkel-Hinweise) kurz im Scan-Abschnitt verankern, wenn ihr sie ausführt.
- Längste Funktionen und Top-Nesting **vollständig** nur in der **Skript-Ausgabe**; im Markdown **Kernaussagen** und ggf. **Offene Schwerpunkte** (2–5 Bulletpoints).

### 2) Informations-Inputliste (Tabelle) befüllen

- Jede erkannte oder verschärfte **Struktur-/Spaghetti-Lücke** bekommt eine **eigene Zeile** mit Spalten: **ID**, **Muster**, **Ort**, **Hinweis / Messidee**, **Richtung** (Lösungsskizze in einem Satz), **Kollisionshinweis** (was parallel riskant wäre).
- **IDs:** bestehende **DS-***-Zeilen **aktualisieren** (Messwerte, Ort, Kollision), statt Duplikate zu erfinden; nur bei **neuen** Themen die nächste freie **DS-***-Nummer vergeben.
- Direkt danach die Tabelle **DS-ID → primärer Workstream** im selben Dokument pflegen (Slug → `artifacts/workstreams/<slug>/pre|post/` laut [state/WORKSTREAM_INDEX.md](state/WORKSTREAM_INDEX.md)).

### 3) Empfohlene Umsetzungsreihenfolge vorschlagen

- Abschnitt **„Empfohlene Umsetzungsreihenfolge“** als **Vorschlag** des Analyse-Agenten: Tabelle **Priorität / Phase**, **DS-ID(s)**, **Kurzlogik**, **Workstream (primär)**, **Anmerkung** (Abhängigkeiten, Gates).
- **Heuristik (Reihenfolge):** Schnittstellen und gemeinsame Kanten (**DTOs, klare Module-Grenzen**) vor großen Verschiebungen; **hohe Kopplung / tiefe Nesting-Hotspots** nicht parallel von zwei Ownern ohne abgestimmte Artefakt-Sets; Builtins-/Import-Themen nicht hinter großen Runtime-Umbauten verstecken, wenn der Scan sie oben hält.
- Wenn nur Zahlen ohne neue inhaltliche These: Reihenfolgetabelle **bestätigen** oder eine Zeile **„keine Änderung gegenüber letztem Scan“** — keine leeren Platzhalter-Phasen stehen lassen, wenn die Inputtabelle Zeilen hat.

### Optional

- **Fortschritt / Arbeitslog** und **`WORKSTREAM_*_STATE.md`**: nur bei **formaler Wave** mit Pre/Post (siehe Governance).

## Ergebnisformat für den Auftraggeber (kurz)

Nach Lauf **3–8 Sätze** zu Länge/Nesting/Hotspots, **1–3 Sätze** zur **vorgeschlagenen Umsetzungsreihenfolge** (erste Phase und warum), plus Verweis auf geänderte Abschnitte in der Inputliste (Scan-Tabelle, DS-Zeilen, Phasen-Tabelle).

## Gegenstück: Umsetzung Welle für Welle

Die **Ausführungs-Spur** (Reihenfolge prüfen, ggf. anpassen, dann Despag-Wellen mit Pre/Post bis zur Liste leer): [spaghetti-solve-task.md](spaghetti-solve-task.md).
