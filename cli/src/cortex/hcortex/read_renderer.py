"""HCORTEX-READ renderer — human-friendly Markdown with profile support.

Per Section 8.1 and 9 of the SKILL:
  - First line declares ``Perfil: CORTEX-<LEVEL>``.
  - Filters entries by P-level/survive according to the profile.
  - Orders entries P0 → P5.
  - In ``AUDIT`` mode, adds a ``source`` column with ``<SIGIL>:<name>``.
  - Declares any omissions by profile budget.
  - Does NOT guarantee reconstruction (roundtrip:false).

Modes (Section 9.2):
  - ``READABLE``  — clean executive view, no source column
  - ``AUDIT``     — adds ``source`` column for traceability
  - ``RECOVERY``  — only P0/P1 entries (alias for profile=RECOVERY + READABLE)
  - ``FULL``      — all entries (alias for profile=FULL + AUDIT)
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..core.ast import CortexDocument, Entry, Glossary
from ..core.writer import serialize_value
from .markdown_model import HCORTEX_READ_HEADER
from .profiles import (
    filter_by_profile,
    resolve_profile,
    sort_by_plevel,
)


# Human-friendly section titles (when the .cortex title is empty)
SECTION_TITLES = {
    "$0": "Glossary (omitted)",
    "$1": "Identity",
    "$2": "Active Work",
    "$3": "Governance",
    "$4": "Rules",
    "$5": "Risks & Limits",
    "$6": "Diagrams",
    "$7": "Field Contracts",
    "$8": "Survival & Priorities",
    "$9": "Context Profiles",
    "$10": "Degradation Policy",
}

# Human-readable sigil names (English) — for header translation
SIGIL_NAMES = {
    "IDN": "Identity",
    "DOM": "Domain",
    "AXM": "Axiom",
    "CNST": "Constraint",
    "FCS": "Focus",
    "OBJ": "Objective",
    "WRK": "Work State",
    "STP": "Next Step",
    "NXT": "Queued Action",
    "RSK": "Risk",
    "AUD": "Audit",
    "STAT": "Status",
    "REF": "Reference",
    "KNW": "Knowledge",
    "SES": "Session",
    "LNG": "Lesson",
    "DIAG": "Diagram",
    "CLAIM": "Claim",
    "LIM": "Limit",
    "HDL": "Handler",
    "TAG": "Tag",
    "PFL": "Pitfall",
    "DEP": "Dependency",
    "DESC": "Description",
    "ERR": "Error",
    "!": "Rule",
}


# Mode aliases (Section 9.2 of SKILL.md)
MODE_PROFILE_ALIAS = {
    "RECOVERY": "RECOVERY",
    "FULL": "FULL",
}


def render_attrs_table(entry: Entry, with_source: bool = False) -> List[str]:
    """Render an attrs entry as a Markdown key/value table.

    When ``with_source=True`` (AUDIT mode), a third column ``source``
    is appended with the ``<SIGIL>:<name>`` tag for traceability.
    """

    if with_source:
        lines = [
            "| key | value | source |",
            "| --- | --- | --- |",
        ]
    else:
        lines = [
            "| key | value |",
            "| --- | --- |",
        ]
    if isinstance(entry.value, dict):
        rows = list(entry.value.items())
    else:
        rows = [("value", entry.value)]
    src = f"{entry.sigil}:{entry.name}"
    for k, v in rows:
        if isinstance(v, str):
            val = v.replace("|", "\\|")
        else:
            val = serialize_value(v)
        if with_source:
            lines.append(f"| {k} | {val} | `{src}` |")
        else:
            lines.append(f"| {k} | {val} |")
    return lines


def render_cuerpo(entry: Entry) -> List[str]:
    text = str(entry.value or "").rstrip()
    return ["```text", text, "```"] if text else []


def render_bloque(entry: Entry) -> List[str]:
    text = str(entry.value or "").rstrip()
    lang = "text"
    if "@startuml" in text or "@enduml" in text:
        lang = "puml"
    return [f"```{lang}", text, "```"]


def render_entry(
    entry: Entry,
    glossary: Glossary,
    with_source: bool = False,
    plevel: Optional[str] = None,
) -> List[str]:
    """Render a single entry to Markdown lines.

    ``plevel`` (when provided) is shown as a small badge next to the
    heading so the reader can see the priority pack assignment.

    v1.1.3 P1-7: in AUDIT mode (``with_source=True``), cuerpo and bloque
    entries now get a visible ``source: `<SIGIL>:<name>` `` line before
    the block, so traceability is uniform across all entry types.
    """

    out: List[str] = []
    sigil_name = SIGIL_NAMES.get(entry.sigil, entry.sigil)
    header = f"### {sigil_name}: {entry.name}"
    if plevel:
        header += f" <sub>[{plevel}]</sub>"
    if with_source and not plevel:
        header += f" <sub>[{entry.sigil}:{entry.name}]</sub>"
    out.append(header)
    out.append("")
    if entry.type in ("attrs", "attrs-pos"):
        out.extend(render_attrs_table(entry, with_source=with_source))
    elif entry.type == "cuerpo":
        # v1.1.3 P1-7: visible source line for cuerpo in audit mode
        if with_source:
            out.append(f"source: `{entry.sigil}:{entry.name}`")
            out.append("")
        out.extend(render_cuerpo(entry))
    elif entry.type == "bloque":
        # v1.1.3 P1-7: visible source line for bloque in audit mode
        if with_source:
            out.append(f"source: `{entry.sigil}:{entry.name}`")
            out.append("")
        out.extend(render_bloque(entry))
    elif entry.type == "relación":
        if with_source:
            out.append(f"source: `{entry.sigil}:{entry.name}`")
            out.append("")
        out.append(f"```\n{entry.value}\n```")
    else:
        out.append(str(entry.value))
    out.append("")
    return out


def render_hcortex_read(
    doc: CortexDocument,
    with_source: bool = False,
    profile: Optional[str] = None,
    mode: str = "READABLE",
    layout: Optional[str] = None,
) -> str:
    """Render ``doc`` as HCORTEX-READ Markdown.

    ``profile`` may be ``MIN``, ``RECOVERY``, ``WORK`` or ``FULL``.
    ``mode`` may be ``READABLE``, ``AUDIT``, ``RECOVERY`` or ``FULL``.
    ``layout`` may be ``priority`` (global P0→P5), ``section``
    (preserve section grouping), or ``None`` (auto-select).

    Mode aliases:
      - ``RECOVERY`` ≡ profile=RECOVERY, mode=READABLE, layout=priority
      - ``FULL``      ≡ profile=FULL, mode=AUDIT

    Layout auto-selection (re-audit H-RA-03):
      - MIN, RECOVERY, AUDIT (default) → ``priority`` (global P0→P5)
      - WORK, FULL, READABLE (default)  → ``section`` (preserve sections)

    The first line of the output declares the profile (Section 9.3 of
    SKILL.md), making it auditable.
    """

    # Resolve mode aliases
    if mode in MODE_PROFILE_ALIAS:
        profile = profile or MODE_PROFILE_ALIAS[mode]
        if mode == "FULL":
            with_source = True

    prof = resolve_profile(profile)
    audit_mode = (mode.upper() == "AUDIT") or with_source
    # v1.1.3 P1-6: report the actual mode the user requested (not a hardcoded
    # "READABLE" string).  AUDIT mode must declare Mode: AUDIT.
    audit_mode_str = "AUDIT" if audit_mode else mode.upper()

    # Layout auto-selection (re-audit H-RA-03)
    if layout is None:
        if prof.name in ("MIN", "RECOVERY") or audit_mode:
            layout = "priority"
        else:
            layout = "section"
    layout = layout.lower()

    # Filter entries by profile
    result = filter_by_profile(doc, prof)
    kept = sort_by_plevel(result.kept)

    out: List[str] = []
    # v1.1.3 P1-5: Perfil MUST be the first real line of HCORTEX output
    # (SKILL.md §9.3).  The cortex-render marker goes on the SECOND line
    # so that auditors and parsers see the profile first.
    out.append(f"Perfil: CORTEX-{prof.name}")
    out.append(HCORTEX_READ_HEADER)
    out.append("")
    out.append("# HCORTEX-READ")
    out.append("")
    out.append(
        f"> Non-reversible human view. Profile: {prof.name} "
        f"(P-levels: {', '.join(prof.plevels)}). "
        f"Mode: {audit_mode_str}. Layout: {layout}."
    )
    out.append("")

    # v1.1.5 P1-5: warn if $0 contains operational entries (hidden from HCORTEX)
    GLOSSARY_ENTRY_SIGILS = frozenset({"GSIG", "GTYP", "GMIC", "GCON"})
    zero_section_ops = []
    for sec in doc.sections:
        if sec.id != "$0":
            continue
        for entry in sec.entries:
            if entry.sigil not in GLOSSARY_ENTRY_SIGILS:
                zero_section_ops.append(f"{entry.sigil}:{entry.name}")
    if zero_section_ops:
        out.append("> ⚠ **WARNING**: $0 contains operational entries that are "
                   "hidden from this view:")
        for op in zero_section_ops[:10]:
            out.append(f"> - `{op}`")
        if len(zero_section_ops) > 10:
            out.append(f"> - ... and {len(zero_section_ops) - 10} more")
        out.append("> Run `cortex verify --strict` to fix (E033_ZERO_SECTION_MEMORY_ENTRY).")
        out.append("")

    if layout == "priority":
        # Global P0→P5 order — re-audit H-RA-03
        # Group entries by P-level, then by section within each P-level
        out.extend(_render_priority_layout(kept, doc, audit_mode))
    else:
        # Section-grouped layout (original behaviour)
        sections_kept: dict = {}
        for sec_id, entry, plevel in kept:
            sections_kept.setdefault(sec_id, []).append((entry, plevel))
        for sec in doc.sections:
            if sec.id == "$0":
                continue
            if sec.id not in sections_kept:
                continue
            title = sec.title or SECTION_TITLES.get(sec.id, sec.id)
            out.append(f"## {sec.id} · {title}")
            out.append("")
            for entry, plevel in sections_kept[sec.id]:
                out.extend(render_entry(
                    entry, doc.glossary,
                    with_source=audit_mode,
                    plevel=plevel,
                ))

    # Declare omissions
    if result.omitted:
        out.append("## Omissions by profile")
        out.append("")
        out.append(
            f"The following entries were omitted by profile **{prof.name}** "
            f"(allowed P-levels: {', '.join(prof.plevels)}):"
        )
        out.append("")
        out.append("| section | sigil | name | plevel | reason |")
        out.append("| --- | --- | --- | --- | --- |")
        for sec_id, entry, plevel, reason in result.omitted:
            out.append(
                f"| {sec_id} | {entry.sigil} | {entry.name} | {plevel} | {reason} |"
            )
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def _render_priority_layout(
    kept: List[Tuple[str, Entry, str]],
    doc: CortexDocument,
    audit_mode: bool,
) -> List[str]:
    """Render entries grouped by P-level (P0 first, P5 last).

    Re-audit H-RA-03: ensures global P0→P5 order regardless of original
    section order.
    """

    from .profiles import PLEVEL_ORDER
    out: List[str] = []
    # Group by P-level preserving the global sort
    by_plevel: dict = {}
    for sec_id, entry, plevel in kept:
        by_plevel.setdefault(plevel, []).append((sec_id, entry))

    for plevel in PLEVEL_ORDER:
        if plevel not in by_plevel:
            continue
        out.append(f"## Priority {plevel}")
        out.append("")
        for sec_id, entry in by_plevel[plevel]:
            # Include section as a sub-heading for traceability
            out.append(f"<!-- section: {sec_id} · {entry.sigil}:{entry.name} · {plevel} -->")
            out.extend(render_entry(
                entry, doc.glossary,
                with_source=audit_mode,
                plevel=plevel,
            ))
    return out
