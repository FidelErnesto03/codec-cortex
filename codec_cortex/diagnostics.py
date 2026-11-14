#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic message helpers (additive 1.x tooling).

Enriches I001/I004 messages with actionable hints. Diagnostic *codes* and
detection order are unchanged — only the human-readable message gains
context (did-you-mean suggestions, expected idea form).
"""

import difflib
from typing import Iterable, List, Optional


def _sigil_name(entry) -> str:
    return getattr(entry, "sigil", entry)


def close_matches(token: str, candidates: Iterable[str],
                  n: int = 3, cutoff: float = 0.6) -> List[str]:
    """Deterministic did-you-mean: close matches sorted by similarity then name."""
    pool = sorted({c for c in candidates if c})
    if not pool:
        return []
    matches = difflib.get_close_matches(token, pool, n=n, cutoff=cutoff)
    return sorted(matches)


def undeclared_sigil_message(sigil: str, symbols: Iterable) -> str:
    """I001 message: names the undeclared sigil and what *is* declared.

    `symbols` is any iterable of SymbolDef-like objects (or bare sigil strings).
    """
    declared = sorted({_sigil_name(s) for s in symbols})
    msg = f"Undeclared sigil: {sigil}"
    sugg = close_matches(sigil, declared)
    if sugg:
        msg += f". Did you mean: {', '.join(sugg)}?"
    elif declared:
        if len(declared) <= 12:
            msg += f". Declared sigils: {', '.join(declared)}"
        else:
            msg += f". ({len(declared)} sigils declared)"
    return msg


_IDEA_FORMS = {
    "attrs": "SIG:name{key:value,...}",
    "cuerpo": "SIG:name{text}",
    "bloque": "SIG:name{\\ntext\\n}",
    "attrs-pos": "SIG:name|cell|cell|...",
    "relacion": "SIG:name|cell|cell|cell|...",
}
_SLOT_FORM = "SIG:name{※N:value,...}"


def expected_form(shape: Optional[str] = None, *,
                  multiline: bool = False, slots: bool = False) -> str:
    """Concrete expected syntax for an idea line (I004 hint)."""
    if slots:
        return _SLOT_FORM
    if multiline:
        return "SIG:name{\\ntext\\n}"
    return _IDEA_FORMS.get(shape or "", "SIG:name{...}")
