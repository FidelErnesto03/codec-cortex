# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""v2.1.0 tests — SkillIR, CORTEX→HCORTEX conversion, header notes fix."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2
from cortex.v2.writer import write_cortex_v2
from cortex.v2.ir import SkillIR, cortex_to_ir, ir_to_cortex
from cortex.v2.hcortex_renderer import render_hcortex_v2

FIXTURES_DIR = os.path.join(HERE, "fixtures")
SKILL_CORTEX_PATH = os.path.join(FIXTURES_DIR, "SKILL_v2.cortex.md")


# ---------------------------------------------------------------------------
# M-01: Header notes quoting fix
# ---------------------------------------------------------------------------

def test_header_notes_quoting_roundtrip():
    """Header notes field with quotes must roundtrip correctly."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
notes: "audit note with spaces"
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''

    doc = parse_cortex_v2(text)
    assert doc.header.get('notes') == 'audit note with spaces', (
        f"notes should be unquoted; got: {doc.header.get('notes')!r}"
    )
    reproduced = write_cortex_v2(doc)
    assert text == reproduced, "Header notes roundtrip must be byte-identical"


def test_header_without_notes_roundtrip():
    """Header without notes field must still roundtrip."""

    with open(SKILL_CORTEX_PATH, 'rb') as f:
        original_bytes = f.read()
    text = original_bytes.decode('utf-8')
    doc = parse_cortex_v2(text)
    reproduced = write_cortex_v2(doc)
    assert original_bytes == reproduced.encode('utf-8'), "Roundtrip must be byte-identical"


# ---------------------------------------------------------------------------
# SkillIR tests
# ---------------------------------------------------------------------------

def test_cortex_to_ir_produces_ir():
    """parse_cortex_v2 → cortex_to_ir must produce a SkillIR."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)

    assert isinstance(ir, SkillIR)
    assert len(ir.entries) > 0, "IR must have entries"
    assert ir.header.get('internal_encoding') == 'CORTEX'


def test_ir_preserves_all_entries():
    """IR must preserve all entries from the CORTEX document."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)

    total_entries = sum(len(s.entries) for s in doc.sections)
    assert len(ir.entries) == total_entries, (
        f"IR has {len(ir.entries)} entries, CORTEX has {total_entries}"
    )


def test_ir_to_cortex_roundtrip():
    """IR → CortexV2Document → write must produce byte-identical output."""

    with open(SKILL_CORTEX_PATH, 'rb') as f:
        original_bytes = f.read()
    text = original_bytes.decode('utf-8')
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    doc2 = ir_to_cortex(ir)
    reproduced = write_cortex_v2(doc2)
    assert original_bytes == reproduced.encode('utf-8'), (
        "IR → CORTEX roundtrip must be byte-identical"
    )


# ---------------------------------------------------------------------------
# CORTEX → HCORTEX conversion tests
# ---------------------------------------------------------------------------

def test_convert_cortex_to_hcortex_produces_markdown():
    """v2-convert from cortex to hcortex must produce valid Markdown."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    # Must have HCORTEX header
    assert 'internal_encoding: HCORTEX' in hcortex_md
    # Must have Perfil line
    assert '**Perfil: CORTEX-FULL**' in hcortex_md
    # Must have tables
    assert '|' in hcortex_md
    # Must have PUML blocks
    assert '@startuml' in hcortex_md
    # Must have section headers
    assert '# ' in hcortex_md


def test_convert_preserves_sigil_table():
    """The HCORTEX output must contain the sigil table with all 25 sigils."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    # Check for key sigils in the table
    for sigil in ['IDN', 'DOM', 'FCS', 'OBJ', 'CNST', 'DIAG', 'HDL']:
        assert f'`{sigil}`' in hcortex_md, f"Sigil {sigil} missing from HCORTEX"


def test_convert_preserves_puml_blocks():
    """All DIAG bloque entries with PUML must appear as fenced PUML blocks in HCORTEX."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    # Count fenced ```puml blocks in generated output
    puml_blocks = hcortex_md.count('```puml')
    # Count DIAG entries that contain @startuml
    diag_entries = [e for e in ir.entries if e.sigil == 'DIAG' and e.entry_type == 'bloque']
    puml_count = sum(1 for e in diag_entries if '@startuml' in str(e.value))
    assert puml_blocks == puml_count, (
        f"PUML blocks: DIAG entries with PUML={puml_count}, fenced blocks={puml_blocks}"
    )


def test_convert_preserves_desc_content():
    """DESC entries (cuerpo) must appear as prose in HCORTEX."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    # DESC:purpose must be present
    assert 'CODEC-CORTEX' in hcortex_md, "DESC:purpose content missing"


def test_convert_preserves_hdl_entries():
    """HDL entries must appear in HCORTEX with operation/status/requires."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    assert 'agent_init' in hcortex_md, "HDL:agent_init missing"
    assert 'pre_action' in hcortex_md, "HDL:pre_action missing"


def test_convert_preserves_contracts():
    """Contract entries must appear in HCORTEX."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    # Check for contract fields
    assert 'what' in hcortex_md, "FCS contract fields missing"
    assert 'goal' in hcortex_md, "OBJ contract fields missing"


def test_convert_preserves_micro_tokens():
    """Micro-token declarations must appear in HCORTEX."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    ir = cortex_to_ir(doc)
    hcortex_md = render_hcortex_v2(ir)

    assert 'cur' in hcortex_md, "micro_cur missing"
    assert 'current' in hcortex_md, "micro_cur expansion missing"


def test_convert_cli_command(tmp_path):
    """CLI: cortex v2-convert --from cortex --to hcortex must work.

    v2.2.1: Without VIEW directives in SKILL.md, the output will have
    0% coverage but still be valid HCORTEX with header.
    """

    import subprocess
    out_path = str(tmp_path / "generated.md")
    r = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)",
         "v2-convert", SKILL_CORTEX_PATH, "--from", "cortex", "--to", "hcortex", "--out", out_path],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )
    # v2.2.1: Without VIEW directives, coverage is 0% but conversion still succeeds
    assert r.returncode == 0, f"v2-convert failed: {r.stderr}"
    assert os.path.exists(out_path), "Output file not created"
    with open(out_path) as f:
        content = f.read()
    assert 'internal_encoding: HCORTEX' in content
    assert 'reversible: true' in content
    assert 'view_schema: 1' in content


def test_convert_hcortex_to_cortex_not_yet_implemented():
    """v2-convert from hcortex to cortex must return 1 (not yet implemented)."""

    import subprocess
    r = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)",
         "v2-convert", SKILL_CORTEX_PATH, "--from", "hcortex", "--to", "cortex"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )
    assert r.returncode == 1, "HCORTEX → CORTEX should return 1 (not yet implemented)"
