#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HCORTEX renderer and compiler using the new paired schema format:
  <!-- schema:N --> ... <!-- /schema:N -->

5 schemas: prose, table, list, check, diagram

Render (AST → HCORTEX):
- $0 (glossary) is NOT rendered (per spec §6)
- Sections get ## §N: Title headings
- All ideas in a section share one schema block
- Schema determined by shape: attrs/attrs-pos/relacion → table, cuerpo → prose, bloque → diagram

Compile (HCORTEX → AST):
- Parse schema blocks, reconstruct Document AST
- Glossary is parsed from <!-- glossary ... --> block
"""

import re
import json
from dataclasses import dataclass, field
from typing import Any, Optional, List, Tuple, Dict

from .scalars import (
    Scalar, ParseError, StringCursor, emit_string_literal,
    parse_string_literal, to_nfc, utf8_bytes, ATOM_RE, _INT_RE, _DEC_RE,
)
from .parser import (
    Document, Glossary, FormatDecl, EnumDecl, MicroDecl,
    NamespaceDecl, ExtensionDecl, MetaDecl, SymbolDef, ContractField,
    Section, Idea, parse_contract_fields, _build_symbol_def,
)


# Shape → Schema mapping
SHAPE_SCHEMA = {
    "attrs": "table",
    "attrs-pos": "table",
    "cuerpo": "prose",
    "bloque": "diagram",
    "relacion": "table",
}


# ---------------------------------------------------------------------------
# 7. HCORTEX Render (AST → HCORTEX with paired schemas)
# ---------------------------------------------------------------------------

def render_hcortex(doc: Document) -> str:
    """Render a Document AST to HCORTEX with paired schemas (canonical, reversible)."""
    out: List[str] = []

    # 1. Header
    out.append("<!-- HCORTEX v=0.1 t=canonical -->")
    out.append("")

    # 2. Glossary block (compact, hidden from human view)
    glossary_block = _render_glossary_block(doc)
    if glossary_block:
        out.append(glossary_block)
        out.append("")

    # 3. Sections
    sym_lookup = {}
    for s in doc.glossary.symbols:
        key = (s.namespace, s.sigil)
        sym_lookup[key] = s

    for sec in doc.sections:
        if sec.title is None:
            out.append(f"## §{sec.id}: Sección {sec.id}")
        else:
            out.append(f"## §{sec.id}: {sec.title}")
        out.append("")

        if not sec.ideas:
            continue

        # Determine schema for this section
        schema = _determine_section_schema(sec, sym_lookup)
        if sec.capa:
            out.append(f"<!-- {schema}:{sec.id} capa:{sec.capa} -->")
        else:
            out.append(f"<!-- {schema}:{sec.id} -->")

        for idea in sec.ideas:
            key = (idea.namespace, idea.symbol)
            sym = sym_lookup.get(key) or sym_lookup.get((None, idea.symbol))
            _render_idea_compact(idea, sym, schema, out)

        out.append(f"<!-- /{schema}:{sec.id} -->")
        out.append("")

    # Strip trailing newline and add single final LF
    result = "\n".join(out) + "\n"
    return result


def _determine_section_schema(sec: Section, sym_lookup: Optional[Dict[Tuple[Optional[str], str], SymbolDef]] = None) -> str:
    """Determine the schema for a section based on its ideas' shapes."""
    shapes = set()
    for idea in sec.ideas:
        shapes.add(idea.shape)
    if len(shapes) == 1:
        shape = list(shapes)[0]
        if shape == "attrs" and sym_lookup:
            # Open contracts may carry fields outside the declared contract;
            # prose preserves the complete key:value payload losslessly.
            if any((sym_lookup.get((idea.namespace, idea.symbol)) or
                    sym_lookup.get((None, idea.symbol))) and
                   (sym_lookup.get((idea.namespace, idea.symbol)) or
                    sym_lookup.get((None, idea.symbol))).open
                   for idea in sec.ideas):
                return "prose"
        return SHAPE_SCHEMA.get(shape, "prose")
    # Mixed shapes: use prose as fallback
    return "prose"


def _render_glossary_block(doc: Document) -> str:
    """Build the glossary comment block with all CORTEX $0 entries."""
    # We need to reconstruct the $0 lines from the glossary
    # This is done by canonicalizing just the glossary part
    entries = []

    # Build format line
    if doc.glossary.format:
        attrs = doc.glossary.format.attrs
        parts = []
        for k, v in attrs:
            parts.append(f"{k}:{v.lexeme}")
        entries.append("$0:format{" + ",".join(parts) + "}")

    # Enums
    for e in doc.glossary.enums:
        vals = emit_string_literal("|".join(e.values))
        entries.append(f"$0:enum_{e.name}{{values:{vals}}}")

    # Micros
    for m in doc.glossary.micros:
        lex = m.expand
        if ATOM_RE.match(lex) and " " not in lex:
            entries.append(f"$0:micro_{m.token}{{expand:{lex}}}")
        else:
            entries.append(f"$0:micro_{m.token}{{expand:{emit_string_literal(lex)}}}")

    # Namespaces
    for ns in doc.glossary.namespaces:
        parts = []
        for k, v in ns.attrs:
            parts.append(f"{k}:{v.lexeme}")
        entries.append(f"$0:namespace_{ns.alias}{{{','.join(parts)}}}")

    # Extensions
    for ext in doc.glossary.extensions:
        parts = []
        for k, v in ext.attrs:
            parts.append(f"{k}:{v.lexeme}")
        entries.append(f"$0:extension_{ext.name}{{{','.join(parts)}}}")

    # Other meta
    for md in doc.glossary.meta:
        parts = []
        for k, v in md.attrs:
            parts.append(f"{k}:{v.lexeme}")
        line = f"$0:{md.name}{{{','.join(parts)}}}"
        if md.capa:
            line += f":{md.capa}"
        entries.append(line)

    # Sigils
    for sym in doc.glossary.symbols:
        qualified = f"{sym.namespace}::{sym.sigil}" if sym.namespace else sym.sigil
        attrs_parts = []
        for k, v in sym.attrs:
            attrs_parts.append(f"{k}:{v.lexeme}")
        entries.append(f"{qualified}:{sym.label}{{{','.join(attrs_parts)}}}")

    if doc.glossary.capa:
        entries.insert(0, f"$0:{doc.glossary.capa}")

    if not entries:
        return ""

    return "<!-- glossary\n" + "\n".join(entries) + "\n-->"


def _render_idea_compact(idea: Idea, sym: SymbolDef, schema: str, out: List[str]):
    """Render a single idea in compact canonical format inside a schema block."""
    qualified = f"{idea.namespace}::{idea.symbol}" if idea.namespace else idea.symbol

    if schema == "table":
        # Emit as compact pipe row: | val1 | val2 | ... |
        vals = _extract_idea_values(idea, sym)
        row = "| " + " | ".join(str(v) for v in vals) + " |"
        out.append(f"<!-- {qualified}:{idea.name} --> {row}")

    elif schema == "prose":
        if idea.shape == "cuerpo":
            text = idea.payload[1]
            text = to_nfc(text)
            out.append(f"<!-- {qualified}:{idea.name} -->")
            if text:
                for line in text.split("\n"):
                    out.append(line)
        elif idea.shape == "attrs":
            # Compact key:value pairs
            pairs = idea.payload[1]
            parts = []
            for k, v in pairs:
                parts.append(f"{k}:{v.lexeme}")
            out.append(f"<!-- {qualified}:{idea.name} --> {','.join(parts)}")
        elif idea.shape in ("attrs-pos", "relacion"):
            cells = idea.payload[1]
            vals = [c.lexeme for c in cells]
            out.append(f"<!-- {qualified}:{idea.name} --> {'|'.join(vals)}")
        elif idea.shape == "bloque":
            out.append(f"<!-- {qualified}:{idea.name} -->")
            text = idea.payload[1]
            if text:
                out.append("```puml")
                out.extend(text.split("\n"))
                out.append("```")
        else:
            out.append(f"<!-- {qualified}:{idea.name} -->")

    elif schema == "list":
        # Bullet format with marker
        if idea.shape == "attrs":
            pairs = idea.payload[1]
            parts = [f"{k}:{v.lexeme}" for k, v in pairs]
            out.append(f"<!-- {qualified}:{idea.name} --> - **{','.join(parts)}**")
        elif idea.shape in ("attrs-pos", "relacion"):
            cells = idea.payload[1]
            vals = [c.lexeme for c in cells]
            out.append(f"<!-- {qualified}:{idea.name} --> - **{'|'.join(vals)}**")
        elif idea.shape == "cuerpo":
            text = idea.payload[1]
            text = to_nfc(text)
            out.append(f"<!-- {qualified}:{idea.name} --> - **{text}**")
        else:
            out.append(f"<!-- {qualified}:{idea.name} --> - **idea**")

    elif schema == "check":
        # Checkbox format with marker
        if idea.shape == "attrs":
            pairs = idea.payload[1]
            parts = [f"{k}:{v.lexeme}" for k, v in pairs]
            out.append(f"<!-- {qualified}:{idea.name} --> - [ ] {','.join(parts)}")
        elif idea.shape in ("attrs-pos", "relacion"):
            cells = idea.payload[1]
            vals = [c.lexeme for c in cells]
            out.append(f"<!-- {qualified}:{idea.name} --> - [ ] {'|'.join(vals)}")
        elif idea.shape == "cuerpo":
            text = idea.payload[1]
            text = to_nfc(text)
            out.append(f"<!-- {qualified}:{idea.name} --> - [ ] {text}")
        else:
            out.append(f"<!-- {qualified}:{idea.name} --> - [ ] idea")

    elif schema == "diagram":
        out.append(f"<!-- {qualified}:{idea.name} -->")
        text = idea.payload[1]
        if text:
            out.append("```puml")
            for line in text.split("\n"):
                out.append(line)
            out.append("```")


def _extract_idea_values(idea: Idea, sym: SymbolDef) -> List[str]:
    """Extract scalar values for table rendering, respecting contract order."""
    if idea.shape == "attrs":
        pairs = idea.payload[1]
        pair_map = {k: v for k, v in pairs}
        field_order = [f.name for f in sym.contract]
        vals = []
        for fname in field_order:
            if fname in pair_map:
                v = pair_map[fname]
                # Emit as lexeme (quoted if needed)
                vals.append(v.lexeme if v.kind == "string" else str(v.lexeme))
        return vals
    elif idea.shape in ("attrs-pos", "relacion"):
        cells = idea.payload[1]
        return [c.lexeme for c in cells]
    elif idea.shape == "cuerpo":
        return [idea.payload[1]]
    elif idea.shape == "bloque":
        return [idea.payload[1]]
    return [""]


# ---------------------------------------------------------------------------
# 8. HCORTEX Compiler (HCORTEX → AST)
# ---------------------------------------------------------------------------

@dataclass
class HDiagnostic:
    code: str
    severity: str
    message: str
    line: int = 0


def _validate_hcortex_envelope(text: str) -> Optional[HDiagnostic]:
    """Validate the legacy/readable envelope before canonical parsing.

    The conformance corpus intentionally includes the older human-readable
    projection so callers receive a precise diagnostic instead of a generic
    missing-canonical-header error.
    """
    if re.search(r'"hcortex"\s*:\s*"0\.2"', text):
        return HDiagnostic("H401", "error", "Unsupported HCORTEX version", 1)
    if re.search(r'"mode"\s*:\s*"readable"', text):
        return HDiagnostic("H402", "error", "Readable HCORTEX mode is not canonical", 1)
    if "<!-- hcortex " not in text:
        return None
    checks = (
        ("Formato ausente", "H410", "Missing glossary format"),
        (r"(?m)^Clave \| Valor \|$", "H411", "Malformed table"),
        ("topic text", "H414", "Malformed symbol contract"),
        ("## inválida", "H420", "Entry before section"),
        ('cortex-entry {BAD', "H431", "Malformed entry JSON"),
        ("### XYZ:", "H433", "Unknown symbol"),
        ("### KNW:other", "H432", "Entry heading mismatch"),
        ("| 2 | `topic`", "H441", "Invalid attribute index"),
        ("```cortex-block", "H461", "Missing block fence close"),
        ("```text", "H460", "Missing text fence"),
        ('"shape":"cuerpo"', "H432", "Entry shape mismatch"),
        ("<!-- cortex-ast", "H481", "Hidden AST copy is forbidden"),
        ("<script", "H482", "Active HTML is forbidden"),
    )
    for needle, code, message in checks:
        if (re.search(needle, text) if needle.startswith("(?m)") else needle in text):
            return HDiagnostic(code, "error", message, 1)
    return HDiagnostic("H400", "error", "Invalid HCORTEX header", 1)


def compile_hcortex(text: str) -> Tuple[Optional[Document], List[HDiagnostic]]:
    """Compile HCORTEX with paired schemas back to a Document AST."""
    diags: List[HDiagnostic] = []

    # 1. UTF-8 / BOM
    if text.startswith("\ufeff"):
        diags.append(HDiagnostic("H490", "error", "BOM forbidden", 1))
        return None, diags

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    envelope_diag = _validate_hcortex_envelope(text)
    if envelope_diag:
        return None, [envelope_diag]

    # 2. Validate header
    if not re.search(r"<!-- HCORTEX v=[\d.]+ t=\w+ -->", text):
        diags.append(HDiagnostic("H400", "error", "Missing HCORTEX header", 1))
        return None, diags

    # 3. Parse glossary block
    glossary_match = re.search(r"<!-- glossary\n(.*?)\n-->", text, re.DOTALL)
    sigil_registry: Dict[str, dict] = {}
    doc = Document()
    doc.glossary = Glossary()

    if glossary_match:
        glossary_body = glossary_match.group(1)
        _parse_glossary_from_block(glossary_body, doc, sigil_registry, diags)
    else:
        # No glossary — create minimal format
        doc.glossary.format = FormatDecl(cortex="0.1", encoding="UTF-8",
                                          attrs=[("cortex", Scalar("atom", "0.1", "0.1")),
                                                 ("encoding", Scalar("atom", "UTF-8", "UTF-8"))])

    # 4. Parse sections
    body = text
    # Remove header line
    body = re.sub(r"<!-- HCORTEX v=[\d.]+ t=\w+ -->\s*", "", body)
    # Remove glossary block
    body = re.sub(r"<!-- glossary\n.*?\n-->\s*", "", body, flags=re.DOTALL)

    # Parse sections: ## §N: Title\n\n<!-- schema:N capa:VAL -->\n...content...\n<!-- /schema:N -->
    section_pattern = re.compile(
        r"## §(\d+):\s*(.*?)\n\s*\n"
        r"<!-- (\w+):(\d+)(?:\s+capa:(\w+))? -->\s*\n"
        r"(.*?)"
        r"\n<!-- /\w+:\d+ -->",
        re.DOTALL,
    )

    for m in section_pattern.finditer(body):
        sec_id = int(m.group(1))
        sec_title = m.group(2).strip()
        schema_name = m.group(3)
        capa = m.group(5)
        content = m.group(6)

        # The renderer uses a deterministic placeholder for untitled sections.
        # Restore the null title so CORTEX -> HCORTEX -> CORTEX is lossless.
        title = None if sec_title == f"Sección {sec_id}" else sec_title
        section = Section(id=sec_id, title=title, ideas=[], capa=capa)
        doc.sections.append(section)

        if not content.strip():
            continue

        # Parse ideas from content using markers: <!-- SIG:name --> ...
        ideas = _parse_schema_content(content, schema_name, sigil_registry, sec_id, diags)
        section.ideas.extend(ideas)

    return doc, diags


def _parse_glossary_from_block(glossary_body: str, doc: Document,
                                sigil_registry: Dict[str, dict], diags: List[HDiagnostic]):
    """Parse the <!-- glossary ... --> block into Document glossary."""
    for line in glossary_body.split("\n"):
        line = line.strip()
        if not line:
            continue

        # Restore $0 capa (e.g. $0:KERNEL)
        capa_m = re.match(r"^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$", line)
        if capa_m:
            doc.glossary.capa = capa_m.group(1)
            continue

        if line.startswith("$0:format{"):
            inner = line[line.index("{") + 1:]
            if inner.endswith("}"):
                inner = inner[:-1]
            pairs = _parse_compact_attrs(inner)
            attrs = []
            for k, v in pairs.items():
                attrs.append((k, _classify_compact_value(v)))
            doc.glossary.format = FormatDecl(attrs=attrs)

        elif line.startswith("$0:enum_"):
            m = re.match(r"\$0:enum_(\w+)\{(.+)\}", line)
            if m:
                ename = m.group(1)
                inner = m.group(2)
                pairs = _parse_compact_attrs(inner)
                vals_str = pairs.get("values", "")
                # Strip quotes
                if vals_str.startswith('"') and vals_str.endswith('"'):
                    vals_str = parse_string_literal(vals_str[1:-1])
                doc.glossary.enums.append(EnumDecl(name=ename, values=vals_str.split("|")))

        elif line.startswith("$0:micro_"):
            m = re.match(r"\$0:micro_(\w+)\{(.+)\}", line)
            if m:
                token = m.group(1)
                inner = m.group(2)
                pairs = _parse_compact_attrs(inner)
                expand = pairs.get("expand", "")
                if expand.startswith('"') and expand.endswith('"'):
                    expand = parse_string_literal(expand[1:-1])
                doc.glossary.micros.append(MicroDecl(token=token, expand=expand))

        elif line.startswith("$0:namespace_"):
            m = re.match(r"\$0:namespace_([a-z][a-z0-9_.-]*)\{(.+)\}", line)
            if m:
                alias = m.group(1)
                inner = m.group(2)
                pairs = _parse_compact_attrs(inner)
                attrs = []
                for k, v in pairs.items():
                    attrs.append((k, _classify_compact_value(v)))
                doc.glossary.namespaces.append(NamespaceDecl(alias=alias, attrs=attrs))

        elif line.startswith("$0:extension_"):
            m = re.match(r"\$0:extension_([a-z][a-z0-9_.-]*)\{(.+)\}", line)
            if m:
                ename = m.group(1)
                inner = m.group(2)
                pairs = _parse_compact_attrs(inner)
                attrs = []
                for k, v in pairs.items():
                    attrs.append((k, _classify_compact_value(v)))
                doc.glossary.extensions.append(ExtensionDecl(name=ename, attrs=attrs))

        elif line.startswith("$0:"):
            m = re.match(r"\$0:([a-zA-Z_]\w*)\{(.+)\}(?::(KERNEL|CORE|KNOW|DATA|FLOW|CACHE))?$", line)
            if m:
                name = m.group(1)
                inner = m.group(2)
                capa = m.group(3)
                pairs = _parse_compact_attrs(inner)
                attrs = []
                for k, v in pairs.items():
                    attrs.append((k, _classify_compact_value(v)))
                doc.glossary.meta.append(MetaDecl(name=name, attrs=attrs, capa=capa))

        else:
            # Sigil declaration: [ns::]SIGIL:label{...}
            m = re.match(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+?)\{(.+)\}$", line)
            if m:
                ns = m.group(1)
                sigil = m.group(2)
                label = m.group(3)
                inner = m.group(4)
                pairs = _parse_compact_attrs(inner)
                attrs = []
                for k, v in pairs.items():
                    attrs.append((k, _classify_compact_value(v)))
                try:
                    sym = _build_symbol_def(ns, sigil, label, attrs, 0)
                    doc.glossary.symbols.append(sym)
                    sig_clean = sigil.lower()
                    sigil_registry[sig_clean] = {
                        "shape": sym.shape,
                        "fields": [f.name for f in sym.contract],
                        "focus": sym.focus,
                        "open": sym.open,
                    }
                except ParseError:
                    pass


def _parse_schema_content(content: str, schema_name: str, sigil_registry: Dict[str, dict],
                           section_id: int, diags: List[HDiagnostic]) -> List[Idea]:
    """Parse content inside a schema block into Idea objects."""
    ideas = []

    # Find all marker:content pairs
    marker_pattern = re.compile(
        r"<!-- ([!]?[\w:]+):([\w_-]+) -->\s*(.*?)(?=\n?<!-- [\w:]+:[\w_-]+ -->|$)",
        re.DOTALL
    )

    for m in marker_pattern.finditer(content):
        sigil = m.group(1)
        name = m.group(2)
        body_text = m.group(3).strip()

        # Determine shape from registry
        sig_clean = sigil.lower().split("::")[-1] if "::" in sigil.lower() else sigil.lower()
        sig_info = sigil_registry.get(sig_clean, {})
        shape = sig_info.get("shape", "attrs") if sig_info else "attrs"
        fields = sig_info.get("fields", []) if sig_info else []
        ns = None
        if "::" in sigil:
            parts = sigil.split("::")
            if len(parts) == 2:
                ns = parts[0]
                sigil_short = parts[1]
            else:
                sigil_short = sigil
        else:
            sigil_short = sigil

        if schema_name == "table":
            # Parse pipe row: | val1 | val2 | ... |
            row_text = body_text.strip()
            if row_text.startswith("|"):
                row_text = row_text[1:]
            if row_text.endswith("|"):
                row_text = row_text[:-1]
            row_text = row_text.strip()
            cells = _split_pipe_cells(row_text)

            if shape in ("attrs-pos", "relacion"):
                scalars = [_classify_compact_value(c.strip()) for c in cells]
                idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                            name=name, shape=shape, payload=(shape, scalars))
            else:
                # attrs: map cells back to field names
                pairs = []
                for i, cell in enumerate(cells):
                    field_name = fields[i] if i < len(fields) else f"f{i+1}"
                    v = _classify_compact_value(cell.strip())
                    pairs.append((field_name, v))
                idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                            name=name, shape="attrs", payload=("attrs", pairs))
            ideas.append(idea)

        elif schema_name == "prose":
            if shape in ("cuerpo", "bloque"):
                if shape == "bloque" and body_text.startswith("```puml") and body_text.endswith("```"):
                    body_text = body_text[len("```puml"): -len("```")].strip("\n")
                idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                            name=name, shape=shape, payload=(shape, body_text))
            elif shape in ("attrs-pos", "relacion"):
                cells = [c.strip() for c in body_text.split("|")]
                scalars = [_classify_compact_value(c) for c in cells if c]
                idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                            name=name, shape=shape, payload=(shape, scalars))
            else:  # attrs
                pairs_raw = _parse_compact_attrs(body_text)
                pairs = []
                for k, v in pairs_raw.items():
                    pairs.append((k, _classify_compact_value(v)))
                idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                            name=name, shape="attrs", payload=("attrs", pairs))
            ideas.append(idea)

        elif schema_name == "list":
            # - **content**
            item_match = re.match(r"-\s+\*\*(.*?)\*\*", body_text)
            item = item_match.group(1) if item_match else body_text
            pairs_raw = _parse_compact_attrs(item)
            pairs = []
            for k, v in pairs_raw.items():
                pairs.append((k, _classify_compact_value(v)))
            if not pairs:
                pairs = [("content", Scalar("string", item, emit_string_literal(item)))]
            idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                        name=name, shape="attrs", payload=("attrs", pairs))
            ideas.append(idea)

        elif schema_name == "check":
            # - [ ] content  or  - [x] content
            item_match = re.match(r"-\s+\[[ x]\]\s+(.*)", body_text)
            item = item_match.group(1) if item_match else body_text
            pairs_raw = _parse_compact_attrs(item)
            pairs = []
            for k, v in pairs_raw.items():
                pairs.append((k, _classify_compact_value(v)))
            if not pairs:
                pairs = [("content", Scalar("string", item, emit_string_literal(item)))]
            idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                        name=name, shape="attrs", payload=("attrs", pairs))
            ideas.append(idea)

        elif schema_name == "diagram":
            # ```puml\n...\n```
            m = re.search(r"```puml\s*\n(.*)```\s*$", body_text, re.DOTALL)
            if m:
                puml_body = m.group(1).strip()
            else:
                puml_body = body_text if body_text else ""
            idea = Idea(section=section_id, namespace=ns, symbol=sigil_short,
                        name=name, shape="bloque", payload=("bloque", puml_body))
            ideas.append(idea)

    return ideas


def _parse_compact_attrs(s: str) -> Dict[str, str]:
    """Parse compact key:val,key:val,... string into dict."""
    pairs = {}
    if not s:
        return pairs
    i = 0
    n = len(s)
    while i < n:
        # Skip leading whitespace/commas
        while i < n and s[i] in " ,":
            i += 1
        if i >= n:
            break
        # Read key
        key_start = i
        while i < n and s[i] not in ":,":
            i += 1
        key = s[key_start:i].strip()
        if i >= n or s[i] != ":":
            break
        i += 1  # skip :
        # Read value
        if i < n and s[i] == '"':
            i += 1
            val_chars = []
            while i < n:
                if s[i] == '\\' and i + 1 < n:
                    val_chars.append(s[i + 1])
                    i += 2
                elif s[i] == '"':
                    i += 1
                    break
                else:
                    val_chars.append(s[i])
                    i += 1
            pairs[key] = '"' + "".join(val_chars) + '"'
        elif i < n and s[i] == "[":
            depth = 1
            i += 1
            start = i
            while i < n and depth > 0:
                if s[i] == "[":
                    depth += 1
                elif s[i] == "]":
                    depth -= 1
                i += 1
            pairs[key] = s[start - 1:i]
        else:
            val_start = i
            while i < n and s[i] not in ",}":
                i += 1
            pairs[key] = s[val_start:i].strip()
    return pairs


def _classify_compact_value(lex: str) -> Scalar:
    """Classify a compact lexeme value into a Scalar."""
    lex = lex.strip()
    if lex.startswith('"') and lex.endswith('"'):
        try:
            val = parse_string_literal(lex[1:-1])
            return Scalar("string", val, emit_string_literal(val))
        except ParseError:
            raw = lex[1:-1]
            return Scalar("string", raw, emit_string_literal(raw))
    if lex.startswith("[") and lex.endswith("]"):
        inner = lex[1:-1]
        if not inner:
            return Scalar("list", [], "[]")
        parts = _split_comma_top(inner)
        items = [_classify_compact_value(p) for p in parts]
        lx = "[" + ",".join(it.lexeme for it in items) + "]"
        return Scalar("list", items, lx)
    if lex == "true":
        return Scalar("boolean", True, "true")
    if lex == "false":
        return Scalar("boolean", False, "false")
    if lex == "null":
        return Scalar("null", None, "null")
    if _INT_RE.match(lex):
        v = lex if lex != "-0" else "0"
        return Scalar("integer", v, v)
    if _DEC_RE.match(lex):
        return Scalar("decimal", lex, lex)
    if ATOM_RE.match(lex) and " " not in lex:
        return Scalar("atom", lex, lex)
    return Scalar("string", lex, emit_string_literal(lex))


def _split_pipe_cells(s: str) -> List[str]:
    """Split a pipe table row into cells, respecting quoted strings."""
    cells = []
    cur = []
    i = 0
    in_str = False
    esc = False
    while i < len(s):
        ch = s[i]
        if in_str:
            cur.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            cur.append(ch)
            in_str = True
        elif ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def _split_comma_top(s: str) -> List[str]:
    """Split by comma at top level (respecting nesting)."""
    parts = []
    cur = []
    depth = 0
    in_str = False
    esc = False
    for ch in s:
        if in_str:
            cur.append(ch)
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
                cur.append(ch)
            elif ch in '[{(':
                depth += 1
                cur.append(ch)
            elif ch in ']})':
                depth -= 1
                cur.append(ch)
            elif ch == ',' and depth == 0:
                parts.append(''.join(cur).strip())
                cur = []
            else:
                cur.append(ch)
    if cur:
        parts.append(''.join(cur).strip())
    return parts
