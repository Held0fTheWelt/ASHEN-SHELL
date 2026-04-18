from __future__ import annotations

from fy_platform.ai.adapter_cli_helper import run_adapter_cli
from templatify.adapter.service import TemplatifyAdapter


def main(argv=None) -> int:
    return run_adapter_cli(TemplatifyAdapter, argv)


if __name__ == '__main__':
    raise SystemExit(main())
