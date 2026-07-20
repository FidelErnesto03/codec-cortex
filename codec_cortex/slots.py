#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.2 scalars — slot lexer + slot contract parser.

NEW module: does NOT touch codec_cortex/scalars.py (0.1 preserved).
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, List, Tuple, Optional

from .scalars import (
    Scalar, ParseError, StringCursor, emit_string_literal,
    parse_string_literal, ATOM_RE, _INT_RE, _DEC_RE, to_nfc,
)


# Slot marker constants
SLOT_MARKER = "※"                    # U+203B REFERENCE MARK
SLOT_MARKER_BYTES = b"\xe2\x80\xbb"
SLOT_MARKER_CODEPOINT = 0x203B
SLOT_INDEX_MAX = 1_000_000

# Forbidden homoglyphs (L020_INVALID_SLOT_MARKER)
HOMOGLYPHS = {
    "•": "U+2022 BULLET",
    "·": "U+00B7 MIDDLE DOT",
    "∙": "U+2219 BULLET OPERATOR",
    "●": "U+25CF BLACK CIRCLE",
}

# Regexes
_SLOT_INDEX_RE = re.compile(r"^([1-9][0-9]*)$")


@dataclass
class SlotContractField:
    position: int
    name: str
    type: str
    required: bool


@dataclass
class SlotEntry:
    """A parsed slot reference from an Idea payload: (index, scalar)."""
    index: int
    value: Scalar
    line: int
    col: int
    byte_offset: int


@dataclass
class FieldValue:
    """Resolved slot value with full contract metadata."""
    position: int
    name: str
    type: str
    required: bool
    value: Scalar
    source_span: Optional[Tuple[int, int]] = None


def detect_homoglyph(ch: str) -> Optional[str]:
    return HOMOGLYPHS.get(ch)


def is_ascii_digit(ch: str) -> bool:
    """Return True only for ASCII 0-9. Rejects Unicode digits (Arabic-Indic, etc.)."""
    return ch in "0123456789"


def is_nonzero_ascii_digit(ch: str) -> bool:
    return ch in "123456789"


# ---------------------------------------------------------------------------
# Slot contract parser — used to parse the `slots:"1=name:type?|2=name:type?"` attr
# in a sigil declaration. Does NOT contain ※.
# ---------------------------------------------------------------------------

def parse_slot_contract(s: str, line: int = 0) -> List[SlotContractField]:
    """Parse '1=name:type?|2=name:type?' into ordered SlotContractField list."""
    out: List[SlotContractField] = []
    if not s:
        return out
    parts = s.split("|")
    for part in parts:
        part = part.strip()
        if not part:
            raise ParseError("G008_INVALID_CONTRACT",
                             f"Empty slot-contract entry in {s!r}", line)
        if "=" not in part:
            raise ParseError("G008_INVALID_CONTRACT",
                             f"Slot entry missing '=': {part!r}", line)
        pos_str, rest = part.split("=", 1)
        pos_str = pos_str.strip()
        if not _SLOT_INDEX_RE.match(pos_str):
            raise ParseError("G008_INVALID_CONTRACT",
                             f"Invalid slot position {pos_str!r}", line)
        position = int(pos_str)
        if position == 0:
            raise ParseError("L022_SLOT_ZERO_FORBIDDEN",
                             "Slot position 0 forbidden", line)
        if position > SLOT_INDEX_MAX:
            raise ParseError("I057_SLOT_INDEX_LIMIT",
                             f"Slot position {position} exceeds max {SLOT_INDEX_MAX}", line)
        # name:type[?]
        required = True
        if rest.endswith("?"):
            required = False
            rest = rest[:-1]
        if ":" in rest:
            name, type_ = rest.split(":", 1)
        else:
            name, type_ = rest, "any"
        name = name.strip()
        type_ = type_.strip()
        if not name:
            raise ParseError("G008_INVALID_CONTRACT",
                             f"Empty slot name in {part!r}", line)
        out.append(SlotContractField(position=position, name=name, type=type_, required=required))
    return out


def validate_slot_contract(fields: List[SlotContractField], line: int = 0) -> None:
    """Validate a parsed slot contract: contiguous from 1, no dup positions, no dup names."""
    seen_pos = set()
    seen_name = set()
    for f in fields:
        if f.position in seen_pos:
            raise ParseError("G035_DUPLICATE_SLOT_POSITION",
                             f"Duplicate slot position {f.position}", line)
        if f.name in seen_name:
            raise ParseError("G036_DUPLICATE_SLOT_NAME",
                             f"Duplicate slot name {f.name!r}", line)
        seen_pos.add(f.position)
        seen_name.add(f.name)
    # Contiguity check (sorted)
    sorted_fields = sorted(fields, key=lambda f: f.position)
    expected = 1
    for f in sorted_fields:
        if f.position != expected:
            raise ParseError("G034_SLOT_CONTRACT_GAP",
                             f"Slot positions not contiguous: expected {expected}, got {f.position}", line)
        expected += 1


# ---------------------------------------------------------------------------
# Slot ref parser — used in Idea payloads {※N:valor}
# ---------------------------------------------------------------------------

def parse_slot_ref(cur: StringCursor) -> int:
    """Parse ※N: at cursor. Returns the validated integer index."""
    ch = cur.peek()
    if ch != SLOT_MARKER:
        hg = detect_homoglyph(ch)
        if hg:
            raise ParseError("L020_INVALID_SLOT_MARKER",
                             f"Slot marker is not ※ (got {hg})",
                             cur.line, cur.col)
        raise ParseError("L020_INVALID_SLOT_MARKER",
                         f"Expected ※ at start of slot ref, got {ch!r}",
                         cur.line, cur.col)
    cur.next()  # consume ※
    # Read ASCII digits only
    digits = []
    while cur.peek() and is_ascii_digit(cur.peek()):
        digits.append(cur.peek())
        cur.next()
    if not digits:
        raise ParseError("L021_INVALID_SLOT_INDEX",
                         "Missing integer after ※",
                         cur.line, cur.col)
    raw = "".join(digits)
    if len(raw) > 1 and raw[0] == "0":
        raise ParseError("L023_SLOT_LEADING_ZERO",
                         f"Slot index has leading zero: ※{raw}",
                         cur.line, cur.col)
    if raw == "0":
        raise ParseError("L022_SLOT_ZERO_FORBIDDEN",
                         "Slot index 0 is forbidden",
                         cur.line, cur.col)
    idx = int(raw)
    if idx > SLOT_INDEX_MAX:
        raise ParseError("I057_SLOT_INDEX_LIMIT",
                         f"Slot index {idx} exceeds max {SLOT_INDEX_MAX}",
                         cur.line, cur.col)
    if cur.peek() != ":":
        raise ParseError("L024_SLOT_SEPARATOR_REQUIRED",
                         f"Missing ':' after slot index ※{raw}",
                         cur.line, cur.col)
    cur.next()  # consume :
    return idx


def parse_slot_payload(s: str, start_line: int = 1) -> List[Tuple[int, Scalar, Tuple[int, int]]]:
    """Parse {※1:v,※2:v} payload. Returns list of (index, Scalar, (line, col))."""
    from .scalars import parse_scalar, skip_inline_ws
    cur = StringCursor(s, line=start_line)
    skip_inline_ws(cur)
    if cur.peek() != "{":
        raise ParseError("S006_INVALID_ATTRS", "Expected { for slot payload",
                         cur.line, cur.col)
    cur.next()
    entries: List[Tuple[int, Scalar, Tuple[int, int]]] = []
    skip_inline_ws(cur)
    if cur.peek() == "}":
        cur.next()
        return entries
    # First entry must start with ※ (or be a homoglyph / pipe / named key)
    _check_slot_start(cur)
    while True:
        skip_inline_ws(cur)
        # Detect pipe or named attr at start of entry
        _check_slot_start(cur)
        idx = parse_slot_ref(cur)
        skip_inline_ws(cur)
        v = parse_scalar(cur)
        entries.append((idx, v, (cur.line, cur.col)))
        skip_inline_ws(cur)
        c = cur.peek()
        if c == ",":
            cur.next()
            skip_inline_ws(cur)
            # Trailing comma check (P17)
            if cur.peek() == "}":
                cur.next()
                raise ParseError("S006_INVALID_ATTRS",
                                 "Trailing comma before } in slot payload",
                                 cur.line, cur.col)
            continue
        elif c == "}":
            cur.next()
            break
        else:
            raise ParseError("S006_INVALID_ATTRS",
                             f"Expected , or }} got {c!r}",
                             cur.line, cur.col)
    return entries


def _check_slot_start(cur: StringCursor) -> None:
    """Verify the next non-ws char is a valid slot-ref start; raise I055/I056/L020 appropriately."""
    ch = cur.peek()
    if ch == "":
        return
    if ch == SLOT_MARKER:
        return
    # Homoglyph
    if detect_homoglyph(ch):
        raise ParseError("L020_INVALID_SLOT_MARKER",
                         f"Slot marker is not ※ (got {detect_homoglyph(ch)})",
                         cur.line, cur.col)
    # Pipe → I056
    if ch == "|":
        raise ParseError("I056_PIPE_PAYLOAD_IN_SLOT_IDEA",
                         "Pipe payload not allowed in slot-encoded Idea",
                         cur.line, cur.col)
    # Named key:value → I055: peek ahead for alpha+colon
    if ch.isalpha() or ch == "_":
        save = (cur.i, cur.line, cur.col)
        while cur.peek() and cur.peek() not in " \t:,":
            if cur.peek() == "}":
                break
            cur.next()
        if cur.peek() == ":":
            raise ParseError("I055_NAMED_ATTR_IN_SLOT_IDEA",
                             "Named key:value not allowed in slot-encoded Idea",
                             save[1], save[2])
        # Restore
        cur.i, cur.line, cur.col = save


# ---------------------------------------------------------------------------
# Mixed-version check for 0.1 parser (I058)
# ---------------------------------------------------------------------------

def check_mixed_surface_legacy(source: str) -> None:
    """Raise I058_MIXED_SURFACE_VERSION if a structural ※ slot-ref appears in a 0.1 doc.

    A structural slot-ref is ※N: that appears OUTSIDE of:
    - string literals (quoted)
    - cuerpo content (between { } on its own line for cuerpo shape)
    - bloque content (between { } on its own line for bloque shape)
    - comments (# ...)

    Inside strings/cuerpo/bloque, ※ is ordinary content (P01/P02/P03).

    This is intentionally conservative: we walk the source tracking which regions
    are "structural" vs "content". A simple line-based scan is insufficient because
    cuerpo/bloque can span multiple lines. We use a state machine.
    """
    # We need to know the shape of each Idea to know if {...} is cuerpo/bloque
    # or attrs. Without parsing the full doc, we use a heuristic:
    # - Track when we enter a multiline body (line ends with just `{` and the
    #   Idea sigil was declared with shape cuerpo/bloque in $0).
    # This is hard to do reliably without parsing. Instead, we delegate to the
    # 0.1 parser: if the doc parses cleanly as 0.1, then any ※ inside string
    # values or cuerpo/bloque payloads is preserved as content (no I058).
    # Only ※ that the 0.1 parser would interpret as a structural token (which
    # is none, since 0.1 doesn't recognize ※) triggers I058.
    #
    # Strategy: parse the doc as 0.1. Walk the resulting AST. For each Idea,
    # check if ※N: appears in:
    #   - attrs keys (would mean a slot-ref was used as a key — structural)
    #   - attrs string values (allowed — content)
    #   - cuerpo/bloque text (allowed — content)
    # The structural violation is when ※N: appears in an attrs *key* position.
    # Since 0.1 attrs keys are parsed as `[^ \t:,}]+`, ※1 would parse as a key.
    # If we see ※N: as a key in an attrs Idea, that's I058.
    #
    # However, this requires the 0.1 parser to NOT choke on ※ in keys. Let's
    # check empirically: 0.1 ATOM_RE doesn't include ※, so ※1 as an atom would
    # fail with L010_INVALID_ATOM. We need a different approach.
    #
    # Final strategy: scan the source line by line. For each line that is NOT
    # inside a cuerpo/bloque block and NOT inside a string, look for ※N: pattern.
    # Track multiline body state by detecting lines that are just `{` (start of
    # cuerpo/bloque) and lines that are just `}` (end). This is a heuristic but
    # covers the P02/P03 cases correctly.
    in_multiline_body = False
    for ln_no, ln in enumerate(source.split("\n"), 1):
        stripped = ln.strip()
        if stripped.startswith("#"):
            continue
        if in_multiline_body:
            if stripped == "}":
                in_multiline_body = False
            continue  # don't scan body content
        # Check if this line starts a multiline body
        # (an Idea line ending with just `{`)
        if stripped.endswith("{") and not stripped.startswith("{"):
            # Check if it's an Idea line (starts with sigil pattern)
            if re.match(r"^(?:[a-z][a-z0-9_.-]*::)?(!|[A-Z][A-Z0-9_]*):", stripped):
                in_multiline_body = True
                # Don't scan this line further (the `{` is structural, no ※ before it
                # would be inside the body)
                # But check the part before `{` for ※N: (that would be in the head)
                before_brace = stripped[:-1]
                _scan_for_structural_slot_ref(before_brace, ln_no)
                continue
        # Single-line case: scan the line, respecting string boundaries
        _scan_for_structural_slot_ref(ln, ln_no)


def _scan_for_structural_slot_ref(line: str, ln_no: int) -> None:
    """Scan a single line for ※N: pattern outside string literals."""
    in_string = False
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if c == '"':
            in_string = not in_string
        elif not in_string and c == SLOT_MARKER:
            # Peek for ASCII digits then ':'
            j = i + 1
            while j < n and is_ascii_digit(line[j]):
                j += 1
            if j > i + 1 and j < n and line[j] == ":":
                raise ParseError("I058_MIXED_SURFACE_VERSION",
                                 f"Structural ※ slot-ref in 0.1 document at line {ln_no}",
                                 ln_no, i + 1)
        i += 1
