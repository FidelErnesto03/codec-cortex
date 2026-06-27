"""Minimal-glossary factory — produces a fully-seeded :class:`Glossary`.

The minimal glossary always includes the canonical expansion types
(attrs, attrs-pos, cuerpo, bloque, relación) and the canonical
micro-tokens (Section 4.1.1 of SKILL.md).  Sigils are added by the
template factories (brain / skill / package / generic).
"""

from __future__ import annotations

from typing import List

from ..core.ast import AttrsPosContract, Glossary, SigilDef, TypeDef, MicroDef
from ..core.errors import CANONICAL_MICRO
from ..glossary.contracts import DEFAULT_CONTRACTS


def build_minimal_glossary(sigils: List[SigilDef]) -> Glossary:
    """Build a glossary from a list of sigils + canonical types/micro."""

    g = Glossary()
    # Canonical expansion types
    for name, desc in [
        ("attrs", "key:value pairs"),
        ("attrs-pos", "positional with explicit contract"),
        ("cuerpo", "free text body"),
        ("bloque", "verbatim multiline block"),
        ("relación", "causal A -> B form"),
    ]:
        g.add_type(TypeDef(name=name, description=desc))
    # Canonical micro-tokens
    for tok, val in CANONICAL_MICRO.items():
        g.add_micro(MicroDef(token=tok, value=val))
    # Sigils provided by the caller
    for sd in sigils:
        g.add_sigil(sd)
    # Default contracts for attrs-pos sigils in the sigil set
    sigil_names = {sd.sigil for sd in sigils}
    for sig, fields in DEFAULT_CONTRACTS.items():
        if sig in sigil_names:
            g.add_contract(AttrsPosContract(sigil=sig, fields=list(fields)))
    return g
