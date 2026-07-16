# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Equivalence engine v2.3.0 — compare CORTEX and HCORTEX artefacts.

Implements F-16..F-22 from v2.3.0 spec:
  F-16: byte-identical comparison (CORTEX→CORTEX, HCORTEX→HCORTEX)
  F-17: AST-equivalent (same logical structure)
  F-18: semantic-equivalent (same operational meaning)
  F-19: content-equivalent (HCORTEX regenerado conserva contenido)
  F-20: diff by sigil
  F-21: diff by section
  F-22: diff by VIEW

Architecture:
  Two CortexV2Documents → compare → EquivalenceResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .parser import CortexV2Document, V2Entry


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class Diff:
    """A single difference between two documents."""
    kind: str  # added | removed | modified | moved
    location: str  # e.g. "$0/IDN:project" or "VIEW:foo"
    field: Optional[str] = None  # specific field if modified
    left: Any = None
    right: Any = None

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "location": self.location,
            "field": self.field,
            "left": str(self.left)[:200],
            "right": str(self.right)[:200],
        }


@dataclass
class EquivalenceResult:
    """Result of an equivalence comparison."""
    byte_identical: bool = False
    ast_equivalent: bool = False
    semantic_equivalent: bool = False
    content_equivalent: bool = False
    diffs: List[Diff] = field(default_factory=list)

    @property
    def equivalent(self) -> bool:
        """Equivalence at the AST level (the canonical notion)."""
        return self.ast_equivalent

    def to_dict(self) -> dict:
        return {
            "byte_identical": self.byte_identical,
            "ast_equivalent": self.ast_equivalent,
            "semantic_equivalent": self.semantic_equivalent,
            "content_equivalent": self.content_equivalent,
            "diffs": [d.to_dict() for d in self.diffs],
            "diff_count": len(self.diffs),
        }


# ---------------------------------------------------------------------------
# F-16: byte-identical comparison
# ---------------------------------------------------------------------------

def compare_byte_identical(left_bytes: bytes, right_bytes: bytes) -> bool:
    """F-16: Pure byte comparison."""
    return left_bytes == right_bytes


# ---------------------------------------------------------------------------
# F-17: AST-equivalent comparison
# ---------------------------------------------------------------------------

def compare_ast_equivalent(left: CortexV2Document, right: CortexV2Document) -> Tuple[bool, List[Diff]]:
    """F-17: Compare two CortexV2Documents at the AST level.

    AST-equivalent means same sections, same entries (by sigil:name),
    same entry types, same values (modulo key ordering in attrs).
    """

    diffs: List[Diff] = []

    # Compare sections
    left_sections = {s.id: s for s in left.sections}
    right_sections = {s.id: s for s in right.sections}

    for sec_id in left_sections:
        if sec_id not in right_sections:
            diffs.append(Diff("removed", sec_id, left=left_sections[sec_id]))
    for sec_id in right_sections:
        if sec_id not in left_sections:
            diffs.append(Diff("added", sec_id, right=right_sections[sec_id]))

    # Compare entries within shared sections
    for sec_id in left_sections:
        if sec_id not in right_sections:
            continue
        left_entries = {f"{e.sigil}:{e.name}": e for e in left_sections[sec_id].entries}
        right_entries = {f"{e.sigil}:{e.name}": e for e in right_sections[sec_id].entries}

        for key in left_entries:
            if key not in right_entries:
                diffs.append(Diff("removed", f"{sec_id}/{key}", left=left_entries[key]))
        for key in right_entries:
            if key not in left_entries:
                diffs.append(Diff("added", f"{sec_id}/{key}", right=right_entries[key]))

        for key in left_entries:
            if key not in right_entries:
                continue
            le = left_entries[key]
            re_ = right_entries[key]
            entry_diffs = _compare_entry(le, re_, f"{sec_id}/{key}")
            diffs.extend(entry_diffs)

    return len(diffs) == 0, diffs


def _compare_entry(left: V2Entry, right: V2Entry, location: str) -> List[Diff]:
    """Compare two entries for AST equivalence."""

    diffs: List[Diff] = []

    if left.entry_type != right.entry_type:
        diffs.append(Diff("modified", location, "entry_type", left.entry_type, right.entry_type))
        return diffs

    if left.entry_type in ("cuerpo", "bloque"):
        if left.value != right.value:
            diffs.append(Diff("modified", location, "value", left.value, right.value))
    elif left.entry_type == "attrs":
        left_attrs = dict(left.value) if isinstance(left.value, dict) else {}
        right_attrs = dict(right.value) if isinstance(right.value, dict) else {}
        for k in left_attrs:
            if k not in right_attrs:
                diffs.append(Diff("modified", location, k, left_attrs[k], None))
            elif left_attrs[k] != right_attrs[k]:
                diffs.append(Diff("modified", location, k, left_attrs[k], right_attrs[k]))
        for k in right_attrs:
            if k not in left_attrs:
                diffs.append(Diff("modified", location, k, None, right_attrs[k]))
    elif left.entry_type == "attrs-pos":
        left_list = list(left.value) if isinstance(left.value, list) else []
        right_list = list(right.value) if isinstance(right.value, list) else []
        if left_list != right_list:
            diffs.append(Diff("modified", location, "value", left_list, right_list))

    return diffs


# ---------------------------------------------------------------------------
# F-18: semantic-equivalent comparison
# ---------------------------------------------------------------------------

def compare_semantic_equivalent(left: CortexV2Document, right: CortexV2Document) -> Tuple[bool, List[Diff]]:
    """F-18: Same operational meaning with tolerable differences.

    Semantic equivalence is AST-equivalent +:
    - Same critical sigils present (FCS, OBJ, CNST)
    - Same P0/P1 entries (blocking constraints)
    - Tolerable differences in non-critical attrs (e.g., status fields)
    """

    ast_eq, ast_diffs = compare_ast_equivalent(left, right)
    if ast_eq:
        return True, []

    # Filter diffs to only critical ones
    critical_sigils = {"FCS", "OBJ", "CNST", "AXM", "LIM"}
    critical_diffs: List[Diff] = []
    for d in ast_diffs:
        # Parse location: $N/SIGIL:name[/field]
        parts = d.location.split("/")
        if len(parts) >= 2:
            sigil_part = parts[1].split(":")[0]
            if sigil_part in critical_sigils:
                critical_diffs.append(d)

    return len(critical_diffs) == 0, critical_diffs


# ---------------------------------------------------------------------------
# F-19: content-equivalent (HCORTEX regenerado)
# ---------------------------------------------------------------------------

def compare_content_equivalent(left_hcortex: str, right_hcortex: str) -> Tuple[bool, List[Diff]]:
    """F-19: HCORTEX regenerado conserva contenido humano equivalente.

    Content-equivalent means same VIEW blocks, same table rows (modulo
    whitespace), same list items, same verbatim blocks.
    """

    diffs: List[Diff] = []

    # Extract VIEW blocks from each
    left_blocks = _extract_view_blocks(left_hcortex)
    right_blocks = _extract_view_blocks(right_hcortex)

    left_names = {b[0] for b in left_blocks}
    right_names = {b[0] for b in right_blocks}

    for name in left_names - right_names:
        diffs.append(Diff("removed", f"VIEW:{name}"))
    for name in right_names - left_names:
        diffs.append(Diff("added", f"VIEW:{name}"))

    for name in left_names & right_names:
        left_content = next((c for n, c in left_blocks if n == name), "")
        right_content = next((c for n, c in right_blocks if n == name), "")
        # Normalize whitespace
        left_norm = _normalize_whitespace(left_content)
        right_norm = _normalize_whitespace(right_content)
        if left_norm != right_norm:
            diffs.append(Diff("modified", f"VIEW:{name}", "content", left_norm[:200], right_norm[:200]))

    return len(diffs) == 0, diffs


def _extract_view_blocks(text: str) -> List[Tuple[str, str]]:
    """Extract (view_name, content) pairs from HCORTEX text."""

    import re
    blocks: List[Tuple[str, str]] = []
    pattern = re.compile(r'<!-- VIEW:(\w+)\s+.*?-->(.*?)<!-- /VIEW:\1 -->', re.DOTALL)
    for m in pattern.finditer(text):
        blocks.append((m.group(1), m.group(2)))
    return blocks


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace for content comparison."""
    import re
    # Collapse multiple spaces to one
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse multiple blank lines to one
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()


# ---------------------------------------------------------------------------
# F-20/F-21/F-22: Diffs by sigil / section / VIEW
# ---------------------------------------------------------------------------

def diff_by_sigil(diffs: List[Diff]) -> Dict[str, List[Diff]]:
    """F-20: Group diffs by sigil."""
    grouped: Dict[str, List[Diff]] = {}
    for d in diffs:
        parts = d.location.split("/")
        if len(parts) >= 2:
            sigil = parts[1].split(":")[0] if ":" in parts[1] else parts[1]
        else:
            sigil = "unknown"
        grouped.setdefault(sigil, []).append(d)
    return grouped


def diff_by_section(diffs: List[Diff]) -> Dict[str, List[Diff]]:
    """F-21: Group diffs by section."""
    grouped: Dict[str, List[Diff]] = {}
    for d in diffs:
        parts = d.location.split("/")
        section = parts[0] if parts else "unknown"
        grouped.setdefault(section, []).append(d)
    return grouped


def diff_by_view(diffs: List[Diff]) -> Dict[str, List[Diff]]:
    """F-22: Group diffs by VIEW."""
    grouped: Dict[str, List[Diff]] = {}
    for d in diffs:
        if d.location.startswith("VIEW:"):
            view_name = d.location.split(":")[1].split("/")[0]
            grouped.setdefault(f"VIEW:{view_name}", []).append(d)
        else:
            grouped.setdefault("non-VIEW", []).append(d)
    return grouped


# ---------------------------------------------------------------------------
# Full comparison
# ---------------------------------------------------------------------------

def compare_documents(
    left: CortexV2Document,
    right: CortexV2Document,
    left_bytes: Optional[bytes] = None,
    right_bytes: Optional[bytes] = None,
    left_hcortex: Optional[str] = None,
    right_hcortex: Optional[str] = None,
) -> EquivalenceResult:
    """Full comparison between two documents across all equivalence levels."""

    result = EquivalenceResult()

    # F-16: byte-identical
    if left_bytes is not None and right_bytes is not None:
        result.byte_identical = compare_byte_identical(left_bytes, right_bytes)

    # F-17: AST-equivalent
    result.ast_equivalent, ast_diffs = compare_ast_equivalent(left, right)
    result.diffs.extend(ast_diffs)

    # F-18: semantic-equivalent
    result.semantic_equivalent, sem_diffs = compare_semantic_equivalent(left, right)
    # Don't add sem_diffs to result.diffs (they're a subset of ast_diffs)

    # F-19: content-equivalent
    if left_hcortex is not None and right_hcortex is not None:
        result.content_equivalent, content_diffs = compare_content_equivalent(left_hcortex, right_hcortex)
        result.diffs.extend(content_diffs)

    return result
