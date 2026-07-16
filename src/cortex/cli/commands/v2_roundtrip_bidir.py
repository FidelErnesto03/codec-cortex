# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex roundtrip-bidir`` — validate CORTEX ⇄ HCORTEX roundtrip.

Canonical name: ``roundtrip-bidir`` (since v0.3.2).
Deprecated alias: ``v2-roundtrip-bidir`` (still accepted).

v2.3.1: Fixed Direction 2 logic — was using CORTEX as HCORTEX.
Now properly tests both directions with correct format detection.
"""

from __future__ import annotations

import os
import sys

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.writer import write_cortex_v2
from ...v2.view_renderer import render_hcortex
from ...v2.hcortex_parser import parse_hcortex
from ...v2.encoder import encode_cortex_from_ast
from ...v2.equivalence import compare_ast_equivalent, compare_content_equivalent


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    is_hcortex = "<!-- CODEC-CORTEX" in text and "internal_encoding: HCORTEX" in text
    is_cortex = "<!-- CODEC-CORTEX" in text and "internal_encoding: CORTEX" in text

    if is_cortex:
        # Input is CORTEX
        # Direction 1: CORTEX → HCORTEX → CORTEX (AST-equivalent)
        print("=== Direction 1: CORTEX → HCORTEX → CORTEX ===")
        rc1 = _roundtrip_cortex_to_hcortex_to_cortex(text)

        # Direction 2: CORTEX → HCORTEX → CORTEX → HCORTEX (content-equivalent)
        # We use the HCORTEX produced in Direction 1 as input
        print("\n=== Direction 2: HCORTEX → CORTEX → HCORTEX ===")
        # Generate HCORTEX from CORTEX first, then test HCORTEX → CORTEX → HCORTEX
        doc = parse_cortex_v2(text)
        hcortex_md, _ = render_hcortex(doc)
        rc2 = _roundtrip_hcortex_to_cortex_to_hcortex(hcortex_md)
        return rc1 or rc2

    elif is_hcortex:
        # Input is HCORTEX
        # Direction 1: HCORTEX → CORTEX → HCORTEX (content-equivalent)
        print("=== Direction 1: HCORTEX → CORTEX → HCORTEX ===")
        rc1 = _roundtrip_hcortex_to_cortex_to_hcortex(text)

        # Direction 2: HCORTEX → CORTEX → HCORTEX → CORTEX (AST-equivalent)
        # Use the CORTEX reconstructed in Direction 1 as input
        print("\n=== Direction 2: CORTEX → HCORTEX → CORTEX ===")
        hdoc = parse_hcortex(text, strict=False)
        doc, _ = encode_cortex_from_ast(hdoc)
        cortex_text = write_cortex_v2(doc)
        rc2 = _roundtrip_cortex_to_hcortex_to_cortex(cortex_text)
        return rc1 or rc2
    else:
        print("ERROR: Could not detect format (no CODEC-CORTEX header)", file=sys.stderr)
        return 1


def _roundtrip_cortex_to_hcortex_to_cortex(cortex_text: str) -> int:
    """CORTEX → HCORTEX → CORTEX: verify AST equivalence."""

    cortex_text.encode("utf-8")
    doc_orig = parse_cortex_v2(cortex_text)
    sum(len(s.entries) for s in doc_orig.sections)

    # CORTEX → HCORTEX
    hcortex_md, diags = render_hcortex(doc_orig)
    print(f"CORTEX → HCORTEX: {len(hcortex_md)} chars, {len(diags)} diags")

    # HCORTEX → CORTEX
    hdoc = parse_hcortex(hcortex_md, strict=False)
    doc_reconstructed, enc_diags = encode_cortex_from_ast(hdoc)
    recon_entry_count = sum(len(s.entries) for s in doc_reconstructed.sections)
    print(f"HCORTEX → CORTEX: {len(doc_reconstructed.sections)} sections, {recon_entry_count} entries")
    if enc_diags:
        for enc_d in enc_diags[:3]:
            print(f"  [{enc_d.severity}] {enc_d.code}: {enc_d.message}")

    # Compare AST
    ast_eq, diffs = compare_ast_equivalent(doc_orig, doc_reconstructed)
    print(f"AST equivalent: {ast_eq} ({len(diffs)} diffs)")

    if ast_eq:
        print("✓ CORTEX → HCORTEX → CORTEX roundtrip: AST-equivalent")
        return 0
    else:
        print("✗ Roundtrip NOT AST-equivalent")
        for d2 in diffs[:5]:
            print(f"  {d2.kind} at {d2.location}" + (f".{d2.field}" if d2.field else ""))
        return 1


def _roundtrip_hcortex_to_cortex_to_hcortex(hcortex_text: str) -> int:
    """HCORTEX → CORTEX → HCORTEX: verify content equivalence."""

    # HCORTEX → CORTEX
    hdoc_orig = parse_hcortex(hcortex_text, strict=False)
    doc, enc_diags = encode_cortex_from_ast(hdoc_orig)
    print(f"HCORTEX → CORTEX: {len(doc.sections)} sections, {sum(len(s.entries) for s in doc.sections)} entries")
    if enc_diags:
        for enc_d in enc_diags[:3]:
            print(f"  [{enc_d.severity}] {enc_d.code}: {enc_d.message}")

    # CORTEX → HCORTEX
    hcortex_regen, diags = render_hcortex(doc)
    print(f"CORTEX → HCORTEX: {len(hcortex_regen)} chars")

    # Compare content
    content_eq, diffs = compare_content_equivalent(hcortex_text, hcortex_regen)
    print(f"Content equivalent: {content_eq} ({len(diffs)} diffs)")

    if content_eq:
        print("✓ HCORTEX → CORTEX → HCORTEX roundtrip: content-equivalent")
        return 0
    else:
        print("✗ Roundtrip NOT content-equivalent")
        for d2 in diffs[:5]:
            print(f"  {d2.kind} at {d2.location}")
        return 1
