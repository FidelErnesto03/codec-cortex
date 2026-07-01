"""HCORTEX parser v2.3.0 — read canonical HCORTEX and reconstruct AST.

Implements F-01..F-08 from v2.3.0 spec:
  F-01: parse_hcortex() entry point
  F-02: header reading (internal_encoding, source_artifact, view_schema, etc.)
  F-03: VIEW marker reading (kind, target, reverse, fields, etc.)
  F-04: table parsing (reverse=rows_to_entries)
  F-05: list parsing (numbered/bullet → entries or cuerpo)
  F-06: verbatim blocks (DIAG, code, PUML with preserve:verbatim)
  F-07: HUMAN_BLOCK parsing (preserve_human_block)
  F-08: section normalizer (titles → $N sections per VIEW)

Architecture:
  HCORTEX markdown → parse_hcortex() → HCortexDocument → encode_cortex_from_ast() → CORTEX

The parser is strict by default: any block without VIEW contract is
flagged E_VIEW_MISSING (in strict mode) or W_HCORTEX_DISPLAY_ONLY (normal).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .diagnostics import Diagnostic
from .view import ViewKind, ReverseStrategy, KIND_REVERSE_COMPAT


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class HCorTEXHeader:
    """Parsed HCORTEX header."""
    internal_encoding: str = ""
    source_artifact: str = ""
    source_version: str = ""
    status: str = ""
    derived_from: str = ""
    reversible: bool = False
    view_schema: int = 0
    view_coverage: int = 0
    mode: str = "normal"  # normal | display | strict | audit | recovery
    raw: Dict[str, str] = field(default_factory=dict)


@dataclass
class HCorTEXBlock:
    """A block in HCORTEX — typically one VIEW directive's worth of content."""
    view_name: str
    kind: str  # ViewKind value
    target: str
    reverse: str  # ReverseStrategy value
    fields: Optional[List[str]] = None
    order: Optional[str] = None
    title: Optional[str] = None
    status: str = "cur"
    scope: Optional[str] = None
    section: Optional[str] = None
    source_section: Optional[str] = None
    preserve: Optional[str] = None
    hash: Optional[str] = None
    fallback: Optional[str] = None
    content_lines: List[str] = field(default_factory=list)  # raw markdown lines between markers
    raw_marker: str = ""  # full opening marker text


@dataclass
class HCorTEXDocument:
    """Parsed HCORTEX document."""
    header: HCorTEXHeader
    blocks: List[HCorTEXBlock] = field(default_factory=list)
    orphan_content: List[str] = field(default_factory=list)  # content outside any VIEW
    diags: List[Diagnostic] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "header": self.header.__dict__,
            "blocks": [b.__dict__ for b in self.blocks],
            "orphan_content": self.orphan_content,
            "diags": [d.to_dict() for d in self.diags],
        }


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

_HEADER_RE = re.compile(r'<!-- CODEC-CORTEX\n(.*?)\n-->', re.DOTALL)
_VIEW_OPEN_RE = re.compile(
    r'<!-- (VIEW:[\w_-]+)\s+(.*?)\s*-->'
)
_VIEW_CLOSE_RE = re.compile(r'<!-- /VIEW:([\w_-]+)\s*-->')


def parse_hcortex(text: str, strict: bool = False) -> HCorTEXDocument:
    """F-01: Parse canonical HCORTEX into HCorTEXDocument.

    If strict=True, E_VIEW_MISSING and E_HUMAN_BLOCK_UNDECLARED become errors
    instead of warnings.
    """

    diags: List[Diagnostic] = []

    # F-02: header
    header, header_diags = _parse_header(text)
    diags.extend(header_diags)

    # Strip header from body
    body = _HEADER_RE.sub('', text, count=1).lstrip('\n')

    # F-03/F-08: walk the body, extracting VIEW blocks
    blocks, orphans, block_diags = _parse_blocks(body, strict=strict)
    diags.extend(block_diags)

    # Validate header consistency
    if header.view_coverage == 100 and not header.reversible:
        diags.append(Diagnostic(
            "E_HCORTEX_NOT_REVERSIBLE",
            "view_coverage=100 but reversible=false — inconsistent header",
            "error",
        ))

    if header.reversible and header.view_coverage < 100:
        diags.append(Diagnostic(
            "E_HCORTEX_NOT_REVERSIBLE",
            f"reversible=true but view_coverage={header.view_coverage} (<100)",
            "error",
        ))

    if orphans and strict:
        diags.append(Diagnostic(
            "E_VIEW_MISSING",
            f"{len(orphans)} content lines outside any VIEW block — strict mode requires all content under VIEW",
            "error",
        ))

    # v2.3.0 T-08: Validate table schemas for blocks with declared fields
    for block in blocks:
        if block.kind == "table" and block.fields:
            _, table_diags = parse_table_block(block)
            diags.extend(table_diags)

    return HCorTEXDocument(
        header=header,
        blocks=blocks,
        orphan_content=orphans,
        diags=diags,
    )


# ---------------------------------------------------------------------------
# F-02: Header parsing
# ---------------------------------------------------------------------------

def _parse_header(text: str) -> Tuple[HCorTEXHeader, List[Diagnostic]]:
    """Parse the <!-- CODEC-CORTEX ... --> header."""

    diags: List[Diagnostic] = []
    header = HCorTEXHeader()

    m = _HEADER_RE.search(text)
    if not m:
        diags.append(Diagnostic(
            "E_HCORTEX_HEADER_INVALID",
            "Missing <!-- CODEC-CORTEX ... --> header",
            "error",
        ))
        return header, diags

    body = m.group(1)
    for line in body.split('\n'):
        line = line.strip()
        if not line or line.startswith('<!--') or line.startswith('-->'):
            continue
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        header.raw[key] = value

        if key == "internal_encoding":
            header.internal_encoding = value
        elif key == "source_artifact":
            header.source_artifact = value
        elif key == "source_version":
            header.source_version = value
        elif key == "status":
            header.status = value
        elif key == "derived_from":
            header.derived_from = value
        elif key == "reversible":
            header.reversible = (value.lower() == "true")
        elif key == "view_schema":
            try:
                header.view_schema = int(value)
            except ValueError:
                diags.append(Diagnostic(
                    "E_HCORTEX_HEADER_INVALID",
                    f"view_schema not an integer: {value!r}",
                    "error",
                ))
        elif key == "view_coverage":
            try:
                header.view_coverage = int(value)
            except ValueError:
                diags.append(Diagnostic(
                    "E_HCORTEX_HEADER_INVALID",
                    f"view_coverage not an integer: {value!r}",
                    "error",
                ))
        elif key == "mode":
            header.mode = value

    # Validate required fields
    if header.internal_encoding != "HCORTEX":
        diags.append(Diagnostic(
            "E_HCORTEX_HEADER_INVALID",
            f"internal_encoding must be 'HCORTEX', got {header.internal_encoding!r}",
            "error",
        ))

    return header, diags


# ---------------------------------------------------------------------------
# F-03/F-04/F-05/F-06/F-07/F-08: Block parsing
# ---------------------------------------------------------------------------

def _parse_blocks(body: str, strict: bool = False) -> Tuple[List[HCorTEXBlock], List[str], List[Diagnostic]]:
    """Walk the body, extract VIEW blocks, collect orphans."""

    diags: List[Diagnostic] = []
    blocks: List[HCorTEXBlock] = []
    orphans: List[str] = []

    lines = body.split('\n')
    i = 0
    in_block = False
    current_block: Optional[HCorTEXBlock] = None
    orphan_buffer: List[str] = []

    while i < len(lines):
        line = lines[i]

        # Opening VIEW marker
        open_m = _VIEW_OPEN_RE.match(line)
        if open_m and not in_block:
            # Flush orphan buffer
            if orphan_buffer:
                orphans.extend(orphan_buffer)
                orphan_buffer = []

            open_m.group(0)
            view_tag = open_m.group(1)  # "VIEW:name"
            attrs_str = open_m.group(2)
            view_name = view_tag.split(':', 1)[1]

            block, block_diag = _parse_view_marker(view_name, attrs_str)
            diags.extend(block_diag)
            current_block = block
            in_block = True
            i += 1
            continue

        # Closing VIEW marker
        close_m = _VIEW_CLOSE_RE.match(line)
        if close_m and in_block:
            view_name_close = close_m.group(1)
            if current_block and current_block.view_name == view_name_close:
                blocks.append(current_block)
            else:
                diags.append(Diagnostic(
                    "E_VIEW_MISSING",
                    f"Closing marker /VIEW:{view_name_close} does not match opening VIEW:{current_block.view_name if current_block else 'None'}",
                    "error",
                ))
            current_block = None
            in_block = False
            i += 1
            continue

        if in_block and current_block is not None:
            current_block.content_lines.append(line)
        else:
            # Orphan content (outside VIEW)
            stripped = line.strip()
            if stripped and not stripped.startswith('**') and stripped not in ('---',):
                orphan_buffer.append(line)
            elif stripped == '---':
                # Section separator — flush orphans
                if orphan_buffer:
                    orphans.extend(orphan_buffer)
                    orphan_buffer = []

        i += 1

    # Flush any remaining orphan buffer
    if orphan_buffer:
        orphans.extend(orphan_buffer)

    # Filter out trivial orphans (blank lines, "Perfil: ...")
    orphans = [o for o in orphans if o.strip() and not o.strip().startswith('**Perfil')]

    return blocks, orphans, diags


def _parse_view_marker(view_name: str, attrs_str: str) -> Tuple[HCorTEXBlock, List[Diagnostic]]:
    """Parse the attributes inside <!-- VIEW:name kind=... target=... -->."""

    diags: List[Diagnostic] = []
    block = HCorTEXBlock(
        view_name=view_name,
        kind="",
        target="",
        reverse="",
    )

    # Parse key=value pairs, with quoted values
    # Pattern: key="value with spaces" OR key=bare_value
    pattern = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')
    for m in pattern.finditer(attrs_str):
        key = m.group(1)
        value = m.group(2) if m.group(2) is not None else m.group(3)

        if key == "kind":
            block.kind = value
            # Validate kind
            if value not in {k.value for k in ViewKind}:
                diags.append(Diagnostic(
                    "E_VIEW_REVERSE_UNSUPPORTED",
                    f"VIEW:{view_name} unknown kind {value!r}",
                    "error",
                    f"VIEW:{view_name}",
                ))
        elif key == "target":
            block.target = value
        elif key == "reverse":
            block.reverse = value
            if value not in {r.value for r in ReverseStrategy}:
                diags.append(Diagnostic(
                    "E_VIEW_REVERSE_UNSUPPORTED",
                    f"VIEW:{view_name} unknown reverse {value!r}",
                    "error",
                    f"VIEW:{view_name}",
                ))
        elif key == "fields":
            block.fields = [f.strip() for f in value.split(',')]
        elif key == "order":
            block.order = value
        elif key == "title":
            block.title = value
        elif key == "status":
            block.status = value
        elif key == "scope":
            block.scope = value
        elif key == "section":
            block.section = value
        elif key == "source_section":
            block.source_section = value
        elif key == "preserve":
            block.preserve = value
        elif key == "hash":
            block.hash = value
        elif key == "fallback":
            block.fallback = value

    # Validate required fields
    if not block.kind:
        diags.append(Diagnostic(
            "E_VIEW_MISSING",
            f"VIEW:{view_name} missing kind",
            "error",
            f"VIEW:{view_name}",
        ))
    if not block.target:
        diags.append(Diagnostic(
            "E_VIEW_TARGET_UNRESOLVED",
            f"VIEW:{view_name} missing target",
            "error",
            f"VIEW:{view_name}",
        ))
    if not block.reverse:
        diags.append(Diagnostic(
            "E_VIEW_REVERSE_UNSUPPORTED",
            f"VIEW:{view_name} missing reverse",
            "error",
            f"VIEW:{view_name}",
        ))

    # Validate kind/reverse compatibility
    if block.kind and block.reverse:
        try:
            kind_enum = ViewKind(block.kind)
            reverse_enum = ReverseStrategy(block.reverse)
            if reverse_enum not in KIND_REVERSE_COMPAT.get(kind_enum, set()):
                diags.append(Diagnostic(
                    "E_VIEW_REVERSE_UNSUPPORTED",
                    f"VIEW:{view_name} kind={block.kind!r} incompatible with reverse={block.reverse!r}",
                    "error",
                    f"VIEW:{view_name}",
                ))
        except ValueError:
            pass  # already reported above

    return block, diags


# ---------------------------------------------------------------------------
# Block content parsers (used by encoder)
# ---------------------------------------------------------------------------

def parse_table_block(block: HCorTEXBlock) -> Tuple[List[Dict[str, str]], List[Diagnostic]]:
    """F-04: Parse a Markdown table into rows."""

    diags: List[Diagnostic] = []
    rows: List[Dict[str, str]] = []

    lines = block.content_lines
    if not lines:
        return rows, diags

    # Find the header row and separator
    header_idx = None
    sep_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            if header_idx is None:
                header_idx = i
            elif sep_idx is None and '---' in stripped:
                sep_idx = i
                break

    if header_idx is None or sep_idx is None:
        diags.append(Diagnostic(
            "E_TABLE_SCHEMA_MISMATCH",
            f"VIEW:{block.view_name} table has no header/separator",
            "error",
            f"VIEW:{block.view_name}",
        ))
        return rows, diags

    # Parse header
    header_cells = _split_table_row(lines[header_idx])
    if not header_cells:
        diags.append(Diagnostic(
            "E_TABLE_SCHEMA_MISMATCH",
            f"VIEW:{block.view_name} empty header row",
            "error",
            f"VIEW:{block.view_name}",
        ))
        return rows, diags

    # Validate against declared fields
    # v2.4.0: Allow Source as an implicit column and extra attrs columns
    # (renderer includes ALL attrs, not just declared fields)
    if block.fields:
        effective_header = [h for h in header_cells if h.lower().strip() != "source"]
        # v2.4.0: Only error if header has FEWER columns than declared fields
        if len(effective_header) < len(block.fields):
            diags.append(Diagnostic(
                "E_TABLE_SCHEMA_MISMATCH",
                f"VIEW:{block.view_name} header has {len(effective_header)} data cols (excl. Source) but fields declares {len(block.fields)}: "
                f"header={header_cells!r}, fields={block.fields!r}",
                "error",
                f"VIEW:{block.view_name}",
            ))

    # Parse data rows
    for line in lines[sep_idx + 1:]:
        stripped = line.strip()
        if not stripped or not stripped.startswith('|'):
            continue
        if '---' in stripped:
            continue
        cells = _split_table_row(stripped)
        if not cells:
            continue
        row = {}
        for i, cell in enumerate(cells):
            key = header_cells[i] if i < len(header_cells) else f"col_{i}"
            row[key.lower().strip()] = cell.strip()
        rows.append(row)

    return rows, diags


def _split_table_row(line: str) -> List[str]:
    """Split a Markdown table row into cells, respecting \\| escapes."""

    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    # Split on | but respect \|
    cells = []
    current = ''
    i = 0
    while i < len(line):
        c = line[i]
        if c == '\\' and i + 1 < len(line) and line[i + 1] == '|':
            current += '|'
            i += 2
        elif c == '|':
            cells.append(current)
            current = ''
            i += 1
        else:
            current += c
            i += 1
    cells.append(current)
    return cells


def parse_list_block(block: HCorTEXBlock) -> Tuple[List[str], List[Diagnostic]]:
    """F-05: Parse a bullet/numbered list into items.

    v2.4.0: Skip ## headers and blank lines.
    """

    diags: List[Diagnostic] = []
    items: List[str] = []

    for line in block.content_lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip markdown headers
        if stripped.startswith('#'):
            continue
        # Bullet: - item or * item
        if stripped.startswith('- ') or stripped.startswith('* '):
            items.append(stripped[2:].strip())
        # Numbered: 1. item
        elif re.match(r'^\d+\.\s', stripped):
            items.append(re.sub(r'^\d+\.\s+', '', stripped))
        # Checklist: - [x] item or - [ ] item
        elif stripped.startswith('- [x] ') or stripped.startswith('- [ ] '):
            items.append(stripped[6:])
        # Callout header: ### RSK:name
        elif stripped.startswith('### '):
            items.append(stripped[4:])
        else:
            # Could be a continuation or non-list line
            items.append(stripped)

    return items, diags


def parse_verbatim_block(block: HCorTEXBlock) -> Tuple[str, List[Diagnostic]]:
    """F-06: Parse a verbatim code block (``` ... ```)."""

    diags: List[Diagnostic] = []
    lines = block.content_lines

    # Find opening ``` and closing ```
    open_idx = None
    close_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```'):
            if open_idx is None:
                open_idx = i
            else:
                close_idx = i
                break

    if open_idx is None:
        return '\n'.join(lines), diags

    if close_idx is None:
        diags.append(Diagnostic(
            "E_BLOCK_NOT_PRESERVED",
            f"VIEW:{block.view_name} verbatim block has no closing ```",
            "error",
            f"VIEW:{block.view_name}",
        ))
        return '\n'.join(lines[open_idx + 1:]), diags

    content = '\n'.join(lines[open_idx + 1:close_idx])

    # v2.2.3 PRE-04 / F-32: preserve:verbatim means no strip/trim/normalize
    if block.preserve == "verbatim":
        return content, diags
    else:
        return content.strip(), diags


def parse_prose_block(block: HCorTEXBlock) -> Tuple[str, List[Diagnostic]]:
    """F-07: Parse a prose block (HUMAN_BLOCK with preserve_human_block).

    v2.4.0: Preserve content faithfully — strip leading blank lines and
    title header, keep internal structure.
    """

    diags: List[Diagnostic] = []
    lines = []
    skip_headers = True
    for line in block.content_lines:
        stripped = line.strip()
        if skip_headers:
            if not stripped:
                continue
            if stripped.startswith('#'):
                continue
            skip_headers = False
        lines.append(line)
    # Strip trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines), diags
