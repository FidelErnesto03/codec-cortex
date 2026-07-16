# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""M5 / T-7 — verify --strict emits E003 for undeclared sigils.

Tests that strict validation:
  - Emits E003 for entries whose sigil is not in $0
  - Emits E003 for entries whose sigil was auto-added (needs_review=True)
  - Does NOT emit E003 for properly declared sigils
  - The standalone validate_sigils_strict() function works correctly
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.core.ast import (
    CortexDocument, Section, Entry, Glossary, SigilDef, TypeDef,
)
from cortex.core.errors import E003_UNKNOWN_SIGIL
from cortex.core.parser import parse_cortex
from cortex.core.validator import validate, validate_sigils_strict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _declared_doc() -> CortexDocument:
    """Document where the sigil IS declared in $0, with all required fields."""
    g = Glossary()
    g.add_sigil(SigilDef(sigil="FCS", name="focus", type="attrs", risk="H", layer="Working"))
    g.add_sigil(SigilDef(sigil="OBJ", name="objective", type="attrs", risk="H", layer="Working"))
    # Seed canonical types so resolver_types works
    for t in ("attrs", "attrs-pos", "cuerpo", "bloque", "relación"):
        g.add_type(TypeDef(name=t, description="canonical type"))
    return CortexDocument(
        glossary=g,
        sections=[
            Section(id="$0", title=""),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="FCS", name="primary", type="attrs",
                       value={"what": "main", "priority": "high", "status": "current",
                              "survive": "min", "name": "primary"}),
                Entry(section="$1", sigil="OBJ", name="goal", type="attrs",
                       value={"goal": "finish", "status": "current", "success": "done",
                              "survive": "work", "name": "goal"}),
            ]),
        ],
    )


def _undeclared_doc() -> CortexDocument:
    """Document where the entry's sigil is NOT in the glossary.

    This simulates what happens when the parser encounters a sigil
    but `ensure_in_glossary` was NOT called (e.g. a document was
    constructed manually, or a future parser change skips auto-add).
    """
    g = Glossary()
    g.add_sigil(SigilDef(sigil="FCS", name="focus", type="attrs", risk="H", layer="Working"))
    return CortexDocument(
        glossary=g,
        sections=[
            Section(id="$0", title=""),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="FCS", name="primary", type="attrs",
                       value={"what": "main"}),
                Entry(section="$1", sigil="MYSTERY", name="unknown", type="attrs",
                       value={"key": "val"}),
            ]),
        ],
    )


def _auto_added_doc() -> CortexDocument:
    """Document where the sigil was auto-added by the parser with needs_review.

    This simulates parse_cortex processing a source with an unknown sigil.
    The parser calls ensure_in_glossary which sets needs_review=True.
    """
    source = """$0
# -- $0: GLOSSARY --
# FCS | focus | attrs | H | Working | Focus

$1
FCS:primary{what:"main"}
MYSTERY:unknown{key:"val"}
"""
    return parse_cortex(source)


# ---------------------------------------------------------------------------
# validate(..., strict=True) — E003 for auto-added sigils
# ---------------------------------------------------------------------------

def test_strict_emits_e003_for_auto_added_sigil():
    """When a sigil was auto-added by the parser, strict mode emits E003."""
    doc = _auto_added_doc()
    # The parser auto-added MYSTERY with needs_review=True
    assert "MYSTERY" in doc.glossary.sigils
    assert doc.glossary.sigils["MYSTERY"].needs_review is True

    findings = validate(doc, strict=True)
    e003 = [f for f in findings if f.get("code") == E003_UNKNOWN_SIGIL]
    assert len(e003) == 1, f"Expected 1 E003, got {len(e003)}: {e003}"
    assert e003[0]["sigil"] == "MYSTERY"
    assert e003[0]["severity"] == "error"


def test_strict_does_not_emit_e003_for_declared_sigil():
    """Properly declared sigils should NOT get E003 in strict mode."""
    doc = _declared_doc()
    findings = validate(doc, strict=True)
    e003 = [f for f in findings if f.get("code") == E003_UNKNOWN_SIGIL]
    assert len(e003) == 0, f"Expected 0 E003, got {len(e003)}: {e003}"


# ---------------------------------------------------------------------------
# validate(..., strict=False) — normal mode, no E003
# ---------------------------------------------------------------------------

def test_non_strict_does_not_emit_e003():
    """Normal mode (strict=False) should NOT emit E003."""
    doc = _auto_added_doc()
    findings = validate(doc, strict=False)
    e003 = [f for f in findings if f.get("code") == E003_UNKNOWN_SIGIL]
    assert len(e003) == 0, f"Expected 0 E003 in non-strict mode, got {len(e003)}"


def test_non_strict_emits_i001_for_auto_added():
    """Normal mode should emit I001 (info) for auto-added sigils."""
    doc = _auto_added_doc()
    findings = validate(doc, strict=False)
    i001 = [f for f in findings if f.get("code") == "I001_UNDECLARED_SIGIL"]
    assert len(i001) >= 1


def test_non_strict_emits_i001_for_absent_sigil():
    """Normal mode still calls ensure_in_glossary for fully absent sigils."""
    doc = _undeclared_doc()
    findings = validate(doc, strict=False)
    i001 = [f for f in findings if f.get("code") == "I001_UNDECLARED_SIGIL"]
    assert len(i001) >= 1


# ---------------------------------------------------------------------------
# validate_sigils_strict() — standalone function
# ---------------------------------------------------------------------------

def test_validate_sigils_strict_detects_auto_added():
    """validate_sigils_strict reports E003 for auto-added sigils."""
    doc = _auto_added_doc()
    findings = validate_sigils_strict(doc)
    assert len(findings) == 1
    assert findings[0]["code"] == E003_UNKNOWN_SIGIL
    assert findings[0]["sigil"] == "MYSTERY"


def test_validate_sigils_strict_detects_absent():
    """validate_sigils_strict reports E003 for completely absent sigils."""
    doc = _undeclared_doc()
    findings = validate_sigils_strict(doc)
    assert len(findings) == 1
    assert findings[0]["code"] == E003_UNKNOWN_SIGIL
    assert findings[0]["sigil"] == "MYSTERY"


def test_validate_sigils_strict_clean_with_declared():
    """validate_sigils_strict returns empty for fully declared doc."""
    doc = _declared_doc()
    findings = validate_sigils_strict(doc)
    assert len(findings) == 0


# ---------------------------------------------------------------------------
# validate_sigils_strict does NOT mutate the glossary
# ---------------------------------------------------------------------------

def test_validate_sigils_strict_no_mutation():
    """validate_sigils_strict must not call ensure_in_glossary."""
    doc = _undeclared_doc()
    sigil_count_before = len(doc.glossary.sigils)
    _ = validate_sigils_strict(doc)
    sigil_count_after = len(doc.glossary.sigils)
    assert sigil_count_before == sigil_count_after, (
        "validate_sigils_strict mutated the glossary"
    )


# ---------------------------------------------------------------------------
# is_valid with strict=True fails on E003
# ---------------------------------------------------------------------------

def test_is_valid_strict_fails_on_auto_added():
    """is_valid(..., strict=True) must return False when E003 is present."""
    doc = _auto_added_doc()
    from cortex.core.validator import is_valid
    assert is_valid(doc, strict=True) is False


def test_is_valid_strict_passes_on_clean():
    """is_valid(..., strict=True) returns True for a clean doc."""
    doc = _declared_doc()
    from cortex.core.validator import is_valid
    assert is_valid(doc, strict=True) is True
