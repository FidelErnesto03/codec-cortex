r"""CORTEX v2 parser — handles the exact format of ``skill/cortex/SKILL.md``.

The v2 format has these key characteristics:
  1. File wrapped in ``\`\`\`markdown ... \`\`\``
  2. ``<!-- CODEC-CORTEX -->`` header with internal_encoding
  3. ``$0`` glossary declared via entries: ``IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"..."}``
  4. ``$0`` metadata: ``$0:type_attrs{rule:"..."}``, ``$0:contract_hdl{pos:"..."}``, etc.
  5. HDL uses bare ``attrs-pos``: ``HDL:agent_init|specification|SKILL.md|notes...``
  6. Micro-tokens as bare values: ``status:cur``, ``survive:min``
  7. ``DESC``/``AXM`` (cuerpo): ``SIGIL:name{long text...}``
  8. ``DIAG`` (bloque): ``SIGIL:name{\nmultiline\n}``
  9. ``!`` rules: ``!:name{rule:"...",survive:min}``
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class V2Entry:
    """A single entry in a CORTEX v2 document."""
    sigil: str
    name: str
    entry_type: str  # attrs | attrs-pos | cuerpo | bloque
    value: Any  # dict for attrs, list for attrs-pos, str for cuerpo/bloque
    raw: str = ""  # original text for verbatim reproduction
    section: str = ""

    def to_dict(self) -> dict:
        return {
            "sigil": self.sigil,
            "name": self.name,
            "type": self.entry_type,
            "value": self.value,
            "section": self.section,
        }


@dataclass
class V2Section:
    """A ``$N`` section in a CORTEX v2 document."""
    id: str  # "$0", "$1", etc.
    entries: List[V2Entry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"id": self.id, "entries": [e.to_dict() for e in self.entries]}


@dataclass
class CortexV2Document:
    """Parsed CORTEX v2 document."""
    header: Dict[str, str] = field(default_factory=dict)  # CODEC-CORTEX header fields
    sections: List[V2Section] = field(default_factory=list)
    raw_text: str = ""  # original text (for roundtrip verification)

    def get_section(self, section_id: str) -> Optional[V2Section]:
        for s in self.sections:
            if s.id == section_id:
                return s
        return None

    def get_entries(self, section_id: str = None, sigil: str = None) -> List[V2Entry]:
        result = []
        for sec in self.sections:
            if section_id and sec.id != section_id:
                continue
            for e in sec.entries:
                if sigil and e.sigil != sigil:
                    continue
                result.append(e)
        return result

    def to_dict(self) -> dict:
        return {
            "header": dict(self.header),
            "sections": [s.to_dict() for s in self.sections],
        }


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# Regex for the markdown wrapper
_WRAPPER_OPEN = re.compile(r'^```markdown\n', re.MULTILINE)
_WRAPPER_CLOSE = re.compile(r'\n```$', re.MULTILINE)

# Regex for the CODEC-CORTEX header
_HEADER_RE = re.compile(
    r'<!-- CODEC-CORTEX\n(.*?)\n-->',
    re.DOTALL
)

# Regex for section headers: bare $N on its own line.
# v0.3.2: also accept v1-style "$N: DESCRIPTION" headers (used by the
# benchmark corpus). The description must start with a space after the
# colon to distinguish from $0 metadata entries like $0:type_attrs{...}.
# The description must not contain braces (those are entry bodies, not
# section descriptions). The captured section id is just $N.
_SECTION_RE = re.compile(r'^\$(\d+)(?::\s+[^\n{}]*)?$', re.MULTILINE)

# Regex for entry starts: SIGIL:name{ or $0:name{ or HDL:name|
# Special case: ! entries can be !:name{ or !name{ (without colon)
_ENTRY_START_RE = re.compile(
    r'^(?P<sigil>[A-Z][A-Z0-9_]*|\$0):(?P<name>[A-Za-z_][A-Za-z0-9_]*)\{',
    re.MULTILINE
)
# Separate regex for ! entries: !name{ or !:name{
_BANG_ENTRY_RE = re.compile(
    r'^!(?::(?P<name1>[A-Za-z_][A-Za-z0-9_]*)|(?P<name2>[A-Za-z_][A-Za-z0-9_]*))\{',
    re.MULTILINE
)

# Regex for HDL bare attrs-pos: HDL:name|val1|val2|...
_HDL_RE = re.compile(
    r'^HDL:(?P<name>[A-Za-z_][A-Za-z0-9_]*)\|',
    re.MULTILINE
)

# Regex for $0 metadata entries: $0:name{...}
_META_RE = re.compile(
    r'^\$0:(?P<name>\w+)\{',
    re.MULTILINE
)

# Keys that are always bare (enum/micro values)
_BARE_KEYS = frozenset({
    'type', 'risk', 'cortex', 'status', 'survive', 'severity',
    'encoding', 'license', 'priority', 'expand', 'pos',
})

# Keys that are always quoted
_QUOTED_KEYS = frozenset({
    'desc', 'rule', 'content', 'topic', 'effect', 'prevention',
    'role', 'author', 'version', 'spec', 'project', 'name',
    'domain', 'lang_struct', 'lang_semantic', 'output_human',
    'category', 'nature', 'target', 'path', 'limit', 'scope',
    'risk_desc', 'impact', 'mitigation', 'pattern', 'values',
    'statement', 'evidence', 'event', 'result', 'date',
    'action', 'reason', 'owner', 'what', 'goal', 'success',
    'phase', 'current', 'notes',
})


def parse_cortex_v2(text: str) -> CortexV2Document:
    """Parse a CORTEX v2 file into a :class:`CortexV2Document`.

    Handles the exact format used in ``skill/cortex/SKILL.md``:
    - Markdown code fence wrapper
    - ``<!-- CODEC-CORTEX -->`` header
    - ``$0`` entry-based glossary
    - HDL bare ``attrs-pos``
    - ``DIAG`` multiline ``bloque`` entries
    """

    doc = CortexV2Document()
    doc.raw_text = text

    # 1. Strip markdown wrapper
    inner = text
    m = _WRAPPER_OPEN.match(inner)
    if m:
        inner = inner[m.end():]
    # Remove closing ```
    idx = inner.rfind('\n```')
    if idx != -1:
        inner = inner[:idx]

    # 2. Parse CODEC-CORTEX header
    m = _HEADER_RE.search(inner)
    if m:
        header_text = m.group(1)
        for line in header_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                k = k.strip()
                v = v.strip()
                # v2.0.1 M-01: if value is already quoted, strip the quotes
                if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]
                doc.header[k] = v
        # Remove header from inner text for section parsing
        inner = inner[:m.start()] + inner[m.end():]

    # 3. Parse sections
    # Find all section boundaries
    section_matches = list(_SECTION_RE.finditer(inner))
    if not section_matches:
        # No sections found — treat entire content as $0
        sections_text = [("$0", inner.strip())]
    else:
        sections_text = []
        for i, m in enumerate(section_matches):
            sec_num = m.group(1)
            start = m.end()
            if i + 1 < len(section_matches):
                end = section_matches[i + 1].start()
            else:
                end = len(inner)
            sec_text = inner[start:end].strip()
            sections_text.append((f"${sec_num}", sec_text))

    # 4. Parse entries in each section
    for sec_id, sec_text in sections_text:
        section = V2Section(id=sec_id)
        section.entries = _parse_entries(sec_text, sec_id)
        doc.sections.append(section)

    return doc


def _parse_entries(text: str, section_id: str) -> List[V2Entry]:
    """Parse all entries in a section's text."""

    entries: List[V2Entry] = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        # Check for HDL bare attrs-pos: HDL:name|...
        if stripped.startswith('HDL:') and '|' in stripped:
            entry = _parse_hdl_entry(stripped, section_id)
            if entry:
                entries.append(entry)
            i += 1
            continue

        # Check for $0 metadata: $0:name{...}
        if stripped.startswith('$0:'):
            entry = _parse_meta_entry(stripped, section_id)
            if entry:
                entries.append(entry)
            i += 1
            continue

        # Check for ! entries: !name{ or !:name{
        if stripped.startswith('!'):
            m_bang = _BANG_ENTRY_RE.match(stripped)
            if m_bang:
                name = m_bang.group('name1') or m_bang.group('name2')
                full_raw, end_line = _collect_entry_raw(lines, i)
                entry = _parse_bang_entry(full_raw, name, section_id)
                if entry:
                    entries.append(entry)
                i = end_line + 1
                continue

        # Check for regular entry: SIGIL:name{...}
        m = _ENTRY_START_RE.match(stripped)
        if m:
            sigil = m.group('sigil')
            name = m.group('name')
            # Check if this is a single-line or multi-line entry
            # Count braces in the remaining text from this line
            full_raw, end_line = _collect_entry_raw(lines, i)
            entry = _parse_single_entry(full_raw, sigil, name, section_id)
            if entry:
                entries.append(entry)
            i = end_line + 1
            continue

        # Unrecognized line — skip
        i += 1

    return entries


def _collect_entry_raw(lines: List[str], start: int) -> Tuple[str, int]:
    """Collect the full raw text of an entry starting at ``lines[start]``.

    Handles multi-line bloque entries by counting braces.
    Returns ``(raw_text, last_line_index)``.
    """

    line = lines[start]
    # Check if entry is complete on this line (braces balanced)
    depth = 0
    in_string = False
    escape = False
    for ch in line:
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if in_string:
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1

    if depth <= 0:
        # Single-line entry
        return line, start

    # Multi-line entry: collect until braces balanced
    parts = [line]
    j = start + 1
    while j < len(lines):
        parts.append(lines[j])
        for ch in lines[j]:
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
                continue
            if in_string:
                if ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
        if depth <= 0:
            break
        j += 1

    return '\n'.join(parts), j


def _parse_single_entry(raw: str, sigil: str, name: str, section_id: str) -> Optional[V2Entry]:
    """Parse a single entry from its raw text."""

    # Extract body between { and }
    start = raw.find('{')
    if start == -1:
        return None
    # Find matching close brace
    depth = 0
    in_string = False
    escape = False
    end = -1
    for i in range(start, len(raw)):
        ch = raw[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if in_string:
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        return None

    body = raw[start + 1:end]

    # Determine entry type based on sigil
    # For $0 sigil declarations: IDN:identity{type:attrs,risk:B,...}
    # For $0 metadata: $0:type_attrs{rule:"..."}
    if sigil == '$0':
        # This is a $0 metadata entry
        return _parse_meta_body(raw, name, body, section_id)

    # For regular sigils, check if it's a cuerpo/bloque (DESC, AXM, DIAG)
    if sigil in ('DESC', 'AXM') :
        # cuerpo type: literal text
        return V2Entry(
            sigil=sigil, name=name, entry_type='cuerpo',
            value=body, raw=raw, section=section_id,
        )

    if sigil == 'DIAG':
        # bloque type: verbatim multiline
        return V2Entry(
            sigil=sigil, name=name, entry_type='bloque',
            value=body, raw=raw, section=section_id,
        )

    # For ! sigil: attrs with rule/survive
    if sigil == '!':
        attrs = _parse_attrs(body)
        return V2Entry(
            sigil=sigil, name=name, entry_type='attrs',
            value=attrs, raw=raw, section=section_id,
        )

    # For $0 sigil declarations (IDN:identity{type:attrs,...})
    # These are glossary declaration entries
    if section_id == '$0' and sigil not in ('$',):
        attrs = _parse_attrs(body)
        # Check if this is a sigil declaration (has type/risk/cortex/desc)
        if 'type' in attrs or 'risk' in attrs or 'cortex' in attrs:
            return V2Entry(
                sigil=sigil, name=name, entry_type='sigil_decl',
                value=attrs, raw=raw, section=section_id,
            )

    # Default: attrs
    attrs = _parse_attrs(body)
    return V2Entry(
        sigil=sigil, name=name, entry_type='attrs',
        value=attrs, raw=raw, section=section_id,
    )


def _parse_meta_entry(line: str, section_id: str) -> Optional[V2Entry]:
    """Parse a $0:name{...} metadata entry."""

    m = _META_RE.match(line)
    if not m:
        return None
    name = m.group('name')
    # Extract body
    start = line.find('{')
    if start == -1:
        return None
    # Find matching close brace
    depth = 0
    in_string = False
    escape = False
    end = -1
    for i in range(start, len(line)):
        ch = line[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if in_string:
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return None
    body = line[start + 1:end]
    attrs = _parse_attrs(body)
    return V2Entry(
        sigil='$0', name=name, entry_type='meta',
        value=attrs, raw=line, section=section_id,
    )


def _parse_meta_body(raw: str, name: str, body: str, section_id: str) -> Optional[V2Entry]:
    """Parse a $0 metadata entry from its body text."""

    attrs = _parse_attrs(body)
    return V2Entry(
        sigil='$0', name=name, entry_type='meta',
        value=attrs, raw=raw, section=section_id,
    )


def _parse_bang_entry(raw: str, name: str, section_id: str) -> Optional[V2Entry]:
    """Parse a ! rule entry: ``!name{rule:"...",survive:min}`` or ``!:name{...}``."""

    # Extract body between { and }
    start = raw.find('{')
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    end = -1
    for i in range(start, len(raw)):
        ch = raw[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if in_string:
            if ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return None
    body = raw[start + 1:end]
    attrs = _parse_attrs(body)

    # In $0, if the entry has type/risk/cortex/desc keys, it's a sigil declaration
    if section_id == '$0' and ('type' in attrs or 'risk' in attrs or 'cortex' in attrs):
        return V2Entry(
            sigil='!', name=name, entry_type='sigil_decl',
            value=attrs, raw=raw, section=section_id,
        )

    return V2Entry(
        sigil='!', name=name, entry_type='attrs',
        value=attrs, raw=raw, section=section_id,
    )


def _parse_hdl_entry(line: str, section_id: str) -> Optional[V2Entry]:
    """Parse an HDL bare attrs-pos entry: ``HDL:name|v1|v2|v3|v4``."""

    # HDL:name|status|requires|notes
    m = re.match(r'^HDL:(?P<name>[A-Za-z_][A-Za-z0-9_]*)\|(?P<rest>.*)$', line)
    if not m:
        return None
    name = m.group('name')
    rest = m.group('rest')
    # Split by | — but notes field may contain | characters
    # Contract: operation|status|requires|notes
    # We split on the first 3 | characters
    parts = rest.split('|', 3)
    fields = ['operation', 'status', 'requires', 'notes']
    value = {}
    for i, field_name in enumerate(fields):
        if i < len(parts):
            value[field_name] = parts[i]
        else:
            value[field_name] = ''

    return V2Entry(
        sigil='HDL', name=name, entry_type='attrs-pos',
        value=value, raw=line, section=section_id,
    )


def _parse_attrs(body: str) -> Dict[str, Any]:
    """Parse an attrs body into a dict.

    Handles mixed quoting:
    - Bare values: ``status:cur``, ``risk:B``, ``survive:min``
    - Quoted values: ``desc:"..."``, ``rule:"..."``
    - Escaped quotes inside strings: ``rule:"... clave:\"valor\" ..."``
    """

    out: Dict[str, Any] = {}
    s = body.strip()
    if not s:
        return out
    i = 0
    n = len(s)
    while i < n:
        # Skip whitespace and commas
        while i < n and (s[i].isspace() or s[i] == ','):
            i += 1
        if i >= n:
            break
        # Read key
        m = re.match(r'([^\W\d_][\w]*)', s[i:])
        if not m:
            break
        key = m.group(1)
        i += len(key)
        # Skip whitespace
        while i < n and s[i].isspace():
            i += 1
        if i >= n or s[i] != ':':
            break
        i += 1  # skip ':'
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            break
        # Read value
        if s[i] == '"':
            # Quoted string — handle escaped quotes
            j = i + 1
            buf: List[str] = []
            escape = False
            while j < n:
                ch = s[j]
                if escape:
                    if ch == 'n':
                        buf.append('\n')
                    elif ch == 't':
                        buf.append('\t')
                    elif ch == '"':
                        buf.append('"')
                    elif ch == '\\':
                        buf.append('\\')
                    else:
                        buf.append(ch)
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    break
                else:
                    buf.append(ch)
                j += 1
            value: Any = ''.join(buf)
            i = j + 1  # skip closing "
        else:
            # Bare value — read until , or end
            j = i
            while j < n and s[j] != ',':
                j += 1
            raw_val = s[i:j].strip()
            i = j
            # Interpret bare values
            if raw_val in ('true', 'false'):
                value = (raw_val == 'true')
            elif raw_val == 'null':
                value = None
            elif re.fullmatch(r'-?\d+', raw_val):
                value = int(raw_val)
            elif re.fullmatch(r'-?\d+\.\d+', raw_val):
                value = float(raw_val)
            else:
                value = raw_val
        out[key] = value
    return out
