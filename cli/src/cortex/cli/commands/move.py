"""``cortex move`` — move an entry to another section.

v1.1.2: post-mutation validation via :func:`~cortex.cli.commands.post_mutation_gate`
(so moving an entry to a section that violates level policy is rejected
unless ``--force``).
"""

from __future__ import annotations

import json

from ...core.errors import CortexError
from ...crud.mutations import move_entry
from ...crud.transactions import atomic_write_cortex
from ..commands import load_doc, post_mutation_gate


def run(args) -> int:
    doc = load_doc(args.input)
    try:
        entry = move_entry(doc, args.selector, args.to_section)
    except CortexError as e:
        print(f"error: {e}")
        return 1

    if args.dry_run:
        print(json.dumps({
            "ok": True, "dry_run": True,
            "moved": entry.to_dict(),
        }, indent=2, default=str))
        return 0

    # v1.1.2: post-mutation validation gate (same as add).
    err = post_mutation_gate(doc, args)
    if err is not None:
        print(json.dumps(err, indent=2, default=str))
        return 1

    result = atomic_write_cortex(doc, args.input, force=args.force)
    print(json.dumps({
        "ok": True,
        "moved": entry.to_dict(),
        "written": result.to_dict(),
    }, indent=2, default=str))
    return 0
