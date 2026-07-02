# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex format`` — re-serialize a .cortex file canonically."""

from __future__ import annotations

import json

from ...crud.transactions import atomic_write_cortex
from ...core.writer import write_cortex
from ..commands import load_doc


def run(args) -> int:
    doc = load_doc(args.input)
    out_path = args.out or args.input
    if args.dry_run:
        text = write_cortex(doc)
        print(json.dumps({
            "ok": True,
            "dry_run": True,
            "bytes": len(text.encode("utf-8")),
            "preview": text[:500],
        }, indent=2))
        return 0
    result = atomic_write_cortex(doc, out_path, force=args.force)
    print(json.dumps({
        "ok": True,
        "written": result.to_dict(),
    }, indent=2, default=str))
    return 0
