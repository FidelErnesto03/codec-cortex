# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Tests for the glossary review command."""

from cortex.cli.commands.glossary import review_glossary
from cortex.core.parser import ensure_in_glossary, parse_cortex
from cortex.core.schema import SchemaResolver
from cortex.core.validator import validate
from cortex.core.writer import write_cortex


def test_review_glossary_lists_declared_and_pending_elements():
    doc = parse_cortex(
        """$0

# IDN | identity | attrs | B | Semantic | Identity
# status: active, archived

$1: BODY

ZZZ:item{name:"undeclared"}
"""
    )

    items = review_glossary(doc)
    assert {item["name"] for item in items} >= {"IDN", "ZZZ", "active", "archived"}
    pending = next(item for item in items if item["name"] == "ZZZ")
    assert pending == {
        "kind": "sigil",
        "name": "ZZZ",
        "location": "$0",
        "status": "needs_review",
        "action": "define type, risk, layer, and description",
    }


def test_review_glossary_lists_custom_types():
    doc = parse_cortex("$0\n\n# IDN | identity | attrs | B | Semantic | Identity\n")
    doc.glossary.types_custom = ["record"]
    assert {
        "kind": "type",
        "name": "record",
        "location": "$0",
        "status": "declared",
        "action": "none",
    } in review_glossary(doc)


def test_definition_immediately_resolves_an_unknown_sigil():
    doc = parse_cortex("$0\n\n# IDN | identity | attrs | B | Semantic | Identity\n")
    ensure_in_glossary(doc, sigil="DEC", definition={"name": "decision", "type": "attrs"})
    assert doc.glossary.sigils["DEC"].needs_review is False


def test_status_and_type_declarations_are_operational_and_serialized():
    doc = parse_cortex(
        """$0

# IDN | identity | attrs | B | Semantic | Identity
# status: active, archived
# record = custom record type

$1: BODY

IDN:identity{name:"x", status:"active"}
"""
    )
    assert not [finding for finding in validate(doc) if finding["code"] == "W002_INVALID_STATUS"]
    assert "record" in SchemaResolver(doc.glossary).valid_types()
    assert "# status: active, archived" in write_cortex(doc)


def test_declared_fields_override_canonical_required_fields():
    doc = parse_cortex(
        """$0

GSIG:STP{name:"step", type:"attrs", fields:"action"}

$1: BODY

STP:one{action:"run"}
"""
    )
    findings = validate(doc)
    assert not [finding for finding in findings if finding["code"] == "E032_CRITICAL_SIGIL_INCOMPLETE"]


def test_absent_declarations_use_the_canonical_schema():
    doc = parse_cortex("$0\n\n# IDN | identity | attrs | B | Semantic | Identity\n")
    assert SchemaResolver(doc.glossary).valid_statuses()
    assert "attrs" in SchemaResolver(doc.glossary).valid_types()


def test_auto_population_does_not_duplicate_existing_sigil():
    doc = parse_cortex("$0\n\n# IDN | identity | attrs | B | Semantic | Identity\n")
    ensure_in_glossary(doc, sigil="NEW")
    ensure_in_glossary(doc, sigil="NEW")
    assert list(doc.glossary.sigils).count("NEW") == 1
