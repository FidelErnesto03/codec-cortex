# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""SelectorEngine hardening — M5 / T-10.

Verifies that select(), select_one(), and parse_selector() handle:
  - unambiguous (exact) matches
  - ambiguous (wildcard) matches
  - not-found cases
  - edge cases (empty document, *, section wildcards)
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
from cortex.core.errors import AmbiguousSelectorError, NotFoundError
from cortex.crud.selectors import select, select_one, parse_selector


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_doc() -> CortexDocument:
    """A completely empty document with just $0 glossary."""
    return CortexDocument(
        glossary=Glossary(),
        sections=[Section(id="$0", title="")],
    )


@pytest.fixture
def single_doc() -> CortexDocument:
    """Document with one entry per section."""
    g = Glossary()
    g.add_sigil(SigilDef(sigil="FCS", name="focus", type="attrs", risk="H", layer="Working"))
    g.add_sigil(SigilDef(sigil="OBJ", name="objective", type="attrs", risk="H", layer="Working"))
    g.add_sigil(SigilDef(sigil="WRK", name="work", type="attrs", risk="B", layer="Working"))
    return CortexDocument(
        glossary=g,
        sections=[
            Section(id="$0", title=""),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="FCS", name="primary", type="attrs",
                       value={"what": "main"}),
            ]),
            Section(id="$2", entries=[
                Entry(section="$2", sigil="OBJ", name="goal", type="attrs",
                       value={"goal": "finish"}),
            ]),
        ],
    )


@pytest.fixture
def multi_doc() -> CortexDocument:
    """Document with multiple entries sharing the same sigil across sections."""
    g = Glossary()
    g.add_sigil(SigilDef(sigil="FCS", name="focus", type="attrs", risk="H", layer="Working"))
    g.add_sigil(SigilDef(sigil="TAG", name="tag", type="attrs", risk="B", layer="Semantic"))
    return CortexDocument(
        glossary=g,
        sections=[
            Section(id="$0", title=""),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="FCS", name="primary", type="attrs",
                       value={"what": "main"}),
                Entry(section="$1", sigil="TAG", name="area", type="attrs",
                       value={"name": "core"}),
            ]),
            Section(id="$2", entries=[
                Entry(section="$2", sigil="FCS", name="secondary", type="attrs",
                       value={"what": "side"}),
                Entry(section="$2", sigil="TAG", name="label", type="attrs",
                       value={"name": "extra"}),
            ]),
            Section(id="$3", entries=[
                Entry(section="$3", sigil="TAG", name="area", type="attrs",
                       value={"name": "another-area"}),
            ]),
        ],
    )


# ---------------------------------------------------------------------------
# parse_selector
# ---------------------------------------------------------------------------

def test_parse_selector_exact():
    sel = parse_selector("$2/FCS:primary")
    assert sel.section == "$2"
    assert sel.sigil == "FCS"
    assert sel.name == "primary"


def test_parse_selector_sigil_wildcard():
    sel = parse_selector("FCS:*")
    assert sel.section is None
    assert sel.sigil == "FCS"
    assert sel.name == "*"


def test_parse_selector_section_wildcard():
    sel = parse_selector("$2/*")
    assert sel.section == "$2"
    assert sel.sigil == "*"
    assert sel.name == "*"


def test_parse_selector_global_wildcard():
    sel = parse_selector("*")
    assert sel.section is None  # no section prefix → any section
    assert sel.sigil == "*"
    assert sel.name == "*"


def test_parse_selector_section_only():
    sel = parse_selector("$1/")
    assert sel.section == "$1"
    assert sel.sigil == "*"
    assert sel.name == "*"


def test_parse_selector_colon_only():
    sel = parse_selector("FCS:")
    assert sel.section is None
    assert sel.sigil == "FCS"
    assert sel.name == "*"


# ---------------------------------------------------------------------------
# select — unambiguous
# ---------------------------------------------------------------------------

def test_select_exact_match(single_doc):
    entries = select(single_doc, "$1/FCS:primary")
    assert len(entries) == 1
    assert entries[0].sigil == "FCS"
    assert entries[0].name == "primary"


def select_select_by_sigil(single_doc):
    entries = select(single_doc, "FCS:*")
    assert len(entries) == 1


def test_select_by_section(multi_doc):
    entries = select(multi_doc, "$1/*")
    assert len(entries) == 2  # FCS:primary + TAG:area
    sigils = {e.sigil for e in entries}
    assert sigils == {"FCS", "TAG"}


def test_select_by_sigil_across_sections(multi_doc):
    entries = select(multi_doc, "TAG:*")
    assert len(entries) == 3  # TAG:area ($1), TAG:label ($2), TAG:area ($3)


def test_select_global_wildcard_returns_all(multi_doc):
    entries = select(multi_doc, "*")
    # All entries across all sections
    assert len(entries) == 5


# ---------------------------------------------------------------------------
# select — not-found
# ---------------------------------------------------------------------------

def test_select_not_found_returns_empty(empty_doc):
    assert select(empty_doc, "FCS:*") == []


def test_select_not_found_wrong_sigil(multi_doc):
    assert select(multi_doc, "OBJ:*") == []


def test_select_not_found_wrong_section(multi_doc):
    assert select(multi_doc, "$99/*") == []


def test_select_not_found_wrong_name(multi_doc):
    assert select(multi_doc, "FCS:nonexistent") == []


# ---------------------------------------------------------------------------
# select_one — unambiguous
# ---------------------------------------------------------------------------

def test_select_one_exact_match(single_doc):
    e = select_one(single_doc, "$1/FCS:primary")
    assert e.sigil == "FCS"
    assert e.name == "primary"


def test_select_one_sigil_name_only(single_doc):
    e = select_one(single_doc, "FCS:primary")
    assert e.sigil == "FCS"


# ---------------------------------------------------------------------------
# select_one — not-found
# ---------------------------------------------------------------------------

def test_select_one_raises_not_found(empty_doc):
    with pytest.raises(NotFoundError):
        select_one(empty_doc, "FCS:primary")


def test_select_one_raises_not_found_wrong_sigil(multi_doc):
    with pytest.raises(NotFoundError):
        select_one(multi_doc, "OBJ:primary")


def test_select_one_raises_not_found_wrong_name(single_doc):
    with pytest.raises(NotFoundError):
        select_one(single_doc, "FCS:nonexistent")


# ---------------------------------------------------------------------------
# select_one — ambiguous
# ---------------------------------------------------------------------------

def test_select_one_raises_ambiguous_sigil_wildcard(multi_doc):
    """FCS:* matches 2 entries across sections — ambiguous."""
    with pytest.raises(AmbiguousSelectorError):
        select_one(multi_doc, "FCS:*")


def test_select_one_raises_ambiguous_repeated_name(multi_doc):
    """TAG:area matches 2 entries ($1 and $3) — ambiguous."""
    with pytest.raises(AmbiguousSelectorError):
        select_one(multi_doc, "TAG:area")


def test_select_one_raises_ambiguous_global_wildcard(multi_doc):
    """Global wildcard matches all entries — ambiguous."""
    with pytest.raises(AmbiguousSelectorError):
        select_one(multi_doc, "*")


def test_select_one_raises_ambiguous_section_wildcard(multi_doc):
    """$1/* matches 2 entries — ambiguous."""
    with pytest.raises(AmbiguousSelectorError):
        select_one(multi_doc, "$1/*")


def test_select_one_raises_ambiguous_same_sigil_different_section(multi_doc):
    """Without section, FCS matches two entries."""
    with pytest.raises(AmbiguousSelectorError):
        select_one(multi_doc, "FCS:*")


# ---------------------------------------------------------------------------
# select_one — unambiguous with section narrowing
# ---------------------------------------------------------------------------

def test_select_one_unambiguous_with_section(multi_doc):
    """FCS:primary matched exactly when section is specified."""
    e = select_one(multi_doc, "$1/FCS:primary")
    assert e.sigil == "FCS"
    assert e.name == "primary"


def test_select_one_unambiguous_tag_area_in_s3(multi_doc):
    """TAG:area in $3 is unambiguous because only $3 has it."""
    e = select_one(multi_doc, "$3/TAG:area")
    assert e.sigil == "TAG"
    assert e.name == "area"


def test_select_one_unambiguous_single_result(multi_doc):
    """When only one entry matches overall, it's unambiguous."""
    e = select_one(multi_doc, "FCS:secondary")
    assert e.sigil == "FCS"
    assert e.name == "secondary"
