from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .service import MetrifyAdapter


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description='Metrify adapter CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    p_audit = sub.add_parser('audit', help='Audit a target repo and write metrify artifacts')
    p_audit.add_argument('target_repo_root')

    p_init = sub.add_parser('init', help='Bind metrify to a target repo')
    p_init.add_argument('target_repo_root')

    sub.add_parser('inspect', help='Inspect latest metrify state')
    ns = parser.parse_args(argv)
    adapter = MetrifyAdapter()
    if ns.command == 'init':
        out = adapter.init(ns.target_repo_root)
    elif ns.command == 'inspect':
        out = adapter.inspect()
    else:
        out = adapter.audit(ns.target_repo_root)
    print(json.dumps(out, indent=2))
    return 0
