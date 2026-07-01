"""Selectors — locate entries in a :class:`CortexDocument`.

Selector grammar (Section 12.1 of the spec):

    $SECTION/SIGIL:NAME     exact match
    SIGIL:NAME              match any section
    SIGIL:*                 all entries with that sigil
    $SECTION/*              all entries in a section

Wildcards ``*`` are supported on name and section.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..core.ast import CortexDocument, Entry, normalize_section_id
from ..core.errors import AmbiguousSelectorError, NotFoundError


@dataclass
class Selector:
    section: Optional[str]   # "$2" or "*" or None
    sigil: str               # "FCS" or "*"
    name: str                # "primary" or "*"

    def __str__(self) -> str:
        s = ""
        if self.section:
            s += f"{self.section}/"
        s += f"{self.sigil}:{self.name}"
        return s


def parse_selector(s: str) -> Selector:
    """Parse a selector string into a :class:`Selector`."""

    s = s.strip()
    if not s:
        raise ValueError("empty selector")
    # Split on /
    if "/" in s:
        section_part, rest = s.split("/", 1)
    else:
        section_part, rest = None, s
    # section_part may be "$2" or "*"
    if section_part == "*":
        section = "*"
    elif section_part:
        section = normalize_section_id(section_part)
    else:
        section = None
    # rest is "SIGIL:NAME" or "SIGIL:*" or "*"
    if ":" in rest:
        sigil, name = rest.split(":", 1)
    else:
        sigil, name = rest, "*"
    if sigil == "":
        sigil = "*"
    if name == "":
        name = "*"
    return Selector(section=section, sigil=sigil, name=name)


def select(doc: CortexDocument, selector_str: str) -> List[Entry]:
    """Return all entries that match ``selector_str``."""

    sel = parse_selector(selector_str)
    out: List[Entry] = []
    for sec, entry in doc.iter_entries():
        if sel.section and sel.section != "*":
            if sec.id != normalize_section_id(sel.section):
                continue
        if sel.sigil != "*" and entry.sigil != sel.sigil:
            continue
        if sel.name != "*" and entry.name != sel.name:
            continue
        out.append(entry)
    return out


def select_one(doc: CortexDocument, selector_str: str) -> Entry:
    """Return exactly one matching entry or raise.

    Raises :class:`NotFoundError` if 0 matches and
    :class:`AmbiguousSelectorError` if >1 matches.
    """

    matches = select(doc, selector_str)
    if not matches:
        raise NotFoundError(selector_str)
    if len(matches) > 1:
        raise AmbiguousSelectorError(selector_str, len(matches))
    return matches[0]
