# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex get`` — fetch a single entry by selector."""

from __future__ import annotations

import json

from ...core.errors import CortexError
from ...crud.selectors import select_one
from ..commands import load_doc


def run(args) -> int:
    doc = load_doc(args.input)
    try:
        entry = select_one(doc, args.selector)
    except CortexError as e:
        if args.format == "json":
            print(json.dumps({"ok": False, "error": {"code": e.code, "message": e.message}}))
        else:
            print(f"error: {e}")
        return 1
    if args.format == "json":
        print(json.dumps({
            "ok": True,
            "entry": entry.to_dict(),
        }, indent=2, ensure_ascii=False, default=str))
    else:
        lines = []
        lines.append(f"section: {entry.section}")
        lines.append(f"sigil:   {entry.sigil}")
        lines.append(f"name:    {entry.name}")
        lines.append(f"type:    {entry.type}")
        lines.append(f"hash:    {entry.hash}")
        lines.append(f"lines:   {entry.line_start}-{entry.line_end}")
        lines.append("")
        lines.append("value:")
        if isinstance(entry.value, dict):
            for k, v in entry.value.items():
                lines.append(f"  {k}: {v!r}")
        else:
            lines.append(f"  {entry.value}")
        lines.append("")
        lines.append(f"raw: {entry.raw}")
        print("\n".join(lines))
    return 0
