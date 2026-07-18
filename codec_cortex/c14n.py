#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C14N-0.1 canonicalizer.
Section 5 of the independent reviewer's implementation.
"""

import re
from typing import List, Tuple

from .scalars import (
    Scalar, emit_string_literal, to_nfc, utf8_bytes, ATOM_RE,
)
from .parser import Document, Section, Idea, SymbolDef


# ---------------------------------------------------------------------------
# 6. C14N canonicalizer
# ---------------------------------------------------------------------------

# C14N key orders
FORMAT_KEY_ORDER = ["cortex", "encoding", "language"]
SIGIL_KEY_ORDER = ["type", "weight", "fields", "pos", "focus", "desc", "open", "namespace", "version"]
ENUM_KEY_ORDER = ["values"]
MICRO_KEY_ORDER = ["expand"]
NS_KEY_ORDER = ["id", "uri", "version", "required", "desc"]
EXT_KEY_ORDER = ["namespace", "id", "version", "required", "desc"]


def _sort_keys_canonical(attrs, order: List[str]) -> List[Tuple[str, Scalar]]:
    """Sort attrs: known keys in `order`, then extras by key UTF-8 NFC."""
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
    extras = sorted(((k, v) for k, v in items if k not in used), key=lambda kv: utf8_bytes(to_nfc(kv[0])))
    out.extend(extras)
    return out


def _nfc_scalar(s: Scalar) -> Scalar:
    """Return a new Scalar with NFC-normalized value/lexeme (for non-bloque contexts)."""
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


def _expand_microtokens(doc: Document):
    """Expand microtoken atoms in idea payloads (not keys, not strings, not names)."""
    if not doc.glossary.micros:
        return
    micro_map = {m.token: m.expand for m in doc.glossary.micros}
    for sec in doc.sections:
        for idea in sec.ideas:
            if idea.shape == "attrs":
                pairs = idea.payload[1]
                new_pairs = []
                for k, v in pairs:
                    if v.kind == "atom" and v.value in micro_map:
                        expanded = micro_map[v.value]
                        v = Scalar("atom", expanded, expanded)
                    new_pairs.append((k, v))
                idea.payload = ("attrs", new_pairs)
            elif idea.shape in ("attrs-pos", "relacion"):
                cells = idea.payload[1]
                new_cells = []
                for c in cells:
                    if c.kind == "atom" and c.value in micro_map:
                        expanded = micro_map[c.value]
                        c = Scalar("atom", expanded, expanded)
                    new_cells.append(c)
                idea.payload = (idea.shape, new_cells)


def _is_atom_safe_bare(s: str) -> bool:
    """Check if an atom value can be emitted bare (no whitespace, no structural delimiters)."""
    if not s:
        return False
    if re.search(r"[\s\[\]{},""|]", s):
        return False
    return True


def _is_text_safe_bare(s: str) -> bool:
    """Check if a text value can be emitted bare in attrs-pos cell."""
    if not s:
        return False
    if "\n" in s or "\r" in s:
        return False
    if "|" in s:
        return False
    if s != s.strip():
        return False
    if s.startswith('"'):
        return False
    return True


def _emit_scalar_attrs(v: Scalar, is_focus_text: bool, is_text_field: bool) -> str:
    """Emit a scalar for an attrs field, applying I7 quoting rules."""
    if v.kind == "string":
        if is_focus_text:
            return v.lexeme
        elif is_text_field:
            if _is_atom_safe_bare(v.value) and ATOM_RE.match(v.value):
                return v.value
            return v.lexeme
        else:
            return v.lexeme
    elif v.kind == "atom":
        if _is_atom_safe_bare(v.value):
            return v.value
        return emit_string_literal(v.value)
    elif v.kind == "integer":
        return v.lexeme
    elif v.kind == "decimal":
        return v.lexeme
    elif v.kind == "boolean":
        return v.lexeme
    elif v.kind == "null":
        return v.lexeme
    elif v.kind == "list":
        return v.lexeme
    return v.lexeme


def _emit_scalar_positional(v: Scalar, is_text_field: bool) -> str:
    """Emit a scalar for an attrs-pos/relacion cell."""
    if v.kind == "string":
        if is_text_field:
            if _is_text_safe_bare(v.value):
                return v.value
            return v.lexeme
        else:
            return v.lexeme
    elif v.kind == "atom":
        if _is_atom_safe_bare(v.value):
            return v.value
        return emit_string_literal(v.value)
    elif v.kind in ("integer", "decimal", "boolean", "null"):
        return v.lexeme
    elif v.kind == "list":
        return v.lexeme
    return v.lexeme


def _emit_glossary_attrs(attrs: List[Tuple[str, Scalar]]) -> str:
    """Emit attrs for a glossary declaration (always literal lexemes, no I7 shortening)."""
    out = []
    for k, v in attrs:
        out.append(f"{k}:{v.lexeme}")
    return "{" + ",".join(out) + "}"


def _emit_meta_attrs(attrs: List[Tuple[str, Scalar]]) -> str:
    """Emit attrs for a meta-declaration."""
    return _emit_glossary_attrs(attrs)


def _format_canonical(format_decl) -> str:
    """Canonical $0:format declaration."""
    sorted_attrs = _sort_keys_canonical(format_decl.attrs, FORMAT_KEY_ORDER)
    return "$0:format" + _emit_glossary_attrs(sorted_attrs)


def _enum_canonical(e, attrs_lookup: dict) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, ENUM_KEY_ORDER)
    return f"$0:enum_{e.name}" + _emit_glossary_attrs(sorted_attrs)


def _micro_canonical(m, attrs_lookup: dict) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, MICRO_KEY_ORDER)
    return f"$0:micro_{m.token}" + _emit_glossary_attrs(sorted_attrs)


def _ns_canonical(ns, attrs_lookup: dict) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, NS_KEY_ORDER)
    return f"$0:namespace_{ns.alias}" + _emit_glossary_attrs(sorted_attrs)


def _ext_canonical(e, attrs_lookup: dict) -> str:
    sorted_attrs = _sort_keys_canonical(attrs_lookup, EXT_KEY_ORDER)
    return f"$0:extension_{e.name}" + _emit_glossary_attrs(sorted_attrs)


def _symbol_canonical(s: SymbolDef) -> str:
    """Canonical sigil declaration."""
    sorted_attrs = _sort_keys_canonical(s.attrs, SIGIL_KEY_ORDER)
    qualified = f"{s.namespace}::{s.sigil}" if s.namespace else s.sigil
    return f"{qualified}:{s.label}" + _emit_glossary_attrs(sorted_attrs)


def _meta_canonical(m) -> str:
    """Canonical other meta-declaration."""
    sorted_attrs = sorted(m.attrs, key=lambda kv: utf8_bytes(to_nfc(kv[0])))
    base = f"$0:{m.name}" + _emit_meta_attrs(sorted_attrs)
    if m.capa:
        base += f":{m.capa}"
    return base


def _idea_canonical(idea: Idea, sym: SymbolDef) -> str:
    """Canonical idea line."""
    qualified = f"{idea.namespace}::{idea.symbol}" if idea.namespace else idea.symbol
    head = f"{qualified}:{idea.name}"
    if idea.shape == "attrs":
        pairs = idea.payload[1]
        field_order = [f.name for f in sym.contract]
        pair_map = {}
        for k, v in pairs:
            pair_map[k] = v
        out_pairs: List[Tuple[str, Scalar]] = []
        used = set()
        for fname in field_order:
            if fname in pair_map:
                out_pairs.append((fname, pair_map[fname]))
                used.add(fname)
        if sym.open:
            extras = sorted(((k, v) for k, v in pairs if k not in used),
                            key=lambda kv: utf8_bytes(to_nfc(kv[0])))
            out_pairs.extend(extras)
        field_types = {f.name: f.type for f in sym.contract}
        focus = sym.focus
        parts = []
        for k, v in out_pairs:
            ftype = field_types.get(k, "any")
            is_text = ftype == "text"
            is_focus_text = (k == focus and ftype == "text")
            parts.append(f"{k}:{_emit_scalar_attrs(v, is_focus_text, is_text)}")
        return head + "{" + ",".join(parts) + "}"
    elif idea.shape in ("attrs-pos", "relacion"):
        cells = idea.payload[1]
        field_types = [f.type for f in sym.contract]
        parts = []
        for idx, c in enumerate(cells):
            ftype = field_types[idx] if idx < len(field_types) else "any"
            is_text = (ftype == "text")
            parts.append(_emit_scalar_positional(c, is_text))
        return head + "|" + "|".join(parts)
    elif idea.shape == "cuerpo":
        text = idea.payload[1]
        text = to_nfc(text)
        if "\n" in text:
            return head + "{\n" + text + "\n}"
        else:
            return head + "{" + text + "}"
    elif idea.shape == "bloque":
        text = idea.payload[1]
        return head + "{\n" + text + "\n}"
    return head


def canonicalize(doc: Document) -> str:
    """Apply C14N-0.1 canonicalization. Returns the canonical string (UTF-8, LF, single final LF)."""
    # 1. NFC all text values (except in bloque), expand microtokens
    if doc.glossary.format:
        new_attrs = []
        for k, v in doc.glossary.format.attrs:
            new_attrs.append((k, _nfc_scalar(v)))
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
        new_attrs = []
        for k, v in sym.attrs:
            new_attrs.append((k, _nfc_scalar(v)))
        sym.attrs = new_attrs
        sym.desc = to_nfc(sym.desc)
    for sec in doc.sections:
        for idea in sec.ideas:
            if idea.shape == "attrs":
                pairs = idea.payload[1]
                new_pairs = []
                for k, v in pairs:
                    new_pairs.append((k, _nfc_scalar(v)))
                idea.payload = ("attrs", new_pairs)
            elif idea.shape in ("attrs-pos", "relacion"):
                cells = idea.payload[1]
                new_cells = [_nfc_scalar(c) for c in cells]
                idea.payload = (idea.shape, new_cells)
            elif idea.shape == "cuerpo":
                idea.payload = ("cuerpo", to_nfc(idea.payload[1]))
        if sec.title is not None:
            sec.title = to_nfc(sec.title)

    # 2. Expand microtokens in idea atoms
    _expand_microtokens(doc)

    # 3. Build the canonical output
    lines: List[str] = []
    if doc.glossary.capa:
        lines.append(f"$0:{doc.glossary.capa}")
    else:
        lines.append("$0")
    # format first
    lines.append(_format_canonical(doc.glossary.format))
    # enums by name UTF-8 NFC
    for e in sorted(doc.glossary.enums, key=lambda x: utf8_bytes(to_nfc(x.name))):
        attrs_lookup = {"values": Scalar("string", "|".join(e.values), emit_string_literal("|".join(e.values)))}
        lines.append(_enum_canonical(e, attrs_lookup))
    # micros by token
    for m in sorted(doc.glossary.micros, key=lambda x: utf8_bytes(to_nfc(x.token))):
        attrs_lookup = {"expand": Scalar("atom", m.expand, m.expand) if ATOM_RE.match(m.expand) else Scalar("string", m.expand, emit_string_literal(m.expand))}
        lines.append(_micro_canonical(m, attrs_lookup))
    # namespaces by alias
    for ns in sorted(doc.glossary.namespaces, key=lambda x: utf8_bytes(to_nfc(x.alias))):
        lines.append(_ns_canonical(ns, {k: v for k, v in ns.attrs}))
    # extensions by name
    for ext in sorted(doc.glossary.extensions, key=lambda x: utf8_bytes(to_nfc(x.name))):
        lines.append(_ext_canonical(ext, {k: v for k, v in ext.attrs}))
    # other meta-declarations by name
    for md in sorted(doc.glossary.meta, key=lambda x: utf8_bytes(to_nfc(x.name))):
        lines.append(_meta_canonical(md))
    # sigil declarations by qualified identity
    def sym_sort_key(s: SymbolDef):
        ns_key = to_nfc(s.namespace) if s.namespace else ""
        return (utf8_bytes(ns_key), utf8_bytes(to_nfc(s.sigil)), utf8_bytes(to_nfc(s.label)))
    for sym in sorted(doc.glossary.symbols, key=sym_sort_key):
        lines.append(_symbol_canonical(sym))

    # 4. Sections in source order
    sym_lookup = {}
    for s in doc.glossary.symbols:
        key = (s.namespace, s.sigil)
        sym_lookup[key] = s
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
            sym = sym_lookup.get(key)
            if sym is None:
                sym = sym_lookup.get((None, idea.symbol))
            lines.append(_idea_canonical(idea, sym))

    return "\n".join(lines) + "\n"
