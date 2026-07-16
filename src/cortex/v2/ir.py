# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

r"""SkillIR — Intermediate Representation for bidirectional CORTEX ⇄ HCORTEX.

The IR preserves:
  - CORTEX entries (sigil, name, type, value, section, raw)
  - HCORTEX blocks (heading path, kind, raw markdown, source mapping)
  - Mappings between CORTEX entries and HCORTEX blocks
  - Human blocks (HCORTEX content not derivable from CORTEX)
  - Warnings (orphan content, ambiguities, unmapped entries)

The IR is the single source of truth for conversion:
  CORTEX → parse_cortex_v2 → SkillIR → render_hcortex_v2 → HCORTEX
  HCORTEX → parse_hcortex_v2 → SkillIR → write_cortex_v2 → CORTEX
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from .parser import CortexV2Document, V2Entry, V2Section


# ---------------------------------------------------------------------------
# IR data model
# ---------------------------------------------------------------------------

@dataclass
class IREntry:
    """A CORTEX entry in the IR."""
    sigil: str
    name: str
    entry_type: str  # attrs | attrs-pos | cuerpo | bloque | sigil_decl | meta
    value: Any
    section: str = ""
    raw: str = ""
    # Mapping to HCORTEX block(s) this entry was rendered into
    hcortex_blocks: List[str] = field(default_factory=list)  # block IDs

    def to_dict(self) -> dict:
        return {
            "sigil": self.sigil, "name": self.name, "type": self.entry_type,
            "value": self.value, "section": self.section,
        }


@dataclass
class IRBlock:
    """An HCORTEX block in the IR."""
    block_id: str  # unique ID
    heading_path: str  # e.g. "4.2" or "9.6.1"
    heading_text: str  # e.g. "Sigilos canónicos"
    kind: str  # table | prose | puml | list | checklist | code | blockquote
    raw_markdown: str  # the actual markdown content
    # Mapping to CORTEX entry(ies) this block was derived from
    source_entries: List[Tuple[str, str]] = field(default_factory=list)  # [(sigil, name), ...]
    # Whether this block is derivable from CORTEX or is human-added
    derivable: bool = True

    def to_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "heading_path": self.heading_path,
            "heading_text": self.heading_text,
            "kind": self.kind,
            "source_entries": self.source_entries,
            "derivable": self.derivable,
        }


@dataclass
class IRWarning:
    """A warning about content that couldn't be mapped."""
    code: str
    message: str
    severity: str = "warning"  # warning | info


@dataclass
class SkillIR:
    """Intermediate Representation for bidirectional CORTEX ⇄ HCORTEX.

    This is the single source of truth for conversion.  Both CORTEX
    and HCORTEX parse into this IR, and both render from it.
    """
    header: Dict[str, str] = field(default_factory=dict)
    entries: List[IREntry] = field(default_factory=list)
    blocks: List[IRBlock] = field(default_factory=list)
    warnings: List[IRWarning] = field(default_factory=list)
    # Section structure: list of (section_id, hcortex_num, hcortex_title) for HCORTEX rendering
    section_map: List[Tuple[str, str, str]] = field(default_factory=list)

    def add_entry(self, entry: V2Entry) -> IREntry:
        ir_entry = IREntry(
            sigil=entry.sigil, name=entry.name, entry_type=entry.entry_type,
            value=entry.value, section=entry.section, raw=entry.raw,
        )
        self.entries.append(ir_entry)
        return ir_entry

    def add_block(self, block: IRBlock) -> None:
        self.blocks.append(block)

    def add_warning(self, code: str, message: str, severity: str = "warning") -> None:
        self.warnings.append(IRWarning(code=code, message=message, severity=severity))

    def get_entries(self, sigil: str | None = None, section: str | None = None) -> List[IREntry]:
        result = []
        for e in self.entries:
            if sigil and e.sigil != sigil:
                continue
            if section and e.section != section:
                continue
            result.append(e)
        return result

    def to_dict(self) -> dict:
        return {
            "header": dict(self.header),
            "entries": [e.to_dict() for e in self.entries],
            "blocks": [b.to_dict() for b in self.blocks],
            "warnings": [{"code": w.code, "message": w.message, "severity": w.severity} for w in self.warnings],
            "section_map": self.section_map,
        }


# ---------------------------------------------------------------------------
# CORTEX → IR
# ---------------------------------------------------------------------------

def cortex_to_ir(doc: CortexV2Document) -> SkillIR:
    """Convert a parsed CORTEX v2 document into a SkillIR."""
    ir = SkillIR()
    ir.header = dict(doc.header)

    for sec in doc.sections:
        for entry in sec.entries:
            ir.add_entry(entry)

    # Build section map for HCORTEX rendering
    _build_section_map(ir, doc)

    return ir


def _build_section_map(ir: SkillIR, doc: CortexV2Document) -> None:
    """Build the mapping from CORTEX sections to HCORTEX section numbers.

    This mapping is based on the analysis of the canonical SKILL.md ↔ SKILL_HCORTEX.md pair.
    """
    # Mapping: CORTEX $N → HCORTEX section number(s)
    SECTION_MAP = {
        "$0": [("4", "Glosario cognitivo universal"),
               ("4.1", "Regla de autoridad y autocontención"),
               ("4.2", "Sigilos canónicos"),
               ("4.3", "Tipos de expansión"),
               ("4.4", "Micro-glosario")],
        "$1": [("0", "Control del documento"),
               ("0.1", "Relación con otros artefactos")],
        "$2": [("1", "Resumen ejecutivo"),
               ("1.1", "Canon mínimo"),
               ("1.2", "META-SKILL"),
               ("1.3", "Problema que resuelve"),
               ("1.4", "Principio rector"),
               ("3", "Ontología cognitiva")],
        "$3": [("8", "Operación de agentes")],
        "$4": [("5", "Sintaxis .cortex"),
               ("9.6", "Directrices canónicas de construcción documental HCORTEX")],
        "$5": [("7", "Reglas de separación de niveles"),
               ("20", "Pitfalls empresariales")],
        "$6": [("2.1", "Diagrama canónico"),
               ("3.1", "Diagrama de capas"),
               ("8.1", "Secuencia mínima al iniciar"),
               ("8.3", "Al absorber un paquete Nivel 3"),
               ("9.4", "Diagrama HCORTEX")],
        "$7": [("6", "Contratos mínimos por sigilo crítico")],
        "$8": [("11", "Supervivencia contextual y triaje P0-P5")],
        "$9": [("9.6.3", "Perfiles de contexto"),
               ("11.4", "Perfiles")],
        "$10": [("11.1", "Principio"),
                ("11.5", "Diagrama de degradación")],
        "$11": [("9", "HCORTEX"),
                ("9.6", "Directrices canónicas de construcción documental HCORTEX")],
        "$12": [("10", "CORTEX-OUT")],
    }

    for sec in doc.sections:
        if sec.id in SECTION_MAP:
            for hcortex_num, hcortex_title in SECTION_MAP[sec.id]:
                ir.section_map.append((sec.id, hcortex_num, hcortex_title))
        else:
            ir.add_warning("UNMAPPED_SECTION", f"section {sec.id} has no HCORTEX mapping")


# ---------------------------------------------------------------------------
# IR → CORTEX
# ---------------------------------------------------------------------------

def ir_to_cortex(ir: SkillIR) -> CortexV2Document:
    """Convert a SkillIR back to a CortexV2Document for writing."""
    doc = CortexV2Document()
    doc.header = dict(ir.header)

    # Group entries by section
    sections_map: Dict[str, V2Section] = {}
    for ir_entry in ir.entries:
        sec_id = ir_entry.section or "$0"
        if sec_id not in sections_map:
            sections_map[sec_id] = V2Section(id=sec_id)
        v2_entry = V2Entry(
            sigil=ir_entry.sigil,
            name=ir_entry.name,
            entry_type=ir_entry.entry_type,
            value=ir_entry.value,
            raw=ir_entry.raw,
            section=sec_id,
        )
        sections_map[sec_id].entries.append(v2_entry)

    # Sort sections by number
    for sec_id in sorted(sections_map.keys(), key=lambda x: int(x[1:])):
        doc.sections.append(sections_map[sec_id])

    return doc
