"""``cortex compare`` — compare two CORTEX/HCORTEX artefacts.

Canonical name: ``compare`` (since v0.3.2).
Deprecated alias: ``v2-compare`` (still accepted).
"""

from __future__ import annotations

import json
import os
import sys

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.hcortex_parser import parse_hcortex
from ...v2.encoder import encode_cortex_from_ast
from ...v2.equivalence import compare_documents, diff_by_sigil, diff_by_section, diff_by_view


def run(args) -> int:
    if not os.path.exists(args.left):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.left}")
    if not os.path.exists(args.right):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.right}")

    with open(args.left, "r", encoding="utf-8") as f:
        left_text = f.read()
    with open(args.right, "r", encoding="utf-8") as f:
        right_text = f.read()

    # Parse both
    left_doc = _parse_any(left_text)
    right_doc = _parse_any(right_text)

    left_bytes = left_text.encode("utf-8")
    right_bytes = right_text.encode("utf-8")

    result = compare_documents(left_doc, right_doc, left_bytes, right_bytes)

    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print(f"byte_identical: {result.byte_identical}")
        print(f"ast_equivalent: {result.ast_equivalent}")
        print(f"semantic_equivalent: {result.semantic_equivalent}")
        print(f"content_equivalent: {result.content_equivalent}")
        print(f"diff_count: {len(result.diffs)}")

        if result.diffs:
            print("\nDiffs by section:")
            for sec, ds in diff_by_section(result.diffs).items():
                print(f"  {sec}: {len(ds)} diffs")
            print("\nDiffs by sigil:")
            for sig, ds in diff_by_sigil(result.diffs).items():
                print(f"  {sig}: {len(ds)} diffs")
            print("\nDiffs by VIEW:")
            for v, ds in diff_by_view(result.diffs).items():
                print(f"  {v}: {len(ds)} diffs")

            if args.verbose:
                print("\nFirst 20 diffs:")
                for d in result.diffs[:20]:
                    print(f"  {d.kind} at {d.location}" + (f".{d.field}" if d.field else ""))

    return 0 if result.equivalent else 1


def _parse_any(text):
    """Parse text as CORTEX or HCORTEX, return CortexV2Document."""
    if "internal_encoding: HCORTEX" in text:
        hdoc = parse_hcortex(text, strict=False)
        doc, _ = encode_cortex_from_ast(hdoc)
        return doc
    else:
        return parse_cortex_v2(text)
