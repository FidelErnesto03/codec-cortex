# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""HCORTEX-EDIT renderer — human-editable, structurally reversible Markdown.

Per Section 8.2 of the spec:
  - Preserves $0 glossary (as a fenced ```` ```cortex-glossary ```` block)
  - Every section has a ``<!-- cortex-section -->`` marker
  - Every entry has a ``<!-- cortex-entry -->`` marker with section,
    sigil, name, type and hash
  - ``bloque`` entries are preserved verbatim inside fenced code blocks
  - The first line declares the file is roundtrip-compilable
"""

from __future__ import annotations

from typing import List

from ..core.ast import CortexDocument, Entry, Glossary, SigilDef
from ..core.writer import serialize_value
from .markdown_model import HCORTEX_EDIT_HEADER
from .read_renderer import SECTION_TITLES


def _render_glossary_block(glossary: Glossary) -> List[str]:
    """Render the $0 glossary as a fenced pipe-separated table."""

    lines: List[str] = []
    lines.append("```cortex-glossary")
    lines.append("# Sigil | Name | Type | Risk | Layer | Description")
    # Order sigils deterministically
    canonical_order = [
        "IDN", "DOM", "KNW", "REF", "TAG", "AXM", "CNST", "!",
        "CLAIM", "LIM", "AUD", "RSK", "FCS", "OBJ", "WRK", "STP",
        "NXT", "SES", "LNG", "DIAG", "HDL", "PFL", "DEP", "DESC", "ERR",
    ]
    sigils = list(glossary.sigils.values())
    def _sort(sd: SigilDef):
        if sd.sigil in canonical_order:
            return (0, canonical_order.index(sd.sigil))
        return (1, sd.sigil)
    sigils.sort(key=_sort)
    for sd in sigils:
        lines.append(
            f"{sd.sigil} | {sd.name} | {sd.type} | {sd.risk} | {sd.layer} | {sd.description}"
        )
    lines.append("# Types:")
    for td in glossary.types.values():
        lines.append(f"# {td.name} = {td.description}")
    lines.append("# Micro-glossary:")
    parts = [f"{m.token}={m.value}" for m in glossary.micro.values()]
    for i in range(0, len(parts), 4):
        lines.append("# " + " ".join(parts[i : i + 4]))
    if glossary.contracts:
        lines.append("# Positional contracts:")
        for c in glossary.contracts.values():
            lines.append(f"# contract: {c.sigil} | " + " | ".join(c.fields))
    lines.append("```")
    return lines


def _render_attrs_table(entry: Entry) -> List[str]:
    lines = [
        "| key | value |",
        "| --- | --- |",
    ]
    if isinstance(entry.value, dict):
        for k, v in entry.value.items():
            if isinstance(v, str):
                # escape pipe in value
                val = v.replace("|", "\\|")
            else:
                val = serialize_value(v)
            lines.append(f"| {k} | {val} |")
    return lines


def _render_cuerpo(entry: Entry) -> List[str]:
    """Render cuerpo as a fenced text block."""

    text = str(entry.value or "").rstrip()
    return ["```text", text, "```"]


def _render_bloque(entry: Entry) -> List[str]:
    """Render bloque verbatim in a fenced block."""

    text = str(entry.value or "").rstrip()
    # Try to detect language from content (puml, plantuml, code)
    lang = "text"
    if "@startuml" in text or "@enduml" in text:
        lang = "puml"
    elif "```" in text:
        # Nested fences — wrap in a 4-tilde fence to avoid collision
        return ["~~~~", text, "~~~~"]
    return [f"```{lang}", text, "```"]


def _render_entry(entry: Entry) -> List[str]:
    out: List[str] = []
    # Heading
    out.append(f"### {entry.sigil}:{entry.name}")
    out.append("")
    # Marker (after heading, before body)
    out.append(
        f'<!-- cortex-entry: section="{entry.section}" sigil="{entry.sigil}" '
        f'name="{entry.name}" type="{entry.type}" hash="{entry.hash}" -->'
    )
    out.append("")
    if entry.type in ("attrs", "attrs-pos"):
        out.extend(_render_attrs_table(entry))
    elif entry.type == "cuerpo":
        out.extend(_render_cuerpo(entry))
    elif entry.type == "bloque":
        out.extend(_render_bloque(entry))
    elif entry.type == "relación":
        out.append(f"```\n{entry.value}\n```")
    else:
        out.append(str(entry.value))
    out.append("")
    return out


def render_hcortex_edit(doc: CortexDocument, source: str = "<ast>") -> str:
    """Render ``doc`` as HCORTEX-EDIT Markdown (reversible)."""

    header = HCORTEX_EDIT_HEADER.format(
        source=source,
        hash=doc.meta.get("hash", "sha256:unknown"),
    )
    out: List[str] = [header, ""]
    out.append("# HCORTEX-EDIT")
    out.append("")
    out.append("> Structurally reversible. Edit entries below; preserve markers.")
    out.append("")

    # $0 glossary
    out.append("## $0 · GLOSSARY")
    out.append("")
    out.append('<!-- cortex-section: id="$0" title="GLOSSARY" -->')
    out.append("")
    out.extend(_render_glossary_block(doc.glossary))
    out.append("")

    # Other sections
    for sec in doc.sections:
        if sec.id == "$0":
            continue
        title = sec.title or SECTION_TITLES.get(sec.id, "")  # type: ignore[attr-defined]
        out.append(f"## {sec.id} · {title}" if title else f"## {sec.id}")
        out.append("")
        out.append(f'<!-- cortex-section: id="{sec.id}" title="{title}" -->')
        out.append("")
        if not sec.entries:
            out.append("_(no entries)_")
            out.append("")
            continue
        for entry in sec.entries:
            out.extend(_render_entry(entry))

    return "\n".join(out).rstrip() + "\n"
