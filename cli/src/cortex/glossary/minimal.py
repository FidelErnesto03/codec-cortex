"""Minimal sigil sets per template kind.

Each function returns a list of :class:`~cortex.core.ast.SigilDef`
appropriate for the template (brain / skill / package / generic).
"""

from __future__ import annotations

from typing import List

from ..core.ast import SigilDef


def brain_sigils() -> List[SigilDef]:
    """Sigils for a ``brain.cortex`` template (Nivel 2 operativo)."""

    return [
        SigilDef("IDN", "identity",   "attrs",  "B", "Semantic",   "Actor or memory identity"),
        SigilDef("DOM", "domain",     "attrs",  "B", "Semantic",   "Operating domain or scope"),
        SigilDef("CNST","constraint", "attrs",  "H", "Prefrontal", "Hard operational boundary"),
        SigilDef("FCS", "focus",      "attrs",  "H", "Working",    "Active attention anchor"),
        SigilDef("OBJ", "objective",  "attrs",  "H", "Working",    "Active goal with success criterion"),
        SigilDef("WRK", "work",       "attrs",  "M", "Working",    "Current operational state"),
        SigilDef("STP", "step",       "attrs",  "M", "Working",    "Immediate next action"),
        SigilDef("NXT", "next",       "attrs",  "M", "Working",    "Queued next action"),
        SigilDef("RSK", "risk",       "attrs",  "M", "Prefrontal", "Risk and mitigation"),
        SigilDef("AUD", "audit",      "attrs",  "M", "Prefrontal", "Audit or verification record"),
        SigilDef("STAT","status",     "attrs",  "B", "Semantic",   "Status or maturity declaration"),
        SigilDef("REF", "reference",  "attrs",  "B", "Semantic",   "File, object or source reference"),
        SigilDef("KNW", "knowledge",  "attrs",  "B", "Semantic",   "Stable or promoted knowledge"),
        SigilDef("SES", "session",    "attrs",  "M", "Episodic",   "Compressed episode I/O/R"),
        SigilDef("LNG", "lesson",     "attrs",  "M", "Episodic",   "Lesson or pattern"),
        SigilDef("DIAG","diagram",    "bloque", "M", "Episodic/Visual", "Verbatim diagram block"),
        SigilDef("!",   "rule",       "attrs",  "H", "Prefrontal", "Mandatory compact rule"),
    ]


def skill_sigils() -> List[SigilDef]:
    """Sigils for a ``SKILL.cortex`` template (Nivel 1)."""

    return [
        SigilDef("IDN", "identity",   "attrs",  "B", "Semantic",   "Skill identity"),
        SigilDef("DOM", "domain",     "attrs",  "B", "Semantic",   "Adoption scope and context"),
        SigilDef("AXM", "axiom",      "cuerpo", "H", "Prefrontal", "Non-negotiable principle"),
        SigilDef("CNST","constraint", "attrs",  "H", "Prefrontal", "Hard operational boundary"),
        SigilDef("KNW", "knowledge",  "attrs",  "B", "Semantic",   "Protocol knowledge"),
        SigilDef("HDL", "handler",    "attrs-pos","M","Semantic",  "Operation descriptor (positional)"),
        SigilDef("STAT","status",     "attrs",  "B", "Semantic",   "Status or maturity declaration"),
        SigilDef("DIAG","diagram",    "bloque", "M", "Episodic/Visual", "Normative diagram"),
        SigilDef("REF", "reference",  "attrs",  "B", "Semantic",   "Source or cross-reference"),
        SigilDef("RSK", "risk",       "attrs",  "M", "Prefrontal", "Protocol risk and mitigation"),
        SigilDef("AUD", "audit",      "attrs",  "M", "Prefrontal", "Spec audit record"),
        SigilDef("!",   "rule",       "attrs",  "H", "Prefrontal", "Mandatory compact rule"),
    ]


def package_sigils() -> List[SigilDef]:
    """Sigils for a Nivel 3 ``*.cortex`` package."""

    return [
        SigilDef("IDN", "identity",   "attrs",  "B", "Semantic",   "Package identity"),
        SigilDef("DOM", "domain",     "attrs",  "B", "Semantic",   "Scope and purpose"),
        SigilDef("KNW", "knowledge",  "attrs",  "B", "Semantic",   "Compressed knowledge"),
        SigilDef("REF", "reference",  "attrs",  "B", "Semantic",   "Source or traceability reference"),
        SigilDef("LIM", "limit",      "attrs",  "M", "Prefrontal", "Explicit operational limit"),
        SigilDef("CLAIM","claim",     "attrs",  "M", "Prefrontal", "Verifiable assertion"),
        SigilDef("DIAG","diagram",    "bloque", "M", "Episodic/Visual", "Verbatim diagram block"),
        SigilDef("STAT","status",     "attrs",  "B", "Semantic",   "Status declaration"),
        SigilDef("AUD", "audit",      "attrs",  "M", "Prefrontal", "Audit record"),
        SigilDef("RSK", "risk",       "attrs",  "M", "Prefrontal", "Risk and mitigation"),
    ]


def generic_sigils() -> List[SigilDef]:
    """A superset sigil set for generic ``.cortex`` files."""

    return brain_sigils() + [
        SigilDef("AXM", "axiom",      "cuerpo", "H", "Prefrontal", "Non-negotiable principle"),
        SigilDef("CLAIM","claim",     "attrs",  "M", "Prefrontal", "Verifiable assertion"),
        SigilDef("LIM", "limit",      "attrs",  "M", "Prefrontal", "Explicit operational limit"),
        SigilDef("HDL", "handler",    "attrs-pos","M","Semantic",  "Operation descriptor (positional)"),
        SigilDef("TAG", "tag",        "attrs",  "B", "Semantic",   "Classification metadata"),
        SigilDef("PFL", "pitfall",    "attrs",  "M", "Prefrontal", "Known antipattern"),
        SigilDef("DEP", "dependency", "attrs",  "M", "Semantic",   "Cross-artefact dependency"),
        SigilDef("DESC","description","cuerpo", "B", "Semantic",   "Structured description"),
        SigilDef("ERR", "error",      "attrs",  "M", "Prefrontal", "Known error with cause/solution"),
    ]


def hdL_contract():
    """Default positional contract for ``HDL`` (operation | status | requires)."""

    from ..core.ast import AttrsPosContract
    return AttrsPosContract(sigil="HDL", fields=["operation", "status", "requires"])
