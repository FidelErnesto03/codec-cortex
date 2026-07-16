# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex diagram`` — DIAG bloque operations (list, extract, validate).

Closes audit gap B-010: the SKILL plans ``diagram list/extract/validate``
(Section 22.2). This module implements them as thin wrappers over the AST.
"""

from __future__ import annotations

import json
import sys

from ...core.ast import CortexDocument
from ...core.errors import CortexError, NotFoundError
from ..commands import load_doc


def _find_diagrams(doc: CortexDocument, name: str | None = None) -> list:
    """Return all DIAG entries (optionally filtered by name)."""

    out = []
    for sec, entry in doc.iter_entries():
        if entry.sigil != "DIAG":
            continue
        if name and entry.name != name:
            continue
        out.append((sec, entry))
    return out


def run_list(args) -> int:
    doc = load_doc(args.input)
    diags = _find_diagrams(doc)
    if args.format == "json":
        print(json.dumps({
            "ok": True,
            "count": len(diags),
            "diagrams": [
                {
                    "section": sec.id,
                    "name": e.name,
                    "hash": e.hash,
                    "bytes": len(str(e.value or "").encode("utf-8")),
                }
                for sec, e in diags
            ],
        }, indent=2, default=str))
    else:
        if not diags:
            print("(no DIAG entries)")
            return 0
        print(f"{'SECTION':<8} {'NAME':<24} {'BYTES':<8} HASH")
        print("-" * 70)
        for sec, e in diags:
            nbytes = len(str(e.value or "").encode("utf-8"))
            print(f"{sec.id:<8} {e.name:<24} {nbytes:<8} {e.hash[:16]}")
    return 0


def run_extract(args) -> int:
    """Extract a DIAG bloque verbatim.

    Re-audit H-RA-04: the previous implementation appended a trailing
    newline, which broke byte-exact preservation.  Now we write the
    value as-is.  Use ``--print-newline`` to add a trailing newline on
    stdout output for terminal friendliness.
    """

    doc = load_doc(args.input)
    diags = _find_diagrams(doc, name=args.name)
    if not diags:
        raise NotFoundError(f"DIAG:{args.name}")
    if len(diags) > 1:
        raise CortexError(
            "E014_AMBIGUOUS_SELECTOR",
            f"multiple DIAG entries named {args.name!r}",
        )
    _, entry = diags[0]
    text = str(entry.value or "")
    if args.out:
        # Write exactly the bytes — no appended newline.
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"extracted DIAG:{args.name} → {args.out} ({len(text)} bytes, verbatim)")
    else:
        # Default: write exactly the bytes (no trailing newline)
        sys.stdout.write(text)
        if getattr(args, "print_newline", False):
            sys.stdout.write("\n")
    return 0


def run_validate(args) -> int:
    doc = load_doc(args.input)
    diags = _find_diagrams(doc, name=args.name)
    if not diags:
        if args.format == "json":
            print(json.dumps({"ok": False, "error": "no DIAG entries found"}))
        else:
            print("no DIAG entries found")
        return 1
    findings = []
    for sec, entry in diags:
        text = str(entry.value or "")
        issues = []
        # Heuristics: check for balanced @startuml/@enduml, balanced braces
        if "@startuml" in text and "@enduml" not in text:
            issues.append("missing @enduml")
        if "@enduml" in text and "@startuml" not in text:
            issues.append("missing @startuml")
        if text.count("{") != text.count("}"):
            issues.append(f"unbalanced braces ({text.count('{')} '{{' vs {text.count('}')} '}}')")
        findings.append({
            "section": sec.id,
            "name": entry.name,
            "bytes": len(text),
            "issues": issues,
            "valid": len(issues) == 0,
        })
    if args.format == "json":
        print(json.dumps({"ok": all(f["valid"] for f in findings), "diagrams": findings},
                         indent=2, default=str))
    else:
        all_valid = all(f["valid"] for f in findings)
        print(f"validation: {'OK' if all_valid else 'ISSUES'}")
        for f in findings:
            status = "✓" if f["valid"] else "✗"
            print(f"  {status} {f['section']}/DIAG:{f['name']} ({f['bytes']} bytes)")
            for issue in f["issues"]:
                print(f"      - {issue}")
    return 0 if all(f["valid"] for f in findings) else 2
