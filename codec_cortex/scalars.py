#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scalar value model and lexer for CORTEX 0.1.
Sections 1-2 of the independent reviewer's implementation.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, List, Tuple


# ---------------------------------------------------------------------------
# 0. Utilities
# ---------------------------------------------------------------------------

def to_nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def utf8_bytes(s: str) -> bytes:
    return s.encode("utf-8")


# ---------------------------------------------------------------------------
# 1. Scalar value model
# ---------------------------------------------------------------------------

@dataclass
class Scalar:
    """A CORTEX scalar value with its lexeme (canonical or source)."""
    kind: str            # "string" | "atom" | "integer" | "decimal" | "boolean" | "null" | "list"
    value: Any           # str for atom/string/integer/decimal; bool; None; list[Scalar] for list
    lexeme: str          # canonical lexeme to emit

    def clone(self) -> "Scalar":
        if self.kind == "list":
            return Scalar("list", [x.clone() for x in self.value], self.lexeme)
        return Scalar(self.kind, self.value, self.lexeme)


# ---------------------------------------------------------------------------
# 2. Lexer / scalar parser
# ---------------------------------------------------------------------------

class ParseError(Exception):
    def __init__(self, code: str, message: str, line: int = 0, col: int = 0):
        self.code = code
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"{code} @ {line}:{col} — {message}")


# Atom grammar per spec §17.2 and ABNF:
#   atom = ["$" positive-integer ":"] (ALPHA / "_") *(ALPHA / DIGIT / "_" / "." / "/" / ":" / "@" / "+" / "%" / "$" / "-")
ATOM_BODY = r"[_A-Za-z][_A-Za-z0-9./:@+%$-]*"
ATOM_RE = re.compile(r"^(?:\$[0-9]+:)?" + ATOM_BODY + r"$")


_INT_RE = re.compile(r"^-?(0|[1-9][0-9]*)$")
_DEC_RE = re.compile(r"^-?(0|[1-9][0-9]*)\.[0-9]+$")


def is_atom_lexeme(s: str) -> bool:
    """Check if a string could be a valid bare atom lexeme (no quotes)."""
    if not s:
        return False
    # No whitespace, no structural delimiters
    if re.search(r"[\s\[\]{}\s,\"|]", s):
        return False
    # Length check (max 32 chars per spec)
    if len(s) > 32:
        return False
    # Must start with letter or _ (after optional $N: prefix)
    return bool(ATOM_RE.match(s))


# String escape / unescape
ESCAPE_MAP = {
    '"': '"',
    "\\": "\\",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "b": "\b",
    "f": "\f",
}
REV_ESCAPE = {
    '"': '\\"',
    "\\": "\\\\",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
    "\b": "\\b",
    "\f": "\\f",
}


def parse_string_literal(s: str) -> str:
    """Parse a quoted string literal body (without surrounding quotes)."""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\":
            if i + 1 >= len(s):
                raise ParseError("L005_INVALID_STRING", "Trailing backslash in string")
            nxt = s[i + 1]
            if nxt in ESCAPE_MAP:
                out.append(ESCAPE_MAP[nxt])
                i += 2
            elif nxt == "u":
                hexs = s[i + 2:i + 6]
                if len(hexs) != 4 or not all(ch in "0123456789abcdefABCDEF" for ch in hexs):
                    raise ParseError("L005_INVALID_STRING", "Bad \\u escape")
                out.append(chr(int(hexs, 16)))
                i += 6
            elif nxt == "/":
                # allow \/ as /
                out.append("/")
                i += 2
            else:
                raise ParseError("L005_INVALID_STRING", f"Unknown escape \\{nxt}")
        elif c == '"':
            raise ParseError("L005_INVALID_STRING", "Unescaped quote in string body")
        else:
            out.append(c)
            i += 1
    return "".join(out)


def emit_string_literal(value: str) -> str:
    """Emit a quoted string literal body using canonical escapes."""
    out = []
    for ch in value:
        if ch in REV_ESCAPE:
            out.append(REV_ESCAPE[ch])
        elif ord(ch) < 0x20:
            out.append("\\u%04X" % ord(ch))
        elif ord(ch) == 0x7F:
            out.append("\\u007F")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


# ---------------------------------------------------------------------------
# 3. Attrs payload parser
# ---------------------------------------------------------------------------

class StringCursor:
    """Simple cursor over a string with position tracking."""
    def __init__(self, s: str, line: int = 1, col: int = 1):
        self.s = s
        self.i = 0
        self.line = line
        self.col = col

    def eof(self) -> bool:
        return self.i >= len(self.s)

    def peek(self, off: int = 0) -> str:
        j = self.i + off
        return self.s[j] if 0 <= j < len(self.s) else ""

    def next(self) -> str:
        c = self.s[self.i]
        self.i += 1
        if c == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return c


def parse_scalar(cur: StringCursor, in_list: bool = False) -> Scalar:
    """Parse a single scalar from cursor. Stops at , } ] | or EOF."""
    skip_inline_ws(cur)
    c = cur.peek()
    if c == '"':
        return parse_string_scalar(cur)
    elif c == "[":
        return parse_list_scalar(cur)
    else:
        return parse_atom_or_number(cur)


def skip_inline_ws(cur: StringCursor):
    while cur.peek() in " \t":
        cur.next()


def parse_string_scalar(cur: StringCursor) -> Scalar:
    assert cur.peek() == '"'
    cur.next()  # consume opening "
    body = []
    while True:
        c = cur.peek()
        if c == "":
            raise ParseError("L005_INVALID_STRING", "Unterminated string", cur.line, cur.col)
        if c == '"':
            cur.next()
            break
        if c == "\\":
            body.append(c)
            cur.next()
            nxt = cur.peek()
            if nxt == "":
                raise ParseError("L005_INVALID_STRING", "Trailing backslash", cur.line, cur.col)
            body.append(nxt)
            cur.next()
            if nxt == "u":
                for _ in range(4):
                    h = cur.peek()
                    if h == "":
                        raise ParseError("L005_INVALID_STRING", "Bad \\u escape", cur.line, cur.col)
                    body.append(h)
                    cur.next()
        else:
            body.append(c)
            cur.next()
    raw = "".join(body)
    value = parse_string_literal(raw)
    lex = emit_string_literal(value)
    return Scalar("string", value, lex)


def parse_list_scalar(cur: StringCursor) -> Scalar:
    assert cur.peek() == "["
    cur.next()  # consume [
    items = []
    skip_inline_ws(cur)
    if cur.peek() == "]":
        cur.next()
        return Scalar("list", items, "[]")
    while True:
        v = parse_scalar(cur, in_list=True)
        items.append(v)
        skip_inline_ws(cur)
        c = cur.peek()
        if c == ",":
            cur.next()
            skip_inline_ws(cur)
            continue
        elif c == "]":
            cur.next()
            break
        else:
            raise ParseError("L007_INVALID_LIST", f"Expected , or ] got {c!r}", cur.line, cur.col)
    lex = "[" + ",".join(it.lexeme for it in items) + "]"
    return Scalar("list", items, lex)


def parse_atom_or_number(cur: StringCursor) -> Scalar:
    """Parse a bare atom/integer/decimal/boolean/null token."""
    start = cur.i
    while True:
        c = cur.peek()
        if c == "" or c in " \t\r\n,}]|":
            break
        cur.next()
    raw = cur.s[start:cur.i]
    if raw == "true":
        return Scalar("boolean", True, "true")
    if raw == "false":
        return Scalar("boolean", False, "false")
    if raw == "null":
        return Scalar("null", None, "null")
    if _INT_RE.match(raw):
        # Normalize: -0 -> 0, no leading zeros (already enforced by regex)
        v = raw
        if v == "-0":
            v = "0"
        return Scalar("integer", v, v)
    if _DEC_RE.match(raw):
        # Preserve exactly
        return Scalar("decimal", raw, raw)
    # Otherwise treat as atom
    if not ATOM_RE.match(raw):
        raise ParseError("L010_INVALID_ATOM", f"Invalid atom: {raw!r}", cur.line, cur.col)
    return Scalar("atom", raw, raw)


def parse_attrs_payload(s: str, start_line: int = 1) -> List[Tuple[str, Scalar]]:
    """Parse {key:value,key:value} payload. Input s includes surrounding braces."""
    cur = StringCursor(s, line=start_line)
    skip_inline_ws(cur)
    if cur.peek() != "{":
        raise ParseError("S006_INVALID_ATTRS", "Expected {", cur.line, cur.col)
    cur.next()
    pairs: List[Tuple[str, Scalar]] = []
    skip_inline_ws(cur)
    if cur.peek() == "}":
        cur.next()
        return pairs
    while True:
        skip_inline_ws(cur)
        # Read key
        kstart = cur.i
        while cur.peek() and cur.peek() not in " \t:,":
            if cur.peek() == "}":
                break
            cur.next()
        key = cur.s[kstart:cur.i]
        if not key:
            raise ParseError("L003_INVALID_KEY", "Empty key", cur.line, cur.col)
        skip_inline_ws(cur)
        if cur.peek() != ":":
            raise ParseError("S006_INVALID_ATTRS", "Expected : after key", cur.line, cur.col)
        cur.next()
        v = parse_scalar(cur)
        pairs.append((key, v))
        skip_inline_ws(cur)
        c = cur.peek()
        if c == ",":
            cur.next()
            skip_inline_ws(cur)
            if cur.peek() == "}":
                cur.next()
                break
            continue
        elif c == "}":
            cur.next()
            break
        else:
            raise ParseError("S006_INVALID_ATTRS", f"Expected , or }} got {c!r}", cur.line, cur.col)
    return pairs
