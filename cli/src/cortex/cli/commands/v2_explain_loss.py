# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex explain-loss`` — explain loss, omission, or non-reversible content.

Canonical name: ``explain-loss`` (since v0.3.2).
Deprecated alias: ``v2-explain-loss`` (still accepted).
"""

from __future__ import annotations

import json
import os

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.view import parse_view_entries_from_doc, calculate_view_coverage
from ...v2.view_renderer import render_hcortex
from ...v2.hcortex_parser import parse_hcortex
from ...v2.encoder import encode_cortex_from_ast
from ...v2.equivalence import compare_ast_equivalent


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    is_hcortex = "internal_encoding: HCORTEX" in text

    losses = []

    if not is_hcortex:
        # CORTEX input: explain what would be lost in CORTEX → HCORTEX → CORTEX
        doc_orig = parse_cortex_v2(text)
        hcortex_md, _ = render_hcortex(doc_orig)
        hdoc = parse_hcortex(hcortex_md, strict=False)
        doc_reconstructed, _ = encode_cortex_from_ast(hdoc)

        ast_eq, diffs = compare_ast_equivalent(doc_orig, doc_reconstructed)
        if not ast_eq:
            losses.append({
                "direction": "CORTEX → HCORTEX → CORTEX",
                "type": "AST-equivalence fail",
                "diff_count": len(diffs),
                "diffs": [d.to_dict() for d in diffs[:10]],
            })

        # Check VIEW coverage
        directives, _ = parse_view_entries_from_doc(doc_orig)
        coverage, uncovered = calculate_view_coverage(doc_orig, directives)
        if coverage < 1.0:
            losses.append({
                "direction": "CORTEX → HCORTEX",
                "type": "incomplete VIEW coverage",
                "coverage_percent": int(coverage * 100),
                "uncovered_count": len(uncovered),
                "uncovered": uncovered[:10],
            })
    else:
        # HCORTEX input
        hdoc = parse_hcortex(text, strict=False)
        losses.append({
            "direction": "HCORTEX parse",
            "type": "diagnostics",
            "diag_count": len(hdoc.diags),
            "diags": [d.to_dict() for d in hdoc.diags[:10]],
        })
        if hdoc.orphan_content:
            losses.append({
                "direction": "HCORTEX parse",
                "type": "orphan content (outside VIEW)",
                "line_count": len(hdoc.orphan_content),
                "sample": hdoc.orphan_content[:5],
            })

    result = {
        "input": args.input,
        "format": "HCORTEX" if is_hcortex else "CORTEX",
        "loss_count": len(losses),
        "losses": losses,
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(f"Input: {args.input} ({result['format']})")
        print(f"Losses detected: {len(losses)}")
        for i, loss in enumerate(losses, 1):
            print(f"\n  Loss {i}: {loss['direction']} — {loss['type']}")
            if 'diff_count' in loss:
                print(f"    diff_count: {loss['diff_count']}")
            if 'coverage_percent' in loss:
                print(f"    coverage: {loss['coverage_percent']}%")
            if 'uncovered_count' in loss:
                print(f"    uncovered: {loss['uncovered_count']} entries")

    return 0 if not losses else 1
