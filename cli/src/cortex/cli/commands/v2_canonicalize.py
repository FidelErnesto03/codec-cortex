"""``cortex v2-canonicalize`` — normalize artefacts without changing semantics."""

from __future__ import annotations

import os
import sys

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.writer import write_cortex_v2
from ...v2.view_renderer import render_hcortex
from ...v2.hcortex_parser import parse_hcortex
from ...v2.encoder import encode_cortex_from_ast


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    is_hcortex = "internal_encoding: HCORTEX" in text

    if is_hcortex:
        # HCORTEX → CORTEX → HCORTEX (canonicalize both)
        hdoc = parse_hcortex(text, strict=False)
        doc, _ = encode_cortex_from_ast(hdoc)
        cortex_text = write_cortex_v2(doc)
        hcortex_md, _ = render_hcortex(doc)

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(hcortex_md)
            print(f"canonicalized HCORTEX: {args.input} → {args.out}")
        else:
            sys.stdout.write(hcortex_md)
    else:
        # CORTEX → CORTEX (canonical form)
        doc = parse_cortex_v2(text)
        canon_text = write_cortex_v2(doc)

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(canon_text)
            print(f"canonicalized CORTEX: {args.input} → {args.out}")
        else:
            sys.stdout.write(canon_text)

    return 0
