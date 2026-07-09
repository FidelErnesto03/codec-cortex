# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Schema resolution and precedence logic.

SchemaResolver is the single entry point for determining required fields,
valid statuses, and valid types. It consults the per-file glossary ($0)
first, then falls back to canonical constants from errors.py.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from .ast import Glossary


class SchemaResolver:
    """Resolve field/status/type precedence: $0 wins, canonical is fallback.

    Parameters
    ----------
    glossary : Glossary | None
        The per-file glossary parsed from $0. ``None`` means "use canonical".
    """

    ALWAYS_REQUIRED: FrozenSet[str] = frozenset({"name"})

    def __init__(self, glossary: Optional[Glossary] = None) -> None:
        self.glossary = glossary

    def required_fields(self, sigil: str) -> Tuple[Set[str], Set[str]]:
        """Return ``(required, optional)`` field sets for *sigil*.

        *required* — fields declared in $0 (if any).
        *optional* — canonical fields not declared in $0 (so callers can
        warn instead of error).
        """
        if self.glossary and sigil in self.glossary.sigils:
            sd = self.glossary.sigils[sigil]
            if sd.fields:
                declared = set(sd.fields)
                try:
                    from .errors import REQUIRED_FIELDS  # type: ignore
                except ImportError:
                    return (declared, set())
                canonical = set(REQUIRED_FIELDS.get(sigil, set()))
                optional = canonical - declared
                return (declared, optional)
        try:
            from .errors import REQUIRED_FIELDS
        except ImportError:
            return (set(self.ALWAYS_REQUIRED), set())
        return (set(REQUIRED_FIELDS.get(sigil, [])) | self.ALWAYS_REQUIRED, set())

    def valid_statuses(self) -> FrozenSet[str]:
        """Return the set of allowed status values."""
        if self.glossary and self.glossary.status_custom:
            return frozenset(self.glossary.status_custom)
        try:
            from .errors import ALLOWED_STATUS
        except ImportError:
            return frozenset()
        return ALLOWED_STATUS

    def valid_types(self) -> FrozenSet[str]:
        """Return the set of allowed type values (canonical + custom)."""
        base: FrozenSet[str]
        try:
            from .errors import CANONICAL_TYPES
        except ImportError:
            base = frozenset({"attrs", "cuerpo", "bloque"})
        else:
            base = CANONICAL_TYPES
        if self.glossary:
            declared = frozenset(self.glossary.types)
            custom = frozenset(self.glossary.types_custom or [])
            return base | declared | custom
        return base

    def has_fields(self, sigil: str) -> bool:
        """Check if *sigil* has field declarations in $0."""
        if self.glossary and sigil in self.glossary.sigils:
            sd = self.glossary.sigils[sigil]
            return sd.fields is not None and len(sd.fields) > 0
        return False

    def needs_review(self, sigil: str) -> bool:
        """Check if *sigil* needs review (auto-detected without definition)."""
        if self.glossary and sigil in self.glossary.sigils:
            return self.glossary.sigils[sigil].needs_review
        return False
