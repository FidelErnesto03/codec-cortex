# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Glossary resolver — runtime queries over a :class:`Glossary`.

Used by renderers, the validator and the CRUD layer to answer:
  - "what is the type of sigil X?"
  - "is this sigil declared?"
  - "does this sigil have a positional contract?"
  - "what is the expansion of this micro-token?"
  - "is this token used by any entry?"
"""

from __future__ import annotations

from typing import Iterable, Optional

from ..core.ast import Entry, Glossary
from ..core.errors import CANONICAL_SIGILS


def is_canonical(sigil: str) -> bool:
    return sigil in CANONICAL_SIGILS


def is_declared(glossary: Glossary, sigil: str) -> bool:
    return sigil in glossary.sigils


def type_of(glossary: Glossary, sigil: str) -> Optional[str]:
    sd = glossary.sigils.get(sigil)
    return sd.type if sd else None


def contract_of(glossary: Glossary, sigil: str):
    return glossary.contracts.get(sigil)


def expand_micro(glossary: Glossary, value: str) -> str:
    """Expand micro-tokens in ``value`` if they are properly delimited.

    Delimiters recognised: whitespace, ``,``, ``{``, ``}``, start/end.
    Tokens inside words (e.g. ``param_cur``) are NOT expanded.
    """

    if not isinstance(value, str):
        return value
    out = []
    i = 0
    n = len(value)
    while i < n:
        ch = value[i]
        if ch.isalnum() or ch == "_":
            # consume identifier
            j = i
            while j < n and (value[j].isalnum() or value[j] == "_"):
                j += 1
            word = value[i:j]
            # check if word matches a micro-token AND is delimited
            prev_ch = value[i - 1] if i > 0 else ""
            next_ch = value[j] if j < n else ""
            left_delim = (prev_ch == "" or prev_ch in " ,{}\n\t")
            right_delim = (next_ch == "" or next_ch in " ,{}\n\t")
            if left_delim and right_delim and word in glossary.micro:
                out.append(glossary.micro[word].value)
            else:
                out.append(word)
            i = j
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def sigil_usage_count(entries: Iterable[Entry]) -> dict:
    counts: dict = {}
    for e in entries:
        if e.sigil in {"GSIG", "GTYP", "GMIC", "GCON"}:
            continue
        counts[e.sigil] = counts.get(e.sigil, 0) + 1
    return counts


def is_micro_used(entries: Iterable[Entry], token: str) -> bool:
    """Return True if any entry's value contains the micro-token.

    Conservative check: scans string values for delimited occurrences.
    """

    for e in entries:
        if e.type == "bloque":
            continue  # micro-tokens never expand inside bloque
        if isinstance(e.value, dict):
            for v in e.value.values():
                if isinstance(v, str) and token in v.split():
                    return True
        elif isinstance(e.value, str) and token in e.value.split():
            return True
    return False
