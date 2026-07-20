#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.2 canonicalizer + hash with domain separation.

NEW module: does NOT touch codec_cortex/c14n.py (0.1 preserved).
"""

import hashlib
import re
from typing import List, Tuple

from .scalars import (
    Scalar, emit_string_literal, to_nfc, utf8_bytes, ATOM_RE,
)
from .parser import Document, Section, Idea, SymbolDef, ContractField
from .slotparser import FieldValue, SigilMapDecl, GlossarySlots


HASH_DOMAIN_LEGACY = b"CORTEX-C14N-0.1"
HASH_DOMAIN_SLOTS = b"CORTEX-C14N-0.2"


# C14N 0.2 key orders
FORMAT_KEY_ORDER = ["cortex", "encoding", "language", "type"]
SIGIL_KEY_ORDER_SLOTS = ["type", "encoding", "weight", "slots", "focus", "schema", "desc", "open", "namespace", "version"]
SIGIL_MAP_KEY_ORDER = ["marker", "codepoint", "base", "syntax", "order"]
ENUM_KEY_ORDER = ["values"]
MICRO_KEY_ORDER = ["expand"]
NS_KEY_ORDER = ["id", "uri", "version", "required", "desc"]
EXT_KEY_ORDER = ["namespace", "id", "version", "required", "desc"]


def canonicalize_slots(doc: Document) -> str:
    """Apply C14N-0.2 canonicalisation."""
    _pre_normalize(doc)
    lines: List[str] = []
    if doc.glossary.capa:
        lines.append(f"$0:{doc.glossary.capa}")
    else:
        lines.append("$0")
    lines.append(_format_canonical(doc.glossary.format))
    # sigil-map second (if any slots-encoded sigil)
    any_slots = any(getattr(s, "encoding", None) == "slots" for s in doc.glossary.symbols)
    if any_slots and getattr(doc.glossary, "sigil_map", None) is not None:
        lines.append(_sigil_map_canonical(doc.glossary.sigil_map))
    for e in sorted(doc.glossary.enums, key=lambda x: utf8_bytes(to_nfc(x.name))):
        attrs_lookup = {"values": Scalar("string", "|".join(e.values), emit_string_literal("|".join(e.values)))}
        lines.append(_enum_canonical(e, attrs_lookup))
    for m in sorted(doc.glossary.micros, key=lambda x: utf8_bytes(to_nfc(x.token))):
        attrs_lookup = {"expand": Scalar("atom", m.expand, m.expand) if ATOM_RE.match(m.expand) else Scalar("string", m.expand, emit_string_literal(m.expand))}
        lines.append(_micro_canonical(m, attrs_lookup))
    for ns in sorted(doc.glossary.namespaces, key=lambda x: utf8_bytes(to_nfc(x.alias))):
        lines.append(_ns_canonical(ns, ns.attrs))
    for ext in sorted(doc.glossary.extensions, key=lambda x: utf8_bytes(to_nfc(x.name))):
        lines.append(_ext_canonical(ext, ext.attrs))
    for md in sorted(doc.glossary.meta, key=lambda x: utf8_bytes(to_nfc(x.name))):
        lines.append(_meta_canonical(md))
    def sym_sort_key(s):
        ns_key = to_nfc(s.namespace) if s.namespace else ""
        return (utf8_bytes(ns_key), utf8_bytes(to_nfc(s.sigil)), utf8_bytes(to_nfc(s.label)))
    for sym in sorted(doc.glossary.symbols, key=sym_sort_key):
        lines.append(_symbol_canonical_slots(sym))
    sym_lookup = {(s.namespace, s.sigil): s for s in doc.glossary.symbols}
    for sec in doc.sections:
        if sec.title is None:
            if sec.capa:
                lines.append(f"${sec.id}:{sec.capa}")
            else:
                lines.append(f"${sec.id}")
        else:
            title = sec.title.strip()
            if sec.capa:
                lines.append(f"${sec.id}: {title}:{sec.capa}")
            else:
                lines.append(f"${sec.id}: {title}")
        for idea in sec.ideas:
            key = (idea.namespace, idea.symbol)
            sym = sym_lookup.get(key) or sym_lookup.get((None, idea.symbol))
            lines.append(_idea_canonical_slots(idea, sym))
    return "\n".join(lines) + "\n"


def hash_slots(doc: Document) -> str:
    """SHA-256(CORTEX-C14N-0.2 || 0x00 || canonical_bytes)."""
    canon = canonicalize_slots(doc).encode("utf-8")
    return hashlib.sha256(HASH_DOMAIN_SLOTS + b"\x00" + canon).hexdigest()


def hash_legacy(doc: Document) -> str:
    """SHA-256(CORTEX-C14N-0.1 || 0x00 || canonical_bytes).

    Per directive P21, both 0.1 and 0.2 hash domains use the 0x00 separator.
    This is the historical 0.1 hash format (CORTEX-C14N-0.1 domain with 0x00 byte).
    """
    from .c14n import canonicalize as canonicalize_legacy
    canon = canonicalize_legacy(doc).encode("utf-8")
    return hashlib.sha256(HASH_DOMAIN_LEGACY + b"\x00" + canon).hexdigest()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pre_normalize(doc: Document):
    """Apply NFC to text values (except bloque), expand microtokens in slot atoms."""
    if doc.glossary.format:
        new_attrs = [(k, _nfc_scalar(v)) for k, v in doc.glossary.format.attrs]
        doc.glossary.format.attrs = new_attrs
    for e in doc.glossary.enums:
        e.values = [to_nfc(x) for x in e.values]
    for m in doc.glossary.micros:
        m.expand = to_nfc(m.expand)
    for ns in doc.glossary.namespaces:
        ns.attrs = [(k, _nfc_scalar(v)) for k, v in ns.attrs]
    for ext in doc.glossary.extensions:
        ext.attrs = [(k, _nfc_scalar(v)) for k, v in ext.attrs]
    for md in doc.glossary.meta:
        md.attrs = [(k, _nfc_scalar(v)) for k, v in md.attrs]
    for sym in doc.glossary.symbols:
        new_attrs = [(k, _nfc_scalar(v)) for k, v in sym.attrs]
        sym.attrs = new_attrs
        sym.desc = to_nfc(sym.desc)
    # Microtoken map
    micro_map = {m.token: m.expand for m in doc.glossary.micros}
    for sec in doc.sections:
        for idea in sec.ideas:
            if not idea.payload:
                continue
            kind = idea.payload[0]
            if kind == "attrs":
                pairs = idea.payload[1]
                new_pairs = [(k, _nfc_scalar(v)) for k, v in pairs]
                idea.payload = ("attrs", new_pairs)
            elif kind in ("attrs-pos", "relacion"):
                cells = idea.payload[1]
                new_cells = [_nfc_scalar(c) for c in cells]
                idea.payload = (kind, new_cells)
            elif kind == "slots":
                fvs = idea.payload[1]
                new_fvs = []
                for fv in fvs:
                    v = fv.value
                    if v.kind == "atom" and v.value in micro_map:
                        v = Scalar("atom", micro_map[v.value], micro_map[v.value])
                    new_fvs.append(FieldValue(fv.position, fv.name, fv.type, fv.required,
                                              _nfc_scalar(v), fv.source_span))
                idea.payload = ("slots", new_fvs)
            elif kind == "cuerpo":
                idea.payload = ("cuerpo", to_nfc(idea.payload[1]))
        if sec.title is not None:
            sec.title = to_nfc(sec.title)


def _nfc_scalar(s: Scalar) -> Scalar:
    if s.kind == "string":
        v = to_nfc(s.value)
        return Scalar("string", v, emit_string_literal(v))
    if s.kind == "atom":
        v = to_nfc(s.value)
        return Scalar("atom", v, v)
    if s.kind == "list":
        items = [_nfc_scalar(x) for x in s.value]
        lex = "[" + ",".join(it.lexeme for it in items) + "]"
        return Scalar("list", items, lex)
    return s


def _sort_keys_canonical(attrs, order):
    """Sort attrs (list of (key, Scalar) pairs OR dict) by canonical order."""
    if isinstance(attrs, dict):
        items = list(attrs.items())
    else:
        items = list(attrs)
    by_key = {k: v for k, v in items}
    out = []
    used = set()
    for k in order:
        if k in by_key:
            out.append((k, by_key[k]))
            used.add(k)
    extras = sorted(((k, v) for k, v in items if k not in used),
                    key=lambda kv: utf8_bytes(to_nfc(kv[0])))
    out.extend(extras)
    return out


def _is_atom_safe_bare(s: str) -> bool:
    if not s:
        return False
    if re.search(r"[\s\[\]{},""|]", s):
        return False
    return True


def _emit_scalar_attrs(v: Scalar, is_focus_text: bool, is_text_field: bool) -> str:
    if v.kind == "string":
        if is_focus_text:
            return v.lexeme
        elif is_text_field:
            if _is_atom_safe_bare(v.value) and ATOM_RE.match(v.value):
                return v.value
            return v.lexeme
        return v.lexeme
    elif v.kind == "atom":
        if _is_atom_safe_bare(v.value):
            return v.value
        return emit_string_literal(v.value)
    return v.lexeme


def _emit_glossary_attrs(attrs) -> str:
    out = []
    for k, v in attrs:
        out.append(f"{k}:{v.lexeme}")
    return "{" + ",".join(out) + "}"


def _format_canonical(format_decl) -> str:
    sorted_attrs = _sort_keys_canonical(format_decl.attrs, FORMAT_KEY_ORDER)
    return "$0:format" + _emit_glossary_attrs(sorted_attrs)


def _enum_canonical(e, attrs_lookup) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, ENUM_KEY_ORDER)
    return f"$0:enum_{e.name}" + _emit_glossary_attrs(sorted_attrs)


def _micro_canonical(m, attrs_lookup) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, MICRO_KEY_ORDER)
    return f"$0:micro_{m.token}" + _emit_glossary_attrs(sorted_attrs)


def _ns_canonical(ns, attrs_lookup) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, NS_KEY_ORDER)
    return f"$0:namespace_{ns.alias}" + _emit_glossary_attrs(sorted_attrs)


def _ext_canonical(e, attrs_lookup) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, EXT_KEY_ORDER)
    return f"$0:extension_{e.name}" + _emit_glossary_attrs(sorted_attrs)


def _meta_canonical(m) -> str:
    sorted_attrs = sorted(m.attrs, key=lambda kv: utf8_bytes(to_nfc(kv[0])))
    base = f"$0:{m.name}" + _emit_glossary_attrs(sorted_attrs)
    if m.capa:
        base += f":{m.capa}"
    return base


def _sigil_map_canonical(sm: SigilMapDecl) -> str:
    attrs = [
        ("marker", Scalar("string", sm.marker, emit_string_literal(sm.marker))),
        ("codepoint", Scalar("string", sm.codepoint, emit_string_literal(sm.codepoint))),
        ("base", Scalar("integer", str(sm.base), str(sm.base))),
        ("syntax", Scalar("string", sm.syntax, emit_string_literal(sm.syntax))),
        ("order", Scalar("string", sm.order, emit_string_literal(sm.order))),
    ]
    sorted_attrs = _sort_keys_canonical(attrs, SIGIL_MAP_KEY_ORDER)
    return "$0:sigil-map" + _emit_glossary_attrs(sorted_attrs)


def _symbol_canonical_slots(s: SymbolDef) -> str:
    sorted_attrs = _sort_keys_canonical(s.attrs, SIGIL_KEY_ORDER_SLOTS)
    qualified = f"{s.namespace}::{s.sigil}" if s.namespace else s.sigil
    return f"{qualified}:{s.label}" + _emit_glossary_attrs(sorted_attrs)


def _idea_canonical_slots(idea: Idea, sym: SymbolDef) -> str:
    qualified = f"{idea.namespace}::{idea.symbol}" if idea.namespace else idea.symbol
    head = f"{qualified}:{idea.name}"
    if idea.payload and idea.payload[0] == "slots":
        fvs: List[FieldValue] = idea.payload[1]
        # Build position→type map
        field_types = {f.position: f.type for f in sym.contract}
        focus_pos = None
        for f in sym.contract:
            if f.name == sym.focus:
                focus_pos = f.position
                break
        parts = []
        # fvs is already in ascending order (parser enforced)
        for fv in fvs:
            ftype = field_types.get(fv.position, "any")
            is_text = (ftype == "text")
            is_focus_text = (fv.position == focus_pos and ftype == "text")
            val_str = _emit_scalar_attrs(fv.value, is_focus_text, is_text)
            parts.append(f"※{fv.position}:{val_str}")
        return head + "{" + ",".join(parts) + "}"
    # 0.1 surface (attrs / attrs-pos / relacion / cuerpo / bloque) — delegate to 0.1 emit
    # Inline simple version for safety
    if idea.payload and idea.shape == "attrs":
        pairs = idea.payload[1]
        field_types = {f.name: f.type for f in sym.contract}
        focus = sym.focus
        parts = []
        for k, v in pairs:
            ftype = field_types.get(k, "any")
            is_text = (ftype == "text")
            is_focus_text = (k == focus and ftype == "text")
            parts.append(f"{k}:{_emit_scalar_attrs(v, is_focus_text, is_text)}")
        return head + "{" + ",".join(parts) + "}"
    elif idea.payload and idea.shape in ("attrs-pos", "relacion"):
        cells = idea.payload[1]
        parts = [c.lexeme for c in cells]
        return head + "|" + "|".join(parts)
    elif idea.payload and idea.shape == "cuerpo":
        text = to_nfc(idea.payload[1])
        if "\n" in text:
            return head + "{\n" + text + "\n}"
        return head + "{" + text + "}"
    elif idea.payload and idea.shape == "bloque":
        text = idea.payload[1]
        return head + "{\n" + text + "\n}"
    return head
