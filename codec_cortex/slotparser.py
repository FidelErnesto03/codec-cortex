#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.2 parser + AST extensions.

NEW module: extends 0.1 parser with slot-encoded Ideas. Preserves 0.1 intact.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional, List, Tuple

from .scalars import (
    Scalar, ParseError, parse_attrs_payload, parse_string_scalar,
    parse_scalar, emit_string_literal, ATOM_RE, _INT_RE, _DEC_RE, to_nfc,
    StringCursor,
)
from .slots import (
    SLOT_MARKER, HOMOGLYPHS, SLOT_INDEX_MAX,
    SlotContractField, FieldValue,
    parse_slot_contract, validate_slot_contract,
    parse_slot_payload, check_mixed_surface_legacy,
    detect_homoglyph, is_ascii_digit,
)
from .parser import (
    Document, Glossary, FormatDecl, MetaDecl, EnumDecl, MicroDecl,
    NamespaceDecl, ExtensionDecl, MetaDecl, SymbolDef, ContractField,
    Section, Idea,
    parse_contract_fields,
    _normalize_line_endings, _find_matching_brace,
    _is_glossary_decl_line,
)


# ContractField0 extends 0.1 ContractField with optional `position` for slot contracts.
# We do NOT modify the 0.1 ContractField dataclass. Instead we add `position` attribute
# dynamically via a subclass.
@dataclass
class ContractField0(ContractField):
    """0.2-extended ContractField with slot position metadata."""
    position: Optional[int] = None


@dataclass
class SymbolDef0(SymbolDef):
    """0.2-extended SymbolDef with `encoding` attribute for slot-encoded sigils."""
    encoding: Optional[str] = None


# ---------------------------------------------------------------------------
# AST 0.2 extensions
# ---------------------------------------------------------------------------

@dataclass
class SigilMapDecl:
    """The $0:sigil-map declaration. Has 5 attrs: marker, codepoint, base, syntax, order."""
    marker: str = "※"
    codepoint: str = "U+203B"
    base: int = 1
    syntax: str = "※N:valor"
    order: str = "ascending"
    source_line: int = 1


# Extend Glossary with sigil_map (we monkey-patch via subclass)
@dataclass
class GlossarySlots(Glossary):
    sigil_map: Optional[SigilMapDecl] = None


# ---------------------------------------------------------------------------
# Public parse_slots
# ---------------------------------------------------------------------------

def parse_slots(source: str) -> Document:
    """Parse a CORTEX 0.2 source string. Does NOT touch 0.1 parser."""
    if source.startswith("\ufeff"):
        raise ParseError("U001_BOM_FORBIDDEN", "BOM forbidden")
    source = _normalize_line_endings(source)
    return _SlotParser(source).parse()


# ---------------------------------------------------------------------------
# Internal parser
# ---------------------------------------------------------------------------

class _SlotParser:
    def __init__(self, source: str):
        self.source = source
        self.lines = source.split("\n")
        self.doc = Document(cortex_version="0.2")
        self.doc.glossary = GlossarySlots()
        self.in_glossary = False
        self.current_section: Optional[Section] = None
        self.in_body = False
        self.body_lines: List[str] = []
        self.body_idea: Optional[Idea] = None
        self.body_kind: str = ""
        self.seen_sigil_map: bool = False
        self.seen_any_slots_sigil: bool = False
        self.seen_sections: bool = False
        self.diagnostics: List[dict] = []
        # Track seen sections/ideas for duplicate detection
        self.seen_section_ids: set = set()
        self.seen_idea_addresses: set = set()
        self.seen_symbol_keys: set = set()

    def parse(self) -> Document:
        i = 0
        n = len(self.lines)
        while i < n:
            raw = self.lines[i]
            line_no = i + 1
            if self.in_body:
                stripped = raw.strip()
                if stripped == "}":
                    text = "\n".join(self.body_lines)
                    if self.body_kind == "cuerpo":
                        self.body_idea.payload = ("cuerpo", text)
                    else:
                        self.body_idea.payload = ("bloque", text)
                    if self.current_section is not None:
                        self.current_section.ideas.append(self.body_idea)
                    self.in_body = False
                    self.body_lines = []
                    self.body_idea = None
                    self.body_kind = ""
                    i += 1
                    continue
                else:
                    self.body_lines.append(raw)
                    i += 1
                    continue
            stripped = raw.strip()
            if not stripped:
                i += 1
                continue
            if stripped.startswith("#"):
                i += 1
                continue
            # $0:CAPA
            m0 = re.match(r"^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$", stripped)
            if m0:
                if self.in_glossary:
                    raise ParseError("G002_GLOSSARY_REOPENED", "$0 reopened", line_no)
                self.in_glossary = True
                self.doc.glossary.capa = m0.group(1)
                i += 1
                continue
            # $0: title (start glossary)
            m0t = re.match(r"^\$0:\s+(.*)$", stripped)
            if m0t and not re.match(r"^\$0:\s*(?:format|enum_|micro_|namespace_|extension_|sigil-map)", stripped):
                if self.in_glossary:
                    raise ParseError("G002_GLOSSARY_REOPENED", "$0 reopened", line_no)
                self.in_glossary = True
                i += 1
                continue
            # $N:CAPA (no title)
            mn = re.match(r"^\$([1-9][0-9]*):(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$", stripped)
            if mn:
                sid = int(mn.group(1))
                capa = mn.group(2)
                self._start_section(sid, None, capa, line_no)
                i += 1
                continue
            # $N (no title) or $N title
            m = re.match(r"^\$([0-9]+)(?:\s+(.*))?$", stripped)
            if m and not stripped.startswith("$0:"):
                sid = int(m.group(1))
                if sid == 0:
                    if self.in_glossary:
                        raise ParseError("G002_GLOSSARY_REOPENED", "$0 reopened", line_no)
                    self.in_glossary = True
                    i += 1
                    continue
                title_raw = m.group(2)
                title = title_raw.strip() if title_raw is not None else None
                capa = None
                if title:
                    cm = re.search(r':(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$', title)
                    if cm:
                        capa = cm.group(1)
                        title = title[:cm.start()].strip()
                self._start_section(sid, title, capa, line_no)
                i += 1
                continue
            # $N: title
            m = re.match(r"^\$([1-9][0-9]*):\s+(.*)$", stripped)
            if m:
                sid = int(m.group(1))
                title = m.group(2).strip()
                capa = None
                cm = re.search(r':(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$', title)
                if cm:
                    capa = cm.group(1)
                    title = title[:cm.start()].strip()
                self._start_section(sid, title, capa, line_no)
                i += 1
                continue
            # Glossary declaration
            if self.in_glossary and (stripped.startswith("$0:") or _is_glossary_decl_line(stripped)):
                self._parse_glossary_declaration_slots(stripped, line_no)
                i += 1
                continue
            if self.current_section is None and not self.in_glossary:
                raise ParseError("S005_CONTENT_OUTSIDE_SECTION",
                                 f"Content outside section: {stripped!r}", line_no)
            if self.in_glossary:
                self._parse_glossary_declaration_slots(stripped, line_no)
                i += 1
                continue
            # Idea
            idea = self._parse_idea_line_slots(stripped, self.current_section.id, line_no)
            if idea.shape in ("cuerpo", "bloque") and isinstance(idea.payload, tuple) and idea.payload[0] == "_multiline_body":
                self.in_body = True
                self.body_lines = []
                self.body_idea = idea
                self.body_kind = idea.shape
                i += 1
                continue
            self.current_section.ideas.append(idea)
            i += 1
        # Post-parse validation
        self._post_validate()
        return self.doc

    def _start_section(self, sid: int, title: Optional[str], capa: Optional[str], line_no: int):
        # S002_DUPLICATE_SECTION
        if sid in self.seen_section_ids:
            raise ParseError("S002_DUPLICATE_SECTION",
                             f"Duplicate section ${sid}", line_no)
        self.seen_section_ids.add(sid)
        # If we have any slots sigil but no sigil-map yet, fail G030/G041
        if self.seen_any_slots_sigil and not self.seen_sigil_map:
            raise ParseError("G030_SIGIL_MAP_REQUIRED",
                             "0.2 uses slots but $0:sigil-map is missing", line_no)
        self.current_section = Section(id=sid, title=title, ideas=[], capa=capa)
        self.doc.sections.append(self.current_section)
        self.in_glossary = False
        self.seen_sections = True

    def _parse_glossary_declaration_slots(self, line: str, line_no: int):
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
            self._add_meta_declaration_slots(name, payload_str, line_no, capa)
        else:
            m = re.match(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$", head)
            if not m:
                raise ParseError("L001_INVALID_SYMBOL",
                                 f"Invalid sigil declaration head: {head!r}", line_no)
            ns = m.group(1)
            sigil = m.group(2)
            label = m.group(3)
            # G015_DUPLICATE_SYMBOL
            sym_key = (ns, sigil)
            if sym_key in self.seen_symbol_keys:
                raise ParseError("G015_DUPLICATE_SYMBOL",
                                 f"Duplicate symbol {ns + '::' if ns else ''}{sigil}", line_no)
            attrs = parse_attrs_payload(payload_str, line_no)
            sym = self._build_symbol_def_slots(ns, sigil, label, attrs, line_no)
            self.doc.glossary.symbols.append(sym)
            self.seen_symbol_keys.add(sym_key)

    def _add_meta_declaration_slots(self, name: str, payload_str: str, line_no: int, capa: Optional[str]):
        attrs = parse_attrs_payload(payload_str, line_no)
        # I050: slot marker not allowed in $0 (except sigil-map marker value)
        if name != "sigil-map":
            for k, v in attrs:
                if "※" in k:
                    raise ParseError("I050_SLOT_NOT_ALLOWED_IN_GLOSSARY",
                                     f"※ in $0:{name} key {k!r}", line_no)
                if isinstance(v.value, str) and "※" in v.value:
                    raise ParseError("I050_SLOT_NOT_ALLOWED_IN_GLOSSARY",
                                     f"※ in $0:{name} attr {k}", line_no)
        if name == "format":
            if self.doc.glossary.format is not None:
                raise ParseError("G006_DUPLICATE_FORMAT", "Duplicate $0:format", line_no)
            amap = {k: v for k, v in attrs}
            cortex = amap.get("cortex")
            encoding = amap.get("encoding")
            cortex_val = cortex.value if cortex else "0.1"
            encoding_val = encoding.value if encoding else "UTF-8"
            if cortex_val != "0.2":
                raise ParseError("G007_UNSUPPORTED_VERSION",
                                 f"Declared cortex {cortex_val} != parser version 0.2", line_no)
            if encoding_val != "UTF-8":
                raise ParseError("G011_ENCODING_REQUIRED",
                                 f"Encoding must be UTF-8: {encoding_val}", line_no)
            self.doc.glossary.format = FormatDecl(cortex=cortex_val, encoding=encoding_val,
                                                   attrs=attrs, source_line=line_no)
            return
        if name == "sigil-map":
            # G041: sigil-map must appear BEFORE any sigilo with encoding:slots
            if self.seen_any_slots_sigil:
                raise ParseError("G041_SIGIL_MAP_ORDER",
                                 "$0:sigil-map must appear before any sigil with encoding:slots", line_no)
            if self.seen_sigil_map:
                raise ParseError("G031_DUPLICATE_SIGIL_MAP",
                                 "More than one $0:sigil-map", line_no)
            amap = {k: v for k, v in attrs}
            marker = amap.get("marker")
            codepoint = amap.get("codepoint")
            base = amap.get("base")
            syntax = amap.get("syntax")
            order = amap.get("order")
            sm = SigilMapDecl(
                marker=marker.value if marker else "※",
                codepoint=codepoint.value if codepoint else "U+203B",
                base=int(base.value) if base and base.kind == "integer" else 1,
                syntax=syntax.value if syntax else "※N:valor",
                order=order.value if order else "ascending",
                source_line=line_no,
            )
            # G032: validate canonical values
            if (sm.marker != "※" or sm.codepoint != "U+203B" or sm.base != 1
                    or sm.syntax != "※N:valor" or sm.order != "ascending"):
                raise ParseError("G032_INVALID_SIGIL_MAP",
                                 "sigil-map values are not canonical", line_no)
            self.doc.glossary.sigil_map = sm
            self.seen_sigil_map = True
            return
        if name.startswith("enum_"):
            ename = name[5:]
            amap = {k: v for k, v in attrs}
            values_v = amap.get("values")
            if values_v is None or values_v.kind != "string":
                raise ParseError("G014_INVALID_ENUM",
                                 f"enum {ename} missing values string", line_no)
            values = values_v.value.split("|")
            self.doc.glossary.enums.append(EnumDecl(name=ename, values=values, source_line=line_no))
            return
        if name.startswith("micro_"):
            token = name[6:]
            amap = {k: v for k, v in attrs}
            expand_v = amap.get("expand")
            if expand_v is None:
                raise ParseError("G012_INVALID_MICRO",
                                 f"micro {token} missing expand", line_no)
            expand_val = expand_v.value if expand_v.kind in ("atom", "string") else expand_v.lexeme
            self.doc.glossary.micros.append(MicroDecl(token=token, expand=expand_val, source_line=line_no))
            return
        if name.startswith("namespace_"):
            alias = name[10:]
            self.doc.glossary.namespaces.append(NamespaceDecl(alias=alias, attrs=attrs, source_line=line_no))
            return
        if name.startswith("extension_"):
            ext_name = name[10:]
            self.doc.glossary.extensions.append(ExtensionDecl(name=ext_name, attrs=attrs, source_line=line_no))
            return
        self.doc.glossary.meta.append(MetaDecl(name=name, attrs=attrs, capa=capa, source_line=line_no))

    def _build_symbol_def_slots(self, ns, sigil, label, attrs, line_no) -> SymbolDef:
        amap = {k: v for k, v in attrs}
        type_v = amap.get("type")
        if type_v is None:
            raise ParseError("G016_SYMBOL_TYPE_REQUIRED",
                             f"sigil {sigil} missing type", line_no)
        shape = type_v.value if type_v.kind in ("atom", "string") else type_v.lexeme
        if shape not in ("attrs", "attrs-pos", "cuerpo", "bloque", "relacion"):
            raise ParseError("G017_UNKNOWN_SHAPE",
                             f"Unknown shape: {shape}", line_no)
        weight_v = amap.get("weight")
        if weight_v is None:
            raise ParseError("G018_SYMBOL_WEIGHT_REQUIRED",
                             f"sigil {sigil} missing weight", line_no)
        weight = weight_v.value if weight_v.kind in ("atom", "string") else weight_v.lexeme
        if weight not in ("B", "M", "H"):
            raise ParseError("G019_INVALID_WEIGHT",
                             f"Invalid weight: {weight}", line_no)
        desc_v = amap.get("desc")
        if desc_v is None:
            raise ParseError("G020_SYMBOL_DESCRIPTION_REQUIRED",
                             f"sigil {sigil} missing desc", line_no)
        desc = desc_v.value if desc_v.kind == "string" else desc_v.lexeme
        open_v = amap.get("open")
        is_open = False
        if open_v is not None:
            is_open = (open_v.kind == "boolean" and open_v.value is True) or \
                      (open_v.kind == "atom" and open_v.value == "true")
        # Encoding (0.2)
        encoding_v = amap.get("encoding")
        encoding = None
        if encoding_v is not None:
            encoding = encoding_v.value if encoding_v.kind in ("atom", "string") else encoding_v.lexeme
            if encoding != "slots":
                raise ParseError("G039_ENCODING_SHAPE_MISMATCH",
                                 f"Unknown encoding: {encoding}", line_no)
            if shape not in ("attrs", "attrs-pos", "relacion"):
                raise ParseError("G039_ENCODING_SHAPE_MISMATCH",
                                 f"encoding:slots not valid for shape {shape}", line_no)
            self.seen_any_slots_sigil = True
            # G030: sigil-map must already be declared
            if not self.seen_sigil_map:
                raise ParseError("G030_SIGIL_MAP_REQUIRED",
                                 f"sigil {sigil} uses encoding:slots but $0:sigil-map not yet declared", line_no)
        # Contract
        contract: List[ContractField] = []
        if encoding == "slots":
            slots_v = amap.get("slots")
            if slots_v is None:
                raise ParseError("G033_SLOT_CONTRACT_REQUIRED",
                                 f"sigil {sigil} with encoding:slots missing slots", line_no)
            slots_str = slots_v.value if slots_v.kind == "string" else slots_v.lexeme
            # G040: fields/pos + slots exclusion
            if amap.get("fields") is not None or amap.get("pos") is not None:
                raise ParseError("G040_CONTRACT_SURFACE_CONFLICT",
                                 f"sigil {sigil} cannot have fields/pos + slots", line_no)
            slot_fields = parse_slot_contract(slots_str, line_no)
            validate_slot_contract(slot_fields, line_no)
            # Build ContractField with position
            contract = [ContractField0(name=f.name, type=f.type, required=f.required,
                                       position=f.position)
                        for f in slot_fields]
            # G038: open:true forbidden with slots
            if is_open:
                raise ParseError("G038_SLOTS_OPEN_FORBIDDEN",
                                 f"sigil {sigil} slots cannot be open", line_no)
        elif shape == "attrs":
            fields_v = amap.get("fields")
            if fields_v is None:
                raise ParseError("G021_ATTRS_CONTRACT_REQUIRED",
                                 f"sigil {sigil} missing fields", line_no)
            contract = parse_contract_fields(fields_v.value)
        elif shape in ("attrs-pos", "relacion"):
            pos_v = amap.get("pos")
            if pos_v is None:
                raise ParseError("G022_POSITIONAL_CONTRACT_REQUIRED",
                                 f"sigil {sigil} missing pos", line_no)
            contract = parse_contract_fields(pos_v.value)
            if shape == "relacion" and len(contract) < 3:
                raise ParseError("G023_RELATION_CONTRACT_TOO_SHORT",
                                 "relacion needs >=3 fields", line_no)
        # Focus
        focus_v = amap.get("focus")
        if focus_v is None:
            if shape in ("cuerpo", "bloque"):
                focus = "$body"
            else:
                raise ParseError("G024_FOCUS_REQUIRED",
                                 f"sigil {sigil} missing focus", line_no)
        else:
            focus = focus_v.value if focus_v.kind in ("atom", "string") else focus_v.lexeme
            if shape in ("attrs", "attrs-pos", "relacion"):
                focus_field = None
                for f in contract:
                    if f.name == focus:
                        focus_field = f
                        break
                if focus_field is None:
                    if encoding == "slots":
                        raise ParseError("G037_SLOT_FOCUS_UNRESOLVED",
                                         f"focus {focus!r} not in slot contract", line_no)
                    raise ParseError("G025_UNKNOWN_FOCUS_FIELD",
                                     f"focus {focus!r} not in contract", line_no)
                if encoding == "slots" and not focus_field.required:
                    raise ParseError("G037_SLOT_FOCUS_UNRESOLVED",
                                     f"focus {focus!r} must be a required slot", line_no)
        return SymbolDef0(namespace=ns, sigil=sigil, label=label, shape=shape,
                         weight=weight, focus=focus, desc=desc, open=is_open,
                         contract=contract, attrs=attrs, encoding=encoding, source_line=line_no)

    def _parse_idea_line_slots(self, line: str, section_id: int, line_no: int) -> Idea:
        line = line.strip()
        m = re.match(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^{|}\s]+)", line)
        if not m:
            raise ParseError("S003_INVALID_IDEA_HEAD",
                             f"Invalid idea head: {line!r}", line_no)
        ns = m.group(1)
        sigil = m.group(2)
        name = m.group(3)
        rest = line[m.end():]
        sym = None
        for s in self.doc.glossary.symbols:
            if s.sigil == sigil and s.namespace == ns:
                sym = s
                break
            if s.sigil == sigil and s.namespace is None and ns is None:
                sym = s
                break
        if sym is None:
            raise ParseError("I001_UNDECLARED_SYMBOL",
                             f"Undeclared sigil: {sigil}", line_no)
        # I006_DUPLICATE_IDEA_ADDRESS
        addr = f"${section_id}:{ns + '::' if ns else ''}{sigil}:{name}"
        if addr in self.seen_idea_addresses:
            raise ParseError("I006_DUPLICATE_IDEA_ADDRESS",
                             f"Duplicate idea address {addr}", line_no)
        self.seen_idea_addresses.add(addr)
        shape = sym.shape
        # Slot-encoded Idea
        if getattr(sym, "encoding", None) == "slots":
            if not rest.startswith("{"):
                raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                                 f"Expected {{ for slot-encoded Idea", line_no)
            if not (rest.endswith("}") and rest.count("\n") == 0):
                raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                                 f"Slot-encoded Idea must be single-line", line_no)
            entries = parse_slot_payload(rest, line_no)
            fvs = self._resolve_slot_entries(entries, sym, line_no)
            return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                        shape=shape, payload=("slots", fvs), source_line=line_no)
        # Standard surface (reuses 0.1 logic via _parse_idea_line_legacy)
        return self._parse_idea_line_legacy(line, section_id, line_no, ns, sigil, name, rest, sym)

    def _parse_idea_line_legacy(self, line: str, section_id: int, line_no: int,
                                    ns, sigil, name, rest, sym: SymbolDef) -> Idea:
        shape = sym.shape
        if shape in ("attrs", "cuerpo", "bloque"):
            if not rest.startswith("{"):
                raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                                 f"Expected {{ for shape {shape}", line_no)
            if rest.endswith("}") and rest.count("\n") == 0:
                payload_str = rest
                if shape == "attrs":
                    pairs = parse_attrs_payload(payload_str, line_no)
                    # Validate against contract (0.1 baseline-style)
                    self._validate_attrs_payload(pairs, sym, line_no)
                    return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                                shape=shape, payload=("attrs", pairs), source_line=line_no)
                else:
                    inner = rest[1:-1]
                    if shape == "cuerpo":
                        inner = to_nfc(inner)
                    return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                                shape=shape, payload=(shape, inner), source_line=line_no)
            else:
                if rest.strip() != "{":
                    raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                                     f"Expected single {{ for multiline {shape}", line_no)
                return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                            shape=shape, payload=("_multiline_body", None), source_line=line_no)
        elif shape in ("attrs-pos", "relacion"):
            if not rest.startswith("|"):
                raise ParseError("I004_SHAPE_DELIMITER_MISMATCH",
                                 f"Expected | for shape {shape}", line_no)
            rest = rest[1:]
            cells = self._parse_pipe_cells(rest, line_no)
            # Arity check
            required_count = sum(1 for f in sym.contract if f.required)
            if len(cells) < required_count:
                raise ParseError("I012_POSITIONAL_ARITY",
                                 f"shape {shape} needs ≥{required_count} cells, got {len(cells)}", line_no)
            if len(cells) > len(sym.contract):
                raise ParseError("I012_POSITIONAL_ARITY",
                                 f"shape {shape} expects ≤{len(sym.contract)} cells, got {len(cells)}", line_no)
            return Idea(section=section_id, namespace=ns, symbol=sigil, name=name,
                        shape=shape, payload=(shape, cells), source_line=line_no)
        raise ParseError("S999_INTERNAL_PARSE_FAILURE",
                         f"Cannot parse idea: {line!r}", line_no)

    def _validate_attrs_payload(self, pairs, sym: SymbolDef, line_no: int):
        """Post-parse validation of attrs nominal Ideas against contract."""
        pair_map = {}
        for k, v in pairs:
            if k in pair_map:
                raise ParseError("I006_DUPLICATE_FIELD",
                                 f"Duplicate field {k!r}", line_no)
            pair_map[k] = v
        # Unknown field check (if closed)
        if not sym.open:
            field_names = {f.name for f in sym.contract}
            for k in pair_map:
                if k not in field_names:
                    raise ParseError("I005_UNKNOWN_FIELD",
                                     f"Unknown field {k!r}", line_no)
        # Required check
        for f in sym.contract:
            if f.required and f.name not in pair_map:
                raise ParseError("I008_REQUIRED_FIELD_MISSING",
                                 f"Required field {f.name!r} missing", line_no)

    def _resolve_slot_entries(self, entries, sym: SymbolDef, line_no: int) -> List[FieldValue]:
        """Resolve (index, scalar, span) → FieldValue; validate order, duplicates, required."""
        seen = set()
        out: List[FieldValue] = []
        last_idx = 0
        for idx, scalar, span in entries:
            if idx in seen:
                raise ParseError("I051_DUPLICATE_SLOT",
                                 f"slot ※{idx} duplicated", line_no)
            seen.add(idx)
            if idx <= last_idx:
                raise ParseError("I054_SLOT_OUT_OF_ORDER",
                                 f"slots not in ascending order (※{idx} after ※{last_idx})", line_no)
            last_idx = idx
            cf = None
            for f in sym.contract:
                if f.position == idx:
                    cf = f
                    break
            if cf is None:
                raise ParseError("I052_UNKNOWN_SLOT",
                                 f"slot ※{idx} not declared in contract", line_no)
            out.append(FieldValue(position=idx, name=cf.name, type=cf.type,
                                  required=cf.required, value=scalar))
        # Required check
        for cf in sym.contract:
            if cf.required and cf.position not in seen:
                raise ParseError("I053_MISSING_REQUIRED_SLOT",
                                 f"missing required slot ※{cf.position} ({cf.name})", line_no)
        return out

    def _parse_pipe_cells(self, s: str, line_no: int) -> List[Scalar]:
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
                    raise ParseError("S006_INVALID_ATTRS",
                                     f"Expected | after quoted cell", line_no, i)
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
                cells.append(self._classify_raw_cell(raw_trimmed, line_no))
                i = j
                if i < n and s[i] == "|":
                    i += 1
                    continue
                else:
                    return cells
        return cells

    def _classify_raw_cell(self, raw: str, line_no: int) -> Scalar:
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

    def _post_validate(self):
        # G030/G041 final check
        if self.seen_any_slots_sigil and not self.seen_sigil_map:
            raise ParseError("G030_SIGIL_MAP_REQUIRED",
                             "0.2 uses slots but $0:sigil-map is missing")
        # S007_UNCLOSED_BODY
        if self.in_body:
            raise ParseError("S007_UNCLOSED_BODY",
                             f"Unclosed {self.body_kind} body at end of document")
