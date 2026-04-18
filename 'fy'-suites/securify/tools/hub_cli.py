from __future__ import annotations

from typing import Sequence

from securify.tools.scanner import main as scanner_main


def main(argv: Sequence[str] | None = None) -> int:
    return int(scanner_main(argv))


if __name__ == '__main__':
    raise SystemExit(main())
