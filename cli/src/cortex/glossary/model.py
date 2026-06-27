"""Glossary model and helpers.

Wraps the :class:`~cortex.core.ast.Glossary` with convenience builders
and queries used by templates, the CRUD layer and the CLI.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from ..core.ast import (
    AttrsPosContract,
    Glossary,
    MicroDef,
    SigilDef,
    TypeDef,
)
from ..core.errors import CANONICAL_MICRO


def minimal_glossary() -> Glossary:
    """Return a fresh glossary seeded with canonical types + micro-tokens.

    Sigils are *not* added here; the caller picks the relevant sigil set
    from :mod:`cortex.glossary.minimal` based on the template kind.
    """

    g = Glossary()
    # Canonical types
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
    return g


def add_sigil(glossary: Glossary, sigil: SigilDef) -> None:
    """Add a sigil, rejecting silent redefinition of existing ones."""

    existing = glossary.sigils.get(sigil.sigil)
    if existing is not None and existing.to_dict() != sigil.to_dict():
        from ..core.errors import ProtectedSigilError
        raise ProtectedSigilError(sigil.sigil)
    glossary.add_sigil(sigil)


def add_micro(glossary: Glossary, micro: MicroDef) -> None:
    existing = glossary.micro.get(micro.token)
    if existing is not None and existing.value != micro.value:
        from ..core.errors import CortexError
        raise CortexError(
            "E021_INVALID_VALUE",
            f"micro-token {micro.token!r} already declared with value {existing.value!r}",
        )
    glossary.add_micro(micro)


def add_contract(glossary: Glossary, contract: AttrsPosContract) -> None:
    glossary.add_contract(contract)


def sigils_in_use(glossary: Glossary, entries: Iterable) -> dict:
    """Return ``{sigil: count}`` for sigils used by ``entries``."""

    counts: dict = {}
    for e in entries:
        if e.sigil in {"GSIG", "GTYP", "GMIC", "GCON"}:
            continue
        counts[e.sigil] = counts.get(e.sigil, 0) + 1
    return counts
