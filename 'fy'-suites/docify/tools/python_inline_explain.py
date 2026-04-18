from __future__ import annotations

import argparse
import ast
import textwrap
from pathlib import Path
from typing import Sequence

FLOW_WIDTH = 88


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _line_indent(lines: list[str], lineno: int) -> str:
    idx = max(lineno - 1, 0)
    if idx >= len(lines):
        return ''
    raw = lines[idx]
    return raw[: len(raw) - len(raw.lstrip())]


def _comment_lines(indent: str, text: str) -> list[str]:
    wrapped = textwrap.wrap(
        text,
        width=max(40, FLOW_WIDTH - len(indent) - 2),
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [f'{indent}# {line}' for line in wrapped] if wrapped else [f'{indent}#']


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
    return ''


def _describe_statement(stmt: ast.stmt, function_name: str) -> str:
    if isinstance(stmt, ast.Assign):
        target_names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
        joined = ', '.join(target_names) or 'these local values'
        if any(name.endswith('_path') or name.endswith('_dir') for name in target_names):
            return f'Build filesystem locations for {joined} so the rest of {function_name} can write, persist, or register artifacts in predictable places.'
        if isinstance(stmt.value, ast.Call):
            call = _call_name(stmt.value)
            if call == 'route':
                return f'Ask the router how this task should run so {function_name} uses the right evidence and reproducibility profile instead of an ad-hoc mode.'
            if call in {'build_and_write', 'summarize'}:
                return f'Run the shared platform service and keep the result in {joined} so later steps can enrich it with suite metadata and outward-facing context.'
        return f'Compute {joined} for the next stage of {function_name}.'
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        call = _call_name(stmt.value)
        if call == 'write_json':
            return 'Persist the structured JSON representation so automated tooling can consume the result without parsing Markdown back into data.'
        if call == 'write_text':
            return 'Write the human-readable companion text so a reviewer can understand the result without opening raw structured payloads first.'
        if call == 'record_artifact':
            return 'Register the written artifact in the evidence registry so later explain, compare, and context-pack flows can discover it as official output.'
        if call == 'append':
            return 'Append a journal event so later status and explain flows can reconstruct what happened during the run.'
        return f'Execute a side-effecting helper call that advances the {function_name} workflow.'
    if isinstance(stmt, ast.If):
        return f'Only enter this branch when the required precondition is true, so {function_name} avoids acting on missing, stale, or unsafe state.'
    if isinstance(stmt, ast.For):
        return f'Walk over repeated items and apply the same step consistently so {function_name} produces complete coverage instead of a one-off result.'
    if isinstance(stmt, ast.Return):
        return f'Return the final outward-facing result of {function_name} once all preparation, persistence, and registration work is complete.'
    if isinstance(stmt, ast.Try):
        return f'Protect the critical part of {function_name} so failures can be converted into controlled output instead of escaping as raw exceptions.'
    return f'Continue the internal control flow of {function_name} with this block.'


def _iter_body_statements(body: list[ast.stmt]) -> list[ast.stmt]:
    statements: list[ast.stmt] = []
    for stmt in body:
        statements.append(stmt)
        nested_bodies: list[list[ast.stmt]] = []
        if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With, ast.AsyncWith, ast.Try)):
            for attr in ('body', 'orelse', 'finalbody'):
                nested = getattr(stmt, attr, None)
                if nested:
                    nested_bodies.append(nested)
            for handler in getattr(stmt, 'handlers', []):
                if handler.body:
                    nested_bodies.append(handler.body)
        for nested in nested_bodies:
            statements.extend(_iter_body_statements(nested))
    return statements


def annotate_function_inline(source: str, function_name: str, mode: str = 'dense') -> str:
    tree = ast.parse(source)
    fn = _find_function(tree, function_name)
    if fn is None:
        raise ValueError(f'function_not_found:{function_name}')

    lines = source.splitlines()
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], 'value', None), ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]

    insertions: list[tuple[int, list[str]]] = []
    for stmt in _iter_body_statements(body):
        lineno = int(getattr(stmt, 'lineno', fn.lineno + 1))
        indent = _line_indent(lines, lineno)
        comment = _describe_statement(stmt, function_name)
        if mode == 'block':
            comment = 'Block purpose: ' + comment
        insertions.append((lineno, _comment_lines(indent, comment)))

    new_lines = lines[:]
    for lineno, comment_lines in sorted(insertions, key=lambda item: item[0], reverse=True):
        idx = max(lineno - 1, 0)
        new_lines[idx:idx] = comment_lines
    return '\n'.join(new_lines) + ('\n' if source.endswith('\n') else '')


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Generate dense inline explanations for a Python function.')
    parser.add_argument('--file', required=True)
    parser.add_argument('--function', required=True)
    parser.add_argument('--mode', choices=['dense', 'block'], default='dense')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output', default='')
    args = parser.parse_args(list(argv) if argv is not None else None)

    path = Path(args.file).expanduser().resolve()
    source = path.read_text(encoding='utf-8')
    rendered = annotate_function_inline(source, args.function, mode=args.mode)

    if args.apply:
        path.write_text(rendered, encoding='utf-8')
    elif args.output:
        Path(args.output).expanduser().resolve().write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
