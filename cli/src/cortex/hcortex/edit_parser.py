"""HCORTEX-EDIT parser — turns reversible Markdown back into a :class:`CortexDocument`.

The parser scans for:
  1. The first-line ``cortex-render: hcortex-edit`` header
  2. ``<!-- cortex-section -->`` markers
  3. ``<!-- cortex-entry -->`` markers (with section, sigil, name, type, hash)
  4. The ```` ```cortex-glossary ```` fenced block (rebuilds $0)
  5. Markdown tables (key|value) → attrs
  6. Fenced code blocks → cuerpo or bloque (depending on declared type)

The parser refuses HCORTEX-READ input (raises
:class:`HCortexReadNotCompilableError`).
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from ..core.ast import (
    AttrsPosContract,
    CortexDocument,
    Entry,
    Glossary,
    MicroDef,
    Section,
    SigilDef,
    TypeDef,
    compute_document_hash,
    compute_entry_hash,
)
from ..core.errors import (
    AttrsPosContractMissingError,
    BraceError,
    CortexError,
    HCortexEditMetadataMissingError,
    HCortexReadNotCompilableError,
    InvalidAttrsError,
)
from ..core.parser import parse_attrs_body
from .markdown_model import (
    EditHeader,
    ENTRY_MARKER_RE,
    GLOSARY_FENCE_RE,
    SECTION_MARKER_RE,
    VERBATIM_FENCE_RE,
    is_hcortex_edit,
    is_hcortex_read,
    is_hcortex_read_in_text,
    is_hcortex_edit_in_text,
)


# ---------------------------------------------------------------------------
# Glossary block parser
# ---------------------------------------------------------------------------

_GLOSSARY_DECL_RE = re.compile(
    r"^\s*(?:\#\s*)?"
    r"(?P<sigil>[A-Z][A-Z0-9_]*|!)"
    r"\s*\|\s*"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*\|\s*"
    r"(?P<type>[A-Za-z\-]+)"
    r"\s*\|\s*"
    r"(?P<risk>[A-Z])"
    r"\s*\|\s*"
    r"(?P<layer>[A-Za-z/]+)"
    r"\s*\|\s*"
    r"(?P<desc>.+?)\s*$"
)

_TYPE_DECL_RE = re.compile(r"^\s*\#\s*(?P<name>[\w\-]+)\s*=\s*(?P<desc>.+?)\s*$")
_MICRO_PAIR_RE = re.compile(r"(?P<tok>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?P<val>[^\s,]+)")
_CONTRACT_RE = re.compile(
    r"^\s*\#\s*contract\s*:\s*"
    r"(?P<sigil>[A-Z][A-Z0-9_]*|!)\s*\|\s*(?P<fields>.+?)\s*$"
)


def parse_glossary_block(text: str) -> Glossary:
    """Parse a ```` ```cortex-glossary ```` block into a :class:`Glossary`."""

    g = Glossary()
    # Seed canonical types + micro so the file is operable even if $0 omits them
    from ..core.errors import CANONICAL_MICRO, CANONICAL_TYPES
    for t in CANONICAL_TYPES:
        g.add_type(TypeDef(name=t, description="canonical type"))
    for tok, val in CANONICAL_MICRO.items():
        g.add_micro(MicroDef(token=tok, value=val))

    for line in text.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m = _GLOSSARY_DECL_RE.match(line)
        if m:
            g.add_sigil(SigilDef(
                sigil=m.group("sigil"),
                name=m.group("name"),
                type=m.group("type"),
                risk=m.group("risk"),
                layer=m.group("layer"),
                description=m.group("desc").strip(),
            ))
            continue
        m = _CONTRACT_RE.match(line)
        if m:
            fields = [f.strip() for f in m.group("fields").split("|")]
            g.add_contract(AttrsPosContract(sigil=m.group("sigil"), fields=fields))
            continue
        # Type declaration: ONLY if line has exactly one '='
        eq_count = line.count("=")
        if eq_count == 1:
            m = _TYPE_DECL_RE.match(line)
            if m:
                name = m.group("name")
                canonical_type_names = {"attrs", "cuerpo", "bloque", "attrs-pos", "relación"}
                if name in canonical_type_names or len(name) > 4:
                    g.add_type(TypeDef(name=name, description=m.group("desc")))
                    continue
        # Micro-token pairs
        for tok, val in _MICRO_PAIR_RE.findall(line):
            if tok in {"attrs", "cuerpo", "bloque", "attrs-pos", "relación"}:
                continue
            g.add_micro(MicroDef(token=tok, value=val))
    return g


# ---------------------------------------------------------------------------
# Markdown table parser
# ---------------------------------------------------------------------------

def _split_markdown_row(line: str) -> List[str]:
    """Split a Markdown table row on ``|`` respecting ``\\|`` escapes.

    Per CommonMark, a literal ``|`` inside a table cell MUST be escaped
    as ``\\|``.  This function honours that convention so values
    containing pipes roundtrip correctly (audit gap H-04 / B-007).
    """

    s = line.strip()
    # Strip leading/trailing pipe (CommonMark tables)
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells: List[str] = []
    buf: List[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n and s[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _parse_markdown_table(lines: List[str], start: int) -> Tuple[dict, int]:
    """Parse a Markdown table starting at ``lines[start]``.

    Returns ``(attrs_dict, end_index)``.
    """

    if start >= len(lines):
        return {}, start
    # Skip leading blank lines
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return {}, i
    # Header row
    if "|" not in lines[i]:
        return {}, i
    header = _split_markdown_row(lines[i])
    i += 1
    # Separator row (---|---|...)
    if i < len(lines) and re.match(r"^\s*\|?\s*[-:]+", lines[i]):
        i += 1
    # Data rows
    out: dict = {}
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            break
        if "|" not in line:
            break
        cells = _split_markdown_row(line)
        key = None
        value = None
        for idx, cell in enumerate(cells):
            if idx < len(header) and header[idx].lower() == "key":
                key = cell
            elif idx < len(header) and header[idx].lower() == "value":
                value = cell
        if key is not None and value is not None:
            out[key] = value
        i += 1
    return out, i


def _parse_attrs_table(lines: List[str], start: int) -> Tuple[dict, int]:
    """Parse a 2-column key|value Markdown table into a dict.

    Uses :func:`_split_markdown_row` so escaped pipes ``\\|`` in values
    are correctly preserved (audit gap H-04).
    """

    i = start
    # Skip blanks
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or "|" not in lines[i]:
        return {}, i
    # header
    header_cells = _split_markdown_row(lines[i])
    i += 1
    # separator
    if i < len(lines) and re.match(r"^\s*\|?\s*[-:]+", lines[i]):
        i += 1
    out: dict = {}
    while i < len(lines):
        line = lines[i]
        if not line.strip() or "|" not in line:
            break
        cells = _split_markdown_row(line)
        if len(cells) >= 2:
            key = cells[0]
            value = cells[1]
            # Try to interpret booleans / numbers
            if value == "true":
                value = True
            elif value == "false":
                value = False
            elif re.fullmatch(r"-?\d+", value):
                value = int(value)
            elif re.fullmatch(r"-?\d+\.\d+", value):
                value = float(value)
            out[key] = value
        i += 1
    return out, i


# ---------------------------------------------------------------------------
# Fenced block parser
# ---------------------------------------------------------------------------

def _parse_fenced_block(lines: List[str], start: int) -> Tuple[str, str, int]:
    """Parse a ```lang ... ``` block starting at ``lines[start]``.

    Returns ``(language, body, end_index)`` where ``end_index`` is the
    index *after* the closing fence.
    """

    line = lines[start].strip()
    # Match opening fence: ```lang or ``` or ~~~~lang
    m = re.match(r"^(?P<fence>```+|~~~~+)(?P<lang>\S*)$", line)
    if not m:
        return "", "", start
    fence = m.group("fence")
    lang = m.group("lang") or ""
    i = start + 1
    body_parts: List[str] = []
    while i < len(lines):
        if lines[i].strip().startswith(fence[0] * len(fence)):
            # closing fence
            return lang, "\n".join(body_parts), i + 1
        body_parts.append(lines[i])
        i += 1
    # unterminated fence — return what we have
    return lang, "\n".join(body_parts), i


# ---------------------------------------------------------------------------
# Top-level HCORTEX-EDIT parser
# ---------------------------------------------------------------------------

def parse_hcortex_edit(text: str, source: str = "<hcortex-edit>") -> CortexDocument:
    """Parse HCORTEX-EDIT Markdown back into a :class:`CortexDocument`.

    Raises :class:`HCortexReadNotCompilableError` if the input is an
    HCORTEX-READ file, and :class:`HCortexEditMetadataMissingError` if
    required markers are absent.
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    if not lines:
        raise HCortexEditMetadataMissingError("empty input")

    # v1.1.3 P1-5: HCORTEX-READ now starts with "Perfil: CORTEX-<LEVEL>"
    # as the first real line, with the cortex-render marker on line 2.
    # We scan the first few lines to detect the format robustly.
    first_few = "\n".join(lines[:5])

    # Reject HCORTEX-READ (not compilable)
    if is_hcortex_read_in_text(first_few):
        raise HCortexReadNotCompilableError()

    # Find the cortex-edit header line
    edit_header_line = None
    edit_header_idx = -1
    for idx, line in enumerate(lines[:5]):
        if is_hcortex_edit(line):
            edit_header_line = line
            edit_header_idx = idx
            break
    if edit_header_line is None:
        raise HCortexEditMetadataMissingError(
            "first lines must declare cortex-render: hcortex-edit; "
            f"got first 3 lines: {lines[:3]!r}"
        )

    header = EditHeader.parse(edit_header_line)
    if header is None:
        raise HCortexEditMetadataMissingError("malformed hcortex-edit header")

    doc = CortexDocument()
    doc.meta = {
        "path": source,
        "format": ".hcortex.edit.md",
        "version": None,
        "hash": header.hash,
        "source": header.source,
    }

    # 1. Find the glossary block (```cortex-glossary ... ```)
    glossary_text = None
    for i, line in enumerate(lines):
        if line.strip().startswith("```cortex-glossary"):
            # find the closing fence
            j = i + 1
            buf: List[str] = []
            while j < len(lines):
                if lines[j].strip().startswith("```"):
                    break
                buf.append(lines[j])
                j += 1
            glossary_text = "\n".join(buf)
            break
    if glossary_text is None:
        raise HCortexEditMetadataMissingError("no ```cortex-glossary block found")
    doc.glossary = parse_glossary_block(glossary_text)

    # Create the $0 section (glossary carrier)
    sec0 = Section(id="$0", title="GLOSSARY")
    doc.sections.append(sec0)

    # 2. Walk the lines, collecting section markers and entry markers
    current_section: Optional[Section] = None
    i = 0
    while i < len(lines):
        line = lines[i]
        # Section marker
        m = SECTION_MARKER_RE.search(line)
        if m:
            sec_id = m.group("id")
            sec_title = m.group("title") or ""
            if sec_id == "$0":
                current_section = sec0
                current_section.title = sec_title or "GLOSSARY"
            else:
                # Don't create duplicate sections
                existing = doc.get_section(sec_id)
                if existing is None:
                    current_section = Section(id=sec_id, title=sec_title)
                    doc.sections.append(current_section)
                else:
                    current_section = existing
                    if sec_title:
                        current_section.title = sec_title
            i += 1
            continue
        # Entry marker
        m = ENTRY_MARKER_RE.search(line)
        if m and current_section is not None:
            entry = _parse_entry_block(lines, i, m, current_section.id, doc.glossary)
            current_section.entries.append(entry)
            # Skip past the entry body (we already consumed it)
            # Find the next entry marker or section marker
            j = i + 1
            while j < len(lines):
                if SECTION_MARKER_RE.search(lines[j]):
                    break
                if ENTRY_MARKER_RE.search(lines[j]):
                    break
                j += 1
            i = j
            continue
        i += 1

    # Recompute entry hashes based on parsed values
    for sec, entry in doc.iter_entries():
        entry.hash = compute_entry_hash(entry)
        entry.entry_id = entry.hash

    # Recompute document hash
    doc.meta["hash"] = compute_document_hash(text)
    return doc


def _parse_entry_block(
    lines: List[str],
    marker_idx: int,
    marker_match: re.Match,
    section_id: str,
    glossary: Glossary,
) -> Entry:
    """Parse a single entry starting at ``marker_idx``.

    ``marker_match`` is the regex match for the ``<!-- cortex-entry -->``
    line.  The body follows the marker.
    """

    sigil = marker_match.group("sigil")
    name = marker_match.group("name")
    type_ = marker_match.group("type")
    old_hash = marker_match.group("hash") or ""

    # Body starts on the line after the marker
    i = marker_idx + 1
    # Skip blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1

    value: object = None
    raw_body = ""

    if type_ in ("attrs", "attrs-pos"):
        attrs, i = _parse_attrs_table(lines, i)
        value = attrs
        raw_body = ", ".join(f"{k}:{v!r}" for k, v in attrs.items())
    elif type_ == "cuerpo":
        # expect a fenced block ```text ... ```
        if i < len(lines) and lines[i].strip().startswith("```"):
            lang, body, i = _parse_fenced_block(lines, i)
            value = body
            raw_body = body
        else:
            # fallback: take text until blank line
            buf = []
            while i < len(lines) and lines[i].strip():
                buf.append(lines[i])
                i += 1
            value = "\n".join(buf)
            raw_body = value
    elif type_ == "bloque":
        # expect a fenced block
        if i < len(lines) and (lines[i].strip().startswith("```") or lines[i].strip().startswith("~~~~")):
            lang, body, i = _parse_fenced_block(lines, i)
            value = body
            raw_body = body
        else:
            buf = []
            while i < len(lines) and lines[i].strip():
                buf.append(lines[i])
                i += 1
            value = "\n".join(buf)
            raw_body = value
    elif type_ == "relación":
        if i < len(lines) and lines[i].strip().startswith("```"):
            lang, body, i = _parse_fenced_block(lines, i)
            value = body
            raw_body = body
        else:
            buf = []
            while i < len(lines) and lines[i].strip():
                buf.append(lines[i])
                i += 1
            value = "\n".join(buf)
            raw_body = value
    else:
        # Unknown type — fallback to attrs
        attrs, i = _parse_attrs_table(lines, i)
        value = attrs
        raw_body = ", ".join(f"{k}:{v!r}" for k, v in attrs.items())

    # Build canonical raw text (for AST compatibility)
    from ..core.writer import serialize_entry_value
    raw = f"{sigil}:{name}{{{serialize_entry_value(value, type_)}}}"

    entry = Entry(
        section=section_id,
        sigil=sigil,
        name=name,
        type=type_,
        value=value,
        raw=raw,
        line_start=marker_idx + 1,
        line_end=i,
        hash="",  # filled below
    )
    entry.hash = compute_entry_hash(entry)
    entry.entry_id = entry.hash
    return entry
