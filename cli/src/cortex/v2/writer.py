r"""CORTEX v2 writer — serializes a :class:`CortexV2Document` back to exact format.

Reproduces the exact byte layout of ``skill/cortex/SKILL.md``:
  1. ``\`\`\`markdown`` wrapper
  2. ``<!-- CODEC-CORTEX -->`` header
  3. ``$0`` section with sigil declarations and metadata
  4. Sections ``$1``–``$12`` with entries
  5. Closing ``\`\`\``
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
