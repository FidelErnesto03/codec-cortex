# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex convert`` — convert between CORTEX v2 and HCORTEX.

Canonical name: ``convert`` (since v0.3.2).
Deprecated alias: ``v2-convert`` (still accepted).

v2.3.0: Supports reverse conversion HCORTEX → CORTEX via parse_hcortex + encode_cortex_from_ast.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.writer import write_cortex_v2
from ...v2.view_renderer import render_hcortex
from ...v2.hcortex_parser import parse_hcortex
from ...v2.encoder import encode_cortex_from_ast


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    from_format = args.from_format
    to_format = args.to_format
    deprecated_warning = None

    if from_format == "hcortex-r":
        deprecated_warning = "--from hcortex-r is deprecated. Use --from hcortex."
        from_format = "hcortex"
    if to_format == "hcortex-r":
        deprecated_warning = "--to hcortex-r is deprecated. Use --to hcortex."
        to_format = "hcortex"

    force_write_on_error = getattr(args, "force_write_on_error", False)
    strict = getattr(args, "strict", False)
    mode = getattr(args, "mode", "normal")
    if strict and mode == "normal":
        mode = "strict"

    if deprecated_warning:
        print(f"WARNING: {deprecated_warning}", file=sys.stderr)

    # ---------------------------------------------------------------
    # CORTEX → HCORTEX
    # ---------------------------------------------------------------
    if from_format == "cortex" and to_format == "hcortex":
        doc = parse_cortex_v2(text)
        hcortex_md, diags = render_hcortex(doc, mode=mode)

        errors = [d for d in diags if d.severity == "error"]
        warnings = [d for d in diags if d.severity == "warning"]

        effective_errors = list(errors)
        if strict:
            strict_errors = [d for d in warnings if d.code.startswith("W_VIEW_") or d.code == "W_HCORTEX_DISPLAY_ONLY"]
            effective_errors.extend(strict_errors)
            warnings = [d for d in warnings if d not in strict_errors]

        has_errors = bool(effective_errors)
        should_write_out = bool(args.out) and (not has_errors or force_write_on_error)

        if should_write_out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(hcortex_md)
            _print_cortex_to_hcortex_summary(args, doc, hcortex_md, effective_errors, warnings)
            if has_errors:
                print("  NOTE: --out written despite errors (--force-write-on-error).", file=sys.stderr)
                return 1
        elif args.out and has_errors and not force_write_on_error:
            _print_cortex_to_hcortex_skip(args, doc, hcortex_md, effective_errors, warnings)
            return 1
        else:
            sys.stdout.write(hcortex_md)
            if has_errors:
                _print_diags_to_stderr(effective_errors, warnings)
                return 1
        return 0

    # ---------------------------------------------------------------
    # HCORTEX → CORTEX (v2.3.0 F-09)
    # ---------------------------------------------------------------
    elif from_format == "hcortex" and to_format == "cortex":
        hdoc = parse_hcortex(text, strict=strict)
        doc, enc_diags = encode_cortex_from_ast(hdoc, mode=mode)

        all_diags: list[Any] = list(hdoc.diags) + list(enc_diags)
        errors = [d for d in all_diags if d.severity == "error"]
        warnings = [d for d in all_diags if d.severity == "warning"]

        has_errors = bool(errors)
        should_write_out = bool(args.out) and (not has_errors or force_write_on_error)

        cortex_text = write_cortex_v2(doc)

        if should_write_out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(cortex_text)
            print(f"converted HCORTEX → CORTEX: {args.input} → {args.out}")
            print(f"  sections: {len(doc.sections)}")
            print(f"  entries:  {sum(len(s.entries) for s in doc.sections)}")
            print(f"  blocks:   {len(hdoc.blocks)}")
            print(f"  bytes:    {len(cortex_text.encode('utf-8'))}")
            print(f"  errors:   {len(errors)}")
            print(f"  warnings: {len(warnings)}")
            for d in all_diags[:10]:
                print(f"    [{d.severity}] {d.code}: {d.message}")
            if has_errors:
                print("  NOTE: --out written despite errors (--force-write-on-error).", file=sys.stderr)
                return 1
        elif args.out and has_errors and not force_write_on_error:
            print(f"converted HCORTEX → CORTEX: {args.input} (NOT written — {len(errors)} errors)", file=sys.stderr)
            print(f"  blocks:   {len(hdoc.blocks)}")
            print(f"  errors:   {len(errors)}")
            print(f"  warnings: {len(warnings)}")
            for d in all_diags[:10]:
                print(f"    [{d.severity}] {d.code}: {d.message}")
            print("  Use --force-write-on-error to write --out anyway.", file=sys.stderr)
            return 1
        else:
            sys.stdout.write(cortex_text)
            if has_errors:
                print(f"\n<!-- {len(errors)} errors, {len(warnings)} warnings -->", file=sys.stderr)
                for d in all_diags[:10]:
                    print(f"  [{d.severity}] {d.code}: {d.message}", file=sys.stderr)
                return 1
        return 0

    # ---------------------------------------------------------------
    # CORTEX → CORTEX (identity / format check)
    # ---------------------------------------------------------------
    elif from_format == "cortex" and to_format == "cortex":
        doc = parse_cortex_v2(text)
        reproduced = write_cortex_v2(doc)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(reproduced)
        else:
            sys.stdout.write(reproduced)
        return 0

    else:
        raise CortexError("E021_INVALID_VALUE", f"unsupported conversion: {from_format} → {to_format}")


def _print_cortex_to_hcortex_summary(args, doc, hcortex_md, errors, warnings):
    print(f"converted CORTEX → HCORTEX: {args.input} → {args.out}")
    print(f"  sections: {len(doc.sections)}")
    print(f"  entries:  {sum(len(s.entries) for s in doc.sections)}")
    print(f"  bytes:    {len(hcortex_md.encode('utf-8'))}")
    print(f"  errors:   {len(errors)}")
    print(f"  warnings: {len(warnings)}")
    for d in errors[:10]:
        print(f"    [{d.severity}] {d.code}: {d.message}")
    for d in warnings[:10]:
        print(f"    [{d.severity}] {d.code}: {d.message}")


def _print_cortex_to_hcortex_skip(args, doc, hcortex_md, errors, warnings):
    print(f"converted CORTEX → HCORTEX: {args.input} (NOT written — {len(errors)} errors)", file=sys.stderr)
    print(f"  sections: {len(doc.sections)}")
    print(f"  entries:  {sum(len(s.entries) for s in doc.sections)}")
    print(f"  bytes:    {len(hcortex_md.encode('utf-8'))} (would-be)")
    print(f"  errors:   {len(errors)}")
    print(f"  warnings: {len(warnings)}")
    for d in errors[:10]:
        print(f"    [{d.severity}] {d.code}: {d.message}")
    for d in warnings[:10]:
        print(f"    [{d.severity}] {d.code}: {d.message}")
    print("  Use --force-write-on-error to write --out anyway.", file=sys.stderr)


def _print_diags_to_stderr(errors, warnings):
    print(f"\n<!-- {len(errors)} errors, {len(warnings)} warnings -->", file=sys.stderr)
    for d in errors[:10]:
        print(f"  [{d.severity}] {d.code}: {d.message}", file=sys.stderr)
    for d in warnings[:10]:
        print(f"  [{d.severity}] {d.code}: {d.message}", file=sys.stderr)
