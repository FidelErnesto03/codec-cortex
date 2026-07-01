r"""VIEW renderer — renders CORTEX entries as HCORTEX with VIEW markers.

v2.2.1: HCORTEX-R eliminated. HCORTEX is reversible by definition when
VIEW coverage is valid. Header uses internal_encoding: HCORTEX (not HCORTEX-R).
DIAG with preserve:verbatim is byte-identical (no strip/trim).
VIEW markers preserve all metadata fields.
E_VIEW_* errors produce rc!=0.
"""

from __future__ import annotations

from typing import List, Tuple

from .parser import CortexV2Document, V2Entry
from .view import (
    ViewDirective, ViewKind, ViewDiagnostic,
    parse_view_entries_from_doc, resolve_target, calculate_view_coverage,
)


def render_hcortex(doc: CortexV2Document, mode: str = "normal") -> Tuple[str, List[ViewDiagnostic]]:
    """Render a CORTEX v2 document as canonical HCORTEX (reversible).

    v2.2.1: Uses internal_encoding: HCORTEX (not HCORTEX-R).
    v2.2.3 PRE-04: ``reversible: true`` only if coverage == 1.0 AND no E_VIEW_* errors.
    v2.2.3 PRE-05: ``mode = "display"`` produces Markdown without reversible contract.
    Returns (markdown, diagnostics).
    Errors in diagnostics mean the caller should return rc!=0.
    """

    diags: List[ViewDiagnostic] = []

    # 1. Extract VIEW directives
    directives, view_diags = parse_view_entries_from_doc(doc)
    diags.extend(view_diags)

    # 2. Calculate coverage
    coverage, uncovered = calculate_view_coverage(doc, directives)
    if coverage < 1.0:
        for desc in uncovered[:20]:
            diags.append(ViewDiagnostic(
                "W_VIEW_UNUSED_ENTRY",
                f"entry {desc} is not covered by any VIEW directive",
                severity="warning"
            ))

    # v2.2.3 PRE-04: Gate reversible:true
    # Only reversible if coverage == 100% AND no E_VIEW_* errors
    has_errors = any(d.severity == "error" and d.code.startswith("E_VIEW_") for d in diags)
    is_reversible = (coverage == 1.0) and (not has_errors) and (mode != "display")

    # v2.2.3 PRE-05: Display mode → not canonical HCORTEX
    if mode == "display":
        diags.append(ViewDiagnostic(
            "W_HCORTEX_DISPLAY_ONLY",
            "display mode produces Markdown without reversible contract — not canonical HCORTEX",
            severity="warning"
        ))

    # 3. Build header — v2.2.1: HCORTEX (not HCORTEX-R)
    lines: List[str] = []
    lines.append("<!-- CODEC-CORTEX")
    lines.append("internal_encoding: HCORTEX")
    if "source_artifact" in doc.header:
        lines.append(f"source_artifact: {doc.header['source_artifact']}")
    if "source_version" in doc.header:
        lines.append(f"source_version: {doc.header['source_version']}")
    if "status" in doc.header:
        lines.append(f"status: {doc.header['status']}")
    lines.append(f"derived_from: {doc.header.get('source_artifact', 'skill/cortex/SKILL.md')}")
    # v2.2.3 PRE-04: reversible reflects real state
    lines.append(f"reversible: {'true' if is_reversible else 'false'}")
    lines.append("view_schema: 1")
    lines.append(f"view_coverage: {int(coverage * 100)}")
    if mode == "display":
        lines.append("mode: display")
    lines.append("-->")
    lines.append("")
    lines.append("**Perfil: CORTEX-FULL**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 4. Render each VIEW directive in order
    covered_entries: set = set()
    for directive in directives:
        block_lines = _render_view_block(doc, directive, covered_entries, diags)
        if block_lines:
            lines.extend(block_lines)
            lines.append("")

    # 5. Report coverage
    lines.append("---")
    lines.append("")
    lines.append(f"<!-- VIEW coverage: {coverage:.1%} ({len(covered_entries)} entries covered) -->")
    if uncovered:
        lines.append(f"<!-- Uncovered entries: {len(uncovered)} -->")

    return "\n".join(lines).rstrip() + "\n", diags


# Keep old name as alias for backward compatibility
render_hcortex_r = render_hcortex


def has_view_errors(diags: List[ViewDiagnostic]) -> bool:
    """Check if diagnostics contain any E_VIEW_* errors."""
    return any(d.code.startswith("E_VIEW_") and d.severity == "error" for d in diags)


def has_view_warnings(diags: List[ViewDiagnostic]) -> bool:
    """v2.2.2: Check if diagnostics contain any W_VIEW_* warnings."""
    return any(d.code.startswith("W_VIEW_") and d.severity == "warning" for d in diags)


def _render_view_block(
    doc: CortexV2Document,
    directive: ViewDirective,
    covered_entries: set,
    diags: List[ViewDiagnostic],
) -> List[str]:
    """Render a single VIEW directive as an HCORTEX block."""

    entries = resolve_target(directive.target, doc)
    if not entries and not directive.target.startswith("HUMAN_BLOCK:"):
        # v2.2.2 P0-2: renamed E_VIEW_EMPTY_TARGET → W_VIEW_EMPTY_TARGET
        # Empty target is recoverable (e.g., missing optional section), so warning.
        diags.append(ViewDiagnostic(
            "W_VIEW_EMPTY_TARGET",
            f"VIEW:{directive.name} target '{directive.target}' resolved to 0 entries",
            directive.name, "warning"
        ))

    # v2.2.2 P0-5: Heterogeneous target detection
    # If target matches entries with different entry_types AND no explicit fields,
    # the renderer can't infer consistent columns → emit W_VIEW_HETEROGENEOUS_TARGET
    if entries and not directive.fields and len(entries) > 1:
        entry_types = {e.entry_type for e in entries}
        attr_key_sets = set()
        for e in entries:
            if isinstance(e.value, dict):
                attr_key_sets.add(frozenset(e.value.keys()))
        # Heterogeneous if: different entry_types OR different attr key sets
        if len(entry_types) > 1 or len(attr_key_sets) > 1:
            diags.append(ViewDiagnostic(
                "W_VIEW_HETEROGENEOUS_TARGET",
                f"VIEW:{directive.name} target '{directive.target}' is heterogeneous "
                f"(entry_types={sorted(entry_types)}, {len(attr_key_sets)} distinct attr schemas). "
                f"Add explicit `fields` to silence.",
                directive.name, "warning"
            ))

    for e in entries:
        covered_entries.add(f"{e.section}/{e.sigil}:{e.name}")

    lines: List[str] = []

    # v2.2.1 P0-6: Opening marker with ALL metadata fields
    marker_parts = [f"VIEW:{directive.name}"]
    marker_parts.append(f"kind={directive.kind.value}")
    marker_parts.append(f'target="{directive.target}"')
    marker_parts.append(f"reverse={directive.reverse.value}")
    if directive.fields:
        marker_parts.append(f'fields="{directive.fields}"')
    if directive.order:
        marker_parts.append(f"order={directive.order}")
    if directive.title:
        marker_parts.append(f'title="{directive.title}"')
    if directive.status:
        marker_parts.append(f"status={directive.status}")
    if directive.scope:
        marker_parts.append(f'scope="{directive.scope}"')
    if directive.section:
        marker_parts.append(f'section="{directive.section}"')
    if directive.source_section:
        marker_parts.append(f'source_section="{directive.source_section}"')
    if directive.preserve:
        marker_parts.append(f"preserve={directive.preserve}")
    if directive.hash:
        marker_parts.append(f'hash="{directive.hash}"')
    if directive.fallback:
        marker_parts.append(f'fallback="{directive.fallback}"')
    lines.append(f"<!-- {' '.join(marker_parts)} -->")

    if directive.title:
        lines.append(f"## {directive.title}")
        lines.append("")

    if directive.kind == ViewKind.TABLE:
        lines.extend(_render_table(entries, directive))
    elif directive.kind == ViewKind.KV_TABLE:
        lines.extend(_render_kv_table(entries, directive))
    elif directive.kind == ViewKind.PROSE:
        lines.extend(_render_prose(entries, directive))
    elif directive.kind == ViewKind.QUOTE:
        lines.extend(_render_quote(entries, directive))
    elif directive.kind == ViewKind.PUML:
        lines.extend(_render_puml(entries, directive))
    elif directive.kind == ViewKind.CODE:
        lines.extend(_render_code(entries, directive))
    elif directive.kind == ViewKind.LIST:
        lines.extend(_render_list(entries, directive))
    elif directive.kind == ViewKind.NUMBERED_LIST:
        lines.extend(_render_numbered_list(entries, directive))
    elif directive.kind == ViewKind.CHECKLIST:
        lines.extend(_render_checklist(entries, directive))
    else:
        lines.extend(_render_raw(entries, directive))

    lines.append(f"<!-- /VIEW:{directive.name} -->")
    return lines


def _escape_pipe(value) -> str:
    """v2.4.0: Escape | as \\| in table cell values."""
    if not isinstance(value, str):
        value = str(value)
    return value.replace('|', '\\|')


def _render_table(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    """v2.4.0: Add `source` column (SIGIL:name) for tables without name column.
    v2.4.0: Escape | in cell values; include ALL attrs not just declared fields.
    """
    if not entries:
        return ["_(no entries)_", ""]

    if directive.target == "$0:canonical_sigils":
        lines = [
            "| Sigilo | Nombre | Tipo | Riesgo | Corteza | Descripción |",
            "|---|---|---|:---:|---|---|",
        ]
        for e in entries:
            v = e.value
            lines.append(
                f"| `{e.sigil}` | {e.name} | `{v.get('type', '')}` | "
                f"{v.get('risk', '')} | {v.get('cortex', '')} | {v.get('desc', '')} |"
            )
        lines.append("")
        return lines

    if directive.target == "$0:contracts":
        lines = ["| Sigilo | Campos posicionales |", "|---|---|"]
        for e in entries:
            sigil_name = e.name.replace("contract_", "").upper()
            lines.append(f"| `{sigil_name}` | {_escape_pipe(e.value.get('pos', ''))} |")
        lines.append("")
        return lines

    if directive.target == "$0:microtokens":
        lines = ["| Token | Expansión |", "|---|---|"]
        for e in entries:
            token = e.name.replace("micro_", "")
            lines.append(f"| `{token}` | {e.value.get('expand', '')} |")
        lines.append("")
        return lines

    if directive.target == "$0:type_decls":
        lines = ["| Tipo | Regla |", "|---|---|"]
        for e in entries:
            type_name = e.name.replace("type_", "")
            lines.append(f"| `{type_name}` | {e.value.get('rule', '')} |")
        lines.append("")
        return lines

    if entries and entries[0].entry_type == "attrs-pos":
        # v2.4.0: HDL attrs-pos table — include source column
        lines = ["| Source | Operación | Estado | Requiere | Notas |", "|---|---|---|---|---|"]
        for e in entries:
            v = e.value
            source = f"`{e.sigil}:{e.name}`"
            lines.append(f"| {source} | {v.get('operation', '')} | {v.get('status', '')} | {v.get('requires', '')} | {v.get('notes', '')} |")
        lines.append("")
        return lines

    # v2.4.0: For tables without explicit name column, add a `Source` column
    # with SIGIL:name so the encoder can recover original names.
    if directive.fields:
        fields = [f.strip() for f in directive.fields.split(",")]
    else:
        if isinstance(entries[0].value, dict):
            fields = list(entries[0].value.keys())
        else:
            fields = ["value"]

    # v2.4.0: Include ALL attrs from entries, not just declared fields
    all_attrs: list = list(fields)
    for e in entries:
        if isinstance(e.value, dict):
            for k in e.value.keys():
                if k not in all_attrs:
                    all_attrs.append(k)
    ordered_fields = all_attrs

    # Check if any field is "name" or "sigil" — if not, add Source column
    has_name_col = any(f.lower() in ("name", "nombre", "sigil", "sigilo") for f in ordered_fields)
    if has_name_col:
        header_labels = [f.capitalize() for f in ordered_fields]
        lines = [f"| {' | '.join(header_labels)} |"]
        lines.append(f"|{'|'.join(['---'] * len(ordered_fields))}|")
        for e in entries:
            if isinstance(e.value, dict):
                row = [_escape_pipe(e.value.get(f, "")) for f in ordered_fields]
            else:
                row = [_escape_pipe(e.value) if i == 0 else "" for i, f in enumerate(ordered_fields)]
            lines.append(f"| {' | '.join(row)} |")
    else:
        # v2.4.0: Add Source column
        header_labels = ["Source"] + [f.capitalize() for f in ordered_fields]
        col_count = len(ordered_fields) + 1
        lines = [f"| {' | '.join(header_labels)} |"]
        lines.append(f"|{'|'.join(['---'] * col_count)}|")
        for e in entries:
            source = f"`{e.sigil}:{e.name}`"
            if isinstance(e.value, dict):
                row = [source] + [_escape_pipe(e.value.get(f, "")) for f in ordered_fields]
            else:
                row = [source] + [_escape_pipe(e.value) if i == 0 else "" for i, f in enumerate(ordered_fields)]
            lines.append(f"| {' | '.join(row)} |")
    lines.append("")
    return lines


def _render_kv_table(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    """v2.4.0: For group targets, render each entry with a Source heading.
    v2.4.0: Escape | in values."""
    if not entries:
        return ["_(no entries)_", ""]
    lines: List[str] = []
    for e in entries:
        # v2.4.0: Always add Source heading for reversibility
        lines.append(f"**Source:** `{e.sigil}:{e.name}`")
        lines.append("")
        if not isinstance(e.value, dict):
            lines.append(str(e.value))
            lines.append("")
            continue
        fields = [f.strip() for f in directive.fields.split(",")] if directive.fields else list(e.value.keys())
        # v2.4.0: Include ALL attrs, not just declared fields
        all_keys = list(fields)
        for k in e.value.keys():
            if k not in all_keys:
                all_keys.append(k)
        lines.append("| Campo | Valor |")
        lines.append("|---|---|")
        for f in all_keys:
            lines.append(f"| {f} | {_escape_pipe(e.value.get(f, ''))} |")
        lines.append("")
    return lines


def _render_prose(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    """v2.4.0: Render prose faithfully — preserve original cuerpo text."""
    lines = []
    for e in entries:
        if e.entry_type == "cuerpo" or isinstance(e.value, str):
            lines.append(str(e.value))
            lines.append("")
    return lines


def _render_quote(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    lines = []
    for e in entries:
        if e.entry_type == "cuerpo" or isinstance(e.value, str):
            lines.append(f"> {e.value}")
            lines.append("")
    return lines


def _render_puml(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    """v2.4.0: Add Source heading; preserve verbatim content exactly."""
    lines = []
    for e in entries:
        if e.entry_type == "bloque" or isinstance(e.value, str):
            # v2.4.0: Add Source heading
            lines.append(f"**Source:** `{e.sigil}:{e.name}`")
            lines.append("")
            # v2.4.0: Preserve value as-is (including leading/trailing newlines)
            value = str(e.value)
            lines.append("```puml")
            lines.append(value)
            lines.append("```")
            lines.append("")
    return lines


def _render_code(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    lines = []
    for e in entries:
        if e.entry_type == "bloque" or isinstance(e.value, str):
            lines.append("```")
            if directive.preserve == "verbatim":
                lines.append(str(e.value))
            else:
                lines.append(str(e.value).strip())
            lines.append("```")
            lines.append("")
    return lines


def _render_list(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    """v2.3.1: Render list with proper field extraction, not dict literal."""
    lines = []
    for e in entries:
        if isinstance(e.value, dict):
            desc = (
                e.value.get("desc")
                or e.value.get("rule")
                or e.value.get("content")
                or e.value.get("action")
                or e.value.get("notes")
            )
            if not desc:
                desc = str(e.value)
            survive = e.value.get("survive")
            if survive and survive != desc:
                desc = f"{desc} (survive:{survive})"
            lines.append(f"- `{e.sigil}:{e.name}` — {desc}")
        else:
            lines.append(f"- {e.value}")
    lines.append("")
    return lines


def _render_numbered_list(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    """v2.4.0: Render numbered list with Source marker for reversibility."""
    lines = []
    for i, e in enumerate(entries, 1):
        if isinstance(e.value, dict):
            text = (
                e.value.get("rule")
                or e.value.get("desc")
                or e.value.get("action")
                or e.value.get("notes")
                or str(e.value)
            )
            survive = e.value.get("survive")
            if survive and survive != text:
                text = f"{text} (survive:{survive})"
            # v2.4.0: Include source for reversibility
            lines.append(f"{i}. `{e.sigil}:{e.name}` — {text}")
        else:
            lines.append(f"{i}. `{e.sigil}:{e.name}` — {e.value}")
    lines.append("")
    return lines


def _render_checklist(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    lines = []
    for e in entries:
        if isinstance(e.value, dict):
            status = e.value.get("status", "")
            checked = "x" if status in ("done", "cur") else " "
            desc = e.value.get("desc", e.value.get("rule", str(e.value)))
            lines.append(f"- [{checked}] `{e.sigil}:{e.name}` — {desc}")
        else:
            lines.append(f"- [ ] {e.value}")
    lines.append("")
    return lines


def _render_raw(entries: List[V2Entry], directive: ViewDirective) -> List[str]:
    lines = []
    for e in entries:
        lines.append(f"### {e.sigil}:{e.name}")
        lines.append("")
        if isinstance(e.value, dict):
            for k, v in e.value.items():
                lines.append(f"- {k}: {v}")
        else:
            lines.append(str(e.value))
        lines.append("")
    return lines
