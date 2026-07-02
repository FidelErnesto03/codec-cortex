# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""HCORTEX profile resolver and priority classifier.

Implements audit gaps B-003, B-004, H-03:

- ``ProfileResolver`` maps a profile name to a P-level budget:
    MIN      → P0
    RECOVERY → P0 + P1
    WORK     → P0 + P1 + P2
    FULL     → P0..P5
- ``PriorityClassifier`` assigns each entry a P-level based on its sigil
  and ``survive``/``severity`` attributes, per Section 11.2 of SKILL.md.
- ``filter_by_profile()`` returns the entries that survive the profile.
- ``sort_by_plevel()`` orders entries P0 → P5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..core.ast import CortexDocument, Entry
from ..core.errors import (
    PLEVEL_ORDER,
    SIGIL_DEFAULT_PLEVEL,
    SURVIVE_TO_PLEVEL,
)


# ---------------------------------------------------------------------------
# Profile definitions (Section 11.4 of SKILL.md)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Profile:
    name: str               # MIN | RECOVERY | WORK | FULL
    plevels: Tuple[str, ...]  # P-levels included
    token_budget: Optional[int] = None  # orientative; None = unlimited

    def includes(self, plevel: str) -> bool:
        return plevel in self.plevels


PROFILES: Dict[str, Profile] = {
    "MIN":      Profile("MIN",      ("P0",),                        512),
    "RECOVERY": Profile("RECOVERY", ("P0", "P1"),                  1024),
    "WORK":     Profile("WORK",     ("P0", "P1", "P2"),            3072),
    "FULL":     Profile("FULL",     tuple(PLEVEL_ORDER),           None),
}

# Order of preference for default resolution (Section 9.3 of SKILL.md):
#   explicit > budget > mode > CORTEX-WORK
DEFAULT_PROFILE = "WORK"


def resolve_profile(name: Optional[str] = None) -> Profile:
    """Resolve a profile name to a :class:`Profile`.

    Unknown names raise ``ValueError``.  ``None`` returns the default
    (``WORK``).
    """

    if name is None:
        return PROFILES[DEFAULT_PROFILE]
    key = name.upper()
    if key not in PROFILES:
        raise ValueError(
            f"unknown HCORTEX profile {name!r}; "
            f"expected one of {sorted(PROFILES)}"
        )
    return PROFILES[key]


# ---------------------------------------------------------------------------
# Priority classifier
# ---------------------------------------------------------------------------

def classify_entry(entry: Entry) -> str:
    """Return the P-level (``P0``..``P5``) for ``entry``.

    Rules (Section 11.2 + 11.3 of SKILL.md):
      1. ``survive:min``    → P0
      2. ``survive:recovery``→ P1
      3. ``survive:work``   → P2
      4. ``survive:full``   → P5
      5. ``severity:blocking`` on CNST → P0 (overrides sigil default)
      6. Otherwise: sigil default (see :data:`SIGIL_DEFAULT_PLEVEL`)
      7. Unknown sigil: P5 (lowest priority)
    """

    if isinstance(entry.value, dict):
        survive = entry.value.get("survive")
        if isinstance(survive, str) and survive in SURVIVE_TO_PLEVEL:
            # `min` always wins over everything else (it's the most critical)
            return SURVIVE_TO_PLEVEL[survive]
        severity = entry.value.get("severity")
        if severity == "blocking":
            return "P0"
    return SIGIL_DEFAULT_PLEVEL.get(entry.sigil, "P5")


def classify_doc(doc: CortexDocument) -> Dict[str, List[Tuple[Entry, str]]]:
    """Return ``{section_id: [(entry, plevel), ...]}`` for the whole doc."""

    out: Dict[str, List[Tuple[Entry, str]]] = {}
    for sec in doc.sections:
        if sec.id == "$0":
            continue
        out[sec.id] = [(e, classify_entry(e)) for e in sec.entries]
    return out


def plevel_rank(plevel: str) -> int:
    """Return sort rank for a P-level (P0=0, P5=5)."""

    if plevel in PLEVEL_ORDER:
        return PLEVEL_ORDER.index(plevel)
    return len(PLEVEL_ORDER)


# ---------------------------------------------------------------------------
# Profile filtering
# ---------------------------------------------------------------------------

@dataclass
class ProfileFilterResult:
    """Result of filtering a document by profile.

    ``kept`` contains the entries that survived; ``omitted`` lists the
    entries that were dropped (with reason) so the renderer can declare
    them explicitly per Section 9.3 of the SKILL.
    """

    kept: List[Tuple[str, Entry, str]]  # (section_id, entry, plevel)
    omitted: List[Tuple[str, Entry, str, str]]  # (section_id, entry, plevel, reason)


def filter_by_profile(doc: CortexDocument, profile: Profile) -> ProfileFilterResult:
    """Filter ``doc`` entries by ``profile``, preserving section grouping.

    The output is flat (list of ``(section_id, entry, plevel)``) but
    keeps section grouping via the ``section_id`` field.  The renderer
    decides whether to render per-section or flat.
    """

    kept: List[Tuple[str, Entry, str]] = []
    omitted: List[Tuple[str, Entry, str, str]] = []
    for sec in doc.sections:
        if sec.id == "$0":
            continue
        for entry in sec.entries:
            plevel = classify_entry(entry)
            if profile.includes(plevel):
                kept.append((sec.id, entry, plevel))
            else:
                omitted.append((sec.id, entry, plevel, f"excluded by profile {profile.name}"))
    # Sort kept by P0..P5 (within each section, entries keep original order)
    kept.sort(key=lambda t: plevel_rank(t[2]))
    return ProfileFilterResult(kept=kept, omitted=omitted)


def sort_by_plevel(
    entries: List[Tuple[str, Entry, str]],
) -> List[Tuple[str, Entry, str]]:
    """Stable-sort entries by P-level (P0 first, P5 last)."""

    return sorted(entries, key=lambda t: plevel_rank(t[2]))
