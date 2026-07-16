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


def review_glossary(doc):
    """Return every glossary element with its review state."""
    items = []
    for sigil in sorted(doc.glossary.sigils.values(), key=lambda item: item.sigil):
        items.append({
            "kind": "sigil",
            "name": sigil.sigil,
            "location": "$0",
            "status": "needs_review" if sigil.needs_review else "declared",
            "action": "define type, risk, layer, and description" if sigil.needs_review else "none",
        })
    for status in sorted(doc.glossary.status_custom or []):
        items.append({"kind": "status", "name": status, "location": "$0", "status": "declared", "action": "none"})
    for type_name in sorted(doc.glossary.types_custom or []):
        items.append({"kind": "type", "name": type_name, "location": "$0", "status": "declared", "action": "none"})
    return items


def run_review(args) -> int:
    """List all $0 elements and identify entries that need definition."""
    items = review_glossary(load_doc(args.input))
    pending = sum(item["status"] == "needs_review" for item in items)
    if args.format == "json":
        print(json.dumps({"ok": True, "count": len(items), "pending": pending, "items": items}, indent=2))
    else:
        if not items:
            print("(no glossary elements declared)")
            return 0
        lines = [f"{'KIND':<8} {'NAME':<12} {'STATUS':<14} ACTION", "-" * 72]
        for item in items:
            lines.append(f"{item['kind']:<8} {item['name']:<12} {item['status']:<14} {item['action']}")
        print("\n".join(lines))
    return 0


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
