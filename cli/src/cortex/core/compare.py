# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Structural comparison of two :class:`CortexDocument` ASTs.

Used by ``cortex verify --roundtrip hcortex-edit`` to verify that
``.cortex → HCORTEX-EDIT → .cortex`` preserves structural identity.

Comparison rules (Section 10.2 of the spec):

- Compare: section id, section order, sigil, entry name, expansion type,
  parsed value, raw bloque exact, glossary definitions.
- Ignore: non-structural comments, formatting whitespace, line numbers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .ast import CortexDocument, Entry, Glossary


@dataclass
class Diff:
    kind: str  # section_added | section_removed | section_reordered
              # | entry_added | entry_removed | entry_value_changed
              # | entry_type_changed | bloque_changed | glossary_changed
    path: str
    left: Any = None
    right: Any = None
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "left": self.left,
            "right": self.right,
            "message": self.message,
        }


@dataclass
class DiffResult:
    equal: bool
    diffs: List[Diff] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equal": self.equal,
            "diffs": [d.to_dict() for d in self.diffs],
        }


def compare_glossary(left: Glossary, right: Glossary) -> List[Diff]:
    diffs: List[Diff] = []
    # sigils
    left_sigils = set(left.sigils)
    right_sigils = set(right.sigils)
    for s in sorted(left_sigils - right_sigils):
        diffs.append(Diff("glossary_changed", f"sigils.{s}",
                          left=left.sigils[s].to_dict(), right=None,
                          message=f"sigil {s} removed from glossary"))
    for s in sorted(right_sigils - left_sigils):
        diffs.append(Diff("glossary_changed", f"sigils.{s}",
                          left=None, right=right.sigils[s].to_dict(),
                          message=f"sigil {s} added to glossary"))
    for s in sorted(left_sigils & right_sigils):
        ld = left.sigils[s].to_dict()
        rd = right.sigils[s].to_dict()
        if ld != rd:
            diffs.append(Diff("glossary_changed", f"sigils.{s}",
                              left=ld, right=rd,
                              message=f"sigil {s} definition changed"))
    # types
    lt = set(left.types)
    rt = set(right.types)
    for t in sorted(lt - rt):
        diffs.append(Diff("glossary_changed", f"types.{t}",
                          left=left.types[t].to_dict(), right=None,
                          message=f"type {t} removed"))
    for t in sorted(rt - lt):
        diffs.append(Diff("glossary_changed", f"types.{t}",
                          left=None, right=right.types[t].to_dict(),
                          message=f"type {t} added"))
    # micro
    lm = set(left.micro)
    rm = set(right.micro)
    for tok in sorted(lm - rm):
        diffs.append(Diff("glossary_changed", f"micro.{tok}",
                          left=left.micro[tok].to_dict(), right=None,
                          message=f"micro-token {tok} removed"))
    for tok in sorted(rm - lm):
        diffs.append(Diff("glossary_changed", f"micro.{tok}",
                          left=None, right=right.micro[tok].to_dict(),
                          message=f"micro-token {tok} added"))
    for tok in sorted(lm & rm):
        if left.micro[tok].value != right.micro[tok].value:
            diffs.append(Diff("glossary_changed", f"micro.{tok}",
                              left=left.micro[tok].value,
                              right=right.micro[tok].value,
                              message=f"micro-token {tok} value changed"))
    return diffs


def compare_entry(left: Entry, right: Entry) -> List[Diff]:
    diffs: List[Diff] = []
    path = f"{left.section}/{left.sigil}:{left.name}"
    if left.sigil != right.sigil:
        diffs.append(Diff("entry_type_changed", path,
                          left=left.sigil, right=right.sigil,
                          message="sigil changed"))
    if left.name != right.name:
        diffs.append(Diff("entry_type_changed", path,
                          left=left.name, right=right.name,
                          message="name changed"))
    if left.type != right.type:
        diffs.append(Diff("entry_type_changed", path,
                          left=left.type, right=right.type,
                          message="expansion type changed"))
    # Value comparison
    if left.type == "bloque":
        # Compare verbatim raw
        if left.value != right.value:
            diffs.append(Diff("bloque_changed", path,
                              left=left.value, right=right.value,
                              message="bloque content changed (verbatim mismatch)"))
    else:
        if left.value != right.value:
            diffs.append(Diff("entry_value_changed", path,
                              left=left.value, right=right.value,
                              message="parsed value changed"))
    return diffs


def compare_ast(left: CortexDocument, right: CortexDocument) -> DiffResult:
    """Compare two ASTs structurally; return :class:`DiffResult`."""

    diffs: List[Diff] = []
    diffs.extend(compare_glossary(left.glossary, right.glossary))

    # Sections
    left_secs = {s.id: s for s in left.sections if s.id != "$0"}
    right_secs = {s.id: s for s in right.sections if s.id != "$0"}
    left_order = [s.id for s in left.sections if s.id != "$0"]
    right_order = [s.id for s in right.sections if s.id != "$0"]
    # added/removed
    for sid in left_order:
        if sid not in right_secs:
            diffs.append(Diff("section_removed", sid,
                              message=f"section {sid} removed"))
    for sid in right_order:
        if sid not in left_secs:
            diffs.append(Diff("section_added", sid,
                              message=f"section {sid} added"))
    # order (only among common sections)
    common_left = [s for s in left_order if s in right_secs]
    common_right = [s for s in right_order if s in left_secs]
    if common_left != common_right:
        diffs.append(Diff("section_reordered", "sections",
                          left=common_left, right=common_right,
                          message="section order changed"))

    # Entries per common section
    for sid in common_left:
        ls = left_secs[sid]
        rs = right_secs[sid]
        le = {f"{e.sigil}:{e.name}": e for e in ls.entries}
        re_ = {f"{e.sigil}:{e.name}": e for e in rs.entries}
        for key in le:
            if key not in re_:
                diffs.append(Diff("entry_removed", f"{sid}/{key}",
                                  message=f"entry {key} removed from {sid}"))
        for key in re_:
            if key not in le:
                diffs.append(Diff("entry_added", f"{sid}/{key}",
                                  message=f"entry {key} added to {sid}"))
        for key in le:
            if key in re_:
                diffs.extend(compare_entry(le[key], re_[key]))

    return DiffResult(equal=(len(diffs) == 0), diffs=diffs)
