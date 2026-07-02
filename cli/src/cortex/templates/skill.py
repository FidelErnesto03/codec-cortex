# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``SKILL.cortex`` template factory.

Builds a Nivel 1 (mind) skill document with:
  - $0: UNIVERSAL GLOSSARY
  - $1: IDENTITY (IDN:skill, DOM:protocol)
  - $2: AXIOMS (AXM:level_separation, AXM:self_contained)

Mirrors Section 18.1 of SKILL.md.
"""

from __future__ import annotations

from ..core.ast import CortexDocument, Section
from ..core.parser import build_entry_from_value
from ..glossary.minimal import skill_sigils
from .minimal_glossary import build_minimal_glossary


def build_skill(
    name: str = "codec-cortex",
    version: str = "1.0.0",
    domain: str = "LLM/SLM contextual memory",
    owner: str = "agent",
    language: str = "en",
    template: str = "standard",
    with_diagrams: bool = False,
) -> CortexDocument:
    doc = CortexDocument()
    doc.meta = {
        "path": "<template:skill>",
        "format": ".cortex",
        "version": version,
        "hash": "",
    }
    doc.glossary = build_minimal_glossary(skill_sigils())

    sec0 = Section(id="$0", title="UNIVERSAL GLOSSARY")
    doc.sections.append(sec0)

    sec1 = Section(id="$1", title="IDENTITY")
    sec1.entries.append(build_entry_from_value(
        "$1", "IDN", "skill", "attrs",
        {
            "name": name,
            "version": version,
            "status": "specification",
            "nature": "cognitive_memory_protocol",
        },
    ))
    sec1.entries.append(build_entry_from_value(
        "$1", "DOM", "protocol", "attrs",
        {
            "area": domain,
            "format": ".cortex",
            "memory_output": "HCORTEX",
            "conversational_output": "CORTEX-OUT",
        },
    ))
    doc.sections.append(sec1)

    sec2 = Section(id="$2", title="AXIOMS")
    sec2.entries.append(build_entry_from_value(
        "$2", "AXM", "level_separation", "cuerpo",
        "SKILL.cortex governs behavior and contracts. It never stores live working state.",
    ))
    sec2.entries.append(build_entry_from_value(
        "$2", "AXM", "self_contained", "cuerpo",
        "Every .cortex artifact must include a minimal $0 local glossary for safe interpretation.",
    ))
    doc.sections.append(sec2)

    sec3 = Section(id="$3", title="CONSTRAINTS")
    sec3.entries.append(build_entry_from_value(
        "$3", "CNST", "no_live_state_in_skill", "attrs",
        {
            "rule": "SKILL.cortex MUST NOT contain FCS/OBJ/WRK/STP/NXT as live state.",
            "severity": "blocking",
            "survive": "min",
        },
    ))
    doc.sections.append(sec3)

    if with_diagrams:
        sec6 = Section(id="$6", title="DIAGRAMS")
        sec6.entries.append(build_entry_from_value(
            "$6", "DIAG", "architecture", "bloque",
            "@startuml\n[A]-->[B]\n@enduml",
        ))
        doc.sections.append(sec6)

    return doc
