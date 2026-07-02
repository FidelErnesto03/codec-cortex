# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Positional contracts for ``attrs-pos`` sigils.

A contract is the ordered list of field names that the parser must use
when splitting a positional body.  Contracts live in ``$0`` and are
declared via ``# contract: SIGIL | field1 | field2 | ...`` or via
explicit ``GCON:SIGIL{sigil:"SIGIL", fields:"f1|f2"}`` entries.
"""

from __future__ import annotations

from typing import List, Optional

from ..core.ast import AttrsPosContract, Glossary
from ..core.errors import AttrsPosContractMissingError


def get_contract(glossary: Glossary, sigil: str) -> Optional[AttrsPosContract]:
    return glossary.contracts.get(sigil)


def require_contract(glossary: Glossary, sigil: str) -> AttrsPosContract:
    c = get_contract(glossary, sigil)
    if c is None:
        raise AttrsPosContractMissingError(sigil)
    return c


def declare_contract(glossary: Glossary, sigil: str, fields: List[str]) -> AttrsPosContract:
    c = AttrsPosContract(sigil=sigil, fields=list(fields))
    glossary.add_contract(c)
    return c


# Default contracts for canonical attrs-pos sigils (Section 6)
DEFAULT_CONTRACTS = {
    "HDL": ["operation", "status", "requires"],
}
