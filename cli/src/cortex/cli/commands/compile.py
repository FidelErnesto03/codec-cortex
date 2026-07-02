# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex compile`` — compile HCORTEX-EDIT markdown back to .cortex."""

from __future__ import annotations

import os

from ...core.errors import CortexError
from ...core.parser import parse_cortex
from ...core.writer import write_cortex
from ...crud.transactions import atomic_write_text
from ...hcortex import parse_hcortex_edit
from ..commands import emit


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()
    doc = parse_hcortex_edit(text, source=args.input)
    cortex_text = write_cortex(doc)
    # Re-parse to verify compile output is itself valid
    parse_cortex(cortex_text, path=args.out)
    result = atomic_write_text(cortex_text, args.out, keep_backup=False)
    emit({
        "text": f"compiled {args.input} → {args.out} ({result.bytes_written} bytes)",
        "input": args.input,
        "out": args.out,
        "bytes": result.bytes_written,
    }, json_mode=False)
    return 0
