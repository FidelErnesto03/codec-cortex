# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex roundtrip`` — verify CORTEX v2 roundtrip fidelity.

Canonical name: ``roundtrip`` (since v0.3.2).
Deprecated alias: ``v2-roundtrip`` (still accepted).

v2.0.1: compares bytes (not text) using read_bytes(), reports stat bytes.
"""

from __future__ import annotations

import json
import os

from ...core.errors import CortexError
from ...v2.parser import parse_cortex_v2
from ...v2.writer import write_cortex_v2


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")

    # v2.0.1: read as BYTES, not text, to catch CRLF and other encoding differences
    with open(args.input, "rb") as f:
        original_bytes = f.read()

    # Parse from text (UTF-8 decoded) — the parser works on text
    text = original_bytes.decode("utf-8")
    doc = parse_cortex_v2(text)
    reproduced_text = write_cortex_v2(doc)
    reproduced_bytes = reproduced_text.encode("utf-8")

    # v2.0.1: compare BYTES, not text
    stat_bytes = os.path.getsize(args.input)
    text_chars = len(text)
    repro_bytes = len(reproduced_bytes)

    if original_bytes == reproduced_bytes:
        if args.format == "json":
            print(json.dumps({
                "ok": True,
                "input": args.input,
                "sections": len(doc.sections),
                "entries": sum(len(s.entries) for s in doc.sections),
                "stat_bytes": stat_bytes,
                "text_chars": text_chars,
                "repro_bytes": repro_bytes,
                "roundtrip": "byte-identical",
            }, indent=2))
        else:
            print(f"✓ Roundtrip byte-identical: {args.input}")
            print(f"  sections: {len(doc.sections)}")
            print(f"  entries:  {sum(len(s.entries) for s in doc.sections)}")
            print(f"  stat_bytes: {stat_bytes}")
            print(f"  text_chars: {text_chars}")
            print(f"  repro_bytes: {repro_bytes}")
        return 0
    else:
        # Find first byte difference
        diff_offset = -1
        for i in range(min(len(original_bytes), len(reproduced_bytes))):
            if original_bytes[i] != reproduced_bytes[i]:
                diff_offset = i
                break

        # Also find first text line difference for human readability
        orig_lines = text.split('\n')
        repro_lines = reproduced_text.split('\n')
        diff_line = -1
        for i in range(min(len(orig_lines), len(repro_lines))):
            if orig_lines[i] != repro_lines[i]:
                diff_line = i + 1
                break

        if args.format == "json":
            print(json.dumps({
                "ok": False,
                "input": args.input,
                "stat_bytes": stat_bytes,
                "repro_bytes": repro_bytes,
                "text_chars": text_chars,
                "orig_lines": len(orig_lines),
                "repro_lines": len(repro_lines),
                "first_byte_diff": diff_offset,
                "first_line_diff": diff_line,
                "orig_excerpt": orig_lines[diff_line - 1][:120] if diff_line > 0 else "",
                "repro_excerpt": repro_lines[diff_line - 1][:120] if diff_line > 0 else "",
            }, indent=2))
        else:
            print(f"✗ Roundtrip FAILED: {args.input}")
            print(f"  stat_bytes: {stat_bytes}")
            print(f"  repro_bytes: {repro_bytes}")
            print(f"  text_chars: {text_chars}")
            print(f"  orig_lines: {len(orig_lines)}")
            print(f"  repro_lines: {len(repro_lines)}")
            if diff_byte := diff_offset:
                print(f"  first byte diff at offset {diff_byte}:")
                print(f"    orig:  0x{original_bytes[diff_byte]:02x}")
                print(f"    repro: 0x{reproduced_bytes[diff_byte]:02x}")
            if diff_line > 0:
                print(f"  first line diff at line {diff_line}:")
                print(f"    orig:  {orig_lines[diff_line - 1][:120]!r}")
                print(f"    repro: {repro_lines[diff_line - 1][:120]!r}")
        return 1
