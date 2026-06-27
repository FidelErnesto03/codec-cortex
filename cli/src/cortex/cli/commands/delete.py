"""``cortex delete`` (alias: ``cortex patch_remove``) — delete an entry.

v1.1.2: post-mutation validation via :func:`~cortex.cli.commands.post_mutation_gate`
(so deleting a critical FCS in a brain is rejected unless ``--force``).
"""

from __future__ import annotations

import json

from ...core.errors import CortexError
from ...crud.mutations import delete_entry
from ...crud.transactions import atomic_write_cortex
from ..commands import load_doc, post_mutation_gate


def run(args) -> int:
    doc = load_doc(args.input)
    try:
        entry = delete_entry(doc, args.selector, force=args.force)
    except CortexError as e:
        print(f"error: {e}")
        return 1

    if args.dry_run:
        print(json.dumps({
            "ok": True, "dry_run": True,
            "deleted": entry.to_dict(),
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
        "deleted": entry.to_dict(),
        "written": result.to_dict(),
    }, indent=2, default=str))
    return 0
