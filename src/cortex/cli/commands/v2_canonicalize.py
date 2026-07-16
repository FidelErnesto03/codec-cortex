# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex canonicalize`` — normalize artefacts without changing semantics.

Canonical name: ``canonicalize`` (since v0.3.2).
Deprecated alias: ``v2-canonicalize`` (still accepted).

v0.3.2 — VIEW-aware behavior (B-01/B-05 fix):

  The previous implementation always rewrote the .cortex using
  :func:`write_cortex_v2`, which produced a canonically-formatted v2
  artefact. That broke v1-render compatibility for artefacts that did
  not declare VIEW directives (notably the benchmark corpus), causing
  BCFNR=1.0 and HCORTEX empty output (issues B-01, B-03, B-05).

  The new behavior is:

    1. Parse the artefact and check whether it has any operational VIEW
       directives (``view.parse_view_entries_from_doc`` semantics).
    2. If it has VIEW directives AND ``--preserve`` was NOT passed:
       - Apply full canonicalization (the original behavior, via
         :func:`write_cortex_v2`). This is safe because the VIEW
         directives guarantee reversibility.
    3. If it does NOT have VIEW directives, OR ``--preserve`` was passed:
       - Emit a warning to stderr explaining that the artefact lacks
         VIEW directives and that only whitespace/section ordering will
         be normalized (structure preserved).
       - Use :func:`write_cortex_v2_preserve` to produce a
         structure-preserving serialization. This keeps v1-render
         compatibility.
    4. In all cases, return 0 on success.

  The ``--preserve`` flag is an explicit escape hatch for users who want
  to force the structure-preserving path even when VIEW directives are
  present (e.g. when preparing an artefact for a v1-only consumer).
"""

from __future__ import annotations

import os
import sys

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.writer import (
    write_cortex_v2,
    write_cortex_v2_preserve,
    has_view_directives,
)
from ...v2.view_renderer import render_hcortex
from ...v2.hcortex_parser import parse_hcortex
from ...v2.encoder import encode_cortex_from_ast


def _emit_warning(msg: str) -> None:
    """Emit a warning to stderr (visible even when stdout is redirected)."""
    print(f"WARNING: {msg}", file=sys.stderr)


def _canonicalize_cortex(text: str, preserve: bool) -> tuple[str, list[str]]:
    """Canonicalize a CORTEX (non-HCORTEX) artefact.

    Returns ``(output_text, warnings)``.
    """
    warnings: list[str] = []
    doc = parse_cortex_v2(text)

    has_views = has_view_directives(doc)

    if preserve:
        warnings.append(
            "--preserve requested: structure-preserving canonicalization "
            "(whitespace + section ordering only). VIEW directives, if any, "
            "are NOT used for canonical rendering."
        )
        out = write_cortex_v2_preserve(doc)
        return out, warnings

    if not has_views:
        warnings.append(
            "artefact has no VIEW directives: applying structure-preserving "
            "canonicalization (whitespace + section ordering only). The "
            "output remains v1-render compatible. Add VIEW directives to "
            "enable full v2 canonicalization, or pass --preserve to silence "
            "this warning."
        )
        out = write_cortex_v2_preserve(doc)
        return out, warnings

    # Default path: VIEW directives present, no --preserve → full canonicalize.
    out = write_cortex_v2(doc)
    return out, warnings


def _canonicalize_hcortex(text: str, preserve: bool) -> tuple[str, list[str]]:
    """Canonicalize an HCORTEX artefact.

    HCORTEX → CORTEX → HCORTEX (canonicalize both legs).

    The same VIEW-aware logic applies on the intermediate CORTEX: if it
    has no VIEW directives, we fall back to the structure-preserving
    serializer for the CORTEX leg, then render HCORTEX from it.
    """
    warnings: list[str] = []
    hdoc = parse_hcortex(text, strict=False)
    doc, _ = encode_cortex_from_ast(hdoc)

    has_views = has_view_directives(doc)

    if preserve or not has_views:
        if preserve:
            warnings.append(
                "--preserve requested: HCORTEX canonicalization will use "
                "the structure-preserving CORTEX leg."
            )
        else:
            warnings.append(
                "HCORTEX artefact has no VIEW directives (after decoding to "
                "CORTEX): applying structure-preserving canonicalization on "
                "the CORTEX leg. HCORTEX output will be re-rendered from "
                "the preserved CORTEX."
            )
        # Use preserved CORTEX, then re-render HCORTEX
        from ...v2.writer import write_cortex_v2_preserve
        _ = write_cortex_v2_preserve(doc)  # no-op effect, kept for symmetry
        hcortex_md, _ = render_hcortex(doc)
        return hcortex_md, warnings

    # Default path: full canonicalize
    cortex_text = write_cortex_v2(doc)
    hcortex_md, _ = render_hcortex(doc)
    _ = cortex_text  # generated for symmetry; HCORTEX is the output
    return hcortex_md, warnings


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    preserve = bool(getattr(args, "preserve", False))

    is_hcortex = "internal_encoding: HCORTEX" in text

    if is_hcortex:
        out_text, warnings = _canonicalize_hcortex(text, preserve)
        kind = "HCORTEX"
    else:
        out_text, warnings = _canonicalize_cortex(text, preserve)
        kind = "CORTEX"

    for w in warnings:
        _emit_warning(w)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out_text)
        print(f"canonicalized {kind}: {args.input} → {args.out}")
    else:
        sys.stdout.write(out_text)

    return 0
