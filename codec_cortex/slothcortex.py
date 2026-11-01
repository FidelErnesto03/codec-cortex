#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HCORTEX 0.2 renderer + compiler for slots surface (slots surface).

Spec: docs/standard/hcortex-slots.md

Naming:
    hcortex.py       — HCORTEX 0.1 (legacy surface, pre-slots)
    slothcortex.py   — HCORTEX 0.2 (slots surface)

render_hcortex_slots(doc, embed_ast=False) -> str
    embed_ast=True injects <!-- cortex-ast: HASH --> for provenance.

compile_hcortex_slots(text) -> (Document | None, diagnostics)
    Detects hidden CORTEX/AST copies via HIDDEN_COPY_RE → H481.

Envelope:  <!-- HCORTEX v=0.2 t=canonical k=corpus -->
Glossary:  <!-- glossary -->\n...\n<!-- /glossary -->
Sections:  ## §N: Title\n\n<!-- schema:N -->\n...\n<!-- /schema:N -->

Roundtrip: canonicalize(compile(render(D))) == canonicalize(D)
"""

import re
from typing import Any, List, Tuple, Optional

from .scalars import (
    Scalar, emit_string_literal, to_nfc, ATOM_RE, _INT_RE, _DEC_RE,
)
from .slots import FieldValue
from .parser import Document, Section, Idea, SymbolDef
from .dispatcher import parse_cortex, canonicalize, hash_cortex


ENVELOPE_RE = re.compile(r'<!--\s*HCORTEX\s+v=([0-9.]+)\s+t=(\w+)(?:\s+k=(\w+))?\s*-->')
GLOSSARY_RE = re.compile(r'<!--\s*glossary\s*-->\n(.*?)\n<!--\s*/glossary\s*-->', re.DOTALL)
HIDDEN_COPY_RE = re.compile(
    r'<!--\s*(cortex-ast:|base64:|payload-shadow:|shadow:|ast:|internal:)'
)
_SECTION_HEADING_RE = re.compile(r"^##\s*§(\d+):\s*(.*?)\s*$")
_SCHEMA_OPEN_RE = re.compile(r"^<!--\s*schema:(\d+)(?:\s+capa:(\w+))?\s*-->$")
_SCHEMA_CLOSE_RE = re.compile(r"^<!--\s*/schema:\d+\s*-->$")


def render_hcortex_slots(doc: Document, embed_ast: bool = False) -> str:
    from .dispatcher import hash_cortex
    out: List[str] = []
    out.append("<!-- HCORTEX v=0.2 t=canonical k=corpus -->")
    if embed_ast:
        h = hash_cortex(doc)
        out.append(f"<!-- cortex-ast: {h} -->")
    out.append("")
    out.append("<!-- glossary -->")
    out.append(_render_glossary_slots(doc))
    out.append("<!-- /glossary -->")
    out.append("")
    sym_lookup = {}
    for s in doc.glossary.symbols:
        key = (s.namespace, s.sigil)
        sym_lookup[key] = s
    for sec in doc.sections:
        title = sec.title or f"Sección {sec.id}"
        out.append(f"## §{sec.id}: {title}")
        out.append("")
        capa_attr = f" capa:{sec.capa}" if sec.capa else ""
        out.append(f"<!-- schema:{sec.id}{capa_attr} -->")
        for idea in sec.ideas:
            key = (idea.namespace, idea.symbol)
            sym = sym_lookup.get(key) or sym_lookup.get((None, idea.symbol))
            out.extend(_render_idea_slots(idea, sym))
            out.append("")
        out.append(f"<!-- /schema:{sec.id} -->")
        out.append("")
    return "\n".join(out) + "\n"


def compile_hcortex_slots(text: str) -> Tuple[Optional[Document], List[dict]]:
    diags: List[dict] = []

    if text.startswith("\ufeff"):
        diags.append({"code": "H490", "message": "BOM forbidden"})
        return None, diags
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if HIDDEN_COPY_RE.search(text):
        diags.append({"code": "H481_HIDDEN_COPY",
                      "message": "HCORTEX contains hidden CORTEX/AST copy"})
        return None, diags

    vm = ENVELOPE_RE.search(text)
    if not vm:
        diags.append({"code": "H401_MISSING_ENVELOPE",
                      "message": "Missing or malformed HCORTEX envelope"})
        return None, diags
    if vm.group(1) != "0.2":
        diags.append({"code": "H401_UNSUPPORTED_HCORTEX_VERSION",
                      "message": f"Unsupported HCORTEX version: {vm.group(1)}"})
        return None, diags

    gm = GLOSSARY_RE.search(text)
    if not gm:
        diags.append({"code": "H403_MISSING_GLOSSARY_BLOCK",
                      "message": "Missing glossary block"})
        return None, diags

    glossary_src = gm.group(1).strip()
    combined = glossary_src + "\n"
    try:
        doc = parse_cortex(combined)
    except Exception as e:
        code = getattr(e, "code", "S999")
        diags.append({"code": code, "message": f"Glossary parse failed: {e}"})
        return None, diags

    doc.cortex_version = "0.2"

    sym_lookup = {}
    for s in doc.glossary.symbols:
        key = (s.namespace, s.sigil)
        sym_lookup[key] = s

    for sec_id, sec_title_raw, capa, body in _iter_sections(text):
        title = None if sec_title_raw == f"Sección {sec_id}" else sec_title_raw
        section = Section(id=sec_id, title=title, ideas=[], capa=capa)
        doc.sections.append(section)

        if not body.strip():
            continue

        ideas = _parse_schema_ideas(body, sym_lookup, sec_id, diags)
        section.ideas.extend(ideas)

    return doc, diags


def _iter_sections(text: str):
    """Yield (id, title, capa, body) for sections outside fenced blocks."""
    lines = text.split("\n")
    fenced = _fence_mask(lines)
    i = 0
    while i < len(lines):
        m = None if fenced[i] else _SECTION_HEADING_RE.match(lines[i])
        if m and i + 2 < len(lines) and lines[i + 1].strip() == "":
            sm = _SCHEMA_OPEN_RE.match(lines[i + 2])
            if sm:
                j = i + 3
                while j < len(lines):
                    if not fenced[j] and _SCHEMA_CLOSE_RE.match(lines[j]):
                        break
                    j += 1
                if j < len(lines):
                    yield (int(m.group(1)), m.group(2).strip(),
                           sm.group(2), "\n".join(lines[i + 3:j]))
                    i = j + 1
                    continue
        i += 1


def _render_glossary_slots(doc: Document) -> str:
    lines: List[str] = []
    gl = doc.glossary
    if getattr(gl, "capa", None):
        lines.append(f"$0:{gl.capa}")
    if gl.format:
        parts = [f"{k}:{v.lexeme}" for k, v in gl.format.attrs]
        lines.append("$0:format{" + ",".join(parts) + "}")
    for e in gl.enums:
        vals = e.values
        vals_str = "|".join(vals)
        lines.append(f'$0:enum_{e.name}{{values:"{vals_str}"}}')
    for m in gl.micros:
        expand_lex = m.expand
        if expand_lex.startswith('"') and expand_lex.endswith('"'):
            expand_lex = expand_lex[1:-1]
        if " " in expand_lex or not expand_lex:
            lines.append(f'$0:micro_{m.token}{{expand:"{expand_lex}"}}')
        else:
            lines.append(f'$0:micro_{m.token}{{expand:{expand_lex}}}')
    for ns in gl.namespaces:
        parts = [f"{k}:{v.lexeme}" for k, v in ns.attrs]
        lines.append(f"$0:namespace_{ns.alias}{{{','.join(parts)}}}")
    for ext in gl.extensions:
        parts = [f"{k}:{v.lexeme}" for k, v in ext.attrs]
        lines.append(f"$0:extension_{ext.name}{{{','.join(parts)}}}")
    for md in gl.meta:
        parts = [f"{k}:{v.lexeme}" for k, v in md.attrs]
        line = f"$0:{md.name}{{{','.join(parts)}}}"
        if md.capa:
            line += f":{md.capa}"
        lines.append(line)
    sm = getattr(gl, "sigil_map", None)
    if sm and any(getattr(s, "encoding", None) == "slots" for s in gl.symbols):
        cp = sm.codepoint.lstrip("U+").zfill(4)
        lines.append(
            '$0:sigil-map{marker:"%s",codepoint:"U+%s",base:%s,syntax:"%s",order:"%s"}'
            % (sm.marker, cp, sm.base, sm.syntax, sm.order)
        )
    for s in gl.symbols:
        qualified = f"{s.namespace}::{s.sigil}" if s.namespace else s.sigil
        attrs_parts = []
        seen_keys = set()
        for k, v in s.attrs:
            if k == "contract":
                continue
            if k in seen_keys:
                continue
            seen_keys.add(k)
            attrs_parts.append(f"{k}:{v.lexeme}")
        if any(k == "open" for k, _ in s.attrs):
            open_val = next(v.lexeme for k, v in s.attrs if k == "open")
            if "open" not in seen_keys:
                attrs_parts.append(f'open:{open_val}')
        lines.append(f"{qualified}:{s.label}{{{','.join(attrs_parts)}}}")
    return "\n".join(lines) + "\n"


def _render_idea_slots(idea: Idea, sym: Optional[SymbolDef]) -> List[str]:
    out: List[str] = []
    qualified = f"{idea.namespace}::{idea.symbol}" if idea.namespace else idea.symbol
    shape = idea.shape
    encoding = getattr(sym, "encoding", None) if sym else None
    is_slots = encoding == "slots"

    out.append(f"### {qualified}:{idea.name}")

    if shape == "slots" or (idea.payload and idea.payload[0] == "slots"):
        fvs: List[FieldValue] = idea.payload[1]
        headers = [f.name for f in sym.contract]
        out.append("| " + " | ".join(headers) + " |")
        out.append("|" + "|".join("---" for _ in headers) + "|")
        row = []
        for f in sym.contract:
            fv = next((x for x in fvs if x.position == f.position), None)
            row.append(_render_scalar(fv.value) if fv else "")
        out.append("| " + " | ".join(row) + " |")
    elif shape == "attrs" and idea.payload and idea.payload[0] == "attrs":
        pairs = idea.payload[1]
        pair_map = {k: v for k, v in pairs}
        if is_slots and sym:
            headers = [f.name for f in sym.contract]
        else:
            headers = [k for k, _ in pairs]
        out.append("| " + " | ".join(headers) + " |")
        out.append("|" + "|".join("---" for _ in headers) + "|")
        if is_slots and sym:
            row = []
            for f in sym.contract:
                v = pair_map.get(f.name)
                row.append(_render_scalar(v) if v else "")
        else:
            row = [_render_scalar(v) for _, v in pairs]
        out.append("| " + " | ".join(row) + " |")
    elif shape in ("attrs-pos", "relacion") and idea.payload:
        cells = idea.payload[1]
        if is_slots and sym:
            headers = [f.name for f in sym.contract]
        else:
            headers = [getattr(sym.contract[idx], "name", f"c{idx+1}")
                       for idx in range(len(cells))] if sym else []
        out.append("| " + " | ".join(headers) + " |")
        out.append("|" + "|".join("---" for _ in headers) + "|")
        row = [_render_scalar(c) for c in cells]
        out.append("| " + " | ".join(row) + " |")
    elif shape == "cuerpo" and idea.payload:
        out.append(idea.payload[1])
    elif shape == "bloque" and idea.payload:
        out.append("```")
        out.append(idea.payload[1])
        out.append("```")

    return out


def _render_scalar(v: Optional[Scalar]) -> str:
    if v is None:
        return ""
    return v.lexeme


_IDEA_MARKER_RE = re.compile(r"^### ([!]?(?:\w+::)?[!\w]+):([\w_-]+)\s*$")


def _fence_mask(lines: List[str]) -> List[bool]:
    """Mark complete ``` fence spans so their content is never read as ideas."""
    mask = [False] * len(lines)
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            if j < len(lines):
                for k in range(i, j + 1):
                    mask[k] = True
                i = j + 1
                continue
        i += 1
    return mask


def _parse_schema_ideas(body: str, sym_lookup: dict,
                        section_id: int, diags: List[dict]) -> List[Idea]:
    ideas: List[Idea] = []
    lines = body.split("\n")
    fenced = _fence_mask(lines)
    markers = []
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        m = _IDEA_MARKER_RE.match(line)
        if m:
            markers.append((i, m.group(1), m.group(2)))
    for idx, (start, qualified, name) in enumerate(markers):
        end = markers[idx + 1][0] if idx + 1 < len(markers) else len(lines)
        rest = "\n".join(lines[start + 1:end]).strip()

        ns = None
        sigil_short = qualified
        if "::" in qualified:
            parts = qualified.split("::")
            ns = parts[0]
            sigil_short = parts[1]

        sym = sym_lookup.get((ns, sigil_short)) or sym_lookup.get((None, sigil_short))
        shape = sym.shape if sym else "attrs"
        encoding = getattr(sym, "encoding", None) if sym else None
        is_slots = encoding == "slots"

        rows = _parse_table_rows(rest)
        if rows and not (sym and sym.shape in ("bloque", "cuerpo")):
            if is_slots and sym:
                fvs = []
                for f in sym.contract:
                    col_val = rows[0].get(f.name, "")
                    if col_val:
                        sv = _make_scalar(col_val)
                        fvs.append(FieldValue(
                            position=f.position, name=f.name,
                            type=f.type, required=f.required,
                            value=sv,
                        ))
                    elif not f.required:
                        pass
                if fvs:
                    ideas.append(Idea(section=section_id, namespace=ns,
                                      symbol=sigil_short, name=name,
                                      shape="attrs", payload=("slots", fvs)))
            elif sym and sym.shape == "cuerpo":
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape="cuerpo", payload=("cuerpo", rest)))
            elif sym and sym.shape == "bloque":
                body_text = rest
                bc = re.search(r"```\s*\n(.*?)```", rest, re.DOTALL)
                if bc:
                    body_text = bc.group(1).strip()
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape="bloque", payload=("bloque", body_text)))
            elif sym and shape in ("attrs-pos", "relacion"):
                cells = []
                for f in sym.contract:
                    val = rows[0].get(f.name, "")
                    if val == "" and not f.required:
                        break
                    cells.append(_make_scalar(val))
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape=shape, payload=(shape, cells)))
            else:
                pairs = []
                contract_map = {}
                if sym:
                    for f in sym.contract:
                        contract_map[f.name] = f.type
                for hdr in rows[0]:
                    val = rows[0][hdr]
                    pairs.append((hdr, _make_scalar(val)))
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape="attrs", payload=("attrs", pairs)))
        else:
            if sym and sym.shape == "cuerpo":
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape="cuerpo", payload=("cuerpo", rest)))
            elif sym and sym.shape == "bloque":
                body_text = rest
                bc = re.search(r"```\s*\n(.*?)```", rest, re.DOTALL)
                if bc:
                    body_text = bc.group(1).strip()
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape="bloque", payload=("bloque", body_text)))
            else:
                ideas.append(Idea(section=section_id, namespace=ns,
                                  symbol=sigil_short, name=name,
                                  shape=shape, payload=("attrs", [])))

    return ideas


def _split_table_row(line: str) -> List[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    cells: List[str] = []
    buf: List[str] = []
    in_quotes = False
    escaped = False
    for ch in s:
        if escaped:
            buf.append(ch)
            escaped = False
        elif ch == "\\" and in_quotes:
            buf.append(ch)
            escaped = True
        elif ch == '"':
            in_quotes = not in_quotes
            buf.append(ch)
        elif ch == "|" and not in_quotes:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    cells.append("".join(buf).strip())
    return cells


def _parse_table_rows(text: str) -> List[dict]:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    table = [ln for ln in lines if ln.startswith("|") and ln.endswith("|")]
    if len(table) < 2:
        return []
    headers = _split_table_row(table[0])
    data = None
    for ln in table[1:]:
        cells = _split_table_row(ln)
        if all(c == "" or set(c) <= {"-", ":"} for c in cells):
            continue
        data = cells
        break
    if data is None:
        return []
    return [dict(zip(headers, data))]


def _unescape(inner: str) -> str:
    out = []
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == "\\" and i + 1 < len(inner):
            nxt = inner[i + 1]
            mapping = {'"': '"', "\\": "\\", "n": "\n", "t": "\t", "r": "\r"}
            out.append(mapping.get(nxt, "\\" + nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _make_scalar(lex: str) -> Scalar:
    lex = lex.strip()
    if lex == "":
        return Scalar("null", None, "null")
    if lex.startswith('"') and lex.endswith('"'):
        inner = _unescape(lex[1:-1])
        return Scalar("string", inner, emit_string_literal(inner))
    if lex in ("true", "false"):
        return Scalar("boolean", lex == "true", lex)
    if lex == "null":
        return Scalar("null", None, "null")
    if lex.startswith("[") and lex.endswith("]"):
        inner = lex[1:-1]
        if not inner.strip():
            return Scalar("list", [], "[]")
        parts = [p.strip() for p in inner.split(",")]
        items = [_make_scalar(p) for p in parts]
        lx = "[" + ",".join(it.lexeme for it in items) + "]"
        return Scalar("list", items, lx)
    if _INT_RE.match(lex):
        v = lex if lex != "-0" else "0"
        return Scalar("integer", v, v)
    if _DEC_RE.match(lex):
        return Scalar("decimal", lex, lex)
    if ATOM_RE.match(lex) and " " not in lex:
        return Scalar("atom", lex, lex)
    return Scalar("string", lex, emit_string_literal(lex))


def run_roundtrip(valid_dir: str) -> dict:
    import os
    from .dispatcher import parse_cortex, canonicalize

    paths = sorted(os.listdir(valid_dir))
    results = []
    passed = 0
    failed = 0
    for fn in paths:
        if not fn.endswith(".cortex"):
            continue
        path = os.path.join(valid_dir, fn)
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        try:
            doc = parse_cortex(source)
            if doc.cortex_version != "0.2":
                continue
            expected_canon = canonicalize(doc)
            hc = render_hcortex_slots(doc)
            doc2, diags = compile_hcortex_slots(hc)
            if diags:
                failed += 1
                results.append({"case": fn, "status": "fail",
                                "detail": f"compile diagnostics: {diags}"})
                continue
            roundtrip_canon = canonicalize(doc2)
            if expected_canon == roundtrip_canon:
                passed += 1
                results.append({"case": fn, "status": "pass"})
            else:
                failed += 1
                results.append({"case": fn, "status": "fail",
                                "detail": "canonical mismatch after roundtrip"})
        except Exception as e:
            failed += 1
            results.append({"case": fn, "status": "fail",
                            "detail": f"{type(e).__name__}: {e}"})
    return {"total": passed + failed, "passed": passed, "failed": failed,
            "results": results}
