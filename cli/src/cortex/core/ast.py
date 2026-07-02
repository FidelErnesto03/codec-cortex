# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Canonical AST for CODEC-CORTEX.

The AST is the *only* internal representation of a ``.cortex`` document.
Every parser, renderer, compiler and CRUD operation goes through the AST.

The dataclasses below mirror Section 5.1 of the specification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Glossary model
# ---------------------------------------------------------------------------

@dataclass
class SigilDef:
    """A sigil declaration from ``$0``.

    Fields mirror the canonical pipe-separated table:
    ``SIGIL | NAME | TYPE | RISK | LAYER | DESCRIPTION``.
    """

    sigil: str
    name: str
    type: str
    risk: str = "M"
    layer: str = "Semantic"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sigil": self.sigil,
            "name": self.name,
            "type": self.type,
            "risk": self.risk,
            "layer": self.layer,
            "description": self.description,
        }


@dataclass
class TypeDef:
    """An expansion-type declaration from ``$0``."""

    name: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description}


@dataclass
class MicroDef:
    """A micro-token declaration from ``$0``."""

    token: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"token": self.token, "value": self.value}


@dataclass
class AttrsPosContract:
    """Positional contract for an ``attrs-pos`` sigil.

    ``fields`` is the ordered list of field names declared in ``$0``.
    """

    sigil: str
    fields: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"sigil": self.sigil, "fields": list(self.fields)}


@dataclass
class Glossary:
    """Local ``$0`` glossary attached to a :class:`CortexDocument`."""

    sigils: Dict[str, SigilDef] = field(default_factory=dict)
    types: Dict[str, TypeDef] = field(default_factory=dict)
    micro: Dict[str, MicroDef] = field(default_factory=dict)
    contracts: Dict[str, AttrsPosContract] = field(default_factory=dict)

    def add_sigil(self, sigil: SigilDef) -> None:
        self.sigils[sigil.sigil] = sigil

    def add_type(self, t: TypeDef) -> None:
        self.types[t.name] = t

    def add_micro(self, m: MicroDef) -> None:
        self.micro[m.token] = m

    def add_contract(self, c: AttrsPosContract) -> None:
        self.contracts[c.sigil] = c

    def sigil_type(self, sigil: str) -> Optional[str]:
        s = self.sigils.get(sigil)
        return s.type if s else None

    def contract_for(self, sigil: str) -> Optional[AttrsPosContract]:
        return self.contracts.get(sigil)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sigils": {k: v.to_dict() for k, v in self.sigils.items()},
            "types": {k: v.to_dict() for k, v in self.types.items()},
            "micro": {k: v.to_dict() for k, v in self.micro.items()},
            "contracts": {k: v.to_dict() for k, v in self.contracts.items()},
        }


# ---------------------------------------------------------------------------
# Entry / Section / Document
# ---------------------------------------------------------------------------

@dataclass
class Entry:
    """A single ``SIGIL:name{...}`` entry inside a section."""

    section: str
    sigil: str
    name: str
    type: str  # attrs | attrs-pos | cuerpo | bloque | relación
    value: Any  # dict | str | list (depends on type)
    raw: str = ""  # original text (for bloque verbatim)
    line_start: int = 0
    line_end: int = 0
    hash: str = ""
    entry_id: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = compute_entry_hash(self)
        if not self.entry_id:
            self.entry_id = self.hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "section": self.section,
            "sigil": self.sigil,
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "raw": self.raw,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "hash": self.hash,
        }


@dataclass
class Section:
    """A numbered ``$N`` section inside a :class:`CortexDocument`."""

    id: str  # e.g. "$0", "$1"
    title: str = ""
    entries: List[Entry] = field(default_factory=list)
    line_start: int = 0
    # Raw comment lines preserved verbatim — used by $0 glossary parser
    # and by the writer when re-serialising a section.
    comments: List[str] = field(default_factory=list)
    # Raw non-comment, non-entry lines (rare; recorded for round-trip safety)
    raw_lines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "entries": [e.to_dict() for e in self.entries],
            "line_start": self.line_start,
            "comments": list(self.comments),
        }


@dataclass
class CortexDocument:
    """Canonical AST root for a ``.cortex`` document.

    Mirrors Section 5.1 of the spec.
    """

    meta: Dict[str, Any] = field(default_factory=dict)
    glossary: Glossary = field(default_factory=Glossary)
    sections: List[Section] = field(default_factory=list)
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)

    # --- convenience helpers -------------------------------------------------

    @property
    def section_ids(self) -> List[str]:
        return [s.id for s in self.sections]

    def get_section(self, section_id: str) -> Optional[Section]:
        # Normalize "$2", "2", "$2: x" forms
        norm = normalize_section_id(section_id)
        for s in self.sections:
            if s.id == norm:
                return s
        return None

    def get_or_create_section(self, section_id: str, title: str = "") -> Section:
        sec = self.get_section(section_id)
        if sec is not None:
            return sec
        norm = normalize_section_id(section_id)
        sec = Section(id=norm, title=title)
        self.sections.append(sec)
        return sec

    def iter_entries(self):
        for sec in self.sections:
            for e in sec.entries:
                yield sec, e

    def find_entries(self, sigil: Optional[str] = None, name: Optional[str] = None,
                     section: Optional[str] = None) -> List[Entry]:
        out: List[Entry] = []
        for sec, e in self.iter_entries():
            if section is not None and sec.id != normalize_section_id(section):
                continue
            if sigil is not None and e.sigil != sigil:
                continue
            if name is not None and e.name != name:
                continue
            out.append(e)
        return out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": dict(self.meta),
            "glossary": self.glossary.to_dict(),
            "sections": [s.to_dict() for s in self.sections],
            "diagnostics": list(self.diagnostics),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, sort_keys=False)


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------

def compute_entry_hash(entry: Entry) -> str:
    """Stable structural hash of an entry.

    The hash is computed over the *canonical* representation
    (sigil, name, type, value) — not the raw text — so equivalent
    entries that differ only in formatting still hash identically.
    ``bloque`` entries include the verbatim raw text in the hash.
    """

    if entry.type == "bloque":
        payload = {
            "sigil": entry.sigil,
            "name": entry.name,
            "type": entry.type,
            "raw": entry.raw,
        }
    else:
        payload = {
            "sigil": entry.sigil,
            "name": entry.name,
            "type": entry.type,
            "value": entry.value,
        }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def compute_document_hash(text: str) -> str:
    blob = text.encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# Section id normalization
# ---------------------------------------------------------------------------

def normalize_section_id(section_id: str) -> str:
    """Normalize section identifiers.

    Accepts:
      - ``"$2"``        → ``"$2"``
      - ``"2"``         → ``"$2"``
      - ``"$2: TITLE"`` → ``"$2"``
      - ``"$2 · TITLE"``→ ``"$2"``
    """

    if section_id is None:
        return "$0"
    s = section_id.strip()
    if not s:
        return "$0"
    if not s.startswith("$"):
        # accept "2" or "2: title"
        if s.split(":", 1)[0].strip().isdigit():
            return "$" + s.split(":", 1)[0].strip()
        return "$" + s
    # already starts with $
    head = s[1:].split(":", 1)[0].split("·", 1)[0].strip()
    if head.isdigit():
        return "$" + head
    return s
