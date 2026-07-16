# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""HCORTEX → CORTEX encoder v2.4.0 — bidirectional verified release.

v2.3.1 had critical issues:
  - Only 182/266 entries reconstructed (68%)
  - $6 DIAG, $7 contracts, $9 profiles not reconstructed
  - Tables without `name` column produced unparseable names

v2.4.0 fixes:
  - Synthetic names: snake_case, stable, reparsable
  - $0 meta entries: target name → entry name (e.g. $0:enum_state → $0:enum_state{...})
  - $0 canonical_sigils: sigil_decl reconstruction
  - $0 contracts/microtokens/type_decls: group kv_table → multiple entries
  - $6 DIAG: verbatim PUML preservation with hash validation
  - $7 contracts: derive contract_<sigil> names from rule content
  - $9 profiles: derive profile_<level> names from topic content
  - $13 VIEW: reconstruct all 44 directives with full metadata
  - Post-write validation: don't write if reparsing loses entries
  - Hash verification: real SHA-256 per block
"""

from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Optional, Tuple

from .diagnostics import Diagnostic
from .hcortex_parser import (
    HCorTEXDocument, HCorTEXBlock, HCorTEXHeader,
    parse_table_block, parse_list_block, parse_verbatim_block, parse_prose_block,
)
from .parser import CortexV2Document, V2Entry, V2Section
from .view import ViewKind, ReverseStrategy


# ---------------------------------------------------------------------------
# v2.4.0: Column header normalization map
# ---------------------------------------------------------------------------

HEADER_MAP = {
    "sigilo": "sigil", "sigil": "sigil",
    "nombre": "name", "name": "name",
    "tipo": "type", "type": "type",
    "riesgo": "risk", "risk": "risk",
    "corteza": "cortex", "cortex": "cortex",
    "descripción": "desc", "descripcion": "desc", "desc": "desc",
    "operación": "operation", "operacion": "operation", "operation": "operation",
    "estado": "status", "status": "status",
    "requiere": "requires", "requires": "requires",
    "notas": "notes", "notes": "notes",
    "regla": "rule", "rule": "rule",
    "severidad": "severity", "severity": "severity",
    "survive": "survive",
    "tema": "topic", "topic": "topic",
    "contenido": "content", "content": "content",
    "ruta": "path", "path": "path",
    "rol": "role", "role": "role",
    "codificación": "encoding", "codificacion": "encoding", "encoding": "encoding",
    "límite": "limit", "limite": "limit", "limit": "limit",
    "ámbito": "scope", "ambito": "scope", "scope": "scope",
    "impacto": "impact", "impact": "impact",
    "mitigación": "mitigation", "mitigacion": "mitigation", "mitigation": "mitigation",
    "patrón": "pattern", "patron": "pattern", "pattern": "pattern",
    "prevención": "prevention", "prevencion": "prevention", "prevention": "prevention",
    "declaración": "statement", "declaracion": "statement", "statement": "statement",
    "evidencia": "evidence", "evidence": "evidence",
    "valor": "value", "value": "value",
    "campo": "campo", "field": "campo",
    "expand": "expand", "pos": "pos", "values": "values",
    "campos posicionales": "pos",
    "expansión": "expand", "expansion": "expand",
}


def _normalize_field_name(name: str) -> str:
    if not name:
        return name
    cleaned = name.strip().lower()
    return HEADER_MAP.get(cleaned, cleaned)


def _strip_backticks(value: str) -> str:
    if not isinstance(value, str):
        return value
    v = value.strip()
    if v.startswith('`') and v.endswith('`'):
        v = v[1:-1]
    elif v.startswith('`'):
        v = v[1:]
    elif v.endswith('`'):
        v = v[:-1]
    return v.strip()


def _sanitize_value(value: str) -> str:
    if not isinstance(value, str):
        return value
    v = _strip_backticks(value)
    # v2.4.0: Un-escape \| back to | (renderer escapes | in table cells)
    v = v.replace('\\|', '|')
    v = re.sub(r'\s+', ' ', v).strip()
    return v


def _split_table_cells(line: str) -> List[str]:
    """v2.4.0: Split a Markdown table row into cells, respecting \\| escapes."""
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    cells = []
    current = ''
    i = 0
    while i < len(line):
        c = line[i]
        if c == '\\' and i + 1 < len(line) and line[i + 1] == '|':
            current += '|'
            i += 2
        elif c == '|':
            cells.append(current.strip())
            current = ''
            i += 1
        else:
            current += c
            i += 1
    cells.append(current.strip())
    return cells


def _slugify(text: str, max_len: int = 40) -> str:
    """Convert text to snake_case slug suitable for entry names."""
    if not text:
        return "entry"
    # Remove backticks
    text = _strip_backticks(text)
    # Lowercase
    text = text.lower()
    # Replace non-alphanumeric with underscore
    text = re.sub(r'[^a-z0-9]+', '_', text)
    # Strip leading/trailing underscores
    text = text.strip('_')
    # Truncate
    if len(text) > max_len:
        text = text[:max_len].rstrip('_')
    return text or "entry"


def _synthetic_name(sigil: str, section: str, ordinal: int, hint: str = "") -> str:
    """Generate a stable, reparsable synthetic name.

    Format: synthetic_<sigil>_<section>_<ordinal> or synthetic_<sigil>_<section>_<hint>
    v2.4.0: Sanitize sigil (replace ! with rule, $ with s) to keep names reparsable.
    """
    safe_sigil = sigil.replace("!", "rule").replace("$", "s").lower()
    sec = section.replace("$", "s")
    if hint:
        slug = _slugify(hint, max_len=30)
        return f"synthetic_{safe_sigil}_{sec}_{slug}"
    return f"synthetic_{safe_sigil}_{sec}_{ordinal:03d}"


# ---------------------------------------------------------------------------
# F-09: encode_cortex_from_ast()
# ---------------------------------------------------------------------------

def encode_cortex_from_ast(hdoc: HCorTEXDocument, mode: str = "normal") -> Tuple[CortexV2Document, List[Diagnostic]]:
    """Encode an HCorTEXDocument back to a CortexV2Document.

    v2.4.0: Full reconstruction with synthetic names, DIAG preservation,
    $13 VIEW reconstruction, and post-write validation.
    """

    diags: List[Diagnostic] = list(hdoc.diags)

    cortex_doc = CortexV2Document()
    cortex_doc.header = _build_cortex_header(hdoc.header)

    sections: Dict[str, V2Section] = {}

    # F-10/F-13: For each VIEW block, reconstruct entries
    for block in hdoc.blocks:
        entries, entry_diags = _block_to_entries(block, mode)
        diags.extend(entry_diags)

        section_id = _resolve_section(block)
        if section_id not in sections:
            sections[section_id] = V2Section(id=section_id)
        sections[section_id].entries.extend(entries)

    # v2.4.0 P0-6: Reconstruct $13 with VIEW directives
    if hdoc.blocks:
        if "$13" not in sections:
            sections["$13"] = V2Section(id="$13")
        for block in hdoc.blocks:
            view_entry = _block_to_view_entry(block)
            if view_entry is not None:
                sections["$13"].entries.append(view_entry)

    # F-11: Ensure $0 exists
    if "$0" not in sections:
        sections["$0"] = V2Section(id="$0")
        diags.append(Diagnostic(
            "E_VIEW_MISSING",
            "$0 section not found in HCORTEX — empty glossary created",
            "warning" if mode != "strict" else "error",
        ))

    sorted_ids = sorted(sections.keys(), key=lambda s: int(s[1:]) if s[1:].isdigit() else 999)
    cortex_doc.sections = [sections[sid] for sid in sorted_ids]

    # v2.4.0 P0-9: Post-write validation
    from .writer import write_cortex_v2
    from .parser import parse_cortex_v2
    test_text = write_cortex_v2(cortex_doc)
    try:
        re_doc = parse_cortex_v2(test_text)
        re_entries = sum(len(s.entries) for s in re_doc.sections)
        declared_entries = sum(len(s.entries) for s in cortex_doc.sections)
        if re_entries < declared_entries:
            diags.append(Diagnostic(
                "E_AST_EQUIVALENCE_FAIL",
                f"Post-write validation: declared {declared_entries} entries but reparse found {re_entries}",
                "error",
            ))
    except Exception as e:
        diags.append(Diagnostic(
            "E_AST_EQUIVALENCE_FAIL",
            f"Post-write validation: reparse failed: {e}",
            "error",
        ))

    if mode == "strict":
        for d in diags:
            if d.severity == "warning":
                d.severity = "error"

    return cortex_doc, diags


def _block_to_view_entry(block: HCorTEXBlock) -> Optional[V2Entry]:
    """Reconstruct a VIEW directive entry from an HCorTEXBlock."""
    attrs: Dict[str, str] = {
        "kind": block.kind,
        "target": block.target,
        "reverse": block.reverse,
        "status": block.status,
    }
    if block.fields:
        attrs["fields"] = ",".join(block.fields)
    if block.order:
        attrs["order"] = block.order
    if block.title:
        attrs["title"] = block.title
    if block.scope:
        attrs["scope"] = block.scope
    if block.section:
        attrs["section"] = block.section
    if block.source_section:
        attrs["source_section"] = block.source_section
    if block.preserve:
        attrs["preserve"] = block.preserve
    if block.hash:
        attrs["hash"] = block.hash
    if block.fallback:
        attrs["fallback"] = block.fallback

    return V2Entry(
        sigil="VIEW",
        name=block.view_name,
        entry_type="attrs",
        value=attrs,
        section="$13",
    )


def _build_cortex_header(hheader: HCorTEXHeader) -> Dict[str, str]:
    cortex_header: Dict[str, str] = {"internal_encoding": "CORTEX"}
    if hheader.source_artifact:
        cortex_header["source_artifact"] = hheader.source_artifact
    if hheader.source_version:
        cortex_header["source_version"] = hheader.source_version
    if hheader.status:
        cortex_header["status"] = hheader.status
    return cortex_header


def _resolve_section(block: HCorTEXBlock) -> str:
    if block.section:
        return block.section
    if block.source_section:
        return block.source_section
    if block.target.startswith("$"):
        parts = block.target.split(":", 1)
        return parts[0]
    return "$1"


def _derive_sigil_name_from_target(target: str) -> Tuple[str, str]:
    if target.startswith("$") and target.count(":") == 2:
        parts = target.split(":")
        return parts[1], parts[2]
    if target.startswith("$") and target.endswith(":*"):
        parts = target.split(":")
        sigil = parts[1] if len(parts) >= 2 else "IDN"
        return sigil, "entry"
    if target.startswith("$") and ":" in target and target.count(":") == 1:
        parts = target.split(":", 1)
        name = parts[1]
        if name in ("canonical_sigils", "type_decls", "contracts", "microtokens"):
            return "$0", name
        return "IDN", name
    if ":" in target and not target.startswith("$"):
        parts = target.split(":", 1)
        sigil = parts[0]
        name = parts[1] if parts[1] != "*" else "entry"
        return sigil, name
    return "IDN", "entry"


def _block_to_entries(block: HCorTEXBlock, mode: str) -> Tuple[List[V2Entry], List[Diagnostic]]:
    diags: List[Diagnostic] = []
    entries: List[V2Entry] = []

    try:
        kind = ViewKind(block.kind)
        reverse = ReverseStrategy(block.reverse)
    except ValueError as e:
        diags.append(Diagnostic(
            "E_VIEW_REVERSE_UNSUPPORTED",
            f"VIEW:{block.view_name} invalid kind/reverse: {e}",
            "error", f"VIEW:{block.view_name}",
        ))
        return entries, diags

    # v2.4.0 P1-2: Verify hash if present
    if block.hash:
        computed_hash = _compute_block_hash(block)
        if computed_hash != block.hash:
            diags.append(Diagnostic(
                "E_VIEW_HASH_MISMATCH",
                f"VIEW:{block.view_name} hash mismatch: declared={block.hash!r}, computed={computed_hash!r}",
                "error", f"VIEW:{block.view_name}",
            ))

    if kind == ViewKind.TABLE and reverse == ReverseStrategy.ROWS_TO_ENTRIES:
        entries = _table_to_entries(block, diags)
    elif kind == ViewKind.KV_TABLE and reverse == ReverseStrategy.ROW_TO_ATTRS:
        entries = _kv_table_to_entries(block, diags)
    elif kind == ViewKind.LIST and reverse == ReverseStrategy.ITEMS_TO_ENTRIES:
        entries = _list_to_entries(block, diags)
    elif kind == ViewKind.NUMBERED_LIST and reverse == ReverseStrategy.ITEMS_TO_ORDERED_ENTRIES:
        entries = _numbered_list_to_entries(block, diags)
    elif kind in (ViewKind.PROSE, ViewKind.QUOTE) and reverse == ReverseStrategy.BODY_TO_CUERPO:
        entries = _prose_to_cuerpo(block, diags)
    elif kind in (ViewKind.PUML, ViewKind.CODE) and reverse == ReverseStrategy.VERBATIM_TO_BLOQUE:
        entries = _verbatim_to_bloque(block, diags)
    elif kind == ViewKind.CALLOUT and reverse == ReverseStrategy.CALLOUT_TO_RISK:
        entries = _callout_to_risk(block, diags)
    else:
        diags.append(Diagnostic(
            "E_VIEW_REVERSE_UNSUPPORTED",
            f"VIEW:{block.view_name} kind={kind.value} reverse={reverse.value} not yet implemented",
            "warning", f"VIEW:{block.view_name}",
        ))

    return entries, diags


def _compute_block_hash(block: HCorTEXBlock) -> str:
    content = '\n'.join(block.content_lines)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


# ---------------------------------------------------------------------------
# v2.4.0 P0-2: TABLE → entries with synthetic names
# ---------------------------------------------------------------------------

def _table_to_entries(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    """Convert a table to multiple entries.

    v2.4.0: Smart name derivation — uses name column, source, or synthetic names.
    """

    rows, table_diags = parse_table_block(block)
    diags.extend(table_diags)

    default_sigil, _ = _derive_sigil_name_from_target(block.target)
    section_id = _resolve_section(block)

    # v2.4.0: Special handling for $0:canonical_sigils
    if block.target == "$0:canonical_sigils":
        return _canonical_sigils_to_entries(rows, diags)

    # v2.4.0: Special handling for $0:contracts
    if block.target == "$0:contracts":
        return _contracts_decl_to_entries(rows, diags)

    # v2.4.0: Special handling for $0:microtokens
    if block.target == "$0:microtokens":
        return _microtokens_decl_to_entries(rows, diags)

    entries: List[V2Entry] = []
    for i, row in enumerate(rows):
        normalized_row: Dict[str, str] = {}
        for k, v in row.items():
            norm_key = _normalize_field_name(k)
            normalized_row[norm_key] = v

        # v2.4.0: Check for `source` column first (SIGIL:name)
        source = _strip_backticks(normalized_row.get("source", ""))
        sigil = ""
        name = ""
        if source and ":" in source:
            parts = source.split(":", 1)
            sigil = parts[0].strip().upper()
            name = _sanitize_value(parts[1])

        # Fall back to sigil/name columns if present
        if not sigil:
            sigil = _strip_backticks(normalized_row.get("sigil", "")).upper()
        if not name:
            name = _sanitize_value(normalized_row.get("name", ""))

        if not sigil:
            sigil = default_sigil

        # v2.4.0 P0-2: Derive name deterministically if still missing
        if not name:
            name = _derive_name_from_content(normalized_row, sigil, section_id, i, block.target)

        if not sigil or not name:
            continue

        # Build attrs (exclude source, sigil, name; skip empty values)
        attrs: Dict[str, str] = {}
        for k, v in normalized_row.items():
            if k in ("sigil", "name", "source"):
                continue
            sanitized = _sanitize_value(v)
            if sanitized:  # v2.4.0: skip empty attrs to match original
                attrs[k] = sanitized

        # v2.4.0: HDL special case — use attrs-pos
        if sigil == "HDL":
            # HDL uses bare attrs-pos: HDL:name|operation|status|requires|notes
            entry = V2Entry(
                sigil=sigil,
                name=name,
                entry_type="attrs-pos",
                value={
                    "operation": attrs.get("operation", ""),
                    "status": attrs.get("status", ""),
                    "requires": attrs.get("requires", ""),
                    "notes": attrs.get("notes", ""),
                },
                section=section_id,
            )
        elif sigil == "$0":
            entry = V2Entry(
                sigil="$0",
                name=name,
                entry_type="meta",
                value=attrs,
                section="$0",
            )
        else:
            entry = V2Entry(
                sigil=sigil,
                name=name,
                entry_type="attrs",
                value=attrs,
                section=section_id,
            )
        entries.append(entry)

    return entries


def _derive_name_from_content(row: Dict[str, str], sigil: str, section: str, ordinal: int, target: str) -> str:
    """v2.4.0 P0-2: Derive a stable, reparsable name from row content.

    Priority:
    1. If `name` field exists → use it
    2. If `operation` field → slugify it (HDL handlers)
    3. If `path` field → slugify it (REF entries)
    4. If `topic` field → slugify it (KNW entries)
    5. If `rule` field → try to extract sigil name from contract rules
    6. If `pattern` field → slugify it (PFL entries)
    7. If `limit` field → slugify it (LIM entries)
    8. If `risk` field → slugify it (RSK entries)
    9. Fallback: synthetic_<sigil>_<section>_<ordinal>
    """

    # Check for contract patterns: "FCS requiere what,priority,..."
    rule = row.get("rule", "")
    if rule:
        # Contract pattern: "SIGIL requiere ..." or "SIGIL MUST ..."
        m = re.match(r'^(\w+)\s+(?:requiere|MUST|DEBE|debe)', rule, re.IGNORECASE)
        if m:
            contract_sigil = m.group(1).upper()
            return f"contract_{contract_sigil.lower()}"

    # Check for profile patterns in topic: "CORTEX-MIN", "CORTEX-RECOVERY"
    topic = row.get("topic", "")
    if topic:
        slug = _slugify(topic)
        if slug:
            return f"profile_{slug}" if section == "$9" else slug

    # operation field (HDL)
    op = row.get("operation", "")
    if op:
        return _slugify(op)

    # path field (REF)
    path = row.get("path", "")
    if path:
        # Extract filename without extension
        basename = path.split("/")[-1].split(".")[0]
        return _slugify(basename) or f"ref_{ordinal:03d}"

    # pattern field (PFL)
    pattern = row.get("pattern", "")
    if pattern:
        return _slugify(pattern, max_len=30)

    # limit field (LIM)
    limit = row.get("limit", "")
    if limit:
        return _slugify(limit, max_len=30)

    # risk field (RSK)
    risk = row.get("risk", "")
    if risk:
        return _slugify(risk, max_len=30)

    # Fallback: synthetic name
    return _synthetic_name(sigil, section, ordinal)


def _canonical_sigils_to_entries(rows: List[Dict[str, str]], diags: List[Diagnostic]) -> List[V2Entry]:
    """Reconstruct $0 sigil declarations from the canonical_sigils table."""
    entries: List[V2Entry] = []
    for row in rows:
        normalized: Dict[str, str] = {}
        for k, v in row.items():
            normalized[_normalize_field_name(k)] = v

        sigil = _strip_backticks(normalized.get("sigil", "")).upper()
        name = _sanitize_value(normalized.get("name", ""))

        if not sigil or not name:
            continue

        attrs: Dict[str, str] = {}
        for k, v in normalized.items():
            if k in ("sigil", "name"):
                continue
            attrs[k] = _sanitize_value(v)

        entry = V2Entry(
            sigil=sigil,
            name=name,
            entry_type="sigil_decl",
            value=attrs,
            section="$0",
        )
        entries.append(entry)
    return entries


def _contracts_decl_to_entries(rows: List[Dict[str, str]], diags: List[Diagnostic]) -> List[V2Entry]:
    """Reconstruct $0:contract_* entries from the contracts table.

    Table format: | Sigilo | Campos posicionales |
    Entry format: $0:contract_<sigil>{pos:"..."}
    """
    entries: List[V2Entry] = []
    for row in rows:
        normalized: Dict[str, str] = {}
        for k, v in row.items():
            normalized[_normalize_field_name(k)] = v

        sigil = _strip_backticks(normalized.get("sigil", "")).upper()
        pos = _sanitize_value(normalized.get("pos", ""))

        if not sigil:
            continue

        name = f"contract_{sigil.lower()}"
        entry = V2Entry(
            sigil="$0",
            name=name,
            entry_type="meta",
            value={"pos": pos},
            section="$0",
        )
        entries.append(entry)
    return entries


def _microtokens_decl_to_entries(rows: List[Dict[str, str]], diags: List[Diagnostic]) -> List[V2Entry]:
    """Reconstruct $0:micro_* entries from the microtokens table.

    Table format: | Token | Expansión |
    Entry format: $0:micro_<token>{expand:"..."}
    """
    entries: List[V2Entry] = []
    for row in rows:
        normalized: Dict[str, str] = {}
        for k, v in row.items():
            normalized[_normalize_field_name(k)] = v

        token = _strip_backticks(normalized.get("token", normalized.get("campo", "")))
        expand = _sanitize_value(normalized.get("expand", normalized.get("valor", "")))

        if not token:
            continue

        name = f"micro_{_slugify(token)}"
        entry = V2Entry(
            sigil="$0",
            name=name,
            entry_type="meta",
            value={"expand": expand},
            section="$0",
        )
        entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# v2.4.0: KV_TABLE → entries (smart group handling)
# ---------------------------------------------------------------------------

def _kv_table_to_entries(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    """Convert a KV table to entries.

    v2.4.0: Smart handling:
    - **Source:** markers split group kv_tables into individual entries
    - $0:NAME targets → single meta entry with name=NAME
    - $N:SIGIL:name targets → single attrs entry
    """

    rows, table_diags = parse_table_block(block)
    diags.extend(table_diags)

    section_id = _resolve_section(block)
    default_sigil, target_name = _derive_sigil_name_from_target(block.target)

    # v2.4.0: Check for **Source:** markers in the content (group kv_table)
    source_markers = []
    for line in block.content_lines:
        stripped = line.strip()
        if stripped.startswith("**Source:**"):
            import re as _re
            m = _re.search(r'`([$\w]+):(\w+)`', stripped)
            if m:
                source_markers.append((m.group(1), m.group(2)))

    # v2.4.0: If Source markers found, split rows by Source
    if source_markers:
        return _kv_table_group_with_sources(block, rows, source_markers, section_id, diags)

    if not rows:
        return []

    # $0:NAME → single meta entry
    if section_id == "$0" and not block.target.endswith(":*"):
        attrs: Dict[str, str] = {}
        for row in rows:
            campo = _normalize_field_name(row.get("campo", row.get("field", "")))
            valor = _sanitize_value(row.get("valor", row.get("value", "")))
            if campo:
                attrs[campo] = valor

        entry = V2Entry(
            sigil="$0",
            name=target_name,
            entry_type="meta",
            value=attrs,
            section="$0",
        )
        return [entry]

    # $N:SIGIL:name → single attrs entry
    if not block.target.endswith(":*") and default_sigil != "IDN":
        attrs: Dict[str, str] = {}
        for row in rows:
            campo = _normalize_field_name(row.get("campo", row.get("field", "")))
            valor = _sanitize_value(row.get("valor", row.get("value", "")))
            if campo:
                attrs[campo] = valor

        entry = V2Entry(
            sigil=default_sigil,
            name=target_name,
            entry_type="attrs",
            value=attrs,
            section=section_id,
        )
        return [entry]

    # v2.4.0: Group kv_table without Source markers — create one entry with synthetic name
    attrs: Dict[str, str] = {}
    for row in rows:
        campo = _normalize_field_name(row.get("campo", row.get("field", "")))
        valor = _sanitize_value(row.get("valor", row.get("value", "")))
        if campo:
            attrs[campo] = valor

    name = _slugify(target_name) if target_name != "entry" else _synthetic_name(default_sigil, section_id, 1)
    entry = V2Entry(
        sigil=default_sigil,
        name=name,
        entry_type="attrs",
        value=attrs,
        section=section_id,
    )
    return [entry]


def _kv_table_group_with_sources(
    block: HCorTEXBlock,
    rows: List[Dict[str, str]],
    source_markers: List[Tuple[str, str]],
    section_id: str,
    diags: List[Diagnostic],
) -> List[V2Entry]:
    """v2.4.0: Parse a group kv_table with **Source:** markers.

    Each Source marker indicates a new entry. Rows between markers belong to that entry.
    """

    entries: List[V2Entry] = []

    # If we have N source markers, we need to split the rows into N groups
    # The rows don't have Source info, so we split evenly (or by content analysis)
    # Actually, the renderer puts the Source heading BEFORE each table, and
    # parse_table_block only finds the FIRST table. So for group kv_tables,
    # we need to parse each table separately.

    # Re-parse the content to find all tables
    import re as _re
    raw_content = '\n'.join(block.content_lines)

    # Find all table sections (each preceded by **Source:** marker)
    table_pattern = _re.compile(
        r'\*\*Source:\*\*\s*`([$\w]+):(\w+)`\s*\n(.*?)(?=\*\*Source:\*\*|<!-- /VIEW|\Z)',
        _re.DOTALL
    )

    for m in table_pattern.finditer(raw_content):
        sigil = m.group(1)
        name = m.group(2)
        table_content = m.group(3)

        # Parse the Campo|Valor table in this section
        attrs: Dict[str, str] = {}
        for line in table_content.split('\n'):
            stripped = line.strip()
            if not stripped.startswith('|') or '---' in stripped:
                continue
            # v2.4.0: Use proper cell splitting that handles \| escapes
            cells = _split_table_cells(stripped)
            if len(cells) >= 2:
                campo = _normalize_field_name(cells[0])
                valor = _sanitize_value(cells[1])
                if campo and campo != "campo" and campo != "field":
                    attrs[campo] = valor

        # v2.4.0: $0 entries should be meta type
        entry_type = "meta" if sigil == "$0" else "attrs"
        entry = V2Entry(
            sigil=sigil,
            name=name,
            entry_type=entry_type,
            value=attrs,
            section=section_id,
        )
        entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# LIST → entries
# ---------------------------------------------------------------------------

def _list_to_entries(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    items, list_diags = parse_list_block(block)
    diags.extend(list_diags)

    default_sigil, _ = _derive_sigil_name_from_target(block.target)
    section_id = _resolve_section(block)

    entries: List[V2Entry] = []
    for item in items:
        # Parse: "- `SIGIL:name` — description (survive:min)"
        m = re.match(r'^`?([$\w!]+)?:?(\w+)`?\s*[—-]\s*(.*)$', item)
        if m:
            sigil = _strip_backticks(m.group(1) or default_sigil).upper()
            if sigil == "IDN" and default_sigil != "IDN":
                sigil = default_sigil
            name = _sanitize_value(m.group(2))
            desc = _sanitize_value(m.group(3))

            # Extract survive from "(survive:min)" suffix
            survive = ""
            surv_m = re.search(r'\(survive:(\w+)\)', desc)
            if surv_m:
                survive = surv_m.group(1)
                desc = re.sub(r'\s*\(survive:\w+\)', '', desc).strip()

            attrs: Dict[str, str] = {}
            if desc:
                attrs["rule"] = desc
            if survive:
                attrs["survive"] = survive

            entry = V2Entry(
                sigil=sigil,
                name=name,
                entry_type="attrs",
                value=attrs,
                section=section_id,
            )
        else:
            entry = V2Entry(
                sigil=default_sigil if default_sigil != "IDN" else "!",
                name=_synthetic_name(default_sigil, section_id, len(entries)),
                entry_type="attrs",
                value={"rule": _sanitize_value(item)},
                section=section_id,
            )
        entries.append(entry)

    return entries


def _numbered_list_to_entries(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    """Convert a numbered list to ordered entries.

    v2.4.0: Parse `SIGIL:name` source markers from each item.
    """

    items, list_diags = parse_list_block(block)
    diags.extend(list_diags)

    default_sigil, _ = _derive_sigil_name_from_target(block.target)
    if default_sigil == "IDN":
        default_sigil = "!"
    section_id = _resolve_section(block)

    entries: List[V2Entry] = []
    for i, item in enumerate(items):
        # v2.4.0: Don't sanitize before regex — backticks needed for source match
        # Parse `SIGIL:name` — description
        source_m = re.match(r'^`([$\w!]+):(\w+)`\s*[—-]\s*(.*)$', item)
        if source_m:
            sigil = source_m.group(1)
            name = source_m.group(2)
            desc = _sanitize_value(source_m.group(3))
        else:
            sigil = default_sigil
            name = _synthetic_name(default_sigil, section_id, i + 1)
            desc = _sanitize_value(item)

        # Extract survive from "(survive:X)" suffix
        survive = ""
        surv_m = re.search(r'\(survive:(\w+)\)$', desc)
        if surv_m:
            survive = surv_m.group(1)
            desc = re.sub(r'\s*\(survive:\w+\)$', '', desc).strip()

        attrs: Dict[str, str] = {"rule": desc}
        if survive:
            attrs["survive"] = survive

        entry = V2Entry(
            sigil=sigil,
            name=name,
            entry_type="attrs",
            value=attrs,
            section=section_id,
        )
        entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# PROSE/QUOTE → cuerpo
# ---------------------------------------------------------------------------

def _prose_to_cuerpo(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    body, prose_diags = parse_prose_block(block)
    diags.extend(prose_diags)

    sigil, name = _derive_sigil_name_from_target(block.target)
    section_id = _resolve_section(block)

    entry = V2Entry(
        sigil=sigil,
        name=name,
        entry_type="cuerpo",
        value=body,
        section=section_id,
    )
    return [entry]


# ---------------------------------------------------------------------------
# v2.4.0 P0-3: PUML/CODE → bloque (verbatim preservation)
# ---------------------------------------------------------------------------

def _verbatim_to_bloque(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    """Convert a verbatim code block to a bloque entry.

    v2.4.0 P0-3: Preserve DIAG/PUML content verbatim with hash validation.
    v2.4.0: Handle multiple fenced blocks within one VIEW block.
    """

    section_id = _resolve_section(block)
    sigil, name = _derive_sigil_name_from_target(block.target)
    if not sigil or sigil == "IDN":
        sigil = "DIAG"

    # v2.4.0: $0:DIAG:diagram canonical decl — not real PUML, it's sigil attrs
    if block.target == "$0:DIAG:diagram":
        content, _ = parse_verbatim_block(block)
        entry = V2Entry(
            sigil="DIAG",
            name="diagram",
            entry_type="bloque",
            value=content,
            section="$0",
        )
        return [entry]

    # v2.4.0: Find ALL ```puml or ``` fences with Source markers
    raw_content = '\n'.join(block.content_lines)

    # v2.4.0: Parse Source markers + fenced blocks
    # Pattern: **Source:** `SIGIL:name` ... ```puml ... ```
    source_block_pattern = re.compile(
        r'\*\*Source:\*\*\s*`([$\w!]+):(\w+)`\s*\n(.*?)(?=\*\*Source:\*\*|\Z)',
        re.DOTALL
    )

    source_matches = source_block_pattern.findall(raw_content)

    if source_matches:
        entries: List[V2Entry] = []
        for sigil, name, section_content in source_matches:
            # Find ```puml ... ``` within section_content
            fence_m = re.search(r'```(?:puml|plantuml)?\n(.*?)```', section_content, re.DOTALL)
            if fence_m:
                puml_content = fence_m.group(1)
            else:
                puml_content = section_content.strip()

            # v2.4.0 P1-5: PUML validation
            if block.kind == "puml":
                if "@startuml" not in puml_content:
                    diags.append(Diagnostic(
                        "E_PUML_INVALID",
                        f"VIEW:{block.view_name} PUML block '{name}' missing @startuml",
                        "error", f"VIEW:{block.view_name}",
                    ))
                if "@enduml" not in puml_content:
                    diags.append(Diagnostic(
                        "E_PUML_INVALID",
                        f"VIEW:{block.view_name} PUML block '{name}' missing @enduml",
                        "error", f"VIEW:{block.view_name}",
                    ))

            # v2.4.0 P0-3: preserve:verbatim — preserve exact content
            # But strip ONE trailing newline added by the fence format
            if puml_content.endswith('\n'):
                content = puml_content[:-1]
            else:
                content = puml_content

            entry = V2Entry(
                sigil=sigil if sigil != "$0" else "DIAG",
                name=name,
                entry_type="bloque",
                value=content,
                section=section_id,
            )
            entries.append(entry)
        return entries

    # Fallback: find fenced blocks without Source markers
    fence_pattern = re.compile(r'```(?:puml|plantuml)?\n(.*?)```', re.DOTALL)
    matches = fence_pattern.findall(raw_content)

    if not matches:
        content, _ = parse_verbatim_block(block)
        entry = V2Entry(
            sigil=sigil,
            name=name if name != "entry" else "diagram_1",
            entry_type="bloque",
            value=content,
            section=section_id,
        )
        return [entry]

    entries: List[V2Entry] = []
    for i, puml_content in enumerate(matches):
        title_m = re.search(r'title\s+(.+?)(?:\n|$)', puml_content)
        if title_m:
            name = _slugify(title_m.group(1))
        else:
            name = f"diagram_{i+1}"

        if block.preserve == "verbatim":
            content = puml_content
        else:
            content = puml_content.strip()

        entry = V2Entry(
            sigil="DIAG",
            name=name,
            entry_type="bloque",
            value=content,
            section=section_id,
        )
        entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# CALLOUT → RSK
# ---------------------------------------------------------------------------

def _callout_to_risk(block: HCorTEXBlock, diags: List[Diagnostic]) -> List[V2Entry]:
    """Convert a callout block to RSK entries.

    v2.4.0: Parse ### RSK:name headers as entry boundaries.
    Each header starts a new RSK entry; list items below become attrs.
    """

    section_id = _resolve_section(block)
    entries: List[V2Entry] = []

    current_name = None
    current_attrs: Dict[str, str] = {}

    for line in block.content_lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Skip markdown headers (## title)
        if stripped.startswith('## ') and not stripped.startswith('### '):
            continue

        # ### RSK:name — new entry boundary
        import re as _re
        header_m = _re.match(r'^###\s+RSK:(\w+)', stripped)
        if header_m:
            # Save previous entry
            if current_name:
                # Ensure required fields
                current_attrs.setdefault("impact", "")
                current_attrs.setdefault("mitigation", "")
                current_attrs.setdefault("status", "cur")
                current_attrs.setdefault("survive", "min")
                entry = V2Entry(
                    sigil="RSK",
                    name=current_name,
                    entry_type="attrs",
                    value=current_attrs,
                    section=section_id,
                )
                entries.append(entry)
            current_name = header_m.group(1)
            current_attrs = {}
            continue

        # List item: "- key: value"
        item_m = _re.match(r'^-\s+(\w+):\s*(.*)$', stripped)
        if item_m and current_name:
            key = item_m.group(1).lower()
            value = _sanitize_value(item_m.group(2))
            current_attrs[key] = value

    # Save last entry
    if current_name:
        current_attrs.setdefault("impact", "")
        current_attrs.setdefault("mitigation", "")
        current_attrs.setdefault("status", "cur")
        current_attrs.setdefault("survive", "min")
        entry = V2Entry(
            sigil="RSK",
            name=current_name,
            entry_type="attrs",
            value=current_attrs,
            section=section_id,
        )
        entries.append(entry)

    return entries
