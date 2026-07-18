#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.1 parser and AST model.
Sections 3-4 of the independent reviewer's implementation.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional, List, Tuple

from .scalars import (
    Scalar, ParseError, StringCursor, parse_attrs_payload,
    parse_string_scalar, parse_scalar, emit_string_literal,
    ATOM_RE, _INT_RE, _DEC_RE, to_nfc,
)


# ---------------------------------------------------------------------------
# 4. Document / AST model
# ---------------------------------------------------------------------------

@dataclass
class FormatDecl:
    cortex: str = "0.1"
    encoding: str = "UTF-8"
    attrs: List[Tuple[str, Scalar]] = field(default_factory=list)  # all (including cortex/encoding/language) in order
    source_line: int = 1


@dataclass
class MetaDecl:
    name: str
    attrs: List[Tuple[str, Scalar]]
    capa: Optional[str] = None
    source_line: int = 1


@dataclass
class EnumDecl:
    name: str
    values: List[str]
    source_line: int = 1


@dataclass
class MicroDecl:
    token: str
    expand: str
    source_line: int = 1


@dataclass
class NamespaceDecl:
    alias: str
    attrs: List[Tuple[str, Scalar]]  # includes id, version, required, desc, extras
    source_line: int = 1


@dataclass
class ExtensionDecl:
    name: str
    attrs: List[Tuple[str, Scalar]]  # includes namespace, id, version, required, desc, extras
    source_line: int = 1


@dataclass
class ContractField:
    name: str
    type: str
    required: bool


@dataclass
class SymbolDef:
    namespace: Optional[str]
    sigil: str
    label: str
    shape: str  # attrs|attrs-pos|cuerpo|bloque|relacion
    weight: str
    focus: str
    desc: str
    open: bool
    contract: List[ContractField]
    attrs: List[Tuple[str, Scalar]]  # original attrs (in source order)
    source_line: int = 1

    @property
    def qualified(self) -> str:
        return f"{self.namespace}::{self.sigil}" if self.namespace else self.sigil


@dataclass
class Idea:
    section: int  # section id
    namespace: Optional[str]
    symbol: str
    name: str
    shape: str
    payload: Any
    source_line: int = 1

    @property
    def qualified_symbol(self) -> str:
        return f"{self.namespace}::{self.symbol}" if self.namespace else self.symbol

    @property
    def address(self) -> str:
        return f"${self.section}:{self.qualified_symbol}:{self.name}"


@dataclass
class Section:
    id: int
    title: Optional[str]
    ideas: List[Idea]
    capa: Optional[str] = None  # KERNEL|CORE|KNOW|DATA|FLOW|CACHE


@dataclass
class Glossary:
    format: Optional[FormatDecl] = None
    meta: List[MetaDecl] = field(default_factory=list)
    enums: List[EnumDecl] = field(default_factory=list)
    micros: List[MicroDecl] = field(default_factory=list)
    namespaces: List[NamespaceDecl] = field(default_factory=list)
    extensions: List[ExtensionDecl] = field(default_factory=list)
    symbols: List[SymbolDef] = field(default_factory=list)
    capa: Optional[str] = None  # $0 capa (KERNEL), populated when parser sees $0:CAPA


@dataclass
class Document:
    cortex_version: str = "0.1"
    encoding: str = "UTF-8"
    glossary: Glossary = field(default_factory=Glossary)
    sections: List[Section] = field(default_factory=list)


def resolve_capa(section: Section) -> Optional[str]:
    """Return the effective capa for a section.

    - $0 is always KERNEL (handled via glossary.capa)
    - $1 returns its explicit capa or None
    - $N (N>=2) returns its explicit capa, or 'DATA' as default for legacy sections
    """
    if section.capa is not None:
        return section.capa
    if section.id >= 2:
        return "DATA"
    return None


# ---------------------------------------------------------------------------
# 5. CORTEX parser
# ---------------------------------------------------------------------------

def _normalize_line_endings(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def parse_contract_fields(s: str) -> List[ContractField]:
    """Parse a contract string like 'topic:text|content:text|status:%state?'."""
    out = []
    for part in s.split("|"):
        part = part.strip()
        if not part:
            raise ParseError("G008_INVALID_CONTRACT", f"Empty contract field in {s!r}")
        if "?" in part:
            required = False
            part = part[:-1]
        else:
            required = True
        if ":" in part:
            name, type_ = part.split(":", 1)
        else:
            name, type_ = part, "any"
        out.append(ContractField(name=name.strip(), type=type_.strip(), required=required))
    return out


def parse_cortex(source: str) -> Document:
    """Parse a CORTEX 0.1 source string into a Document AST."""
    # 1. UTF-8 / BOM / line endings
    if source.startswith("\ufeff"):
        raise ParseError("U001_BOM_FORBIDDEN", "BOM forbidden")
    source = _normalize_line_endings(source)
    lines = source.split("\n")

    doc = Document()
    in_glossary = False
    current_section: Optional[Section] = None
    in_body = False  # cuerpo/bloque multiline
    body_lines: List[str] = []
    body_idea: Optional[Idea] = None
    body_kind: str = ""  # cuerpo or bloque

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line_no = i + 1
        if in_body:
            # Check if this line closes the body: trimmed == "}"
            stripped = raw.strip()
            if stripped == "}":
                # Close body
                text = "\n".join(body_lines)
                if body_kind == "cuerpo":
                    body_idea.payload = ("cuerpo", text)
                else:
                    body_idea.payload = ("bloque", text)
                if current_section is not None:
                    current_section.ideas.append(body_idea)
                in_body = False
                body_lines = []
                body_idea = None
                body_kind = ""
                i += 1
                continue
            else:
                body_lines.append(raw)
                i += 1
                continue

        # Not in body: check for comments / blanks / sections / ideas
        stripped = raw.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("#"):
            i += 1
            continue

        # Section header? Only `$0` (bare) starts the glossary. `$N` (N>=1) starts a section.
        # `$0:name{...}` is a meta-declaration handled below.
        # Supports optional :CAPA suffix on section headers ($1: Title:CAPA, $0: Title:KERNEL).
        # Also handles `$0:CAPA` (no title, just capa).
        m = re.match(r"^\$([0-9]+)(?:\s+(.*))?$", stripped)
        m0 = re.match(r"^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$", stripped)
        if m0:
            # $0:CAPA — start glossary
            if in_glossary:
                raise ParseError("G002_GLOSSARY_REOPENED", "$0 reopened", line_no)
            in_glossary = True
            doc.glossary.capa = m0.group(1)
            i += 1
            continue
        # $0: Title or $0: Title:CAPA
        m0t = re.match(r"^\$0:\s+(.*)$", stripped)
        if m0t and not re.match(r"^\$0:\s*(?:format|enum_|micro_|namespace_|extension_)", stripped):
            if in_glossary:
                raise ParseError("G002_GLOSSARY_REOPENED", "$0 reopened", line_no)
            in_glossary = True
            i += 1
            continue
        # $N:CAPA — section with capa but no title (N>=1)
        mn = re.match(r"^\$([1-9][0-9]*):(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$", stripped)
        if mn:
            sid = int(mn.group(1))
            capa = mn.group(2)
            current_section = Section(id=sid, title=None, ideas=[], capa=capa)
            doc.sections.append(current_section)
            in_glossary = False
            i += 1
            continue
        if m and not stripped.startswith("$0:"):
            sid = int(m.group(1))
            if sid == 0:
                if in_glossary:
                    raise ParseError("G002_GLOSSARY_REOPENED", "$0 reopened", line_no)
                # $0 header — start glossary
                in_glossary = True
                i += 1
                continue
            # Regular section
            title_raw = m.group(2)
            title = title_raw.strip() if title_raw is not None else None
            capa = None
            if title:
                cm = re.search(r':(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$', title)
                if cm:
                    capa = cm.group(1)
                    title = title[:cm.start()].strip()
            current_section = Section(id=sid, title=title, ideas=[], capa=capa)
            doc.sections.append(current_section)
            in_glossary = False  # exit glossary mode
            i += 1
            continue

        # Section header with title: `$N: title` (requires space after :)
        # Supports optional :CAPA suffix: `$N: title:CAPA`
        m = re.match(r"^\$([1-9][0-9]*):\s+(.*)$", stripped)
        if m:
            sid = int(m.group(1))
            title = m.group(2).strip()
            capa = None
            cm = re.search(r':(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$', title)
            if cm:
                capa = cm.group(1)
                title = title[:cm.start()].strip()
            current_section = Section(id=sid, title=title, ideas=[], capa=capa)
            doc.sections.append(current_section)
            in_glossary = False  # exit glossary mode
            i += 1
            continue

        # Glossary declaration?
        if in_glossary and (stripped.startswith("$0:") or _is_glossary_decl_line(stripped)):
            _parse_glossary_declaration(stripped, doc, line_no)
            i += 1
            continue

        # Idea line?
        if current_section is None and not in_glossary:
            raise ParseError("S005_CONTENT_OUTSIDE_SECTION", f"Content outside section: {stripped!r}", line_no)

        if in_glossary:
            # In glossary but not a $0: line — must be a sigil declaration
            _parse_glossary_declaration(stripped, doc, line_no)
            i += 1
            continue

        # Parse idea
        idea = _parse_idea_line(stripped, current_section.id, doc, line_no)
        # If cuerpo/bloque and not closed on same line, enter multiline mode
        if idea.shape in ("cuerpo", "bloque") and isinstance(idea.payload, tuple) and idea.payload[0] == "_multiline_body":
            in_body = True
            body_lines = []
            body_idea = idea
            body_kind = idea.shape
            i += 1
            continue
        current_section.ideas.append(idea)
        i += 1

    return doc


def _is_glossary_decl_line(s: str) -> bool:
    """A sigil declaration: SIGIL:name{...} or ns::SIGIL:name{...} or ns::SIGIL:name|..."""
    return bool(re.match(r"^(?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]*):", s))


def _parse_glossary_declaration(line: str, doc: Document, line_no: int):
    """Parse a $0:name{...} meta-declaration or SIGIL:name{...} symbol declaration."""
    brace_idx = line.find("{")
    if brace_idx < 0:
        raise ParseError("G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS",
                         f"Glossary declaration must use attrs: {line!r}", line_no)
    close_idx = _find_matching_brace(line, brace_idx)
    head = line[:brace_idx]
    payload_str = line[brace_idx:close_idx + 1]
    tail = line[close_idx + 1:].strip()
    capa = None
    if tail:
        cm = re.match(r"^:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$", tail)
        if cm:
            capa = cm.group(1)
    head = head.strip()
    if head.startswith("$0:"):
        name = head[3:]
        attrs = parse_attrs_payload(payload_str, line_no)
        _add_meta_declaration(name, attrs, doc, line_no, capa=capa)
    else:
        # Sigil declaration
        m = re.match(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$", head)
        if not m:
            raise ParseError("L001_INVALID_SYMBOL", f"Invalid sigil declaration head: {head!r}", line_no)
        ns = m.group(1)
        sigil = m.group(2)
        label = m.group(3)
        attrs = parse_attrs_payload(payload_str, line_no)
        sym = _build_symbol_def(ns, sigil, label, attrs, line_no)
        doc.glossary.symbols.append(sym)


def _find_matching_brace(line: str, brace_idx: int) -> int:
    depth = 0
    i = brace_idx
    while i < len(line):
        if line[i] == '{':
            depth += 1
        elif line[i] == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ParseError("S006_INVALID_ATTRS", "Unclosed {", 1, 1)


def _add_meta_declaration(name: str, attrs: List[Tuple[str, Scalar]], doc: Document, line_no: int, capa: Optional[str] = None):
    if name == "format":
        if doc.glossary.format is not None:
            raise ParseError("G006_DUPLICATE_FORMAT", "Duplicate $0:format", line_no)
        amap = {k: v for k, v in attrs}
        cortex = amap.get("cortex")
        encoding = amap.get("encoding")
        cortex_val = cortex.value if cortex else "0.1"
        encoding_val = encoding.value if encoding else "UTF-8"
        if cortex_val != "0.1":
            raise ParseError("G007_UNSUPPORTED_VERSION", f"Unsupported cortex version: {cortex_val}", line_no)
        if encoding_val != "UTF-8":
            raise ParseError("G011_ENCODING_REQUIRED", f"Encoding must be UTF-8: {encoding_val}", line_no)
        doc.glossary.format = FormatDecl(cortex=cortex_val, encoding=encoding_val, attrs=attrs, source_line=line_no)
        return

    if name.startswith("enum_"):
        ename = name[5:]
        amap = {k: v for k, v in attrs}
        values_v = amap.get("values")
        if values_v is None or values_v.kind != "string":
            raise ParseError("G014_INVALID_ENUM", f"enum {ename} missing values string", line_no)
        values = values_v.value.split("|")
        doc.glossary.enums.append(EnumDecl(name=ename, values=values, source_line=line_no))
        return

    if name.startswith("micro_"):
        token = name[6:]
        amap = {k: v for k, v in attrs}
        expand_v = amap.get("expand")
        if expand_v is None:
            raise ParseError("G012_INVALID_MICRO", f"micro {token} missing expand", line_no)
        expand_val = expand_v.value if expand_v.kind in ("atom", "string") else expand_v.lexeme
        doc.glossary.micros.append(MicroDecl(token=token, expand=expand_val, source_line=line_no))
        return

    if name.startswith("namespace_"):
        alias = name[10:]
        doc.glossary.namespaces.append(NamespaceDecl(alias=alias, attrs=attrs, source_line=line_no))
        return

    if name.startswith("extension_"):
        ext_name = name[10:]
        doc.glossary.extensions.append(ExtensionDecl(name=ext_name, attrs=attrs, source_line=line_no))
        return

    # Other meta-declaration
    doc.glossary.meta.append(MetaDecl(name=name, attrs=attrs, capa=capa, source_line=line_no))


def _build_symbol_def(ns: Optional[str], sigil: str, label: str,
                       attrs: List[Tuple[str, Scalar]], line_no: int) -> SymbolDef:
    amap = {k: v for k, v in attrs}
    type_v = amap.get("type")
    if type_v is None:
        raise ParseError("G016_SYMBOL_TYPE_REQUIRED", f"sigil {sigil} missing type", line_no)
    shape = type_v.value if type_v.kind in ("atom", "string") else type_v.lexeme
    if shape not in ("attrs", "attrs-pos", "cuerpo", "bloque", "relacion"):
        raise ParseError("G017_UNKNOWN_SHAPE", f"Unknown shape: {shape}", line_no)
    weight_v = amap.get("weight")
    if weight_v is None:
        raise ParseError("G018_SYMBOL_WEIGHT_REQUIRED", f"sigil {sigil} missing weight", line_no)
    weight = weight_v.value if weight_v.kind in ("atom", "string") else weight_v.lexeme
    if weight not in ("B", "M", "H"):
        raise ParseError("G019_INVALID_WEIGHT", f"Invalid weight: {weight}", line_no)
    desc_v = amap.get("desc")
    if desc_v is None:
        raise ParseError("G020_SYMBOL_DESCRIPTION_REQUIRED", f"sigil {sigil} missing desc", line_no)
    desc = desc_v.value if desc_v.kind == "string" else desc_v.lexeme
    open_v = amap.get("open")
    is_open = False
    if open_v is not None:
        is_open = (open_v.kind == "boolean" and open_v.value is True) or \
                  (open_v.kind == "atom" and open_v.value == "true")
    # Contract
    contract: List[ContractField] = []
    if shape == "attrs":
        fields_v = amap.get("fields")
        if fields_v is None:
            raise ParseError("G021_ATTRS_CONTRACT_REQUIRED", f"sigil {sigil} missing fields", line_no)
        contract = parse_contract_fields(fields_v.value)
    elif shape in ("attrs-pos", "relacion"):
        pos_v = amap.get("pos")
        if pos_v is None:
            raise ParseError("G022_POSITIONAL_CONTRACT_REQUIRED", f"sigil {sigil} missing pos", line_no)
        contract = parse_contract_fields(pos_v.value)
        if shape == "relacion" and len(contract) < 3:
            raise ParseError("G023_RELATION_CONTRACT_TOO_SHORT", "relacion needs >=3 fields", line_no)
    # Focus
    focus_v = amap.get("focus")
    if focus_v is None:
        if shape in ("cuerpo", "bloque"):
            focus = "$body"
        else:
            raise ParseError("G024_FOCUS_REQUIRED", f"sigil {sigil} missing focus", line_no)
    else:
        focus = focus_v.value if focus_v.kind in ("atom", "string") else focus_v.lexeme
        # Validate focus is in contract (for non-cuerpo/bloque)
        if shape in ("attrs", "attrs-pos", "relacion"):
            if not any(f.name == focus for f in contract):
                raise ParseError("G025_UNKNOWN_FOCUS_FIELD",
                                 f"focus {focus!r} not in contract", line_no)
    return SymbolDef(namespace=ns, sigil=sigil, label=label, shape=shape,
                     weight=weight, focus=focus, desc=desc, open=is_open,
                     contract=contract, attrs=attrs, source_line=line_no)


def _parse_idea_line(line: str, section_id: int, doc: Document, line_no: int) -> Idea:
    """Parse an idea line: SIGIL:name{...} or SIGIL:name|...|..."""
    line = line.strip()
    m = re.match(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^{|}\s]+)", line)
    if not m:
        raise ParseError("S003_INVALID_IDEA_HEAD", f"Invalid idea head: {line!r}", line_no)
    ns = m.group(1)
    sigil = m.group(2)
    name = m.group(3)
    rest = line[m.end():]
    # Look up sigil in glossary
    sym = None
    for s in doc.glossary.symbols:
        if s.sigil == sigil and s.namespace == ns:
            sym = s
            break
        if s.sigil == sigil and s.namespace is None and ns is None:
            sym = s
            break
    if sym is None:
        raise ParseError("I001_UNDECLARED_SYMBOL", f"Undeclared sigil: {sigil}", line_no)

    shape = sym.shape
    if shape == "attrs" or shape == "cuerpo" or shape == "bloque":
        # Braced payload
        if not rest.startswith("{"):
            raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                             f"Expected {{ for shape {shape}", line_no)
        # Check if it's a single-line or multiline
        if rest.endswith("}") and rest.count("\n") == 0:
            # Single line
            payload_str = rest
            if shape == "attrs":
                pairs = parse_attrs_payload(payload_str, line_no)
                return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                            shape=shape, payload=("attrs", pairs), source_line=line_no)
            else:
                # cuerpo or bloque single-line
                inner = rest[1:-1]
                if shape == "cuerpo":
                    inner = to_nfc(inner)
                return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                            shape=shape, payload=(shape, inner), source_line=line_no)
        else:
            # Multiline — body starts; mark for multiline collection
            if rest.strip() != "{":
                raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                                 f"Expected single {{ for multiline {shape}", line_no)
            return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                        shape=shape, payload=("_multiline_body", None), source_line=line_no)
    elif shape in ("attrs-pos", "relacion"):
        # Pipe-delimited
        if not rest.startswith("|"):
            raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                             f"Expected | for shape {shape}", line_no)
        rest = rest[1:]
        cells = _parse_pipe_cells(rest, line_no)
        return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                    shape=shape, payload=(shape, cells), source_line=line_no)
    raise ParseError("S999_INTERNAL_PARSE_FAILURE", f"Cannot parse idea: {line!r}", line_no)


def _parse_pipe_cells(s: str, line_no: int) -> List[Scalar]:
    """Parse positional cells separated by |."""
    cells = []
    i = 0
    n = len(s)
    while i <= n:
        if i < n and s[i] == '"':
            cur = StringCursor(s[i:], line=line_no)
            sc = parse_string_scalar(cur)
            consumed = cur.i
            cells.append(sc)
            i += consumed
            while i < n and s[i] in " \t":
                i += 1
            if i >= n:
                return cells
            if s[i] != "|":
                raise ParseError("S006_INVALID_ATTRS", f"Expected | after quoted cell", line_no, i)
            i += 1
            continue
        else:
            j = i
            while j < n and s[j] != "|":
                j += 1
            raw = s[i:j]
            raw_trimmed = raw.strip()
            if raw_trimmed == "" and j >= n:
                return cells
            cells.append(_classify_raw_cell(raw_trimmed, line_no))
            i = j
            if i < n and s[i] == "|":
                i += 1
                continue
            else:
                return cells
    return cells


def _classify_raw_cell(raw: str, line_no: int) -> Scalar:
    """Classify a raw pipe cell text into a scalar."""
    if _INT_RE.match(raw):
        v = raw
        if v == "-0":
            v = "0"
        return Scalar("integer", v, v)
    if _DEC_RE.match(raw):
        return Scalar("decimal", raw, raw)
    if raw == "true":
        return Scalar("boolean", True, "true")
    if raw == "false":
        return Scalar("boolean", False, "false")
    if raw == "null":
        return Scalar("null", None, "null")
    if ATOM_RE.match(raw) and " " not in raw:
        return Scalar("atom", raw, raw)
    return Scalar("string", raw, emit_string_literal(raw))
