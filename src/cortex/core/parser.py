# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``.cortex`` parser — turns raw text into a :class:`CortexDocument` AST.

The parser follows the algorithm in Section 6 of the spec:

1. Lex the text into tokens.
2. Walk tokens, building sections and entries.
3. Validate that ``$0`` is the first section.
4. Resolve every entry's expansion type from ``$0``.
5. Parse each entry's body according to its type.
6. Return a fully populated :class:`CortexDocument`.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from . import errors
from .ast import (
    AttrsPosContract,
    CortexDocument,
    Entry,
    Glossary,
    MicroDef,
    Section,
    SigilDef,
    TypeDef,
    compute_entry_hash,
    compute_document_hash,
)
from .errors import (
    E017_UNPARSED_LINE,
    E006_INVALID_ATTRS,
    CANONICAL_TYPES,
    CANONICAL_MICRO,
    GLOSSARY_RESERVED_SIGILS,
    ALLOWED_STATUS,
)
from .lexer import lex


# ---------------------------------------------------------------------------
# $0 glossary parser
# ---------------------------------------------------------------------------

# Pipe-separated declaration in a comment line:
#   IDN | identity | attrs | B | Semantic | Identity descriptor
_GLOSSARY_DECL_RE = re.compile(
    r"""^\s*\#?\s*
    (?P<sigil>[A-Z][A-Z0-9_]*|!)
    \s*\|\s*
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    \s*\|\s*
    (?P<type>[A-Za-z\-]+)
    \s*\|\s*
    (?P<risk>[A-Z])              # single uppercase letter (B/H/M canonical, others allowed)
    \s*\|\s*
    (?P<layer>[A-Za-z/]+)
    \s*\|\s*
    (?P<desc>.+?)
    \s*$
    """,
    re.VERBOSE,
)

# Type declaration: "# attrs = key:value pairs"
# Uses \w (Unicode-aware in Python 3) to accept type names like "relación"
_TYPE_DECL_RE = re.compile(
    r"""^\s*\#\s*
    (?P<name>[\w\-]+)
    \s*=\s*
    (?P<desc>.+?)
    \s*$
    """,
    re.VERBOSE,
)

# Micro-token declaration: "# cur=current pln=planned ..."
_MICRO_PAIR_RE = re.compile(r"\b(?P<tok>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?P<val>[^\s,]+)")

# attrs-pos contract declaration inside $0:
#   # contract: HDL | operation | status | requires
_CONTRACT_RE = re.compile(
    r"""^\s*\#\s*contract\s*:\s*
    (?P<sigil>[A-Z][A-Z0-9_]*|!)
    \s*\|\s*
    (?P<fields>.+?)
    \s*$
    """,
    re.VERBOSE,
)

# Status declaration inside $0:
#   # status: active, completed, archived
_STATUS_DECL_RE = re.compile(
    r"""^\s*\#\s*status\s*:\s*
    \[?(?P<statuses>[^\]]+?)\]?
    \s*$
    """,
    re.VERBOSE,
)

# Entry-form declarations inside $0 (alternative explicit form):
#   GSIG:IDN{name:"identity", type:"attrs", ...}
# These are emitted by the writer and re-parsed transparently.
_GSIG_RE = re.compile(r"^GSIG:(?P<sigil>[A-Z][A-Z0-9_]*|!)\s*\{(?P<body>.*)\}\s*$")
_GTYP_RE = re.compile(r"^GTYP:(?P<name>[a-zA-Z\-]+)\s*\{(?P<body>.*)\}\s*$")
_GMIC_RE = re.compile(r"^GMIC:(?P<token>[a-zA-Z_][a-zA-Z0-9_]*)\s*\{(?P<body>.*)\}\s*$")
_GCON_RE = re.compile(r"^GCON:(?P<sigil>[A-Z][A-Z0-9_]*|!)\s*\{(?P<body>.*)\}\s*$")


def parse_attrs_body(body: str) -> Dict[str, Any]:
    """Parse an ``attrs`` body like ``key:"value", key2:42`` into a dict.

    Values may be:
      - double-quoted strings (escapes preserved)
      - bare numbers (int/float)
      - booleans (true/false)
      - bare words (treated as strings)
      - nested ``{...}`` maps, parsed recursively

    Raises :class:`InvalidAttrsError` on malformed input.
    """

    def parse_bare(raw: str) -> Any:
        if raw in ("true", "false"):
            return raw == "true"
        if raw.lower() in ("null", "none", "nil", "undefined"):
            return None
        if re.fullmatch(r"-?\d+", raw):
            return int(raw)
        if re.fullmatch(r"-?\d+\.\d+", raw):
            return float(raw)
        return raw

    out: Dict[str, Any] = {}
    s = body.strip()
    if not s:
        return out
    i = 0
    n = len(s)
    while i < n:
        while i < n and (s[i].isspace() or s[i] == ","):
            i += 1
        if i >= n:
            break
        m = re.match(r"([A-Za-z0-9_][A-Za-z0-9_]*)", s[i:])
        if not m:
            raise errors.InvalidAttrsError(f"expected key at position {i}: {s[i:i+20]!r}")
        key = m.group(1)
        i += len(key)
        while i < n and s[i].isspace():
            i += 1
        if i >= n or s[i] != ":":
            raise errors.InvalidAttrsError(f"expected ':' after key {key!r}")
        i += 1
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            raise errors.InvalidAttrsError(f"missing value for key {key!r}")
        if s[i] == '"':
            j = i + 1
            buf: List[str] = []
            escape = False
            while j < n:
                ch = s[j]
                if escape:
                    if ch == "n":
                        buf.append("\n")
                    elif ch == "t":
                        buf.append("\t")
                    elif ch == "r":
                        buf.append("\r")
                    else:
                        buf.append(ch)
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    break
                else:
                    buf.append(ch)
                j += 1
            if j >= n:
                raise errors.InvalidAttrsError(f"unterminated string for key {key!r}")
            value: Any = "".join(buf)
            i = j + 1
        elif s[i] == "{":
            depth = 0
            j = i
            in_string = False
            escape = False
            while j < n:
                ch = s[j]
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif in_string:
                    if ch == '"':
                        in_string = False
                elif ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j >= n or depth != 0:
                raise errors.InvalidAttrsError(f"unterminated map for key {key!r}")
            value = parse_attrs_body(s[i + 1:j])
            i = j + 1
        else:
            j = i
            in_string = False
            escape = False
            depth = 0
            while j < n:
                ch = s[j]
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif in_string:
                    if ch == '"':
                        in_string = False
                elif ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    if depth == 0:
                        break
                    depth -= 1
                elif ch == "," and depth == 0:
                    break
                j += 1
            raw = s[i:j].strip()
            value = parse_bare(raw)
            i = j
        out[key] = value
    return out


def parse_attrs_pos_body(body: str, contract: AttrsPosContract) -> Dict[str, Any]:
    """Parse an ``attrs-pos`` body using the sigil's positional contract.

    The body is a ``|``-separated list of values.  The number of values
    must match the contract length (trailing missing fields are filled
    with ``None``).

    Re-audit H-RA-05: ``|`` is the delimiter and CANNOT appear inside
    values, even between quotes.  This is the canonical contract per
    SKILL.md §4.3 (``attrs-pos`` = "máxima compresión, solo cuando el
    contrato es estable").  If a value needs ``|``, use ``attrs`` instead.
    Quote-aware splitting is intentionally NOT implemented to keep the
    contract deterministic.
    """

    parts = [p.strip() for p in body.split("|")]
    # strip surrounding quotes from each part
    cleaned: List[str] = []
    for p in parts:
        if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
            cleaned.append(p[1:-1])
        else:
            cleaned.append(p)
    out: Dict[str, Any] = {}
    for idx, field_name in enumerate(contract.fields):
        if idx < len(cleaned):
            out[field_name] = cleaned[idx]
        else:
            out[field_name] = None
    return out


# ---------------------------------------------------------------------------
# Entry body extraction
# ---------------------------------------------------------------------------

def _extract_body(raw: str) -> str:
    """Return the text between the outer ``{`` and the matching ``}``."""

    # raw is the full entry text including SIGIL:name{...}
    start = raw.find("{")
    if start == -1:
        return ""
    # find matching close brace (depth-aware)
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(raw)):
        ch = raw[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
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
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return raw[start + 1 : i]
    return raw[start + 1 :]


def _entry_body_lines(raw: str) -> str:
    """Return ``(body, start_line, end_line)`` for a raw entry text.

    The body is the verbatim content between the outer ``{`` and ``}``,
    including any inner newlines.
    """

    body = _extract_body(raw)
    return body


# ---------------------------------------------------------------------------
# Glossary construction
# ---------------------------------------------------------------------------

def _build_glossary_from_section(section: Section) -> Glossary:
    """Parse a ``$0`` section into a :class:`Glossary`.

    The section may contain either:
      (a) Pipe-separated declaration comments:
            # IDN | identity | attrs | B | Semantic | Identity
            # attrs = key:value pairs
            # cur=current pln=planned
            # contract: HDL | operation | status | requires
      (b) Explicit GSIG/GTYP/GMIC/GCON entries.

    Both forms are accepted and may be mixed.
    """

    g = Glossary()
    # Seed with canonical types so any file is operable even if $0 omits them
    for t in CANONICAL_TYPES:
        g.add_type(TypeDef(name=t, description="canonical type"))

    # Seed canonical micro-tokens as defaults
    for tok, val in CANONICAL_MICRO.items():
        g.add_micro(MicroDef(token=tok, value=val))

    # Process explicit entries first (GSIG/GTYP/GMIC/GCON)
    for entry in section.entries:
        if entry.sigil == "GSIG":
            attrs = parse_attrs_body(entry.raw[entry.raw.find("{") + 1 : entry.raw.rfind("}")])
            sigil = attrs.get("sigil") or entry.name
            fields_raw = attrs.get("fields")
            if isinstance(fields_raw, str) and fields_raw:
                fields_list = [f.strip() for f in fields_raw.replace("[", "").replace("]", "").split(",")]
            else:
                fields_list = None
            sd = SigilDef(
                sigil=sigil,
                name=attrs.get("name", sigil.lower()),
                type=attrs.get("type", "attrs"),
                risk=attrs.get("risk", "M"),
                layer=attrs.get("layer", "Semantic"),
                description=attrs.get("description", ""),
                fields=fields_list,
            )
            g.add_sigil(sd)
        elif entry.sigil == "GTYP":
            attrs = parse_attrs_body(entry.raw[entry.raw.find("{") + 1 : entry.raw.rfind("}")])
            g.add_type(TypeDef(name=attrs.get("name", entry.name),
                               description=attrs.get("description", "")))
        elif entry.sigil == "GMIC":
            attrs = parse_attrs_body(entry.raw[entry.raw.find("{") + 1 : entry.raw.rfind("}")])
            tok = attrs.get("token") or entry.name
            g.add_micro(MicroDef(token=tok, value=attrs.get("value", "")))
        elif entry.sigil == "GCON":
            attrs = parse_attrs_body(entry.raw[entry.raw.find("{") + 1 : entry.raw.rfind("}")])
            sigil = attrs.get("sigil") or entry.name
            fields_str = attrs.get("fields", "")
            if isinstance(fields_str, str) and fields_str:
                fields = [f.strip() for f in fields_str.split("|")]
            else:
                fields = []
            g.add_contract(AttrsPosContract(sigil=sigil, fields=fields))

    # Process comment-line declarations preserved in section.comments
    for line in section.comments:
        m = _STATUS_DECL_RE.match(line)
        if m:
            raw = m.group("statuses")
            g.status_custom = [s.strip() for s in raw.replace("[", "").replace("]", "").split(",")]
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
        # Type declaration: ONLY if line has exactly one '=' and the name
        # looks like a type word (alphabetic, possibly with '-' or '_').
        # Micro-token lines have MULTIPLE '=' pairs (e.g. `cur=cur pln=pln`).
        eq_count = line.count("=")
        if eq_count == 1:
            m = _TYPE_DECL_RE.match(line)
            if m:
                name = m.group("name")
                # Heuristic: type names are full words (attrs, cuerpo, bloque,
                # attrs-pos, relación). Reject if the name is ≤4 chars and
                # not in the canonical type set.
                canonical_type_names = {"attrs", "cuerpo", "bloque", "attrs-pos", "relación"}
                if name in canonical_type_names or len(name) > 4:
                    g.add_type(TypeDef(name=name, description=m.group("desc")))
                    continue
        # Fall through: try micro-token pairs (handles multi-pair lines)
        for tok, val in _MICRO_PAIR_RE.findall(line):
            # Only add as micro if it's NOT a type-like word
            if tok in {"attrs", "cuerpo", "bloque", "attrs-pos", "relación"}:
                continue
            g.add_micro(MicroDef(token=tok, value=val))

    # Also scan entries' raw for comment-style declarations (legacy)
    for entry in section.entries:
        if entry.sigil in GLOSSARY_RESERVED_SIGILS:
            continue
        for line in entry.raw.split("\n"):
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
            m = _TYPE_DECL_RE.match(line)
            if m:
                g.add_type(TypeDef(name=m.group("name"), description=m.group("desc")))
                continue
            for tok, val in _MICRO_PAIR_RE.findall(line):
                g.add_micro(MicroDef(token=tok, value=val))

    return g


# ---------------------------------------------------------------------------
# Auto-population: unknown sigils / statuses / types → $0 with needs_review
# ---------------------------------------------------------------------------

def ensure_in_glossary(
    doc: CortexDocument,
    *,
    sigil: Optional[str] = None,
    entry_sigil: Optional[str] = None,
    status: Optional[str] = None,
    type_: Optional[str] = None,
    definition: Optional[Dict[str, Any]] = None,
) -> None:
    """Auto-populate ``$0`` with elements not declared in the glossary.

    If the model provides a *definition*, the element is added with
    ``needs_review=False``.  Otherwise it is marked ``needs_review=True``
    so the agent can ask the Architect to define it on next consolidation.

    Parameters
    ----------
    doc : CortexDocument
        The document whose glossary is being extended.
    sigil : str, optional
        Sigil to add if missing.
    entry_sigil : str, optional
        Sigil from the entry that triggered the addition (for status/type).
    status : str, optional
        Status value to add if not canonical.
    type_ : str, optional
        Type value to add if not canonical or custom.
    definition : dict, optional
        Full definition provided by the model.
    """
    if sigil is not None and sigil not in doc.glossary.sigils:
        needs_review = definition is None
        name = definition.get("name", sigil.lower()) if definition else sigil.lower()
        type_val = definition.get("type", "attrs") if definition else "attrs"
        risk = definition.get("risk", "M") if definition else "M"
        layer = definition.get("layer", "Semantic") if definition else "Semantic"
        desc = definition.get("description", "TODO: needs_review") if definition else "TODO: needs_review"
        fields_raw = definition.get("fields") if definition else None
        if isinstance(fields_raw, str):
            fields_list = [f.strip() for f in fields_raw.replace("[", "").replace("]", "").split(",")]
        else:
            fields_list = None
        sd = SigilDef(
            sigil=sigil,
            name=name,
            type=type_val,
            risk=risk,
            layer=layer,
            description=desc,
            fields=fields_list,
            needs_review=needs_review,
        )
        doc.glossary.add_sigil(sd)
    if status is not None and status not in ALLOWED_STATUS:
        if doc.glossary.status_custom is None:
            doc.glossary.status_custom = []
        if status not in doc.glossary.status_custom:
            doc.glossary.status_custom.append(status)
    if type_ is not None and type_ not in CANONICAL_TYPES:
        if doc.glossary.types_custom is None:
            doc.glossary.types_custom = []
        if type_ not in doc.glossary.types_custom:
            doc.glossary.types_custom.append(type_)


# ---------------------------------------------------------------------------
# Top-level parser
# ---------------------------------------------------------------------------

def parse_cortex(text: str, path: str = "<string>") -> CortexDocument:
    """Parse ``.cortex`` source text into a :class:`CortexDocument`.

    The parser is deterministic and never invokes an LLM.  Validation
    errors are raised as :class:`~cortex.core.errors.CortexError`;
    non-fatal findings are recorded in ``doc.diagnostics``.
    """

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text = text + "\n"

    doc = CortexDocument()
    doc.meta = {
        "path": path,
        "format": ".cortex",
        "version": None,
        "hash": compute_document_hash(text),
    }

    tokens = lex(text)
    current_section: Optional[Section] = None

    for tok in tokens:
        if tok.kind.value == "blank":
            continue
        if tok.kind.value == "comment":
            # Preserve comment lines inside the current section (esp. $0)
            if current_section is not None:
                current_section.comments.append(tok.text)
            continue
        if tok.kind.value == "section_header":
            sec = Section(
                id=tok.section_id or "$0",
                title=tok.section_title or "",
                line_start=tok.line,
            )
            doc.sections.append(sec)
            current_section = sec
            continue
        if tok.kind.value == "entry_start":
            if current_section is None:
                # Implicit $0 if entries appear before any section header
                current_section = Section(id="$0", title="GLOSSARY")
                doc.sections.append(current_section)
            entry = _build_entry(tok, current_section.id)
            current_section.entries.append(entry)
            continue
        if tok.kind.value == "text":
            # Preserve unparsed lines too (rare) — record in current section
            if current_section is not None:
                current_section.raw_lines.append(tok.text)
            # If the line looks like an entry start (SIGIL:name{...) it's
            # almost certainly an unbalanced-brace error → emit E005
            from .lexer import looks_like_entry_start
            line_text = tok.text.strip()
            if looks_like_entry_start(line_text):
                doc.diagnostics.append({
                    "code": "E005_UNBALANCED_BRACES",
                    "message": f"line {tok.line} looks like an entry start but braces are unbalanced: {line_text!r}",
                    "line": tok.line,
                    "severity": "error",
                })
            else:
                doc.diagnostics.append({
                    "code": E017_UNPARSED_LINE,
                    "message": f"line {tok.line} could not be parsed: {tok.text!r}",
                    "line": tok.line,
                    "severity": "warning",
                })
            continue

    # ---- validation: $0 first ------------------------------------------------
    if not doc.sections:
        raise errors.MissingGlossaryError(
            "document has no sections and no $0 glossary",
        )
    if doc.sections[0].id != "$0":
        # Try to locate $0 anywhere and reorder if it's at top
        raise errors.GlossaryNotFirstError(
            f"first section is {doc.sections[0].id!r}; $0 must come first",
        )

    # ---- build glossary ------------------------------------------------------
    doc.glossary = _build_glossary_from_section(doc.sections[0])

    # ---- resolve types + parse entry values ---------------------------------
    _resolve_entry_types(doc)
    _parse_entry_values(doc)

    return doc


def _build_entry(tok, section_id: str) -> Entry:
    """Build an :class:`Entry` from a lexer ENTRY_START token.

    The entry's body is preserved verbatim in ``raw``; value parsing is
    deferred until the glossary is available.
    """

    sigil = tok.sigil or ""
    name = tok.name or ""
    raw = tok.text
    _extract_body(raw)
    # Compute line range
    line_start = tok.line
    line_end = line_start + raw.count("\n")
    entry = Entry(
        section=section_id,
        sigil=sigil,
        name=name,
        type="",  # filled by _resolve_entry_types
        value=None,
        raw=raw,
        line_start=line_start,
        line_end=line_end,
    )
    return entry


def _resolve_entry_types(doc: CortexDocument) -> None:
    """Look up each entry's expansion type from ``$0``.

    Unknown sigils produce diagnostics; the entry's type falls back to
    ``attrs`` so the AST remains usable for inspection.
    """

    for sec, entry in doc.iter_entries():
        if entry.sigil in GLOSSARY_RESERVED_SIGILS:
            entry.type = "attrs"
            continue
        sigil_def = doc.glossary.sigils.get(entry.sigil)
        if sigil_def is None:
            ensure_in_glossary(doc, sigil=entry.sigil)
            doc.diagnostics.append({
                "code": "I001_UNDECLARED_SIGIL",
                "message": f"sigil {entry.sigil!r} (entry {entry.name!r}) was auto-added to $0 with needs_review",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "info",
            })
            entry.type = "attrs"
            continue
        entry.type = sigil_def.type
        # Validate type is known
        if entry.type not in doc.glossary.types and entry.type not in CANONICAL_TYPES:
            ensure_in_glossary(doc, type_=entry.type)
            doc.diagnostics.append({
                "code": "I002_UNDECLARED_TYPE",
                "message": f"type {entry.type!r} (sigil {entry.sigil!r}) was auto-added to $0 with needs_review",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "info",
            })


def _parse_entry_values(doc: CortexDocument) -> None:
    """Parse each entry's body according to its declared expansion type."""

    for sec, entry in doc.iter_entries():
        if entry.sigil in GLOSSARY_RESERVED_SIGILS:
            # Glossary entries: parse as attrs for the resolver to consume
            try:
                entry.value = parse_attrs_body(_extract_body(entry.raw))
            except errors.InvalidAttrsError as e:
                entry.value = {}
                doc.diagnostics.append({
                    "code": E006_INVALID_ATTRS,
                    "message": str(e),
                    "line": entry.line_start,
                    "section": sec.id,
                    "sigil": entry.sigil,
                    "entry": entry.name,
                    "severity": "error",
                })
            continue

        body = _extract_body(entry.raw)
        t = entry.type
        try:
            if t == "attrs":
                entry.value = parse_attrs_body(body)
            elif t == "attrs-pos":
                contract = doc.glossary.contract_for(entry.sigil)
                if contract is None:
                    entry.value = parse_attrs_body(body)
                else:
                    entry.value = parse_attrs_pos_body(body, contract)
            elif t == "cuerpo":
                entry.value = body.strip("\n")
            elif t == "bloque":
                # Preserved verbatim — leading/trailing newline stripped
                entry.value = body.strip("\n")
            elif t == "relación":
                entry.value = body.strip()
            else:
                # Unknown type — fallback to attrs
                entry.value = parse_attrs_body(body)
        except errors.InvalidAttrsError as e:
            entry.value = {}
            doc.diagnostics.append({
                "code": E006_INVALID_ATTRS,
                "message": str(e),
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })
        # Recompute hash with the final type + value
        entry.hash = compute_entry_hash(entry)
        entry.entry_id = entry.hash


# ---------------------------------------------------------------------------
# Convenience entry constructor (used by CRUD mutations)
# ---------------------------------------------------------------------------

def build_entry_from_value(
    section_id: str,
    sigil: str,
    name: str,
    type_: str,
    value: Any,
) -> Entry:
    """Construct an :class:`Entry` from a parsed value.

    Used by the CRUD layer and templates — produces an entry whose
    ``raw`` text is the canonical serialisation of the value.
    """

    from .writer import serialize_entry_value
    raw = f"{sigil}:{name}{{{serialize_entry_value(value, type_)}}}"
    entry = Entry(
        section=section_id,
        sigil=sigil,
        name=name,
        type=type_,
        value=value,
        raw=raw,
        line_start=0,
        line_end=0,
    )
    entry.hash = compute_entry_hash(entry)
    entry.entry_id = entry.hash
    return entry
