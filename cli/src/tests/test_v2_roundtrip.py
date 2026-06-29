"""v2.0.0 roundtrip tests — CORTEX → AST → CORTEX must be byte-identical."""

import os
import sys
import pytest

# Make the cortex package importable
HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2, CortexV2Document
from cortex.v2.writer import write_cortex_v2


FIXTURES_DIR = os.path.join(HERE, "fixtures")
SKILL_CORTEX_PATH = os.path.join(FIXTURES_DIR, "SKILL_v2.cortex.md")
SKILL_HCORTEX_PATH = os.path.join(FIXTURES_DIR, "SKILL_v2.hcortex.md")


def test_v2_skill_cortex_file_exists():
    """The SKILL.md CORTEX fixture must exist."""
    assert os.path.exists(SKILL_CORTEX_PATH), f"Fixture not found: {SKILL_CORTEX_PATH}"


def test_v2_parse_produces_document():
    """parse_cortex_v2 must produce a CortexV2Document with sections."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    assert isinstance(doc, CortexV2Document)
    assert len(doc.sections) > 0, "Document must have sections"
    # Must have $0
    assert doc.sections[0].id == "$0", f"First section must be $0; got {doc.sections[0].id}"


def test_v2_parse_header():
    """The CODEC-CORTEX header must be parsed correctly."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    assert 'internal_encoding' in doc.header
    assert doc.header['internal_encoding'] == 'CORTEX'
    assert 'source_artifact' in doc.header
    assert 'source_version' in doc.header


def test_v2_parse_sections():
    """All 14 sections ($0-$13) must be present (v2.2.2: $13 holds VIEW directives)."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    section_ids = [s.id for s in doc.sections]
    expected = [f'${i}' for i in range(14)]  # $0-$13
    assert section_ids == expected, f"Sections: {section_ids} != {expected}"


def test_v2_parse_zero_section_has_sigil_decls():
    """$0 must contain sigil declarations."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    sec0 = doc.get_section("$0")
    assert sec0 is not None
    # Must have IDN:identity sigil declaration
    idn_entries = [e for e in sec0.entries if e.sigil == 'IDN' and e.name == 'identity']
    assert len(idn_entries) == 1, "Must have IDN:identity declaration"
    assert idn_entries[0].entry_type == 'sigil_decl'
    assert idn_entries[0].value.get('type') == 'attrs'
    assert idn_entries[0].value.get('risk') == 'B'


def test_v2_parse_zero_section_has_metadata():
    """$0 must contain metadata entries ($0:type_attrs, $0:contract_hdl, etc.)."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    sec0 = doc.get_section("$0")
    meta_entries = [e for e in sec0.entries if e.sigil == '$0']
    assert len(meta_entries) > 0, "Must have $0 metadata entries"
    # Check for type_attrs
    type_attrs = [e for e in meta_entries if e.name == 'type_attrs']
    assert len(type_attrs) == 1, "Must have $0:type_attrs"


def test_v2_parse_hdl_bare_attrs_pos():
    """HDL entries must be parsed as bare attrs-pos (no braces)."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    sec3 = doc.get_section("$3")
    assert sec3 is not None
    hdl_entries = [e for e in sec3.entries if e.sigil == 'HDL']
    assert len(hdl_entries) >= 6, f"Must have at least 6 HDL entries; got {len(hdl_entries)}"
    # Check first HDL entry
    hdl0 = hdl_entries[0]
    assert hdl0.entry_type == 'attrs-pos'
    assert 'operation' in hdl0.value
    assert 'status' in hdl0.value
    assert 'requires' in hdl0.value
    assert 'notes' in hdl0.value


def test_v2_parse_diag_bloque():
    """DIAG entries must be parsed as bloque (multiline verbatim)."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    sec6 = doc.get_section("$6")
    assert sec6 is not None
    diag_entries = [e for e in sec6.entries if e.sigil == 'DIAG']
    assert len(diag_entries) >= 5, f"Must have at least 5 DIAG entries; got {len(diag_entries)}"
    # Check first DIAG has @startuml
    assert '@startuml' in diag_entries[0].value


def test_v2_parse_desc_cuerpo():
    """DESC entries must be parsed as cuerpo (literal text)."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    sec2 = doc.get_section("$2")
    assert sec2 is not None
    desc_entries = [e for e in sec2.entries if e.sigil == 'DESC']
    assert len(desc_entries) >= 2, f"Must have at least 2 DESC entries; got {len(desc_entries)}"
    # Check DESC:purpose
    purpose = [e for e in desc_entries if e.name == 'purpose']
    assert len(purpose) == 1
    assert 'CODEC-CORTEX' in purpose[0].value


def test_v2_parse_micro_tokens_bare():
    """Micro-tokens must be parsed as bare string values (not None/bool)."""
    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    doc = parse_cortex_v2(text)
    # Check KNW:problem has status:cur
    sec2 = doc.get_section("$2")
    knw_problem = [e for e in sec2.entries if e.sigil == 'KNW' and e.name == 'problem']
    assert len(knw_problem) == 1
    assert knw_problem[0].value.get('status') == 'cur'


def test_v2_roundtrip_byte_identical():
    """CORTEX → parse → write must produce byte-identical output.

    v2.0.1: compares BYTES, not text, to catch CRLF and encoding differences.
    """
    with open(SKILL_CORTEX_PATH, 'rb') as f:
        original_bytes = f.read()

    text = original_bytes.decode('utf-8')
    doc = parse_cortex_v2(text)
    reproduced_text = write_cortex_v2(doc)
    reproduced_bytes = reproduced_text.encode('utf-8')

    if original_bytes != reproduced_bytes:
        # Find first difference for debugging
        orig_lines = text.split('\n')
        repro_lines = reproduced_text.split('\n')
        max_len = max(len(orig_lines), len(repro_lines))
        for i in range(max_len):
            o = orig_lines[i] if i < len(orig_lines) else '<EOF>'
            r = repro_lines[i] if i < len(repro_lines) else '<EOF>'
            if o != r:
                pytest.fail(
                    f"First difference at line {i + 1}:\n"
                    f"  original: {o[:120]!r}\n"
                    f"  reproduced: {r[:120]!r}\n"
                    f"  (orig has {len(orig_lines)} lines, repro has {len(repro_lines)} lines)\n"
                    f"  (orig has {len(original_bytes)} bytes, repro has {len(reproduced_bytes)} bytes)"
                )
        pytest.fail(
            f"Bytes differ but no text line difference found. "
            f"Original: {len(original_bytes)} bytes, Reproduced: {len(reproduced_bytes)} bytes"
        )

    assert original_bytes == reproduced_bytes, "Roundtrip must be byte-identical (comparing raw bytes)"
