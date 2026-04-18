from __future__ import annotations

import argparse
import json
from pathlib import Path

from usabilify.tools.evaluator import evaluate, evaluation_markdown, inventory_markdown, view_map
from usabilify.tools.repo_paths import repo_root
from usabilify.tools.template_inventory import inspect_areas


def _reports_root() -> Path:
    return Path(__file__).resolve().parents[1] / 'reports'


def _state_root() -> Path:
    return Path(__file__).resolve().parents[1] / 'state'


def _effective_repo_root(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else repo_root()


def cmd_inspect(args: argparse.Namespace) -> int:
    payload = inspect_areas(_effective_repo_root(args))
    reports = _reports_root()
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'usabilify_inventory.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    (reports / 'usabilify_inventory_report.md').write_text(inventory_markdown(payload), encoding='utf-8')
    print((reports / 'usabilify_inventory.json').as_posix())
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    payload = evaluate(_effective_repo_root(args))
    reports = _reports_root()
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'usabilify_evaluation.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    (reports / 'usabilify_evaluation_report.md').write_text(evaluation_markdown(payload), encoding='utf-8')
    (reports / 'usabilify_view_map.mmd').write_text(view_map(payload), encoding='utf-8')
    print((reports / 'usabilify_evaluation.json').as_posix())
    return 0


def cmd_full(args: argparse.Namespace) -> int:
    cmd_inspect(args)
    return cmd_evaluate(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='usabilify', description='UI/UX and usability governance for World of Shadows')
    sub = parser.add_subparsers(dest='command', required=True)
    inspect_parser = sub.add_parser('inspect', help='inventory template surfaces')
    inspect_parser.add_argument('--repo-root', default='')
    inspect_parser.set_defaults(func=cmd_inspect)
    evaluate_parser = sub.add_parser('evaluate', help='evaluate repository UI surfaces')
    evaluate_parser.add_argument('--repo-root', default='')
    evaluate_parser.set_defaults(func=cmd_evaluate)
    full_parser = sub.add_parser('full', help='run inventory and evaluation')
    full_parser.add_argument('--repo-root', default='')
    full_parser.set_defaults(func=cmd_full)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == '__main__':
    raise SystemExit(main())
