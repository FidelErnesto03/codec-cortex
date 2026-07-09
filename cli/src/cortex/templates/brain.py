# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``brain.cortex`` template factory.

Builds a Nivel 2 operative brain with:
  - $0: minimal local glossary (autocontención)
  - $1: IDENTITY (IDN:agent, IDN:human, DOM:workspace)
  - $2: ACTIVE WORK (FCS:primary, OBJ:main, WRK:state, STP:next)
  - $3: GOVERNANCE (CNST:self_contained)

Mirrors Section 18.2 of SKILL.md.
"""

from __future__ import annotations


from ..core.ast import CortexDocument, Section
from ..core.parser import build_entry_from_value
from ..glossary.minimal import brain_sigils
from .minimal_glossary import build_minimal_glossary


def build_brain(
    name: str = "project-brain",
    domain: str = "active work",
    owner: str = "agent",
    language: str = "en",
    template: str = "standard",
    with_diagrams: bool = False,
) -> CortexDocument:
    """Return a fresh ``brain.cortex`` :class:`CortexDocument`."""

    doc = CortexDocument()
    doc.meta = {
        "path": "<template:brain>",
        "format": ".cortex",
        "version": "1.0.0",
        "hash": "",
    }
    doc.glossary = build_minimal_glossary(brain_sigils())

    # $0 section (will be serialised from the glossary at write-time)
    sec0 = Section(id="$0", title="MINIMAL LOCAL GLOSSARY")
    doc.sections.append(sec0)

    # $1 IDENTITY
    sec1 = Section(id="$1", title="IDENTITY")
    sec1.entries.append(build_entry_from_value(
        "$1", "IDN", "agent", "attrs",
        {"name": name, "role": "operator"},
    ))
    sec1.entries.append(build_entry_from_value(
        "$1", "IDN", "human", "attrs",
        {"name": "human", "role": "architect"},
    ))
    sec1.entries.append(build_entry_from_value(
        "$1", "DOM", "workspace", "attrs",
        {"name": "workspace", "area": domain, "protocol": "CODEC-CORTEX", "artifact": "brain.cortex"},
    ))
    doc.sections.append(sec1)

    # $2 ACTIVE WORK
    sec2 = Section(id="$2", title="ACTIVE WORK")
    sec2.entries.append(build_entry_from_value(
        "$2", "FCS", "primary", "attrs",
        {
            "name": "primary",
            "what": "current focus",
            "priority": "high",
            "status": "current",
            "survive": "min",
        },
    ))
    sec2.entries.append(build_entry_from_value(
        "$2", "OBJ", "main", "attrs",
        {
            "name": "main",
            "goal": "current objective",
            "status": "current",
            "success": "verifiable criterion",
            "survive": "min",
        },
    ))
    sec2.entries.append(build_entry_from_value(
        "$2", "WRK", "state", "attrs",
        {
            "name": "state",
            "phase": "active",
            "current": "work state",
            "blocked": False,
            "survive": "work",
        },
    ))
    sec2.entries.append(build_entry_from_value(
        "$2", "STP", "next", "attrs",
        {
            "name": "next",
            "action": "next action",
            "reason": "why",
            "owner": owner,
            "status": "current",
            "survive": "min",
        },
    ))
    if with_diagrams:
        sec2.entries.append(build_entry_from_value(
            "$2", "DIAG", "flow", "bloque",
            "@startuml\nA --> B\n@enduml",
        ))
    doc.sections.append(sec2)

    # $3 GOVERNANCE
    sec3 = Section(id="$3", title="GOVERNANCE")
    sec3.entries.append(build_entry_from_value(
        "$3", "CNST", "self_contained", "attrs",
        {
            "name": "self_contained",
            "rule": "This brain.cortex carries its own minimal $0 and does not require external glossary to begin safe interpretation.",
            "severity": "blocking",
            "survive": "min",
        },
    ))
    doc.sections.append(sec3)

    return doc
