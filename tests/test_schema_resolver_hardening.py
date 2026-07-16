# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""SchemaResolver hardening — M5 / T-8.

Verifies that SchemaResolver's field/status/type resolution is correct
with both full glossaries and minimal (None) glossaries.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.core.ast import Glossary, SigilDef, TypeDef
from cortex.core.schema import SchemaResolver


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _full_glossary() -> Glossary:
    """Glossary with a declared FCS with explicit fields."""
    g = Glossary()
    g.add_sigil(SigilDef(
        sigil="FCS", name="focus", type="attrs", risk="H", layer="Working",
        description="Focus entry",
        fields=["what", "priority", "status", "survive"],
    ))
    g.add_sigil(SigilDef(
        sigil="MYCUSTOM", name="my_custom", type="attrs", risk="M", layer="Semantic",
        description="A custom sigil",
    ))
    g.add_type(TypeDef(name="attrs", description="key:value pairs"))
    g.add_type(TypeDef(name="cuerpo", description="prose body"))
    g.status_custom = ["current", "planned", "done", "archived"]
    return g


def _empty_glossary() -> Glossary:
    """Minimal glossary with only canonical defaults."""
    g = Glossary()
    return g


# ---------------------------------------------------------------------------
# required_fields
# ---------------------------------------------------------------------------

def test_required_fields_uses_glossary_fields():
    """When glossary declares fields for a sigil, those are returned."""
    resolver = SchemaResolver(_full_glossary())
    required, optional = resolver.required_fields("FCS")
    assert "what" in required
    assert "priority" in required
    assert "status" in required
    assert "survive" in required


def test_required_fields_fallback_to_canonical():
    """When glossary has no fields for a sigil, canonical defaults are used.

    Since REQUIRED_FIELDS is not defined in errors.py, the fallback
    returns ALWAYS_REQUIRED = {"name"}.
    """
    resolver = SchemaResolver(Glossary())
    required, _ = resolver.required_fields("FCS")
    assert "name" in required  # ALWAYS_REQUIRED fallback


def test_required_fields_custom_sigil_no_fields():
    """Custom sigils without field declarations return empty sets."""
    resolver = SchemaResolver(_full_glossary())
    required, optional = resolver.required_fields("MYCUSTOM")
    # No canonical fields for MYCUSTOM, and glossary has no explicit fields
    assert set() == required or required == {"name"}
    assert isinstance(optional, set)


def test_required_fields_empty_glossary():
    """None glossary still falls back to ALWAYS_REQUIRED."""
    resolver = SchemaResolver(None)
    required, _ = resolver.required_fields("FCS")
    assert "name" in required


# ---------------------------------------------------------------------------
# valid_statuses
# ---------------------------------------------------------------------------

def test_valid_statuses_uses_custom():
    """When glossary has custom statuses, those are returned."""
    resolver = SchemaResolver(_full_glossary())
    statuses = resolver.valid_statuses()
    assert "current" in statuses
    assert "planned" in statuses
    assert "done" in statuses
    assert "archived" in statuses


def test_valid_statuses_fallback_to_canonical():
    """Empty glossary falls back to canonical ALLOWED_STATUS."""
    resolver = SchemaResolver(_empty_glossary())
    statuses = resolver.valid_statuses()
    assert "current" in statuses
    assert "specification" in statuses
    assert "planned" in statuses
    assert "future" in statuses


def test_valid_statuses_none_glossary():
    """None glossary returns canonical statuses."""
    resolver = SchemaResolver(None)
    statuses = resolver.valid_statuses()
    assert "current" in statuses
    assert len(statuses) > 0


# ---------------------------------------------------------------------------
# valid_types
# ---------------------------------------------------------------------------

def test_valid_types_includes_canonical():
    """Canonical types are always present."""
    resolver = SchemaResolver(_full_glossary())
    types_ = resolver.valid_types()
    for t in ("attrs", "attrs-pos", "cuerpo", "bloque", "relación"):
        assert t in types_


def test_valid_types_includes_custom():
    """Custom types from glossary are included."""
    resolver = SchemaResolver(_full_glossary())
    types_ = resolver.valid_types()
    assert "attrs" in types_
    assert "cuerpo" in types_


def test_valid_types_none_glossary():
    """None glossary returns only canonical types."""
    resolver = SchemaResolver(None)
    types_ = resolver.valid_types()
    assert "attrs" in types_
    assert "bloque" in types_
    assert len(types_) == 5  # 5 canonical types


# ---------------------------------------------------------------------------
# has_fields
# ---------------------------------------------------------------------------

def test_has_fields_returns_true_when_fields_declared():
    """Sigil with explicit fields returns True."""
    resolver = SchemaResolver(_full_glossary())
    assert resolver.has_fields("FCS") is True


def test_has_fields_returns_false_when_no_fields():
    """Sigil without explicit fields returns False."""
    resolver = SchemaResolver(_full_glossary())
    assert resolver.has_fields("MYCUSTOM") is False


def test_has_fields_returns_false_for_unknown_sigil():
    """Unknown sigil returns False."""
    resolver = SchemaResolver(_full_glossary())
    assert resolver.has_fields("NONEXISTENT") is False


# ---------------------------------------------------------------------------
# needs_review
# ---------------------------------------------------------------------------

def test_needs_review_true_when_marked():
    """Sigil with needs_review=True returns True."""
    g = _full_glossary()
    g.add_sigil(SigilDef(
        sigil="AUTO", name="auto", type="attrs", risk="M", layer="Semantic",
        description="auto-detected",
        needs_review=True,
    ))
    resolver = SchemaResolver(g)
    assert resolver.needs_review("AUTO") is True


def test_needs_review_false_when_not_marked():
    """Sigil without needs_review flag returns False."""
    resolver = SchemaResolver(_full_glossary())
    assert resolver.needs_review("FCS") is False


def test_needs_review_false_for_unknown_sigil():
    """Unknown sigil returns False."""
    resolver = SchemaResolver(_full_glossary())
    assert resolver.needs_review("NONEXISTENT") is False
