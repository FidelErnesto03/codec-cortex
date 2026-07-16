# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Regression tests for local $0 glossary sigils."""

from cortex.core.errors import E006_INVALID_ATTRS
from cortex.core.parser import parse_cortex
from cortex.core.validator import validate


def test_local_sigil_attrs_accepts_numbered_keys():
    text = """\
$0

# STP | step | attrs | M | Working | Procedure step

$1: PROCEDURE

STP:discover{
  1_explain:"Explain the workflow.",
  2:"Continue with the next action.",
}
"""
    doc = parse_cortex(text)
    findings = validate(doc)
    codes = [finding["code"] for finding in findings]

    assert E006_INVALID_ATTRS not in codes
    entry = doc.find_entries("STP", "discover")[0]
    assert entry.value["1_explain"] == "Explain the workflow."
    assert entry.value["2"] == "Continue with the next action."


def test_decimal_section_headers_are_parsed():
    text = """\
$0

# HDL | handler | attrs | M | Semantic | Handler definition

$2.1: WORKSPACE EXAMPLES

HDL:workspace_init{signature:"init(path?)", purpose:"Initialize workspace"}
"""
    doc = parse_cortex(text)

    assert "$2.1" in doc.section_ids
    assert not [d for d in doc.diagnostics if d["code"] == "E017_UNPARSED_LINE"]


def test_local_attrs_pos_without_contract_accepts_attrs_body():
    text = """\
$0

# HDL | handler | attrs-pos | M | Semantic | Handler definition

$1: HANDLERS

HDL:workspace.init{signature:"init(path?)", purpose:"Initialize workspace"}
"""
    doc = parse_cortex(text)
    findings = validate(doc)
    codes = [finding["code"] for finding in findings]

    assert E006_INVALID_ATTRS not in codes
    entry = doc.find_entries("HDL", "workspace.init")[0]
    assert entry.value["signature"] == "init(path?)"


def test_nested_attrs_maps_are_parsed():
    text = """\
$0

# STP | step | attrs | M | Working | Procedure step

$1: BODY

STP:adopt{
  1_init:"Initialize",
  created:{
    manifest:"Workspace manifest",
    skills:"Copied skills",
  },
  3_connectivity:"Verify handlers",
}
"""
    doc = parse_cortex(text)
    findings = validate(doc)
    codes = [finding["code"] for finding in findings]

    assert E006_INVALID_ATTRS not in codes
    entry = doc.find_entries("STP", "adopt")[0]
    assert entry.value["created"]["manifest"] == "Workspace manifest"
    assert entry.value["3_connectivity"] == "Verify handlers"


def test_undeclared_local_sigil_gets_auto_added():
    text = """\
$0

# IDN | identity | attrs | B | Semantic | Identity

$1: BODY

ZZZ:item{name:"not declared"}
"""
    doc = parse_cortex(text)
    findings = validate(doc)
    codes = [finding["code"] for finding in findings]

    assert "I001_UNDECLARED_SIGIL" in codes
    assert "ZZZ" in doc.glossary.sigils
    assert doc.glossary.sigils["ZZZ"].needs_review is True
