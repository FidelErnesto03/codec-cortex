"""Glossary package — minimal sigil sets, resolver, contracts."""

from .model import minimal_glossary, add_sigil, add_micro, add_contract, sigils_in_use
from .minimal import (
    brain_sigils, skill_sigils, package_sigils, generic_sigils, hdL_contract,
)
from .resolver import (
    is_canonical, is_declared, type_of, contract_of,
    expand_micro, sigil_usage_count, is_micro_used,
)
from .contracts import (
    get_contract, require_contract, declare_contract, DEFAULT_CONTRACTS,
)

__all__ = [
    "minimal_glossary", "add_sigil", "add_micro", "add_contract", "sigils_in_use",
    "brain_sigils", "skill_sigils", "package_sigils", "generic_sigils", "hdL_contract",
    "is_canonical", "is_declared", "type_of", "contract_of",
    "expand_micro", "sigil_usage_count", "is_micro_used",
    "get_contract", "require_contract", "declare_contract", "DEFAULT_CONTRACTS",
]
