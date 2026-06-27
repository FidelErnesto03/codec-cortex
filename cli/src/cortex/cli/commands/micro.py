"""``cortex micro`` — micro-token CRUD."""

from __future__ import annotations

import json

from ...core.errors import CortexError
from ...crud.mutations import (
    add_micro_to_glossary,
    delete_micro_from_glossary,
    update_micro_in_glossary,
)
from ...crud.transactions import atomic_write_cortex
from ..commands import load_doc


def run_list(args) -> int:
    doc = load_doc(args.input)
    micro = list(doc.glossary.micro.values())
    if args.format == "json":
        print(json.dumps({
            "ok": True,
            "count": len(micro),
            "micro": [m.to_dict() for m in micro],
        }, indent=2, default=str))
    else:
        if not micro:
            print("(no micro-tokens declared)")
            return 0
        lines = [f"{'TOKEN':<10} VALUE", "-" * 40]
        for m in micro:
            lines.append(f"{m.token:<10} {m.value}")
        print("\n".join(lines))
    return 0


def run_add(args) -> int:
    doc = load_doc(args.input)
    try:
        add_micro_to_glossary(doc, token=args.token, value=args.value)
    except CortexError as e:
        print(f"error: {e}")
        return 1
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "token": args.token}, indent=2))
        return 0
    result = atomic_write_cortex(doc, args.input, force=False)
    print(json.dumps({"ok": True, "token": args.token, "written": result.to_dict()}, indent=2, default=str))
    return 0


def run_update(args) -> int:
    doc = load_doc(args.input)
    try:
        update_micro_in_glossary(doc, token=args.token, value=args.value)
    except CortexError as e:
        print(f"error: {e}")
        return 1
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "token": args.token}, indent=2))
        return 0
    result = atomic_write_cortex(doc, args.input, force=False)
    print(json.dumps({"ok": True, "token": args.token, "written": result.to_dict()}, indent=2, default=str))
    return 0


def run_delete(args) -> int:
    doc = load_doc(args.input)
    try:
        delete_micro_from_glossary(doc, token=args.token, force=args.force)
    except CortexError as e:
        print(f"error: {e}")
        return 1
    if args.dry_run:
        print(json.dumps({"ok": True, "dry_run": True, "token": args.token}, indent=2))
        return 0
    result = atomic_write_cortex(doc, args.input, force=False)
    print(json.dumps({"ok": True, "token": args.token, "written": result.to_dict()}, indent=2, default=str))
    return 0
