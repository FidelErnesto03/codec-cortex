# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Canonical ``.cortex`` writer.

Serialises a :class:`CortexDocument` AST back to ``.cortex`` source text.
The writer is deterministic: the same AST always produces byte-identical
output, which is what makes roundtrip verification meaningful.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .ast import (
    AttrsPosContract,
    CortexDocument,
    Entry,
    Glossary,
    MicroDef,
    SigilDef,
)


# ---------------------------------------------------------------------------
# Value serialisation
# ---------------------------------------------------------------------------

def _escape_string(s: str) -> str:
    """Escape a string for ``attrs`` double-quoted form."""

    out = s.replace("\\", "\\\\").replace('"', '\\"')
    out = out.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
    return f'"{out}"'


def serialize_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return _escape_string(value)
    if value is None:
        return '""'
    # fallback: JSON
    return _escape_string(json.dumps(value, ensure_ascii=False))


def serialize_attrs(attrs: Dict[str, Any]) -> str:
    """Serialise a dict to ``key:"value", key2:val2`` form."""

    parts = []
    for k, v in attrs.items():
        parts.append(f"{k}:{serialize_value(v)}")
    return ", ".join(parts)


def serialize_attrs_pos(attrs: Dict[str, Any], contract: AttrsPosContract) -> str:
    """Serialise positional attrs using the contract's field order.

    Re-audit H-RA-05: ``|`` is the delimiter and CANNOT appear inside
    values.  We raise :class:`~cortex.core.errors.InvalidValueError`
    if any value contains ``|`` — the caller should use ``attrs`` form
    instead for values that need pipes.
    """

    from .errors import InvalidValueError
    parts = []
    for field_name in contract.fields:
        v = attrs.get(field_name)
        if v is None:
            parts.append("")
            continue
        s = serialize_value(v)
        # Detect literal pipe inside the serialised value (after quote stripping)
        # The serialised form is "..." for strings; check the inner content.
        inner = s
        if len(inner) >= 2 and inner[0] == '"' and inner[-1] == '"':
            inner = inner[1:-1]
        if "|" in inner:
            raise InvalidValueError(
                f"attrs-pos value for field {field_name!r} contains '|' "
                f"({inner!r}); use 'attrs' type instead — pipes are forbidden "
                "in attrs-pos values per SKILL.md §4.3"
            )
        parts.append(s)
    return " | ".join(parts)


def serialize_entry_value(value: Any, type_: str) -> str:
    """Serialise the *body* of an entry (content between braces)."""

    if type_ == "attrs":
        return serialize_attrs(value) if isinstance(value, dict) else ""
    if type_ == "attrs-pos":
        # Without a contract we fall back to attrs form
        return serialize_attrs(value) if isinstance(value, dict) else ""
    if type_ == "cuerpo":
        text = str(value) if value is not None else ""
        return _collapse_newlines(text)
    if type_ == "bloque":
        text = str(value) if value is not None else ""
        # Ensure a leading newline if the bloque spans multiple lines
        if "\n" in text:
            return "\n" + text + "\n"
        return text
    if type_ == "relación":
        text = str(value) if value is not None else ""
        return _collapse_newlines(text)
    # Unknown type — fallback to attrs
    return serialize_attrs(value) if isinstance(value, dict) else str(value or "")


def _collapse_newlines(text: str) -> str:
    """Collapse internal newlines to spaces for single-line constraint.

    Preserves content by stripping blank lines and joining non-empty
    segments with a single space.  This satisfies BLP-005 rule 5:
    legacy multiline non-DIAG input canonicalizes without semantic loss.
    """
    if "\n" not in text:
        return text
    lines = [line.strip() for line in text.split("\n")]
    return " ".join(line for line in lines if line)


def serialize_entry(entry: Entry, glossary: Glossary | None = None) -> str:
    """Serialise a single :class:`Entry` to canonical ``.cortex`` text."""

    if entry.type == "attrs-pos" and glossary is not None:
        contract = glossary.contract_for(entry.sigil)
        if contract is not None:
            body = serialize_attrs_pos(entry.value, contract)
            return f"{entry.sigil}:{entry.name}{{{body}}}"
    body = serialize_entry_value(entry.value, entry.type)
    if entry.type == "bloque" and "\n" in body:
        if entry.sigil == "DIAG":
            # DIAG is the sole multiline exception — preserve verbatim
            if not body.startswith("\n"):
                body = "\n" + body
            if not body.endswith("\n"):
                body = body + "\n"
            return f"{entry.sigil}:{entry.name}{{{body}}}"
        # Non-DIAG bloque must be single line per BLP-005 rule 1
        body = _collapse_newlines(body)
    return f"{entry.sigil}:{entry.name}{{{body}}}"


# ---------------------------------------------------------------------------
# Glossary serialisation
# ---------------------------------------------------------------------------

def serialize_glossary(glossary: Glossary) -> str:
    """Serialise the ``$0`` section.

    Uses the pipe-separated comment form (canonical SKILL.md template).
    All declaration lines are prefixed with ``#`` so the lexer classifies
    them as comments and preserves them verbatim for roundtrip.
    """

    lines: List[str] = []
    lines.append("# -- $0: MINIMAL LOCAL GLOSSARY --")
    lines.append("# Required: every .cortex artifact must be locally self-contained.")
    lines.append("# Sigil | Name | Type | Risk | Cognitive Layer | Description")
    # Order sigils deterministically: canonical ones first, then custom
    canonical_order = [
        "IDN", "DOM", "KNW", "REF", "TAG", "AXM", "CNST", "!",
        "CLAIM", "LIM", "AUD", "RSK", "FCS", "OBJ", "WRK", "STP",
        "NXT", "SES", "LNG", "DIAG", "HDL", "PFL", "DEP", "DESC", "ERR",
    ]
    sigils_in_glossary = list(glossary.sigils.values())
    # Sort: canonical first (in canonical order), then custom alphabetically
    def _sort_key(sd: SigilDef) -> tuple:
        if sd.sigil in canonical_order:
            return (0, canonical_order.index(sd.sigil))
        return (1, sd.sigil)
    sigils_in_glossary.sort(key=_sort_key)
    for sd in sigils_in_glossary:
        lines.append(
            f"# {sd.sigil:<5} | {sd.name:<10} | {sd.type:<10} | {sd.risk:<1} | "
            f"{sd.layer:<14} | {sd.description}"
        )
    if glossary.status_custom:
        lines.append("#")
        lines.append("# status: " + ", ".join(glossary.status_custom))
    # Types
    lines.append("#")
    lines.append("# Types:")
    for td in glossary.types.values():
        lines.append(f"# {td.name} = {td.description}")
    # Micro-tokens
    lines.append("#")
    lines.append("# Micro-glossary:")
    micro_items = list(glossary.micro.values())
    # Sort: canonical first (in canonical order), then custom
    canonical_micro_order = list(CANONICAL_MICRO_ORDER)
    def _micro_sort_key(md: MicroDef) -> tuple:
        if md.token in canonical_micro_order:
            return (0, canonical_micro_order.index(md.token))
        return (1, md.token)
    micro_items.sort(key=_micro_sort_key)
    if micro_items:
        line_parts = [f"{md.token}={md.value}" for md in micro_items]
        # Group 4 per line for readability
        for i in range(0, len(line_parts), 4):
            lines.append("# " + " ".join(line_parts[i : i + 4]))
    # Contracts
    if glossary.contracts:
        lines.append("#")
        lines.append("# Positional contracts:")
        for c in glossary.contracts.values():
            lines.append(f"# contract: {c.sigil} | " + " | ".join(c.fields))
    return "\n".join(lines)


# Canonical order for micro-tokens (Section 4.1.1)
CANONICAL_MICRO_ORDER = [
    "cur", "pln", "fut", "blk", "min", "rec", "wrk", "full", "ok", "fail", "part",
]


# ---------------------------------------------------------------------------
# Document serialisation
# ---------------------------------------------------------------------------

def write_cortex(doc: CortexDocument) -> str:
    """Serialise a :class:`CortexDocument` to canonical ``.cortex`` text.

    The ``$0`` glossary section is ALWAYS regenerated from
    ``doc.glossary`` so mutations are reflected in the output.  Other
    sections preserve their comments verbatim.
    """

    out: List[str] = []
    # $0 first — always regenerated from glossary
    if doc.sections and doc.sections[0].id == "$0":
        sec0 = doc.sections[0]
        glossary_text = serialize_glossary(doc.glossary)
        header = "$0"
        if sec0.title:
            header = f"$0: {sec0.title}"
        out.append(header)
        out.append("")
        out.append(glossary_text)
        out.append("")
        # Append any non-glossary entries from $0 section (rare, but supported)
        for entry in sec0.entries:
            if entry.sigil in {"GSIG", "GTYP", "GMIC", "GCON"}:
                continue
            out.append(serialize_entry(entry, doc.glossary))
        out.append("")

    # Other sections
    for sec in doc.sections[1:]:
        header = sec.id
        if sec.title:
            header = f"{sec.id}: {sec.title}"
        out.append(header)
        out.append("")
        # Preserve section comments (after header, before entries)
        if sec.comments:
            out.extend(sec.comments)
            out.append("")
        for entry in sec.entries:
            out.append(serialize_entry(entry, doc.glossary))
        out.append("")

    # Trailing newline
    text = "\n".join(out).rstrip("\n") + "\n"
    return text
