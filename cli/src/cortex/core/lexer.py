# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Character-stream lexer for ``.cortex``.

The lexer is a small deterministic automaton (Section 6.2 of the spec)
that emits low-level tokens consumed by :mod:`cortex.core.parser`.

States:
  - TEXT
  - SECTION_HEADER
  - SIGIL
  - ENTRY_NAME
  - ENTRY_BODY
  - ESCAPE
  - COMMENT

The lexer is intentionally minimal: it identifies *boundaries* (section
headers, entry starts, brace blocks, comments) but does **not** interpret
values — that is the parser's job.  The lexer preserves raw text so the
parser can extract verbatim ``bloque`` content.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from .errors import BraceError


class TokenKind(str, Enum):
    SECTION_HEADER = "section_header"
    COMMENT = "comment"
    BLANK = "blank"
    ENTRY_START = "entry_start"     # SIGIL:name{ ...
    ENTRY_CONTINUATION = "entry_continuation"
    TEXT = "text"                    # unparsed line (recorded as diagnostic)


@dataclass
class Token:
    kind: TokenKind
    text: str
    line: int
    # for ENTRY_START only:
    sigil: Optional[str] = None
    name: Optional[str] = None
    # for SECTION_HEADER:
    section_id: Optional[str] = None
    section_title: Optional[str] = None


# Characters that introduce a comment line
_COMMENT_PREFIXES = ("#", "//")


def looks_like_comment(line: str) -> bool:
    stripped = line.lstrip()
    return any(stripped.startswith(p) for p in _COMMENT_PREFIXES)


def looks_like_section_header(line: str) -> bool:
    """Return True if ``line`` declares a numbered section.

    Recognised forms (per Section 5.2 of the spec):
      - ``$2``
      - ``$2: TITLE``
      - ``$2 · TITLE``
      - ``# -- $2: TITLE --``
      - ``## $2 · TITLE``   (Markdown-friendly)
      - ``2``                (bare number, less common)
    """

    s = line.strip()
    if not s:
        return False
    def is_section_number(value: str) -> bool:
        parts = value.split(".")
        return bool(parts) and all(part.isdigit() for part in parts)

    # Markdown-style: ## $2 · TITLE
    if s.startswith("##"):
        rest = s.lstrip("#").strip()
        if rest.startswith("$"):
            head = rest[1:].split(":", 1)[0].split("·", 1)[0].strip()
            return is_section_number(head)
        return False
    # Comment-style: # -- $2: TITLE --
    if s.startswith("#"):
        inner = s.lstrip("#").strip()
        # remove leading dashes
        inner = inner.lstrip("-").strip()
        if inner.startswith("$"):
            head = inner[1:].split(":", 1)[0].split("·", 1)[0].strip()
            return is_section_number(head)
        return False
    # Plain: $2 or $2: TITLE
    if s.startswith("$"):
        head = s[1:].split(":", 1)[0].split("·", 1)[0].strip()
        return is_section_number(head)
    # Bare number "2" — accept only if the entire token is a digit
    head = s.split(":", 1)[0].split("·", 1)[0].strip()
    return is_section_number(head)


def parse_section_header(line: str) -> Tuple[str, str]:
    """Extract ``(section_id, title)`` from a section header line."""

    s = line.strip()
    # Strip markdown hashes
    if s.startswith("##"):
        s = s.lstrip("#").strip()
    # Strip comment marker (for ``# -- $2: TITLE --``)
    if s.startswith("#"):
        s = s.lstrip("#").strip().lstrip("-").strip()
    # Now s should start with $ or be a bare number
    if s.startswith("$"):
        s = s[1:]
    # Split on first ':' or '·'
    if ":" in s:
        num, title = s.split(":", 1)
    elif "·" in s:
        num, title = s.split("·", 1)
    else:
        num, title = s, ""
    num = num.strip()
    title = title.strip().rstrip("-").strip()
    parts = num.split(".")
    if not parts or not all(part.isdigit() for part in parts):
        # Not a real section header; return as-is and let caller decide.
        return ("$" + num if num else "$0", title)
    return ("$" + num, title)


# Pattern for entry starts: SIGIL:name{
# Sigils are uppercase letters/digits/!; names are snake_case.
import re as _re

_ENTRY_START_RE = _re.compile(
    r"""^
    (?P<sigil>[A-Z][A-Z0-9_]*|!)    # sigil (uppercase, or single '!')
    :
    (?P<name>[A-Za-z_][A-Za-z0-9_.]*) # entry name
    \s*
    \{                              # opening brace (rest of line = body start)
    (?P<rest>.*)
    $""",
    _re.VERBOSE,
)


def looks_like_entry_start(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # Reject comment lines
    if looks_like_comment(line):
        return False
    return _ENTRY_START_RE.match(s) is not None


def parse_entry_start(line: str) -> Tuple[str, str, str]:
    """Return ``(sigil, name, rest_after_open_brace)``."""

    s = line.strip()
    m = _ENTRY_START_RE.match(s)
    if not m:
        raise ValueError(f"not an entry start: {line!r}")
    return m.group("sigil"), m.group("name"), m.group("rest")


def collect_balanced_entry(lines: List[str], start: int) -> Tuple[str, int, int]:
    """Collect a multi-line entry starting at ``lines[start]``.

    Returns ``(raw_text, start_line, end_line)`` where ``end_line`` is the
    index (inclusive) of the line that closed the entry.

    Raises :class:`BraceError` if braces are unbalanced.
    """

    depth = 0
    in_escape = False
    in_string = False
    buffer_parts: List[str] = []
    end = start
    opened = False
    for i in range(start, len(lines)):
        line = lines[i]
        for ch in line:
            if in_escape:
                in_escape = False
                continue
            if ch == "\\":
                in_escape = True
                continue
            if in_string:
                if ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
                continue
            if ch == "{":
                depth += 1
                opened = True
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    raise BraceError(
                        f"unbalanced '}}' on line {i + 1}",
                        line=i + 1,
                    )
        buffer_parts.append(line)
        end = i
        if opened and depth == 0:
            return "\n".join(buffer_parts), start, end
    raise BraceError(f"unclosed entry starting on line {start + 1}", line=start + 1)


# ---------------------------------------------------------------------------
# Top-level lexer
# ---------------------------------------------------------------------------

def lex(text: str) -> List[Token]:
    """Split ``text`` into a flat list of :class:`Token` records.

    The lexer normalises newlines and emits one token per logical line
    (or one token per multi-line entry, when braces span several lines).
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    tokens: List[Token] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_no = i + 1
        stripped = line.strip()
        if not stripped:
            tokens.append(Token(TokenKind.BLANK, line, line_no))
            i += 1
            continue
        if looks_like_comment(line):
            tokens.append(Token(TokenKind.COMMENT, line, line_no))
            i += 1
            continue
        if looks_like_section_header(line):
            sec_id, title = parse_section_header(line)
            tokens.append(Token(
                TokenKind.SECTION_HEADER, line, line_no,
                section_id=sec_id, section_title=title,
            ))
            i += 1
            continue
        if looks_like_entry_start(line):
            try:
                raw, _, end = collect_balanced_entry(lines, i)
            except BraceError:
                # emit a TEXT token and a diagnostic upstream
                tokens.append(Token(TokenKind.TEXT, line, line_no))
                i += 1
                continue
            sigil, name, _ = parse_entry_start(line)
            tokens.append(Token(
                TokenKind.ENTRY_START, raw, line_no,
                sigil=sigil, name=name,
            ))
            i = end + 1
            continue
        # Unparsed line — record so the parser can emit a diagnostic
        tokens.append(Token(TokenKind.TEXT, line, line_no))
        i += 1
    return tokens
