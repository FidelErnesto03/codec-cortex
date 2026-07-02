# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

r"""CORTEX v2 writer — serializes a :class:`CortexV2Document` back to exact format.

Reproduces the exact byte layout of ``skill/cortex/SKILL.md``:
  1. ``\`\`\`markdown`` wrapper
  2. ``<!-- CODEC-CORTEX -->`` header
  3. ``$0`` section with sigil declarations and metadata
  4. Sections ``$1``–``$12`` with entries
  5. Closing ``\`\`\``

v0.3.2 additions:
  - ``write_cortex_v2_preserve()``: structure-preserving serializer used by
    ``cortex canonicalize --preserve`` and by the VIEW-aware fallback path
    of ``cortex canonicalize`` when no VIEW directives are present. It only
    normalizes whitespace and section ordering, leaving entries in their
    original form. This keeps v1-render compatibility (B-01/B-05 fix).
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from .parser import CortexV2Document, V2Entry, V2Section


# Keys that are always bare (enum/micro values)
_BARE_KEYS = frozenset({
    'type', 'risk', 'cortex', 'status', 'survive', 'severity',
    'encoding', 'license', 'priority', 'expand', 'pos',
})

# Keys that should use escaped quotes inside strings
_NEEDS_ESCAPE = re.compile(r'[\\"]')


def write_cortex_v2(doc: CortexV2Document) -> str:
    """Serialize a :class:`CortexV2Document` to CORTEX v2 format.

    Produces output byte-identical to the original when the document
    was parsed from a well-formed CORTEX v2 file.
    """

    parts: List[str] = []

    # 1. Opening wrapper
    parts.append('```markdown')

    # 2. CODEC-CORTEX header
    if doc.header:
        parts.append('<!-- CODEC-CORTEX')
        for k, v in doc.header.items():
            # v2.0.1 M-01: quote values that contain spaces, commas, or special chars
            if isinstance(v, str) and (' ' in v or ',' in v or '"' in v or '—' in v):
                # Escape inner quotes
                escaped = v.replace('"', '\\"')
                parts.append(f'{k}: "{escaped}"')
            else:
                parts.append(f'{k}: {v}')
        parts.append('-->')
        parts.append('')  # blank line after header

    # 3. Sections
    for sec in doc.sections:
        parts.append(sec.id)
        for entry in sec.entries:
            parts.append(_serialize_entry(entry))
        # Add blank line between sections (but not after last entry of last section)
        # Actually, looking at the original, there are blank lines between sections
        parts.append('')  # blank line after each section's entries

    # 4. Remove trailing blank lines and add closing wrapper
    # The original ends with: last_entry\n```
    # So we need to join, strip trailing whitespace, add \n```
    text = '\n'.join(parts)
    # Remove trailing blank lines
    text = text.rstrip('\n')
    text += '\n```'

    return text


def _serialize_entry(entry: V2Entry) -> str:
    """Serialize a single entry to its CORTEX v2 text form."""

    if entry.entry_type == 'attrs-pos' and entry.sigil == 'HDL':
        return _serialize_hdl_entry(entry)

    if entry.entry_type == 'meta':
        return _serialize_meta_entry(entry)

    if entry.entry_type == 'sigil_decl':
        # In $0, sigil declarations use SIGIL:name{} format
        # The ! sigil uses !:name{} (with colon)
        if entry.sigil == '!':
            body = _serialize_attrs(entry.value)
            return f'!:{entry.name}{{{body}}}'
        body = _serialize_attrs(entry.value)
        return f'{entry.sigil}:{entry.name}{{{body}}}'

    if entry.entry_type == 'cuerpo':
        return f'{entry.sigil}:{entry.name}{{{entry.value}}}'

    if entry.entry_type == 'bloque':
        # DIAG entries are multiline: SIGIL:name{\ncontent\n}
        # The value already contains the content between { and }
        # We need to reproduce: SIGIL:name{\n + content + \n}
        value = entry.value
        if '\n' in value:
            # Multi-line bloque: opening { on same line, content, closing } on own line
            return f'{entry.sigil}:{entry.name}{{{value}}}'
        else:
            return f'{entry.sigil}:{entry.name}{{{value}}}'

    # Default: attrs
    body = _serialize_attrs(entry.value)
    # ! entries in $4+ use !name{} format (without colon)
    if entry.sigil == '!':
        return f'!{entry.name}{{{body}}}'
    return f'{entry.sigil}:{entry.name}{{{body}}}'


def _serialize_hdl_entry(entry: V2Entry) -> str:
    """Serialize an HDL bare attrs-pos entry."""

    v = entry.value
    # Build parts list, omitting trailing empty fields
    parts = [
        v.get('operation', ''),
        v.get('status', ''),
        v.get('requires', ''),
        v.get('notes', ''),
    ]
    # Remove trailing empty parts to match original format
    while parts and parts[-1] == '':
        parts.pop()
    return f'HDL:{entry.name}|{"|".join(parts)}'


def _serialize_meta_entry(entry: V2Entry) -> str:
    """Serialize a $0 metadata entry."""

    body = _serialize_attrs(entry.value)
    return f'$0:{entry.name}{{{body}}}'


def _serialize_sigil_decl(entry: V2Entry) -> str:
    """Serialize a $0 sigil declaration entry."""

    body = _serialize_attrs(entry.value)
    return f'{entry.sigil}:{entry.name}{{{body}}}'


def _serialize_attrs(attrs: Dict[str, Any]) -> str:
    """Serialize an attrs dict to ``key:value`` or ``key:"value"`` form.

    Quoting rules (matching the original CORTEX format):
    - Bare values: enum/micro tokens (risk, status, survive, severity, etc.)
      ONLY when the value is a simple identifier (no spaces, pipes, commas)
    - Quoted values: free text (desc, rule, content, etc.)
    - The ``cortex`` field is bare unless it contains ``/``
    - The ``pos`` field is always quoted (contains ``|``)
    - Any value containing spaces, ``|``, ``,``, ``{``, ``}`` must be quoted
    """

    parts: List[str] = []
    for k, v in attrs.items():
        if v is None:
            parts.append(f'{k}:null')
        elif isinstance(v, bool):
            parts.append(f'{k}:{"true" if v else "false"}')
        elif isinstance(v, (int, float)):
            parts.append(f'{k}:{v}')
        elif isinstance(v, str):
            # Determine if this should be bare or quoted
            needs_quotes = False
            if k not in _BARE_KEYS:
                needs_quotes = True
            elif '/' in v:
                needs_quotes = True
            elif any(c in v for c in ' |,{}'):
                needs_quotes = True
            elif ' ' in v:
                needs_quotes = True

            if needs_quotes:
                escaped = _escape_string(v)
                parts.append(f'{k}:"{escaped}"')
            else:
                parts.append(f'{k}:{v}')
        else:
            parts.append(f'{k}:{v}')
    return ','.join(parts)


def _escape_string(s: str) -> str:
    """Escape a string for CORTEX double-quoted form."""

    # In the original, escaped quotes appear as \\" inside rule strings
    # e.g. rule:"pares clave:valor o clave:\"valor\" dentro de {}"
    result = s.replace('\\', '\\\\').replace('"', '\\"')
    return result


# ---------------------------------------------------------------------------
# v0.3.2 — Structure-preserving canonicalizer (B-01/B-05 fix)
# ---------------------------------------------------------------------------

# Section IDs are sorted numerically by their $N component.
_SECTION_SORT_RE = re.compile(r'^\$(\d+)$')


def _section_sort_key(sec: V2Section):
    """Sort key for sections: $0, $1, ..., $12 (numeric)."""
    m = _SECTION_SORT_RE.match(sec.id)
    if m:
        return (0, int(m.group(1)))
    # Non-numeric section ids sort after numeric ones, alphabetically.
    return (1, sec.id)


def has_view_directives(doc: CortexV2Document) -> bool:
    """Return True if ``doc`` has at least one operational VIEW directive.

    A VIEW entry inside ``$0`` that has ``type/risk/cortex/desc`` is a sigil
    declaration, NOT an operational directive (mirrors
    ``view.parse_view_entries_from_doc``).
    """
    for sec in doc.sections:
        for entry in sec.entries:
            if entry.sigil != "VIEW":
                continue
            if sec.id == "$0" and isinstance(entry.value, dict):
                if any(k in entry.value for k in ("type", "risk", "cortex", "desc")):
                    continue
            return True
    return False


def write_cortex_v2_preserve(doc: CortexV2Document) -> str:
    """Serialize ``doc`` preserving original structure (v0.3.2 — B-01/B-05 fix).

    Unlike :func:`write_cortex_v2`, this serializer:

      * Keeps the original entry order within each section (no reordering).
      * Preserves the original entry ``raw`` text when available, falling
        back to a normal serialization only if ``raw`` is missing.
      * Normalizes only whitespace and blank lines between sections.
      * Sorts sections numerically ($0, $1, ..., $12) so the output is
        deterministic, but never reorders entries inside a section.
      * Does NOT touch the markdown wrapper or CODEC-CORTEX header — those
        are reproduced verbatim if present, omitted if absent.

    This guarantees v1-render compatibility for artefacts that do not
    declare VIEW directives (the corpus case), and provides the
    ``--preserve`` escape hatch for artefacts that DO have VIEW but where
    the user explicitly wants the original structure kept.
    """
    parts: List[str] = []

    # 1. Opening wrapper (only if the source had one — detected via raw_text)
    raw = doc.raw_text or ""
    had_wrapper = raw.lstrip().startswith('```markdown')

    if had_wrapper:
        parts.append('```markdown')

    # 2. CODEC-CORTEX header (reproduced verbatim from doc.header)
    if doc.header:
        parts.append('<!-- CODEC-CORTEX')
        for k, v in doc.header.items():
            if isinstance(v, str) and (' ' in v or ',' in v or '"' in v or '—' in v):
                escaped = v.replace('"', '\\"')
                parts.append(f'{k}: "{escaped}"')
            else:
                parts.append(f'{k}: {v}')
        parts.append('-->')
        parts.append('')

    # 3. Sections, numerically sorted; entries preserved in original order.
    sorted_sections = sorted(doc.sections, key=_section_sort_key)
    for sec in sorted_sections:
        parts.append(sec.id)
        for entry in sec.entries:
            # Prefer the original raw text when available — this is what
            # makes the operation structure-preserving.
            if entry.raw:
                parts.append(entry.raw)
            else:
                parts.append(_serialize_entry(entry))
        parts.append('')

    # 4. Trim trailing blank lines and close wrapper if it was opened.
    text = '\n'.join(parts)
    text = text.rstrip('\n')
    if had_wrapper:
        text += '\n```'
    else:
        # Ensure a single trailing newline for non-wrapped artefacts
        # (matches the corpus files convention).
        text += '\n'
    return text
