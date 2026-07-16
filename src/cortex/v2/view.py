# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

r"""VIEW directives — declarative reversible render for CORTEX ⇄ HCORTEX-R.

Implements the VIEW sigilo: a declarative contract inside CORTEX that
specifies how entries should be rendered as human Markdown (HCORTEX-R)
and how to reconstruct them back.

Architecture:
  CORTEX + VIEW → CortexV2Document → SkillIR → render with VIEW → HCORTEX-R
  HCORTEX-R → parse VIEW markers → reverse strategies → CORTEX + VIEW
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ViewKind(str, Enum):
    TABLE = "table"
    KV_TABLE = "kv_table"
    MATRIX = "matrix"
    LIST = "list"
    NUMBERED_LIST = "numbered_list"
    CHECKLIST = "checklist"
    PROSE = "prose"
    QUOTE = "quote"
    PUML = "puml"
    CODE = "code"
    CALLOUT = "callout"
    SECTION = "section"
    RAW = "raw"


class ReverseStrategy(str, Enum):
    ROWS_TO_ENTRIES = "rows_to_entries"
    ROW_TO_ATTRS = "row_to_attrs"
    COLUMNS_TO_ATTRS = "columns_to_attrs"
    ITEMS_TO_ENTRIES = "items_to_entries"
    ITEMS_TO_ORDERED_ENTRIES = "items_to_ordered_entries"
    ITEMS_TO_STATUS_ENTRIES = "items_to_status_entries"
    BODY_TO_CUERPO = "body_to_cuerpo"
    VERBATIM_TO_BLOQUE = "verbatim_to_bloque"
    CALLOUT_TO_RISK = "callout_to_risk"
    CALLOUT_TO_LIMIT = "callout_to_limit"
    PRESERVE_HUMAN_BLOCK = "preserve_human_block"
    IGNORE_WITH_WARNING = "ignore_with_warning"
    MANUAL_REVIEW = "manual_review"


# Compatibility matrix: which reverse strategies are valid for each kind
KIND_REVERSE_COMPAT: Dict[ViewKind, Set[ReverseStrategy]] = {
    ViewKind.TABLE: {ReverseStrategy.ROWS_TO_ENTRIES, ReverseStrategy.COLUMNS_TO_ATTRS},
    ViewKind.KV_TABLE: {ReverseStrategy.ROW_TO_ATTRS},
    ViewKind.MATRIX: {ReverseStrategy.COLUMNS_TO_ATTRS, ReverseStrategy.ROWS_TO_ENTRIES},
    ViewKind.LIST: {ReverseStrategy.ITEMS_TO_ENTRIES, ReverseStrategy.BODY_TO_CUERPO},
    ViewKind.NUMBERED_LIST: {ReverseStrategy.ITEMS_TO_ORDERED_ENTRIES},
    ViewKind.CHECKLIST: {ReverseStrategy.ITEMS_TO_STATUS_ENTRIES},
    ViewKind.PROSE: {ReverseStrategy.BODY_TO_CUERPO, ReverseStrategy.PRESERVE_HUMAN_BLOCK},
    ViewKind.QUOTE: {ReverseStrategy.BODY_TO_CUERPO},
    ViewKind.PUML: {ReverseStrategy.VERBATIM_TO_BLOQUE},
    ViewKind.CODE: {ReverseStrategy.VERBATIM_TO_BLOQUE},
    ViewKind.CALLOUT: {ReverseStrategy.CALLOUT_TO_RISK, ReverseStrategy.CALLOUT_TO_LIMIT, ReverseStrategy.PRESERVE_HUMAN_BLOCK},
    ViewKind.SECTION: {ReverseStrategy.PRESERVE_HUMAN_BLOCK},
    ViewKind.RAW: {ReverseStrategy.VERBATIM_TO_BLOQUE, ReverseStrategy.PRESERVE_HUMAN_BLOCK},
}


# ---------------------------------------------------------------------------
# ViewDirective
# ---------------------------------------------------------------------------

@dataclass
class ViewDirective:
    """A VIEW directive parsed from CORTEX.

    Fields match the contract: ``kind|target|fields|order|reverse|scope|title|status``
    """

    name: str
    kind: ViewKind
    target: str
    reverse: ReverseStrategy
    status: str = "cur"
    fields: Optional[str] = None
    order: Optional[str] = None
    title: Optional[str] = None
    scope: Optional[str] = None
    section: Optional[str] = None
    source_section: Optional[str] = None
    preserve: Optional[str] = None
    hash: Optional[str] = None
    fallback: Optional[str] = None
    raw: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "target": self.target,
            "reverse": self.reverse.value,
            "status": self.status,
            "fields": self.fields,
            "order": self.order,
            "title": self.title,
            "scope": self.scope,
            "preserve": self.preserve,
        }


@dataclass
class ViewDiagnostic:
    """Diagnostic from VIEW parsing/validation."""

    code: str
    message: str
    view_name: Optional[str] = None
    severity: str = "warning"  # warning | error | info

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "view_name": self.view_name, "severity": self.severity}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

VALID_KINDS = frozenset(k.value for k in ViewKind)
VALID_REVERSES = frozenset(r.value for r in ReverseStrategy)
VALID_VIEW_STATUSES = frozenset({"cur", "planned", "deprecated", "human_only", "generated", "edited"})


def parse_view_entry(name: str, attrs: Dict[str, Any], raw: str = "") -> Tuple[Optional[ViewDirective], List[ViewDiagnostic]]:
    """Parse a VIEW entry from its attrs dict.

    Returns (directive, diagnostics).  If the directive is invalid,
    returns (None, diagnostics).
    """

    diags: List[ViewDiagnostic] = []

    # Required fields
    kind_str = attrs.get("kind")
    target = attrs.get("target")
    reverse_str = attrs.get("reverse")
    status = attrs.get("status", "cur")

    # Validate kind
    if not kind_str:
        diags.append(ViewDiagnostic("E_VIEW_UNKNOWN_KIND", f"VIEW:{name} missing required field 'kind'", name, "error"))
        return None, diags
    if kind_str not in VALID_KINDS:
        diags.append(ViewDiagnostic("E_VIEW_UNKNOWN_KIND", f"VIEW:{name} has unknown kind '{kind_str}'", name, "error"))
        return None, diags

    # Validate target
    if not target:
        diags.append(ViewDiagnostic("E_VIEW_EMPTY_TARGET", f"VIEW:{name} missing required field 'target'", name, "error"))
        return None, diags

    # Validate reverse
    if not reverse_str:
        diags.append(ViewDiagnostic("E_VIEW_UNKNOWN_REVERSE", f"VIEW:{name} missing required field 'reverse'", name, "error"))
        return None, diags
    if reverse_str not in VALID_REVERSES:
        diags.append(ViewDiagnostic("E_VIEW_UNKNOWN_REVERSE", f"VIEW:{name} has unknown reverse '{reverse_str}'", name, "error"))
        return None, diags

    kind = ViewKind(kind_str)
    reverse = ReverseStrategy(reverse_str)

    # Validate kind/reverse compatibility
    if reverse not in KIND_REVERSE_COMPAT.get(kind, set()):
        diags.append(ViewDiagnostic(
            "E_VIEW_INCOMPATIBLE_REVERSE",
            f"VIEW:{name} kind='{kind_str}' is incompatible with reverse='{reverse_str}'",
            name, "error"
        ))
        return None, diags

    # Validate status
    if status not in VALID_VIEW_STATUSES:
        diags.append(ViewDiagnostic(
            "W_VIEW_UNKNOWN_STATUS",
            f"VIEW:{name} has unknown status '{status}', defaulting to 'cur'",
            name, "warning"
        ))
        status = "cur"

    directive = ViewDirective(
        name=name,
        kind=kind,
        target=target,
        reverse=reverse,
        status=status,
        fields=attrs.get("fields"),
        order=attrs.get("order"),
        title=attrs.get("title"),
        scope=attrs.get("scope"),
        section=attrs.get("section"),
        source_section=attrs.get("source_section"),
        preserve=attrs.get("preserve"),
        hash=attrs.get("hash"),
        fallback=attrs.get("fallback"),
        raw=raw,
    )

    return directive, diags


def parse_view_entries_from_doc(doc) -> Tuple[List[ViewDirective], List[ViewDiagnostic]]:
    """Extract and parse all VIEW entries from a CortexV2Document.

    v2.2.1: VIEW entries in $0 with type/risk/cortex/desc are sigil declarations,
    NOT operational directives.  Only VIEW entries outside $0 (or in $0 without
    sigil_decl characteristics) are treated as directives.

    Returns (directives, diagnostics).
    """

    directives: List[ViewDirective] = []
    all_diags: List[ViewDiagnostic] = []
    seen_names: Set[str] = set()

    for sec in doc.sections:
        for entry in sec.entries:
            if entry.sigil != "VIEW":
                continue

            # v2.2.1 P0-2: In $0, if entry has type/risk/cortex/desc, it's a sigil declaration
            if sec.id == "$0" and isinstance(entry.value, dict):
                if any(k in entry.value for k in ("type", "risk", "cortex", "desc")):
                    # This is a sigil declaration, not a directive — skip
                    continue

            # Outside $0 (or $0 without sigil_decl characteristics): parse as directive
            directive, diags = parse_view_entry(entry.name, entry.value, entry.raw)
            all_diags.extend(diags)
            if directive is not None:
                if directive.name in seen_names:
                    all_diags.append(ViewDiagnostic(
                        "E_VIEW_DUPLICATE_NAME",
                        f"VIEW:{directive.name} is defined more than once",
                        directive.name, "error"
                    ))
                else:
                    seen_names.add(directive.name)
                    directives.append(directive)

    return directives, all_diags


# ---------------------------------------------------------------------------
# Target resolution
# ---------------------------------------------------------------------------

def resolve_target(target: str, doc) -> List:
    """Resolve a VIEW target selector against a CortexV2Document.

    Returns a list of matching V2Entry objects.
    """

    from .parser import V2Entry

    results: List[V2Entry] = []

    # $0:canonical_sigils — sigil declarations in $0
    if target == "$0:canonical_sigils":
        sec0 = doc.get_section("$0")
        if sec0:
            for e in sec0.entries:
                if e.entry_type == "sigil_decl":
                    results.append(e)
        return results

    # $0:contracts — contract entries in $0
    if target == "$0:contracts":
        sec0 = doc.get_section("$0")
        if sec0:
            for e in sec0.entries:
                if e.sigil == "$0" and e.name.startswith("contract_"):
                    results.append(e)
        return results

    # $0:microtokens — micro-token entries in $0
    if target == "$0:microtokens":
        sec0 = doc.get_section("$0")
        if sec0:
            for e in sec0.entries:
                if e.sigil == "$0" and e.name.startswith("micro_"):
                    results.append(e)
        return results

    # $0:type_decls — type declaration entries in $0
    if target == "$0:type_decls":
        sec0 = doc.get_section("$0")
        if sec0:
            for e in sec0.entries:
                if e.sigil == "$0" and e.name.startswith("type_"):
                    results.append(e)
        return results

    # $N:NAME — specific entry by name within section $N (v2.2.2: handles $0:enum_state, $0:delimiters, etc.)
    # Single-colon, starts with $ → match by entry name within the section
    if ":" in target and target.count(":") == 1 and target.startswith("$"):
        parts = target.split(":", 1)
        sec_id = parts[0]
        name = parts[1]
        sec = doc.get_section(sec_id)
        if sec:
            for e in sec.entries:
                if e.name == name:
                    results.append(e)
        return results

    # $N — entire section
    if target.startswith("$") and ":" not in target:
        sec = doc.get_section(target)
        if sec:
            results.extend(sec.entries)
        return results

    # $N:SIGIL:* — all entries of a sigil within a section
    # $N:SIGIL:name — specific entry within a section (v2.2.2: fix 3-part name selector)
    if ":" in target and target.count(":") == 2 and target.startswith("$"):
        parts = target.split(":")
        sec_id = parts[0]
        sigil = parts[1]
        third = parts[2]
        sec = doc.get_section(sec_id)
        if sec:
            if third == "*":
                for e in sec.entries:
                    if e.sigil == sigil:
                        results.append(e)
            else:
                # specific entry name within section
                for e in sec.entries:
                    if e.sigil == sigil and e.name == third:
                        results.append(e)
        return results

    # SIGIL:* — all entries of a sigil (any section)
    if ":" in target and target.endswith(":*"):
        sigil = target.split(":")[0]
        for sec in doc.sections:
            for e in sec.entries:
                if e.sigil == sigil:
                    results.append(e)
        return results

    # SIGIL:name — exact entry (2-part, no section qualifier)
    if ":" in target and "*" not in target and not target.startswith("$"):
        parts = target.split(":", 1)
        sigil = parts[0]
        name = parts[1]
        for sec in doc.sections:
            for e in sec.entries:
                if e.sigil == sigil and e.name == name:
                    results.append(e)
        return results

    # HUMAN_BLOCK:name — no CORTEX entries, returns empty
    if target.startswith("HUMAN_BLOCK:"):
        return results

    # group:name — resolve via group (not yet implemented)
    if target.startswith("group:"):
        return results

    return results


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------

def calculate_view_coverage(doc, directives: List[ViewDirective]) -> Tuple[float, List[str]]:
    """Calculate VIEW coverage: what fraction of eligible entries are covered.

    v2.3.1 P0-5: 0 eligible entries + 0 directives = 0% (not 100%).
    A document with no content cannot be "fully covered" — it's empty.

    Returns (coverage_fraction, uncovered_entry_descriptions).
    """

    # Collect all eligible entries (exclude VIEW entries and $0 metadata)
    eligible: List[str] = []
    covered: Set[str] = set()

    for sec in doc.sections:
        for entry in sec.entries:
            if entry.sigil == "VIEW":
                continue
            if entry.sigil == "$0" and entry.entry_type == "meta":
                continue
            desc = f"{entry.section}/{entry.sigil}:{entry.name}"
            eligible.append(desc)

    # v2.3.1 P0-5: If there are no eligible entries, coverage is 0% (not 100%)
    # unless there are also no directives AND no sections (truly empty doc).
    # A document with content but no VIEW directives must report 0%.
    if len(eligible) == 0:
        if len(directives) == 0:
            # Truly empty document
            return 0.0, []
        # Directives exist but nothing to cover (shouldn't happen)
        return 0.0, []

    # Resolve each directive's target and mark covered entries
    for directive in directives:
        matched = resolve_target(directive.target, doc)
        for entry in matched:
            desc = f"{entry.section}/{entry.sigil}:{entry.name}"
            covered.add(desc)

    uncovered = [desc for desc in eligible if desc not in covered]
    total = len(eligible)
    coverage = (total - len(uncovered)) / total if total > 0 else 0.0

    return coverage, uncovered
