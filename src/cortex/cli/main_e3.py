# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""E3 CLI wrapper for documentation and benchmark commands.

The historical parser remains the source of truth for existing commands.  This
wrapper routes the E3 commands and delegates everything else to ``main.py``.
"""

from __future__ import annotations

import sys
from typing import List, Optional

from .main import main as legacy_main
from .commands import benchmark as cmd_benchmark
from .commands import docstring as cmd_docstring


def _first_command(argv: List[str]) -> Optional[str]:
    for token in argv:
        if token == "--json":
            continue
        if token.startswith("-"):
            continue
        return token
    return None


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = _first_command(args)
    try:
        if command == "docstring":
            idx = args.index("docstring")
            parsed = cmd_docstring.build_parser().parse_args(args[idx + 1:])
            return cmd_docstring.run(parsed)
        if command == "benchmark":
            idx = args.index("benchmark")
            parsed = cmd_benchmark.build_parser().parse_args(args[idx + 1:])
            return cmd_benchmark.run(parsed)
        return legacy_main(args)
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
