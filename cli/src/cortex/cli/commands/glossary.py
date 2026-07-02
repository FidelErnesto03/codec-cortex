# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex glossary`` — glossary CRUD (list/add/update/delete sigils)."""

from __future__ import annotations

import json

from ...core.errors import CortexError
from ...crud.mutations import (
    add_sigil_to_glossary,
    delete_sigil_from_glossary,
    update_sigil_in_glossary,
)
from ...crud.transactions import atomic_write_cortex
from ..commands import load_doc


def run_list(args) -> int:
    doc = load_doc(args.input)
    sigils = list(doc.glossary.sigils.values())
    if args.format == "json":
        print(json.dumps({
            "ok": True,
            "count": len(sigils),
            "sigils": [s.to_dict() for s in sigils],
        }, indent=2, default=str))
    else:
        if not sigils:
            print("(no sigils declared)")
            return 0
        lines = [
            f"{'SIGIL':<6} {'NAME':<12} {'TYPE':<10} {'RISK':<4} {'LAYER':<14} DESCRIPTION",
            "-" * 80,
        ]
        for s in sigils:
            lines.append(f"{s.sigil:<6} {s.name:<12} {s.type:<10} {s.risk:<4} {s.layer:<14} {s.description}")
        print("\n".join(lines))
    return 0


def run_add(args) -> int:
    doc = load_doc(args.input)
    try:
        add_sigil_to_glossary(
            doc,
            sigil=args.sigil,
            name=args.name,
            type_=args.type,
            risk=args.risk,
            layer=args.layer,
            description=args.description,
            force_governance=args.force_governance,
        )
    except CortexError as e:
        print(f"error: {e}")
        return 1
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "sigil": args.sigil}, indent=2))
        return 0
    result = atomic_write_cortex(doc, args.input, force=False)
    print(json.dumps({"ok": True, "sigil": args.sigil, "written": result.to_dict()}, indent=2, default=str))
    return 0


def run_update(args) -> int:
    doc = load_doc(args.input)
    try:
        update_sigil_in_glossary(
            doc,
            sigil=args.sigil,
            description=args.description,
            risk=args.risk,
            layer=args.layer,
            force_governance=args.force_governance,
        )
    except CortexError as e:
        print(f"error: {e}")
        return 1
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "sigil": args.sigil}, indent=2))
        return 0
    result = atomic_write_cortex(doc, args.input, force=False)
    print(json.dumps({"ok": True, "sigil": args.sigil, "written": result.to_dict()}, indent=2, default=str))
    return 0


def run_delete(args) -> int:
    doc = load_doc(args.input)
    try:
        delete_sigil_from_glossary(doc, sigil=args.sigil, force=args.force)
    except CortexError as e:
        print(f"error: {e}")
        return 1
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "sigil": args.sigil}, indent=2))
        return 0
    result = atomic_write_cortex(doc, args.input, force=False)
    print(json.dumps({"ok": True, "sigil": args.sigil, "written": result.to_dict()}, indent=2, default=str))
    return 0
