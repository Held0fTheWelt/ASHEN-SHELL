"""File-only discovery lanes for Better Tomorrow implementation surfaces."""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
import fnmatch
from functools import lru_cache
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

from .schemas import ANCHOR_SCHEMA_VERSION, validate_anchor


_SUPPORTED_FILES = (
    ".py",
    ".sql",
    ".yaml",
    ".yml",
    ".json",
    ".html",
    ".js",
    ".css",
    ".toml",
    ".ini",
    ".md",
)
_CREATE_TABLE = re.compile(
    r"(?i)\bCREATE\s+TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+"
    r"[\"']?(?P<name>[A-Za-z_][A-Za-z0-9_.]*)"
)
_ALEMBIC_TABLE = re.compile(
    r"\bop\.create_table\(\s*[\"'](?P<name>[^\"']+)[\"']"
)
_ROUTE_DECORATOR = re.compile(
    r"^\s*@(?P<owner>[\w.]+)\.(?P<method>route|get|post|put|patch|delete|websocket)"
    r"\(\s*[rubfRUBF]*[\"'](?P<route>[^\"']+)",
    re.MULTILINE,
)
_IGNORED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".akdb",
    ".wos",
    "__pycache__",
    "node_modules",
    "reports",
    "tests",
}
_TRANSIENT_PARTS = _IGNORED_PARTS - {"tests"}


def _is_ignored(path: Path) -> bool:
    return any(part.lower() in _IGNORED_PARTS for part in path.parts)


def _is_transient(path: Path) -> bool:
    return any(part.lower() in _TRANSIENT_PARTS for part in path.parts)


def repo_relative(path: Path, repo_root: Path) -> str:
    return Path(os.path.relpath(path.resolve(), repo_root.resolve())).as_posix()


@lru_cache(maxsize=8)
def _repository_visible_files(repo_root: str) -> frozenset[str] | None:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                repo_root,
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            check=False,
            capture_output=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return frozenset(
        item.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for item in result.stdout.split(b"\0")
        if item
    )


def _is_repository_visible(path: Path, repo_root: Path) -> bool:
    relative = repo_relative(path, repo_root)
    if relative == ".." or relative.startswith("../"):
        return False
    visible = _repository_visible_files(str(repo_root.resolve()))
    return visible is None or relative in visible


def _repository_glob(repo_root: Path, pattern: str) -> list[Path]:
    visible = _repository_visible_files(str(repo_root.resolve()))
    if visible is None:
        return sorted(path for path in repo_root.glob(pattern) if path.is_file())
    return sorted(
        (repo_root / relative).resolve()
        for relative in visible
        if fnmatch.fnmatch(relative, pattern)
    )


def _repository_files_under(directory: Path, repo_root: Path) -> list[Path]:
    visible = _repository_visible_files(str(repo_root.resolve()))
    if visible is None:
        return sorted(
            path
            for path in directory.rglob("*")
            if not _is_transient(path)
            and path.is_file()
            and path.suffix.lower() in _SUPPORTED_FILES
        )
    prefix = repo_relative(directory, repo_root).rstrip("/")
    prefix = f"{prefix}/" if prefix not in {"", "."} else ""
    return sorted(
        (repo_root / relative).resolve()
        for relative in visible
        if relative.startswith(prefix)
        and not _is_transient(Path(relative))
        and Path(relative).suffix.lower() in _SUPPORTED_FILES
    )


def _anchor(kind: str, file: str, line: int, **extra: Any) -> dict[str, Any]:
    return validate_anchor(
        {
            "schema_version": ANCHOR_SCHEMA_VERSION,
            "kind": kind,
            "file": file,
            "line": line,
            **extra,
        }
    )


def _public_defs(tree: ast.AST) -> Iterable[tuple[str, ast.AST]]:
    body = getattr(tree, "body", [])
    for node in body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            yield node.name, node


def scan_python(
    roots: Iterable[Path],
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    units: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    files = {
        path.resolve()
        for root in roots
        if root.exists()
        for path in (
            [root] if root.is_file() and root.suffix == ".py" else root.rglob("*.py")
        )
        if not _is_ignored(path)
    }
    for path in sorted(files):
        rel = repo_relative(path, repo_root)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=rel)
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            errors.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        module = rel.removesuffix(".py").replace("/", ".")
        for symbol, node in _public_defs(tree):
            anchor = _anchor(
                "python",
                rel,
                int(getattr(node, "lineno", 1)),
                module=module,
                symbol=symbol,
            )
            units.append(
                {
                    "id": f"python:{module}:{symbol}",
                    "kind": "python",
                    "anchor": anchor,
                }
            )
        source = path.read_text(encoding="utf-8-sig")
        lines = source.splitlines()
        for match in _ROUTE_DECORATOR.finditer(source):
            line = source.count("\n", 0, match.start()) + 1
            method = match.group("method").upper()
            if method == "ROUTE":
                method = "ANY"
            route = match.group("route")
            symbol = ""
            for following in lines[line : min(line + 8, len(lines))]:
                function = re.match(r"\s*(?:async\s+)?def\s+([A-Za-z_]\w*)", following)
                if function:
                    symbol = function.group(1)
                    break
            anchor = _anchor(
                "api",
                rel,
                line,
                method=method,
                route=route,
                symbol=symbol or match.group("owner"),
            )
            units.append(
                {
                    "id": f"api:{method}:{route}:{rel}:{line}",
                    "kind": "api",
                    "anchor": anchor,
                }
            )
    units.sort(key=lambda item: item["id"])
    errors.sort(key=lambda item: item["file"])
    return units, errors


def scan_schema(
    roots: Iterable[Path],
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    units: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    files: set[Path] = set()
    for root in roots:
        if root.is_file() and root.suffix.lower() in {".sql", ".py"}:
            files.add(root.resolve())
        elif root.is_dir():
            files.update(
                path.resolve() for path in root.rglob("*.sql") if not _is_ignored(path)
            )
            files.update(
                path.resolve() for path in root.rglob("*.py") if not _is_ignored(path)
            )
    for path in sorted(files):
        rel = repo_relative(path, repo_root)
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        patterns = (_CREATE_TABLE, _ALEMBIC_TABLE)
        for pattern in patterns:
            for match in pattern.finditer(text):
                table = match.group("name")
                line = text.count("\n", 0, match.start()) + 1
                anchor = _anchor(
                    "schema",
                    rel,
                    line,
                    object=f"table:{table}",
                )
                units.append(
                    {
                        "id": f"schema:table:{table}:{rel}:{line}",
                        "kind": "schema",
                        "anchor": anchor,
                    }
                )
    unique = {item["id"]: item for item in units}
    return [unique[key] for key in sorted(unique)], errors


def _line_for_key(text: str, key: str) -> int:
    pattern = re.compile(rf"(?m)^\s*[\"']?{re.escape(key)}[\"']?\s*:")
    match = pattern.search(text)
    return text.count("\n", 0, match.start()) + 1 if match else 1


def scan_content(
    roots: Iterable[Path],
    repo_root: Path,
    *,
    patterns: Iterable[str] = ("*.yaml", "*.yml", "*.json"),
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    units: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    files: set[Path] = set()
    for root in roots:
        if root.is_file():
            files.add(root.resolve())
        elif root.is_dir():
            for pattern in patterns:
                files.update(
                    path.resolve()
                    for path in root.rglob(pattern)
                    if not _is_ignored(path)
                )
    for path in sorted(files):
        rel = repo_relative(path, repo_root)
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        if path.suffix.lower() == ".json":
            try:
                value = json.loads(text)
            except json.JSONDecodeError as exc:
                errors.append({"file": rel, "error": f"JSONDecodeError: {exc}"})
                continue
            keys = sorted(value) if isinstance(value, dict) else ["$"]
        else:
            keys = [
                match.group(1)
                for match in re.finditer(
                    r"(?m)^([A-Za-z_][A-Za-z0-9_.-]*)\s*:", text
                )
            ][:50]
            if not keys:
                keys = ["$"]
        for key in keys:
            line = _line_for_key(text, key) if key != "$" else 1
            anchor = _anchor(
                "content",
                rel,
                line,
                object=f"{rel}#{key}",
            )
            units.append(
                {
                    "id": f"content:{rel}#{key}",
                    "kind": "content",
                    "anchor": anchor,
                }
            )
    unique = {item["id"]: item for item in units}
    return [unique[key] for key in sorted(unique)], errors


def scan_web(
    roots: Iterable[Path],
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    units: list[dict[str, Any]] = []
    for root in roots:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if (
                not path.is_file()
                or _is_ignored(path)
                or path.suffix.lower() not in {".html", ".js", ".css"}
            ):
                continue
            rel = repo_relative(path, repo_root)
            anchor = _anchor("web", rel, 1, symbol=path.stem)
            units.append(
                {"id": f"web:{rel}", "kind": "web", "anchor": anchor}
            )
    unique = {item["id"]: item for item in units}
    return [unique[key] for key in sorted(unique)], []


def scan_deployment(
    roots: Iterable[Path],
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    units: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in sorted({root.resolve() for root in roots if root.is_file()}):
        rel = repo_relative(path, repo_root)
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            errors.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"})
            continue
        in_services = False
        for index, line in enumerate(lines, start=1):
            if re.match(r"^services:\s*$", line):
                in_services = True
                continue
            if in_services and line and not line.startswith((" ", "\t", "#")):
                in_services = False
            match = re.match(r"^\s{2}([A-Za-z_][A-Za-z0-9_.-]*):\s*$", line)
            if not in_services or not match:
                continue
            service = match.group(1)
            anchor = _anchor(
                "deployment",
                rel,
                index,
                symbol=service,
            )
            units.append(
                {
                    "id": f"deployment:{rel}:{service}",
                    "kind": "deployment",
                    "anchor": anchor,
                }
            )
    return units, errors


def _expand_root(repo_root: Path, raw: str) -> list[Path]:
    normalized = raw.replace("\\", "/").strip("/")
    if any(token in normalized for token in "*?["):
        return sorted(path.resolve() for path in repo_root.glob(normalized))
    path = (repo_root / normalized).resolve()
    return [path] if path.exists() else []


def discover_subsystem(
    config: Mapping[str, Any],
    repo_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    units: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    lane_roots = config.get("lane_roots", {})
    for lane in config.get("lanes", []):
        roots = [
            path
            for raw in lane_roots.get(lane, [])
            for path in _expand_root(repo_root, raw)
        ]
        if lane in {"python", "api"}:
            lane_units, lane_errors = scan_python(roots, repo_root)
            if lane == "python":
                lane_units = [item for item in lane_units if item["kind"] == "python"]
            else:
                lane_units = [item for item in lane_units if item["kind"] == "api"]
        elif lane == "schema":
            lane_units, lane_errors = scan_schema(roots, repo_root)
        elif lane == "content":
            lane_units, lane_errors = scan_content(roots, repo_root)
        elif lane == "web":
            lane_units, lane_errors = scan_web(roots, repo_root)
        elif lane == "deployment":
            lane_units, lane_errors = scan_deployment(roots, repo_root)
        else:
            lane_units, lane_errors = [], [
                {"file": "", "error": f"unknown discovery lane: {lane}"}
            ]
        units.extend(lane_units)
        errors.extend(lane_errors)
    unique = {item["id"]: item for item in units}
    return [unique[key] for key in sorted(unique)], sorted(
        errors, key=lambda item: (item["file"], item["error"])
    )


def _split_declared_path(raw: str) -> list[str]:
    cleaned = raw.strip().strip("`").replace("\\", "/")
    return [
        part.strip()
        for part in re.split(r"\s*,\s*|\s+\+\s+", cleaned)
        if part.strip()
    ]


def resolve_declared_path(
    raw: str,
    repo_root: Path,
    source_roots: Iterable[str],
) -> tuple[Path | None, str | None]:
    for value in _split_declared_path(raw):
        value = value.split("#", 1)[0].strip()
        if not value or "://" in value:
            continue
        candidates: list[Path] = []
        direct = repo_root / value
        candidates.append(direct)
        for source_root in source_roots:
            candidates.append(repo_root / source_root / value)
        for candidate in candidates:
            text = candidate.as_posix()
            if any(token in text for token in "*?["):
                matches = _repository_glob(
                    repo_root, repo_relative(candidate, repo_root)
                )
                if matches:
                    candidate = matches[0]
                else:
                    continue
            if candidate.is_dir():
                preferred = candidate / "__init__.py"
                if preferred.is_file() and _is_repository_visible(
                    preferred, repo_root
                ):
                    candidate = preferred
                else:
                    files = _repository_files_under(candidate, repo_root)
                    if not files:
                        continue
                    candidate = files[0]
            if candidate.is_file() and _is_repository_visible(
                candidate, repo_root
            ):
                return candidate.resolve(), value
    return None, None


def anchor_for_declared_path(
    raw: str,
    repo_root: Path,
    source_roots: Iterable[str],
    *,
    title: str = "",
) -> dict[str, Any] | None:
    path, declared_path = resolve_declared_path(raw, repo_root, source_roots)
    if path is None or declared_path is None:
        return None
    rel = repo_relative(path, repo_root)
    suffix = path.suffix.lower()
    kind = "file"
    extra: dict[str, Any] = {"declared_path": declared_path}
    if suffix == ".py":
        kind = "test" if "/tests/" in f"/{rel.lower()}/" or rel.lower().startswith("tests/") else "python"
        extra["symbol"] = title or path.stem
    elif suffix == ".sql":
        kind = "schema"
        extra["object"] = title or path.stem
    elif suffix in {".yaml", ".yml", ".json"}:
        kind = "content"
        extra["object"] = title or path.stem
    elif suffix in {".html", ".js", ".css"}:
        kind = "web"
        extra["symbol"] = title or path.stem
    elif path.name.lower().startswith(("docker-compose", "dockerfile")):
        kind = "deployment"
        extra["symbol"] = title or path.name
    return _anchor(kind, rel, 1, **extra)


def path_matches_declared(unit_file: str, declared_path: str) -> bool:
    declared = declared_path.replace("\\", "/").strip("/")
    if any(token in declared for token in "*?["):
        return fnmatch.fnmatch(unit_file, declared) or fnmatch.fnmatch(
            unit_file.split("/", 1)[-1], declared
        )
    if Path(declared).suffix:
        return unit_file == declared or unit_file.endswith("/" + declared)
    return unit_file == declared or unit_file.startswith(declared.rstrip("/") + "/")
