"""``cortex inspect`` — show AST, sections, sigils, VIEW coverage, errors.

Canonical name: ``inspect`` (since v0.3.2).
Deprecated alias: ``v2-inspect`` (still accepted).
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.view import parse_view_entries_from_doc, calculate_view_coverage


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    is_hcortex = "internal_encoding: HCORTEX" in text

    if is_hcortex:
        # For HCORTEX, parse and report blocks
        from ...v2.hcortex_parser import parse_hcortex
        hdoc = parse_hcortex(text, strict=False)
        result = {
            "format": "HCORTEX",
            "header": hdoc.header.__dict__,
            "block_count": len(hdoc.blocks),
            "orphan_lines": len(hdoc.orphan_content),
            "diagnostics": [d.to_dict() for d in hdoc.diags],
            "blocks": [
                {
                    "view_name": b.view_name,
                    "kind": b.kind,
                    "target": b.target,
                    "reverse": b.reverse,
                    "section": b.section,
                }
                for b in hdoc.blocks
            ],
        }
    else:
        doc = parse_cortex_v2(text)
        directives, diags = parse_view_entries_from_doc(doc)
        coverage, uncovered = calculate_view_coverage(doc, directives)

        # Sigil distribution
        sigil_counter: Counter = Counter()
        for sec in doc.sections:
            for e in sec.entries:
                sigil_counter[e.sigil] += 1

        # Entry type distribution
        type_counter: Counter = Counter()
        for sec in doc.sections:
            for e in sec.entries:
                type_counter[e.entry_type] += 1

        result = {
            "format": "CORTEX",
            "header": doc.header,
            "section_count": len(doc.sections),
            "entry_count": sum(len(s.entries) for s in doc.sections),
            "view_count": len(directives),
            "view_coverage_percent": int(coverage * 100),
            "uncovered_count": len(uncovered),
            "reversible": (coverage == 1.0) and not any(d.severity == "error" for d in diags),
            "sections": [
                {
                    "id": s.id,
                    "entry_count": len(s.entries),
                }
                for s in doc.sections
            ],
            "sigil_distribution": dict(sigil_counter.most_common()),
            "entry_type_distribution": dict(type_counter.most_common()),
            "diagnostics": [d.to_dict() for d in diags[:20]],
        }

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(f"Format: {result['format']}")
        if result['format'] == "CORTEX":
            print(f"Sections: {result['section_count']}")
            print(f"Entries: {result['entry_count']}")
            print(f"VIEW directives: {result['view_count']}")
            print(f"VIEW coverage: {result['view_coverage_percent']}%")
            print(f"Reversible: {result['reversible']}")
            print(f"\nSections:")
            for s in result['sections']:
                print(f"  {s['id']}: {s['entry_count']} entries")
            print(f"\nSigil distribution:")
            for sig, cnt in list(result['sigil_distribution'].items())[:15]:
                print(f"  {sig}: {cnt}")
            print(f"\nEntry type distribution:")
            for t, cnt in result['entry_type_distribution'].items():
                print(f"  {t}: {cnt}")
        else:
            print(f"Header: reversible={result['header']['reversible']}, view_coverage={result['header']['view_coverage']}")
            print(f"Blocks: {result['block_count']}")
            print(f"Orphan lines: {result['orphan_lines']}")
            print(f"\nBlocks:")
            for b in result['blocks']:
                print(f"  {b['view_name']}: kind={b['kind']}, target={b['target']}, reverse={b['reverse']}")

    return 0
