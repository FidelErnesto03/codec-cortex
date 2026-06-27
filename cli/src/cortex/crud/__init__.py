"""CRUD package — selectors, mutations, atomic transactions."""

from .selectors import Selector, parse_selector, select, select_one
from .mutations import (
    add_entry, update_entry, delete_entry, move_entry,
    add_sigil_to_glossary, update_sigil_in_glossary, delete_sigil_from_glossary,
    add_micro_to_glossary, update_micro_in_glossary, delete_micro_from_glossary,
)
from .transactions import atomic_write_cortex, atomic_write_text, WriteResult

__all__ = [
    "Selector", "parse_selector", "select", "select_one",
    "add_entry", "update_entry", "delete_entry", "move_entry",
    "add_sigil_to_glossary", "update_sigil_in_glossary", "delete_sigil_from_glossary",
    "add_micro_to_glossary", "update_micro_in_glossary", "delete_micro_from_glossary",
    "atomic_write_cortex", "atomic_write_text", "WriteResult",
]
