"""``cortex list`` — list entries in a .cortex file."""

from __future__ import annotations

import json

from ...crud.selectors import select
from ..commands import emit, load_doc


def run(args) -> int:
    doc = load_doc(args.input)
    # Build selector from filters
    if args.section and args.sigil:
        sel = f"{args.section}/*"
        # narrow by sigil after the fact
        entries = [e for e in select(doc, sel) if e.sigil == args.sigil]
    elif args.section:
        entries = select(doc, f"{args.section}/*")
    elif args.sigil:
        entries = select(doc, f"{args.sigil}:*")
    else:
        entries = select(doc, "*:*")

    if args.format == "json":
        print(json.dumps({
            "ok": True,
            "count": len(entries),
            "entries": [e.to_dict() for e in entries],
        }, indent=2, ensure_ascii=False, default=str))
    else:
        if not entries:
            print("(no entries match)")
            return 0
        lines = []
        lines.append(f"{'SECTION':<6} {'SIGIL':<6} {'NAME':<24} {'TYPE':<10} {'HASH':<16}")
        lines.append("-" * 70)
        for e in entries:
            lines.append(
                f"{e.section:<6} {e.sigil:<6} {e.name:<24} {e.type:<10} "
                f"{e.hash[:16] if e.hash else '':<16}"
            )
        print("\n".join(lines))
    return 0
