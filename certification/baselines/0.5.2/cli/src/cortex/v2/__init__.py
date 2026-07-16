# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

r"""CODEC-CORTEX v2 — High-fidelity CORTEX <-> HCORTEX translation.

v2.2.1: HCORTEX is reversible by definition when VIEW coverage is valid.
HCORTEX-R eliminated as separate concept.
"""

from .parser import parse_cortex_v2, CortexV2Document
from .writer import write_cortex_v2
from .ir import SkillIR, IREntry, IRBlock, IRWarning, cortex_to_ir, ir_to_cortex
from .hcortex_renderer import render_hcortex_v2
from .view import (
    ViewDirective, ViewKind, ReverseStrategy, ViewDiagnostic,
    parse_view_entry, parse_view_entries_from_doc,
    resolve_target, calculate_view_coverage,
    VALID_KINDS, VALID_REVERSES, KIND_REVERSE_COMPAT,
)
from .view_renderer import render_hcortex, render_hcortex_r, has_view_errors

__all__ = [
    "parse_cortex_v2", "write_cortex_v2", "CortexV2Document",
    "SkillIR", "IREntry", "IRBlock", "IRWarning",
    "cortex_to_ir", "ir_to_cortex",
    "render_hcortex_v2",
    # VIEW
    "ViewDirective", "ViewKind", "ReverseStrategy", "ViewDiagnostic",
    "parse_view_entry", "parse_view_entries_from_doc",
    "resolve_target", "calculate_view_coverage",
    "VALID_KINDS", "VALID_REVERSES", "KIND_REVERSE_COMPAT",
    "render_hcortex", "render_hcortex_r", "has_view_errors",
]
