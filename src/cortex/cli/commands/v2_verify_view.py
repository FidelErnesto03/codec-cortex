# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex verify-view`` — validate VIEW coverage, reversibility, consistency.

Canonical name: ``verify-view`` (since v0.3.2).
Deprecated alias: ``v2-verify-view`` (still accepted).
"""

from __future__ import annotations

import json
import os

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.view import parse_view_entries_from_doc, calculate_view_coverage
from ...v2.view_renderer import render_hcortex


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    directives, view_diags = parse_view_entries_from_doc(doc)
    coverage, uncovered = calculate_view_coverage(doc, directives)

    # Render to get full diagnostics
    _, render_diags = render_hcortex(doc)

    all_diags = list(view_diags) + list(render_diags)
    errors = [d for d in all_diags if d.severity == "error"]
    warnings = [d for d in all_diags if d.severity == "warning"]

    is_reversible = (coverage == 1.0) and (len(errors) == 0)

    result = {
        "view_count": len(directives),
        "view_coverage_percent": int(coverage * 100),
        "uncovered_count": len(uncovered),
        "uncovered": uncovered[:20],
        "errors": len(errors),
        "warnings": len(warnings),
        "reversible": is_reversible,
        "diagnostics": [d.to_dict() for d in all_diags[:20]],
    }

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"VIEW directives: {len(directives)}")
        print(f"VIEW coverage: {coverage:.1%}")
        print(f"Uncovered entries: {len(uncovered)}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")
        print(f"Reversible: {is_reversible}")
        for d in all_diags[:10]:
            print(f"  [{d.severity}] {d.code}: {d.message}")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0
