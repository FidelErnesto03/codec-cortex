# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex update`` (alias: ``cortex patch_update``) — update an existing entry.

v1.1.2: post-mutation validation via :func:`~cortex.cli.commands.post_mutation_gate`
(so an update that breaks a contract is rejected unless ``--force``).
"""

from __future__ import annotations

import json
import re

from ...core.errors import CortexError
from ...crud.mutations import update_entry
from ...crud.transactions import atomic_write_cortex
from ..commands import load_doc, post_mutation_gate


_SET_PAIR_RE = re.compile(r'^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<val>.*)$')


def _parse_set_pairs(pairs):
    out = {}
    for p in pairs:
        m = _SET_PAIR_RE.match(p)
        if not m:
            raise CortexError("E021_INVALID_VALUE", f"invalid --set pair: {p!r} (expected key=value)")
        key = m.group("key")
        val = m.group("val")
        # Strip surrounding quotes
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        elif val == "true":
            val = True
        elif val == "false":
            val = False
        elif val.lower() in ("null", "none", "nil", "undefined"):
            # v1.1.7 P0-3 + v1.1.8: convert null-like literals to None
            val = None
        elif isinstance(val, str) and re.fullmatch(r"-?\d+", val):
            val = int(val)
        elif isinstance(val, str) and re.fullmatch(r"-?\d+\.\d+", val):
            val = float(val)
        out[key] = val
    return out


def run(args) -> int:
    doc = load_doc(args.input)
    set_ = _parse_set_pairs(args.set_pairs) if args.set_pairs else None
    try:
        entry = update_entry(
            doc,
            args.selector,
            set_=set_,
            replace_body=args.body,
            append=args.append,
        )
    except CortexError as e:
        print(f"error: {e}")
        return 1

    if args.dry_run:
        print(json.dumps({
            "ok": True, "dry_run": True,
            "entry": entry.to_dict(),
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
        "entry": entry.to_dict(),
        "written": result.to_dict(),
    }, indent=2, default=str))
    return 0
