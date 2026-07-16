# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Nivel 3 ``package.cortex`` template factory.

Builds a transportable context package with:
  - $0: minimal local glossary
  - $1: PACKAGE IDENTITY (IDN:package, DOM:scope)
  - $2: CONTENT (KNW:topic, REF:source)
  - $3: LIMITS (LIM:package_lifecycle, CLAIM:self_contained)

Mirrors Section 18.3 of SKILL.md.
"""

from __future__ import annotations

from ..core.ast import CortexDocument, Section
from ..core.parser import build_entry_from_value
from ..glossary.minimal import package_sigils
from .minimal_glossary import build_minimal_glossary


def build_package(
    name: str = "context_package",
    version: str = "0.1.0",
    domain: str = "specific domain",
    owner: str = "source",
    language: str = "en",
    template: str = "standard",
    with_diagrams: bool = False,
) -> CortexDocument:
    doc = CortexDocument()
    doc.meta = {
        "path": "<template:package>",
        "format": ".cortex",
        "version": version,
        "hash": "",
    }
    doc.glossary = build_minimal_glossary(package_sigils())

    sec0 = Section(id="$0", title="MINIMAL LOCAL GLOSSARY")
    doc.sections.append(sec0)

    sec1 = Section(id="$1", title="PACKAGE IDENTITY")
    sec1.entries.append(build_entry_from_value(
        "$1", "IDN", "package", "attrs",
        {"name": name, "version": version, "status": "current"},
    ))
    sec1.entries.append(build_entry_from_value(
        "$1", "DOM", "scope", "attrs",
        {"area": domain, "owner": owner, "purpose": "context injection"},
    ))
    doc.sections.append(sec1)

    sec2 = Section(id="$2", title="CONTENT")
    sec2.entries.append(build_entry_from_value(
        "$2", "KNW", "topic", "attrs",
        {
            "topic": "domain concept",
            "content": "compressed knowledge",
            "status": "current",
        },
    ))
    sec2.entries.append(build_entry_from_value(
        "$2", "REF", "source", "attrs",
        {"PATH": "source.md", "purpose": "traceability"},
    ))
    if with_diagrams:
        sec2.entries.append(build_entry_from_value(
            "$2", "DIAG", "overview", "bloque",
            "@startuml\n[A]-->[B]\n@enduml",
        ))
    doc.sections.append(sec2)

    sec3 = Section(id="$3", title="LIMITS")
    sec3.entries.append(build_entry_from_value(
        "$3", "LIM", "package_lifecycle", "attrs",
        {
            "limit": "package does not mature by itself until formally absorbed by Level 2",
            "scope": "level_3",
            "status": "current",
        },
    ))
    sec3.entries.append(build_entry_from_value(
        "$3", "CLAIM", "self_contained", "attrs",
        {
            "statement": "This package includes its own minimal $0 for safe initial interpretation.",
            "evidence": "$0 section present",
            "status": "current",
        },
    ))
    doc.sections.append(sec3)

    return doc
