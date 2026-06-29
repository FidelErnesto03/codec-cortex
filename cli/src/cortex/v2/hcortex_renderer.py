r"""HCORTEX v2 renderer — converts SkillIR to canonical HCORTEX Markdown.

Produces human-readable Markdown with:
  - Header with internal_encoding:HCORTEX
  - **Perfil: CORTEX-FULL** as first content line
  - Numbered section headers (# N. Title)
  - Tables for sigil definitions, attrs, contracts
  - PUML blocks for DIAG entries
  - Prose for DESC/AXM entries
  - Cross-references where applicable
"""

from __future__ import annotations

from typing import List, Optional

from .ir import SkillIR, IREntry, IRBlock
from .parser import CortexV2Document, V2Entry, V2Section


# Human-readable sigil names
SIGIL_NAMES = {
    "IDN": "Identity", "DOM": "Domain", "KNW": "Knowledge", "REF": "Reference",
    "TAG": "Tag", "AXM": "Axiom", "CNST": "Constraint", "!": "Rule",
    "CLAIM": "Claim", "LIM": "Limit", "AUD": "Audit", "RSK": "Risk",
    "FCS": "Focus", "OBJ": "Objective", "WRK": "Work State", "STP": "Step",
    "NXT": "Next", "SES": "Session", "LNG": "Lesson", "DIAG": "Diagram",
    "HDL": "Handler", "PFL": "Pitfall", "DEP": "Dependency",
    "DESC": "Description", "ERR": "Error",
}

# Section titles for HCORTEX
SECTION_TITLES = {
    "$0": "Glosario cognitivo universal",
    "$1": "Identidad y dominio",
    "$2": "Propósito y contexto",
    "$3": "Operaciones y handlers",
    "$4": "Reglas de sintaxis y render",
    "$5": "Restricciones, riesgos y pitfalls",
    "$6": "Diagramas",
    "$7": "Contratos mínimos por sigilo",
    "$8": "Supervivencia y prioridades",
    "$9": "Perfiles de contexto",
    "$10": "Política de degradación",
    "$11": "HCORTEX",
    "$12": "CORTEX-OUT",
}

# HCORTEX section number mapping
CORTEX_TO_HCORTEX_NUM = {
    "$0": "4", "$1": "0", "$2": "1", "$3": "8", "$4": "5",
    "$5": "7", "$6": "2", "$7": "6", "$8": "11", "$9": "9.6.3",
    "$10": "11.5", "$11": "9", "$12": "10",
}


def render_hcortex_v2(ir: SkillIR) -> str:
    """Render a SkillIR as canonical HCORTEX v2 Markdown."""

    lines: List[str] = []

    # 1. Header
    lines.append("<!-- CODEC-CORTEX")
    lines.append(f"internal_encoding: HCORTEX")
    if "source_artifact" in ir.header:
        lines.append(f"source_artifact: {ir.header['source_artifact']}")
    if "source_version" in ir.header:
        lines.append(f"source_version: {ir.header['source_version']}")
    if "status" in ir.header:
        lines.append(f"status: {ir.header['status']}")
    lines.append(f'derived_from: {ir.header.get("source_artifact", "skill/cortex/SKILL.md")}')
    lines.append('-->')
    lines.append("")

    # 2. Profile
    lines.append("**Perfil: CORTEX-FULL**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 3. Render sections
    for sec_id in sorted(set(e.section for e in ir.entries if e.section), key=lambda x: int(x[1:])):
        _render_section(lines, ir, sec_id)

    return "\n".join(lines).rstrip() + "\n"


def _render_section(lines: List[str], ir: SkillIR, sec_id: str) -> None:
    """Render a single CORTEX section as HCORTEX."""
    hcortex_num = CORTEX_TO_HCORTEX_NUM.get(sec_id, sec_id[1:])
    title = SECTION_TITLES.get(sec_id, sec_id)
    entries = ir.get_entries(section=sec_id)

    if not entries:
        return

    lines.append(f"# {hcortex_num}. {title}")
    lines.append("")

    if sec_id == "$0":
        _render_glossary(lines, ir, entries)
    elif sec_id == "$1":
        _render_identity(lines, ir, entries)
    elif sec_id == "$2":
        _render_purpose(lines, ir, entries)
    elif sec_id == "$3":
        _render_handlers(lines, ir, entries)
    elif sec_id == "$4":
        _render_rules(lines, ir, entries)
    elif sec_id == "$5":
        _render_constraints(lines, ir, entries)
    elif sec_id == "$6":
        _render_diagrams(lines, ir, entries)
    elif sec_id == "$7":
        _render_contracts(lines, ir, entries)
    elif sec_id == "$8":
        _render_survival(lines, ir, entries)
    elif sec_id == "$9":
        _render_profiles(lines, ir, entries)
    elif sec_id == "$10":
        _render_degradation(lines, ir, entries)
    elif sec_id == "$11":
        _render_hcortex_directives(lines, ir, entries)
    elif sec_id == "$12":
        _render_cortex_out(lines, ir, entries)
    else:
        _render_generic(lines, ir, entries)

    lines.append("")


def _render_glossary(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $0 glossary as sigil table + types + micro + contracts."""
    # Sigil declarations
    sigil_decls = [e for e in entries if e.entry_type == "sigil_decl"]
    if sigil_decls:
        lines.append("## Sigilos canónicos")
        lines.append("")
        lines.append("| Sigilo | Nombre | Tipo | Riesgo | Capa | Descripción |")
        lines.append("|---|---|---|:---:|---|---|")
        for e in sigil_decls:
            v = e.value
            lines.append(
                f"| `{e.sigil}` | {e.name} | `{v.get('type', '')}` | "
                f"{v.get('risk', '')} | {v.get('cortex', '')} | {v.get('desc', '')} |"
            )
        lines.append("")

    # Type declarations
    type_decls = [e for e in entries if e.sigil == "$0" and e.name.startswith("type_")]
    if type_decls:
        lines.append("## Tipos de expansión")
        lines.append("")
        lines.append("| Tipo | Regla |")
        lines.append("|---|---|")
        for e in type_decls:
            type_name = e.name.replace("type_", "")
            lines.append(f"| `{type_name}` | {e.value.get('rule', '')} |")
        lines.append("")

    # Contract declarations
    contract_decls = [e for e in entries if e.sigil == "$0" and e.name.startswith("contract_")]
    if contract_decls:
        lines.append("## Contratos posicionales")
        lines.append("")
        lines.append("| Sigilo | Campos posicionales |")
        lines.append("|---|---|")
        for e in contract_decls:
            sigil_name = e.name.replace("contract_", "").upper()
            lines.append(f"| `{sigil_name}` | {e.value.get('pos', '')} |")
        lines.append("")

    # Micro-token declarations
    micro_decls = [e for e in entries if e.sigil == "$0" and e.name.startswith("micro_")]
    if micro_decls:
        lines.append("## Micro-glosario")
        lines.append("")
        lines.append("| Token | Expansión |")
        lines.append("|---|---|")
        for e in micro_decls:
            lines.append(f"| `{e.name.replace('micro_', '')}` | {e.value.get('expand', '')} |")
        lines.append("")

    # Enum declarations
    enum_decls = [e for e in entries if e.sigil == "$0" and e.name.startswith("enum_")]
    if enum_decls:
        lines.append("## Enumeraciones")
        lines.append("")
        for e in enum_decls:
            enum_name = e.name.replace("enum_", "")
            lines.append(f"**{enum_name}:** {e.value.get('values', '')}")
            lines.append("")


def _render_identity(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $1 identity entries."""
    for e in entries:
        if e.sigil == "IDN" and isinstance(e.value, dict):
            lines.append(f"## Identidad del proyecto")
            lines.append("")
            lines.append("| Campo | Valor |")
            lines.append("|---|---|")
            for k, v in e.value.items():
                lines.append(f"| {k} | {v} |")
            lines.append("")
        elif e.sigil == "DOM" and isinstance(e.value, dict):
            lines.append(f"## Dominio")
            lines.append("")
            lines.append("| Campo | Valor |")
            lines.append("|---|---|")
            for k, v in e.value.items():
                lines.append(f"| {k} | {v} |")
            lines.append("")
        elif e.sigil == "REF" and isinstance(e.value, dict):
            # Group REF entries into a table
            pass  # Will be handled in a batch

    # Render REF entries as a table
    ref_entries = [e for e in entries if e.sigil == "REF"]
    if ref_entries:
        lines.append("## Artefactos referenciados")
        lines.append("")
        lines.append("| Artefacto | Ruta | Rol |")
        lines.append("|---|---|---|")
        for e in ref_entries:
            v = e.value
            lines.append(f"| `{e.name}` | `{v.get('path', '')}` | {v.get('role', '')} |")
        lines.append("")


def _render_purpose(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $2 purpose/context entries."""
    for e in entries:
        if e.entry_type == "cuerpo":
            if e.sigil == "AXM":
                # Axioms as blockquotes
                lines.append(f"> {e.value}")
                lines.append("")
            else:
                # DESC as prose
                lines.append(e.value)
                lines.append("")
        elif e.sigil == "KNW" and isinstance(e.value, dict):
            lines.append(f"### {e.value.get('topic', e.name)}")
            lines.append("")
            lines.append(e.value.get('content', ''))
            lines.append("")


def _render_handlers(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $3 HDL handler entries."""
    for e in entries:
        if e.entry_type == "attrs-pos":
            v = e.value
            lines.append(f"## {e.name.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"**Operación:** {v.get('operation', '')}  ")
            lines.append(f"**Estado:** {v.get('status', '')}  ")
            lines.append(f"**Requiere:** {v.get('requires', '')}")
            lines.append("")
            notes = v.get('notes', '')
            if notes:
                lines.append(notes)
                lines.append("")


def _render_rules(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $4 ! rule entries as a table."""
    if entries:
        lines.append("## Reglas operacionales")
        lines.append("")
        lines.append("| Regla | survive |")
        lines.append("|---|---|")
        for e in entries:
            rule_text = e.value.get('rule', '') if isinstance(e.value, dict) else ''
            survive = e.value.get('survive', '') if isinstance(e.value, dict) else ''
            lines.append(f"| `!{e.name}` | {survive} |")
        lines.append("")


def _render_constraints(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $5 constraints, limits, risks, pitfalls."""
    cnst_entries = [e for e in entries if e.sigil == "CNST"]
    if cnst_entries:
        lines.append("## Restricciones")
        lines.append("")
        lines.append("| Restricción | Regla | Severidad | survive |")
        lines.append("|---|---|---|---|")
        for e in cnst_entries:
            v = e.value
            lines.append(f"| `{e.name}` | {v.get('rule', '')} | {v.get('severity', '')} | {v.get('survive', '')} |")
        lines.append("")

    lim_entries = [e for e in entries if e.sigil == "LIM"]
    if lim_entries:
        lines.append("## Límites")
        lines.append("")
        lines.append("| Límite | Alcance | Estado |")
        lines.append("|---|---|---|")
        for e in lim_entries:
            v = e.value
            lines.append(f"| `{e.name}` | {v.get('scope', '')} | {v.get('status', '')} |")
        lines.append("")

    rsk_entries = [e for e in entries if e.sigil == "RSK"]
    if rsk_entries:
        lines.append("## Riesgos")
        lines.append("")
        lines.append("| Riesgo | Impacto | Mitigación | Estado |")
        lines.append("|---|---|---|---|")
        for e in rsk_entries:
            v = e.value
            lines.append(f"| `{e.name}` | {v.get('impact', '')} | {v.get('mitigation', '')} | {v.get('status', '')} |")
        lines.append("")

    pfl_entries = [e for e in entries if e.sigil == "PFL"]
    if pfl_entries:
        lines.append("## Pitfalls")
        lines.append("")
        lines.append("| Patrón | Efecto | Prevención |")
        lines.append("|---|---|---|")
        for e in pfl_entries:
            v = e.value
            lines.append(f"| `{e.name}` | {v.get('effect', '')} | {v.get('prevention', '')} |")
        lines.append("")


def _render_diagrams(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $6 DIAG bloque entries as PUML blocks."""
    for e in entries:
        if e.entry_type == "bloque":
            lines.append(f"## {e.name}")
            lines.append("")
            lines.append("```puml")
            lines.append(e.value.strip())
            lines.append("```")
            lines.append("")


def _render_contracts(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $7 field contracts as a table."""
    if entries:
        lines.append("## Contratos mínimos por sigilo crítico")
        lines.append("")
        lines.append("| Sigilo | Campos requeridos | Severidad |")
        lines.append("|---|---|---|")
        for e in entries:
            v = e.value
            sigil_name = e.name.replace("contract_", "").upper()
            lines.append(f"| `{sigil_name}` | {v.get('rule', '')} | {v.get('severity', '')} |")
        lines.append("")


def _render_survival(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $8 survival/priorities."""
    for e in entries:
        if e.sigil == "KNW" and isinstance(e.value, dict):
            lines.append(f"### {e.value.get('topic', e.name)}")
            lines.append("")
            lines.append(e.value.get('content', ''))
            lines.append("")
        elif e.sigil == "!":
            v = e.value
            lines.append(f"- **`!{e.name}`**: {v.get('rule', '')}")
            lines.append("")


def _render_profiles(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $9 context profiles."""
    if entries:
        lines.append("## Perfiles de contexto")
        lines.append("")
        lines.append("| Perfil | Contenido | Estado |")
        lines.append("|---|---|---|")
        for e in entries:
            if isinstance(e.value, dict):
                v = e.value
                lines.append(f"| `{e.name}` | {v.get('content', '')} | {v.get('status', '')} |")
        lines.append("")


def _render_degradation(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $10 degradation rules."""
    for e in entries:
        v = e.value if isinstance(e.value, dict) else {}
        lines.append(f"- **`!{e.name}`**: {v.get('rule', '')}")
        lines.append("")


def _render_hcortex_directives(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $11 HCORTEX directives."""
    for e in entries:
        if e.entry_type == "cuerpo":
            lines.append(e.value)
            lines.append("")
        elif e.sigil == "KNW" and isinstance(e.value, dict):
            lines.append(f"### {e.value.get('topic', e.name)}")
            lines.append("")
            lines.append(e.value.get('content', ''))
            lines.append("")
        elif e.sigil == "!":
            v = e.value
            lines.append(f"- **`!{e.name}`**: {v.get('rule', '')}")
            lines.append("")
        elif e.sigil == "PFL" and isinstance(e.value, dict):
            v = e.value
            lines.append(f"- **{e.name}**: {v.get('pattern', '')} → {v.get('prevention', '')}")
            lines.append("")


def _render_cortex_out(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Render $12 CORTEX-OUT entries."""
    for e in entries:
        if e.entry_type == "cuerpo":
            lines.append(e.value)
            lines.append("")
        elif e.sigil == "AXM":
            lines.append(f"> {e.value}")
            lines.append("")
        elif e.sigil == "!":
            v = e.value
            lines.append(f"- **`!{e.name}`**: {v.get('rule', '')}")
            lines.append("")
        elif e.sigil == "KNW" and isinstance(e.value, dict):
            lines.append(f"### {e.value.get('topic', e.name)}")
            lines.append("")
            lines.append(e.value.get('content', ''))
            lines.append("")


def _render_generic(lines: List[str], ir: SkillIR, entries: List[IREntry]) -> None:
    """Generic renderer for unmapped sections."""
    for e in entries:
        if e.entry_type == "cuerpo" or e.entry_type == "bloque":
            lines.append(f"### {e.sigil}:{e.name}")
            lines.append("")
            if e.entry_type == "bloque":
                lines.append("```")
                lines.append(e.value.strip())
                lines.append("```")
            else:
                lines.append(e.value)
            lines.append("")
        elif isinstance(e.value, dict):
            lines.append(f"### {e.sigil}:{e.name}")
            lines.append("")
            lines.append("| Campo | Valor |")
            lines.append("|---|---|")
            for k, v in e.value.items():
                lines.append(f"| {k} | {v} |")
            lines.append("")
